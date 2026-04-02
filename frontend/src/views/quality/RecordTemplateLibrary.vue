<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Document } from '@element-plus/icons-vue'
import {
  getRecordTemplates,
  createRecordTemplate,
  updateRecordTemplate,
  deleteRecordTemplate,
  getMergedRecordSchema,
  getTestParameters,
  getTestTaskList,
  getRecordTemplateWordPreview,
} from '@/api/testing'

/** 与 GB/T 50081-2019 立方体抗压试验原始记录常见项对齐（字段名供 record_data / 合并结构使用） */
const DEFAULT_CONCRETE_COMPRESSIVE = {
  layout: 'a4-portrait',
  title: '混凝土立方体抗压强度试验原始记录',
  fields: [
    { name: 'project_no', label: '工程编号/委托编号', type: 'text', required: true },
    { name: 'sample_no', label: '试件编号', type: 'text', required: true },
    { name: 'specimen_size', label: '试件尺寸(mm)', type: 'text', default: '150×150×150' },
    { name: 'age_days', label: '试验龄期(d)', type: 'number', required: true },
    { name: 'test_date', label: '试验日期', type: 'date' },
    { name: 'load_kn', label: '破坏荷载(kN)', type: 'number', required: true },
    { name: 'fcu', label: '抗压强度代表值(MPa)', type: 'number' },
    { name: 'env_temp', label: '环境温度(℃)', type: 'number' },
    { name: 'env_hum', label: '相对湿度(%)', type: 'number' },
    { name: 'equipment', label: '压力试验机型号/管理编号', type: 'text' },
    { name: 'tester', label: '试验人', type: 'text' },
  ],
}

type FieldRow = {
  name: string
  label: string
  type: string
  required?: boolean
  default?: string
  unit?: string
}

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 20, keyword: '', test_parameter: '' as string | number | '' })

const paramOptions = ref<{ id: number; name: string; code: string }[]>([])

const dialogVisible = ref(false)
const createMode = ref<'form' | 'document'>('form')
const form = reactive({
  id: 0,
  name: '',
  code: '',
  test_parameter: null as number | null,
  test_parameters: [] as number[],
  word_file: null as File | null,
  word_template_url: '',
  version: '1.0',
  schema_text: JSON.stringify({ fields: [] as any[] }, null, 2),
  is_active: true,
})

const schemaEditTab = ref<'visual' | 'json'>('visual')
const recordTitle = ref('原始记录')
const fieldRows = ref<FieldRow[]>([])

const dialogTitle = computed(() => (form.id ? '编辑模板' : '新增模板'))

const previewSchema = computed(() => {
  try {
    const o = JSON.parse(form.schema_text)
    return o && typeof o === 'object' ? o : { fields: [] }
  } catch {
    return { fields: [] }
  }
})

const previewFields = computed(() => {
  const f = previewSchema.value.fields
  return Array.isArray(f) ? f : []
})

const previewTaskId = ref<number | null>(null)
const taskOptions = ref<{ id: number; task_no: string; label: string }[]>([])
const previewJson = ref('')
const previewLoading = ref(false)
const wordPreviewJson = ref('')
const wordPreviewLoading = ref(false)
const previewTemplate = ref<any | null>(null)
const syncingFormState = ref(false)

const route = useRoute()

const previewTemplateSchema = computed<Record<string, any>>(() => {
  const raw = previewTemplate.value?.schema
  if (raw && typeof raw === 'object') return raw
  return { fields: [] }
})

const previewTemplateFields = computed<any[]>(() => {
  const f = previewTemplateSchema.value?.fields
  return Array.isArray(f) ? f : []
})

const previewTemplateIsDocument = computed<boolean>(() => {
  return previewTemplate.value?.template_kind === 'document' || !!previewTemplate.value?.word_template_url
})

const previewTemplatePdfUrl = computed<string>(() => {
  const url = String(previewTemplate.value?.word_template_url || '')
  return /\.pdf(\?|$)/i.test(url) ? url : ''
})

async function loadParams() {
  const res: any = await getTestParameters({ page_size: 500 })
  const rows = res.results ?? res.list ?? []
  paramOptions.value = rows.map((p: any) => ({ id: p.id, name: p.name, code: p.code }))
}

