<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import {
  getRecordTemplates,
  createRecordTemplate,
  updateRecordTemplate,
  deleteRecordTemplate,
  getMergedRecordSchema,
  getTestMethods,
  getTestParameters,
} from '@/api/testing'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 20, keyword: '', test_method: '' as string | number | '' })

const methodOptions = ref<{ id: number; name: string }[]>([])
const paramOptions = ref<{ id: number; name: string; code: string }[]>([])

const dialogVisible = ref(false)
const form = reactive({
  id: 0,
  name: '',
  code: '',
  test_method: null as number | null,
  test_parameter: null as number | null,
  version: '1.0',
  schema_text: JSON.stringify({ fields: [] as any[] }, null, 2),
  is_active: true,
})

const dialogTitle = computed(() => (form.id ? '编辑模板' : '新增模板'))

const previewTaskId = ref<number | null>(null)
const previewJson = ref('')
const previewLoading = ref(false)

async function loadMethods() {
  const res: any = await getTestMethods({ page_size: 500 })
  const rows = res.results ?? res.list ?? []
  methodOptions.value = rows.map((m: any) => ({ id: m.id, name: `${m.standard_no} ${m.name}` }))
}

async function loadParamsForMethod(methodId: number | null) {
  paramOptions.value = []
  if (!methodId) return
  const res: any = await getTestParameters({ method: methodId, page_size: 500 })
  const rows = res.results ?? res.list ?? []
  paramOptions.value = rows.map((p: any) => ({ id: p.id, name: p.name, code: p.code }))
}

watch(
  () => form.test_method,
  (id) => {
    form.test_parameter = null
    loadParamsForMethod(id)
  },
)

async function fetchList() {
  loading.value = true
  try {
    const params: any = { ...query }
    if (params.test_method === '' || params.test_method === null) delete params.test_method
    const res: any = await getRecordTemplates(params)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, {
    id: 0,
    name: '',
    code: '',
    test_method: null,
    test_parameter: null,
    version: '1.0',
    schema_text: JSON.stringify({ fields: [{ name: 'example', label: '示例字段', type: 'text' }] }, null, 2),
    is_active: true,
  })
  paramOptions.value = []
  dialogVisible.value = true
}

function openEdit(row: any) {
  Object.assign(form, {
    id: row.id,
    name: row.name,
    code: row.code,
    test_method: row.test_method ?? null,
    test_parameter: row.test_parameter ?? null,
    version: row.version ?? '1.0',
    schema_text: JSON.stringify(row.schema ?? { fields: [] }, null, 2),
    is_active: row.is_active !== false,
  })
  if (form.test_method) loadParamsForMethod(form.test_method)
  dialogVisible.value = true
}

function parseSchema() {
  try {
    return JSON.parse(form.schema_text)
  } catch {
    return null
  }
}

async function handleSubmit() {
  if (!form.name?.trim() || !form.code?.trim()) {
    ElMessage.warning('请填写模板名称与编号')
    return
  }
  if (!form.test_method) {
    ElMessage.warning('请选择检测方法')
    return
  }
  const schema = parseSchema()
  if (!schema) {
    ElMessage.warning('表单定义 JSON 格式不正确')
    return
  }
  const payload: any = {
    name: form.name.trim(),
    code: form.code.trim(),
    test_method: form.test_method,
    test_parameter: form.test_parameter || null,
    version: form.version || '1.0',
    schema,
    is_active: form.is_active,
  }
  if (form.id) {
    await updateRecordTemplate(form.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createRecordTemplate(payload)
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

async function handlePreviewMerged() {
  if (!previewTaskId.value) {
    ElMessage.warning('请输入检测任务 ID')
    return
  }
  previewLoading.value = true
  previewJson.value = ''
  try {
    const data: any = await getMergedRecordSchema(previewTaskId.value)
    previewJson.value = JSON.stringify(data, null, 2)
  } catch (e: any) {
    previewJson.value = e?.message || '加载失败'
  } finally {
    previewLoading.value = false
  }
}

onMounted(() => {
  fetchList()
  loadMethods()
})
</script>

<template>
  <div class="page-container">
    <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px">
      <template #title>
        为每个<strong>检测参数</strong>配置独立的原始记录表单（JSON）；检测任务会按参数将模板<strong>合并</strong>为一份可填写的总表结构。
        未指定参数时，可作为该检测方法下的通用模板。
      </template>
    </el-alert>

    <el-card shadow="never">
      <el-form inline @submit.prevent="() => { query.page = 1; fetchList() }">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="名称/编号" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="检测方法">
          <el-select v-model="query.test_method" placeholder="全部" clearable filterable style="width: 220px">
            <el-option v-for="m in methodOptions" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="() => { query.page = 1; fetchList() }">搜索</el-button>
          <el-button :icon="Refresh" @click="() => { Object.assign(query, { page: 1, keyword: '', test_method: '' }); fetchList() }">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>原始记录模板</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增模板</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="code" label="模板编号" width="140" />
        <el-table-column prop="name" label="模板名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="method_name" label="检测方法" min-width="200" show-overflow-tooltip />
        <el-table-column label="检测参数" width="140">
          <template #default="{ row }">{{ row.parameter_name || '（通用）' }}</template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column label="启用" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <span>合并预览（按检测任务）</span>
      </template>
      <p style="margin: 0 0 12px; color: var(--el-text-color-secondary); font-size: 13px">
        输入「检测任务」主键 ID，可预览该任务下按检测参数合并后的原始记录结构（供原始记录录入页使用）。
      </p>
      <el-space wrap>
        <el-input-number v-model="previewTaskId" :min="1" placeholder="任务 ID" controls-position="right" style="width: 160px" />
        <el-button type="primary" :loading="previewLoading" @click="handlePreviewMerged">预览合并结构</el-button>
      </el-space>
      <el-input
        v-if="previewJson"
        v-model="previewJson"
        type="textarea"
        :rows="14"
        readonly
        style="margin-top: 12px; font-family: monospace; font-size: 12px"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-form-item label="模板编号" required>
          <el-input v-model="form.code" :disabled="!!form.id" placeholder="唯一，如 TPL-GB-001" />
        </el-form-item>
        <el-form-item label="模板名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="检测方法" required>
          <el-select v-model="form.test_method" placeholder="选择方法" filterable style="width: 100%">
            <el-option v-for="m in methodOptions" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检测参数">
          <el-select v-model="form.test_parameter" placeholder="不选则为该方法通用模板" clearable filterable style="width: 100%">
            <el-option v-for="p in paramOptions" :key="p.id" :label="`${p.name} (${p.code})`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="form.version" style="width: 120px" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item label="表单定义 JSON">
          <el-input v-model="form.schema_text" type="textarea" :rows="10" placeholder='{"fields": [...]}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