async function loadRecentTasks() {
  try {
    const res: any = await getTestTaskList({ page_size: 80, ordering: '-id' })
    const rows = res.results ?? res.list ?? []
    taskOptions.value = rows.map((t: any) => ({
      id: t.id,
      task_no: t.task_no,
      label: `${t.task_no}${t.sample_name ? ` · ${t.sample_name}` : ''}`,
    }))
    if (!previewTaskId.value && taskOptions.value.length) {
      previewTaskId.value = taskOptions.value[0].id
    }
  } catch {
    taskOptions.value = []
  }
}


function parseSchema() {
  try {
    return JSON.parse(form.schema_text)
  } catch {
    return null
  }
}

function loadFieldRowsFromSchemaText() {
  const s = parseSchema()
  if (!s || typeof s !== 'object') {
    fieldRows.value = []
    recordTitle.value = '原始记录'
    return
  }
  recordTitle.value = (s as any).title || '原始记录'
  const f = (s as any).fields
  fieldRows.value = Array.isArray(f)
    ? f.map((x: any) => ({
      name: x.name ?? '',
      label: x.label ?? '',
      type: x.type ?? 'text',
      required: !!x.required,
      default: x.default ?? '',
      unit: x.unit ?? '',
    }))
    : []
}

function syncFieldRowsToSchemaText() {
  const fields = fieldRows.value.map((r) => {
    const o: Record<string, unknown> = {
      name: r.name.trim(),
      label: r.label.trim(),
      type: r.type || 'text',
    }
    if (r.required) o.required = true
    if (r.default) o.default = r.default
    if (r.unit) o.unit = r.unit
    return o
  })
  const obj: Record<string, unknown> = {
    layout: 'a4-portrait',
    title: recordTitle.value || '原始记录',
    fields,
  }
  form.schema_text = JSON.stringify(obj, null, 2)
}

watch(
  fieldRows,
  () => {
    if (dialogVisible.value && schemaEditTab.value === 'visual') {
      syncFieldRowsToSchemaText()
    }
  },
  { deep: true },
)

watch(recordTitle, () => {
  if (dialogVisible.value && schemaEditTab.value === 'visual') {
    syncFieldRowsToSchemaText()
  }
})

watch(schemaEditTab, (tab) => {
  if (tab === 'visual') {
    loadFieldRowsFromSchemaText()
  }
})

function addFieldRow() {
  fieldRows.value.push({
    name: `field_${fieldRows.value.length + 1}`,
    label: '新字段',
    type: 'text',
    required: false,
  })
}

function removeFieldRow(i: number) {
  fieldRows.value.splice(i, 1)
}

function applyConcreteTemplate() {
  const t = DEFAULT_CONCRETE_COMPRESSIVE
  recordTitle.value = t.title
  fieldRows.value = t.fields.map((x) => ({ ...x }))
  syncFieldRowsToSchemaText()
  ElMessage.success('已套用混凝土立方体抗压强度原始记录字段（可按需增删）')
}

async function fetchList() {
  loading.value = true
  try {
    const params: any = { ...query }
    if (params.test_parameter === '' || params.test_parameter === null) delete params.test_parameter
    const res: any = await getRecordTemplates(params)
    tableData.value = res.results ?? res.list ?? []
    if (previewTemplate.value?.id) {
      previewTemplate.value = tableData.value.find((x: any) => x.id === previewTemplate.value.id) || null
    }
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

function handleTemplatePreview(row: any) {
  previewTemplate.value = row
}

function openCreateDocument() {
  createMode.value = 'document'
  syncingFormState.value = true
  Object.assign(form, {
    id: 0,
    name: '',
    code: '',
    test_parameter: null,
    test_parameters: [],
    word_file: null,
    word_template_url: '',
    version: '1.0',
    schema_text: JSON.stringify({ layout: 'a4-portrait', title: '文档模板', fields: [] }, null, 2),
    is_active: true,
  })
  syncingFormState.value = false
  schemaEditTab.value = 'json'
  dialogVisible.value = true
}

function openCreate() {
  createMode.value = 'form'
  syncingFormState.value = true
  Object.assign(form, {
    id: 0,
    name: '',
    code: '',
    test_parameter: null,
    test_parameters: [],
    word_file: null,
    word_template_url: '',
    version: '1.0',
    schema_text: JSON.stringify(DEFAULT_CONCRETE_COMPRESSIVE, null, 2),
    is_active: true,
  })
  syncingFormState.value = false
  recordTitle.value = DEFAULT_CONCRETE_COMPRESSIVE.title
  fieldRows.value = DEFAULT_CONCRETE_COMPRESSIVE.fields.map((x) => ({ ...x }))
  schemaEditTab.value = 'visual'
  dialogVisible.value = true
}

function openEdit(row: any) {
  createMode.value = row?.template_kind === 'document' || !!row?.word_template_url ? 'document' : 'form'
  syncingFormState.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    code: row.code,
    test_parameter: row.test_parameter ?? null,
    test_parameters: Array.isArray(row.test_parameters)
      ? row.test_parameters
      : (row.test_parameter ? [row.test_parameter] : []),
    word_file: null,
    word_template_url: row.word_template_url || '',
    version: row.version ?? '1.0',
    schema_text: JSON.stringify(row.schema ?? { fields: [] }, null, 2),
    is_active: row.is_active !== false,
  })
  syncingFormState.value = false
  schemaEditTab.value = 'visual'
  loadFieldRowsFromSchemaText()
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name?.trim() || !form.code?.trim()) {
    ElMessage.warning('请填写模板名称与编号')
    return
  }
  if (!form.test_parameter) {
    ElMessage.warning('请选择检测参数')
    return
  }
  if (schemaEditTab.value === 'visual') {
    syncFieldRowsToSchemaText()
  }
  const schema = parseSchema()
  if (createMode.value === 'form' && (!schema || !Array.isArray((schema as any).fields))) {
    ElMessage.warning('表单定义需包含 fields 数组；可切换到「可视化」修正')
    return
  }
  if (createMode.value === 'document' && !form.id && !form.word_file) {
    ElMessage.warning('文档模板请上传文件')
    return
  }
  const fd = new FormData()
  fd.append('name', form.name.trim())
  fd.append('code', form.code.trim())
  fd.append('test_parameter', String(form.test_parameter))
  for (const pid of form.test_parameters || []) fd.append('test_parameters', String(pid))
  fd.append('version', form.version || '1.0')
  fd.append('schema', JSON.stringify(schema || { layout: 'a4-portrait', title: '文档模板', fields: [] }))
  fd.append('is_active', form.is_active ? 'true' : 'false')
  if (form.word_file) fd.append('word_template', form.word_file)
  if (form.id) {
    await updateRecordTemplate(form.id, fd)
    ElMessage.success('更新成功')
  } else {
    await createRecordTemplate(fd)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除模板「${row.name}」?`, '提示', { type: 'warning' })
  await deleteRecordTemplate(row.id)
  ElMessage.success('已删除')
  fetchList()
}



async function handlePreviewWordTemplate(row: any) {
  const tid = previewTaskId.value
  if (!tid) {
    ElMessage.warning('请先选择下方检测任务后再预览占位符')
    return
  }
  wordPreviewLoading.value = true
  try {
    const data: any = await getRecordTemplateWordPreview(row.id, tid)
    wordPreviewJson.value = JSON.stringify(data, null, 2)
    ElMessage.success('已生成占位符预览')
  } catch (e: any) {
    const msg = e?.response?.data?.message || e?.message || '预览失败'
    ElMessage.error(String(msg))
  } finally {
    wordPreviewLoading.value = false
  }
}

async function handlePreviewMerged() {
  const tid = previewTaskId.value
  if (!tid) {
    ElMessage.warning('请选择检测任务')
    return
  }
  previewLoading.value = true
  previewJson.value = ''
  try {
    const data: any = await getMergedRecordSchema(tid)
    previewJson.value = JSON.stringify(data, null, 2)
  } catch (e: any) {
    const msg = e?.response?.data?.message || e?.message || '加载失败'
    previewJson.value = JSON.stringify({ error: msg }, null, 2)
    ElMessage.error(String(msg))
  } finally {
    previewLoading.value = false
  }
}

onMounted(async () => {
  const q = route.query.task_id
  const tid = q ? Number(Array.isArray(q) ? q[0] : q) : NaN
  if (Number.isFinite(tid) && tid > 0) {
    previewTaskId.value = tid
  }
  fetchList()
  await loadParams()
  await loadRecentTasks()
  if (Number.isFinite(tid) && tid > 0) {
    await handlePreviewMerged()
  }
})
</script>

<template>
  <div class="page-container record-tpl-page">
    <div class="record-tpl-hero">
      <div>
        <h2 class="record-tpl-title">原始记录模板</h2>
        <p class="record-tpl-desc">
          依赖「项目参数库」中已维护的<strong>检测参数</strong>；可为每个模板配置<strong>关联参数（多选）</strong>。版式按<strong>竖版 A4</strong>预览；检测任务会按参数将多模板<strong>合并</strong>为可填结构。
        </p>
      </div>
      <router-link class="record-tpl-link" to="/quality/foundation">← 检测基础配置</router-link>
    </div>

    <el-alert
      v-if="route.query.task_id"
      type="success"
      :closable="false"
      show-icon
      class="record-tpl-alert"
    >
      <template #title>
        已从检测任务跳转（task_id={{ route.query.task_id }}），已尝试加载<strong>合并结构</strong>预览；亦可改选下方任务后重新预览。
      </template>
    </el-alert>

    <el-alert type="info" :closable="false" show-icon class="record-tpl-alert">
      <template #title>
        未指定关联参数时为<strong>方法通用模板</strong>；指定关联参数时优先匹配参数模板。合并预览请选择一条真实检测任务。
      </template>
    </el-alert>

    <el-card shadow="never">
      <el-form inline @submit.prevent="() => { query.page = 1; fetchList() }">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="名称/编号" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="检测参数">
          <el-select v-model="query.test_parameter" placeholder="全部" clearable filterable style="width: 220px">
            <el-option v-for="p in paramOptions" :key="p.id" :label="`${p.name} (${p.code})`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="() => { query.page = 1; fetchList() }">搜索</el-button>
          <el-button :icon="Refresh" @click="() => { Object.assign(query, { page: 1, keyword: '', test_parameter: '' }); fetchList() }">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>原始记录模板</span>
          <el-space>
            <el-button v-permission="'testing:create'" type="primary" :icon="Plus" @click="openCreate">新增模板</el-button>
            <el-button v-permission="'testing:create'" type="success" :icon="Document" @click="openCreateDocument">新增文档模板</el-button>
          </el-space>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="code" label="模板编号" width="140" />
        <el-table-column prop="name" label="模板名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="模板类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.template_kind === 'document' ? 'warning' : 'success'" size="small">{{ row.template_kind === 'document' ? '文档' : '表单' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联参数" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ (row.parameter_names && row.parameter_names.length) ? row.parameter_names.join('、') : (row.parameter_name || '（通用）') }}</template>
        </el-table-column>
        <el-table-column label="文档文件" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            <a v-if="row.word_template_url" :href="row.word_template_url" target="_blank" rel="noopener">查看文件</a>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column label="启用" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'testing:view'" link type="primary" @click="handleTemplatePreview(row)">预览</el-button>
            <el-button v-permission="'testing:edit'" link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-permission="'testing:view'" link type="success" :loading="wordPreviewLoading" @click="handlePreviewWordTemplate(row)">占位预览</el-button>
            <el-button v-permission="'testing:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        style="margin-top: 16px; justify-content: flex-end"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-size="query.page_size"
        :current-page="query.page"
        :page-sizes="[20, 50, 100]"
        @current-change="(p: number) => { query.page = p; fetchList() }"
        @size-change="(s: number) => { query.page_size = s; query.page = 1; fetchList() }"
      />
      <el-input
        v-if="wordPreviewJson"
        v-model="wordPreviewJson"
        type="textarea"
        :rows="10"
        readonly
        class="merge-json"
      />
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <span>中间预览窗口</span>
      </template>
      <el-empty v-if="!previewTemplate" description="请在模板列表点击“预览”" />
      <template v-else-if="!previewTemplateIsDocument">
        <div class="merge-hint" style="margin-bottom: 10px">
          表单模板：{{ previewTemplate.name }}（{{ previewTemplate.code }}）
        </div>
        <el-table :data="previewTemplateFields" stripe border size="small">
          <el-table-column type="index" width="50" label="#" />
          <el-table-column prop="label" label="显示标签" min-width="180" />
          <el-table-column prop="name" label="字段名" min-width="150" />
          <el-table-column prop="type" label="类型" width="110" />
          <el-table-column label="必填" width="90" align="center">
            <template #default="{ row }">{{ row.required ? '是' : '否' }}</template>
          </el-table-column>
        </el-table>
      </template>
      <template v-else>
        <div class="merge-hint" style="margin-bottom: 10px">
          文档模板：{{ previewTemplate.name }}（{{ previewTemplate.code }}）
        </div>
        <iframe
          v-if="previewTemplatePdfUrl"
          :src="previewTemplatePdfUrl"
          style="width: 100%; height: 560px; border: 1px solid var(--el-border-color-light); border-radius: 8px"
        />
        <el-alert v-else type="warning" :closable="false" show-icon>
          <template #title>
            当前文档不是 PDF，暂不支持内嵌预览。请通过
            <a v-if="previewTemplate.word_template_url" :href="previewTemplate.word_template_url" target="_blank" rel="noopener">查看文件</a>
            <span v-else>已上传文件</span>
            打开。
          </template>
        </el-alert>
      </template>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <span>合并预览（按检测任务）</span>
      </template>
      <p class="merge-hint">
        选择检测任务后点击预览，返回 <code>sections</code>（各参数模板）与 <code>merged_fields</code>（字段合并列表）。需数据库中已存在该任务及关联方法/参数。
      </p>
      <el-space wrap alignment="center">
        <el-select
          v-model="previewTaskId"
          placeholder="选择检测任务"
          filterable
          clearable
          style="width: min(100%, 420px)"
        >
          <el-option
            v-for="t in taskOptions"
            :key="t.id"
            :label="t.label"
            :value="t.id"
          />
        </el-select>
        <el-button v-permission="'testing:view'" type="primary" :loading="previewLoading" @click="handlePreviewMerged">预览合并结构</el-button>
        <el-button v-permission="'testing:view'" text type="primary" @click="loadRecentTasks">刷新任务列表</el-button>
      </el-space>
      <el-input
        v-if="previewJson"
        v-model="previewJson"
        type="textarea"
        :rows="16"
        readonly
        class="merge-json"
      />
      <el-input
        v-if="wordPreviewJson"
        v-model="wordPreviewJson"
        type="textarea"
        :rows="10"
        readonly
        class="merge-json"
      />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="min(960px, 96vw)"
      destroy-on-close
      class="tpl-dialog"
      align-center
    >
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="模板编号" required>
              <el-input v-model="form.code" :disabled="!!form.id" placeholder="唯一，如 TPL-GB-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="模板名称" required>
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="检测参数" required>
              <el-select v-model="form.test_parameter" placeholder="选择参数" filterable style="width: 100%">
                <el-option v-for="p in paramOptions" :key="p.id" :label="`${p.name} (${p.code})`" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联参数">
              <el-select v-model="form.test_parameters" multiple clearable filterable placeholder="可不选；不选则为方法通用模板" style="width:100%">
                <el-option v-for="p in paramOptions" :key="`m_${p.id}`" :label="`${p.name} (${p.code})`" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Word模板">
              <el-upload :auto-upload="false" :show-file-list="false" accept=".doc,.docx,.xls,.xlsx,.pdf" :on-change="(f:any)=>{form.word_file=f.raw}">
                <el-button>选择Word文件</el-button>
              </el-upload>
              <span style="margin-left:8px;color:var(--el-text-color-secondary);font-size:12px;">{{ form.word_file ? form.word_file.name : (form.word_template_url ? '已上传' : '未上传') }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="占位符">
              <el-text type="info">支持：%工程名称%、%委托编号%、%样品编号%、%样品名称%、%规格型号%（Word/Excel/PDF 文档模板同样可用）</el-text>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="版本">
              <el-input v-model="form.version" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="启用">
              <el-switch v-model="form.is_active" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-tabs v-if="createMode === 'form'" v-model="schemaEditTab" class="schema-tabs">
          <el-tab-pane label="可视化字段表" name="visual">
            <div class="visual-toolbar">
              <el-input v-model="recordTitle" placeholder="原始记录标题（页眉）" style="max-width: 420px" />
              <el-button
                v-permission="form.id ? 'testing:edit' : 'testing:create'"
                type="primary"
                :icon="Document"
                @click="applyConcreteTemplate"
              >
                套用混凝土抗压模板
              </el-button>
              <el-button v-permission="form.id ? 'testing:edit' : 'testing:create'" @click="addFieldRow">新增一行</el-button>
            </div>
            <el-table :data="fieldRows" border size="small" max-height="280" class="field-edit-table">
              <el-table-column label="#" type="index" width="45" align="center" />
              <el-table-column label="字段名 name" min-width="120">
                <template #default="{ row }">
                  <el-input v-model="row.name" placeholder="英文/拼音" />
                </template>
              </el-table-column>
              <el-table-column label="显示标签" min-width="120">
                <template #default="{ row }">
                  <el-input v-model="row.label" />
                </template>
              </el-table-column>
              <el-table-column label="类型" width="120">
                <template #default="{ row }">
                  <el-select v-model="row.type" style="width: 100%">
                    <el-option label="文本" value="text" />
                    <el-option label="数字" value="number" />
                    <el-option label="日期" value="date" />
                    <el-option label="多行" value="textarea" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="必填" width="70" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.required" />
                </template>
              </el-table-column>
              <el-table-column label="默认值/单位" min-width="100">
                <template #default="{ row }">
                  <el-input v-model="row.default" placeholder="默认" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="" width="70" fixed="right">
                <template #default="{ $index }">
                  <el-button v-permission="form.id ? 'testing:edit' : 'testing:create'" link type="danger" @click="removeFieldRow($index)">删</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="a4-wrap">
              <div class="a4-label">竖版 A4 预览（210×297mm，仅示意排版）</div>
              <div class="a4-sheet">
                <header class="a4-header">{{ recordTitle || '原始记录' }}</header>
                <table class="a4-table">
                  <tbody>
                    <tr v-for="(f, idx) in previewFields" :key="idx">
                      <td class="a4-td-label">{{ f.label }}</td>
                      <td class="a4-td-val">
                        <span class="a4-placeholder">{{ f.type === 'number' ? '____.__' : '________' }}</span>
                        <span v-if="f.unit" class="a4-unit">{{ f.unit }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <p class="a4-foot">字段数 {{ previewFields.length }} · layout: a4-portrait</p>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="JSON 源码" name="json">
            <el-input
              v-model="form.schema_text"
              type="textarea"
              :rows="18"
              placeholder='{"layout":"a4-portrait","title":"...","fields":[...]}'
              class="json-textarea"
            />
            <p class="json-hint">直接编辑 JSON 后，可切回「可视化」同步（会按 JSON 覆盖表格）。</p>
          </el-tab-pane>
        </el-tabs>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-permission="form.id ? 'testing:edit' : 'testing:create'" type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.record-tpl-page .record-tpl-hero {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
  padding: 16px 18px;
  border-radius: 12px;
  background: linear-gradient(120deg, #ecfdf5 0%, #f0f9ff 100%);
  border: 1px solid var(--el-border-color-lighter);
}

.record-tpl-title {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 700;
}

.record-tpl-desc {
  margin: 0;
  max-width: 880px;
  font-size: 13px;
  line-height: 1.65;
  color: var(--el-text-color-regular);
}

.record-tpl-link {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-color-primary);
  text-decoration: none;
  white-space: nowrap;
}

.record-tpl-link:hover {
  text-decoration: underline;
}

.record-tpl-alert {
  margin-bottom: 16px;
  border-radius: 10px;
}

.merge-hint {
  margin: 0 0 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.55;
}

.merge-hint code {
  font-size: 12px;
  padding: 2px 6px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.merge-json {
  margin-top: 12px;
  font-family: ui-monospace, monospace;
  font-size: 12px;
}

.schema-tabs {
  margin-top: 8px;
}

.visual-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}

.field-edit-table {
  margin-bottom: 16px;
}

.a4-wrap {
  margin-top: 8px;
}

.a4-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

/* 竖版 A4 比例：宽 210mm 高 297mm，缩放展示 */
.a4-sheet {
  width: 210mm;
  max-width: 100%;
  min-height: 120mm;
  aspect-ratio: 210 / 297;
  box-sizing: border-box;
  padding: 10mm 12mm;
  background: #fff;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transform: scale(0.72);
  transform-origin: top left;
  margin-bottom: -80px;
}

.a4-header {
  text-align: center;
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #333;
}

.a4-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.a4-table td {
  border: 1px solid #999;
  padding: 6px 8px;
  vertical-align: middle;
}

.a4-td-label {
  width: 38%;
  background: #f5f7fa;
  font-weight: 500;
}

.a4-td-val {
  min-height: 22px;
}

.a4-placeholder {
  color: #c0c4cc;
  letter-spacing: 1px;
}

.a4-unit {
  margin-left: 6px;
  color: var(--el-text-color-secondary);
  font-size: 10px;
}

.a4-foot {
  margin: 10px 0 0;
  font-size: 10px;
  color: #909399;
}

.json-textarea {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}

.json-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
