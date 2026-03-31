<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { apiField, unwrapCrawlPayload } from '@/utils/apiField'
import { deleteStandard } from '@/api/standards'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const query = reactive({ page: 1, page_size: 20, keyword: '', status: '', category: '' })

const statusOptions = [
  { label: '现行', value: 'active' },
  { label: '即将实施', value: 'upcoming' },
  { label: '已废止', value: 'abolished' },
]

const categoryOptions = [
  { label: '国家标准', value: 'GB' },
  { label: '行业标准', value: 'JT' },
  { label: '地方标准', value: 'DB' },
  { label: '企业标准', value: 'QB' },
  { label: '检测方法', value: 'method' },
]

const dialogVisible = ref(false)
const formData = reactive({
  id: 0,
  standard_no: '',
  name: '',
  category: 'GB',
  publish_date: '',
  implement_date: '',
  status: 'active',
  replaced_by: null as number | null,
  replaced_case: '',
  remark: '',
})
const attachmentFile = ref<File | null>(null)
const dialogTitle = computed(() => formData.id ? '编辑标准' : '新增标准')

async function fetchList() {
  loading.value = true
  try {
    const res: any = await request.get('/v1/standards/', {
      params: { ...query, scope: 'all' },
    })
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, { page: 1, keyword: '', status: '', category: '' })
  fetchList()
}

function openCreate() {
  Object.assign(formData, {
    id: 0,
    standard_no: '',
    name: '',
    category: 'GB',
    publish_date: '',
    implement_date: '',
    status: 'active',
    replaced_by: null,
    replaced_case: '',
    remark: '',
  })
  attachmentFile.value = null
  dialogVisible.value = true
}

function openEdit(row: any) {
  Object.assign(formData, {
    id: row.id,
    standard_no: row.standard_no,
    name: row.name,
    category: row.category,
    publish_date: row.publish_date ?? '',
    implement_date: row.implement_date ?? row.implementation_date ?? '',
    status: row.status,
    replaced_by: row.replaced_by ?? null,
    replaced_case: row.replaced_case ?? '',
    remark: row.remark ?? '',
  })
  attachmentFile.value = null
  dialogVisible.value = true
}

function buildStandardPayload() {
  const p: Record<string, unknown> = {
    standard_no: formData.standard_no,
    name: formData.name,
    category: formData.category,
    status: formData.status,
    remark: formData.remark || '',
    publish_date: formData.publish_date || null,
    implement_date: formData.implement_date || null,
    abolish_date: null,
    replaced_case: formData.replaced_case || '',
  }
  p.replaced_by = formData.replaced_by != null ? formData.replaced_by : null
  return p
}

async function handleSubmit() {
  const payload = buildStandardPayload()
  if (attachmentFile.value) {
    const fd = new FormData()
    Object.entries(payload).forEach(([k, v]) => {
      if (v === null || v === undefined) return
      if (k === 'replaced_by' && (v as any) === '') return
      fd.append(k, String(v))
    })
    fd.append('attachment', attachmentFile.value)

    if (formData.id) {
      await request.put(`/v1/standards/${formData.id}/`, fd)
      ElMessage.success('更新成功')
    } else {
      await request.post('/v1/standards/', fd)
      ElMessage.success('创建成功')
    }
  } else {
    if (formData.id) {
      await request.put(`/v1/standards/${formData.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post('/v1/standards/', payload)
      ElMessage.success('创建成功')
    }
  }
  dialogVisible.value = false
  fetchList()
}

async function handleCrawl() {
  if (!formData.standard_no) {
    ElMessage.warning('请先填写标准编号')
    return
  }
  const raw: unknown = await request.post('/v1/standards/crawl/', { standard_no: formData.standard_no })
  const c = unwrapCrawlPayload(raw)
  const v = (k: string) => apiField(c, k)
  Object.assign(formData, {
    standard_no: (v('standard_no') as string) || formData.standard_no,
    category: (v('category') as string) || formData.category,
    status: (v('status') as string) || formData.status,
    name: (v('name') as string) || formData.name,
    publish_date: (v('publish_date') as string) ?? '',
    implement_date: (v('implement_date') as string) ?? '',
    replaced_by: (v('replaced_by') as number | null | undefined) ?? null,
    replaced_case: (v('replaced_case') as string) ?? '',
    remark: ((v('remark') as string) ?? '')
      .replace(/&nbsp;/g, ' ')
      .replace(/\\n/g, '\n'),
  })
  attachmentFile.value = null
  ElMessage.success('爬取成功，已填充表单')
}

function onAttachmentChange(e: Event) {
  const input = e.target as HTMLInputElement
  const f = input.files?.[0] ?? null
  attachmentFile.value = f
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    active: 'success', upcoming: 'warning', abolished: 'danger',
  }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  return statusOptions.find(o => o.value === status)?.label ?? status
}

function categoryLabel(cat: string) {
  return categoryOptions.find(o => o.value === cat)?.label ?? cat
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(
    `确定删除标准「${row.standard_no}」?`,
    '删除确认',
    { type: 'warning' },
  )
  await deleteStandard(row.id)
  ElMessage.success('已删除')
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container standard-list-page">
    <div class="std-hero">
      <div class="std-hero-text">
        <h2 class="std-hero-title">标准规范</h2>
        <p class="std-hero-desc">
          维护检测依据的<strong>标准号、名称、实施日期</strong>及电子版附件。录入后可到「项目参数库」为该标准配置检测方法与参数。
          支持按标准号从工标网<strong>爬取</strong>辅助填充（保存前请核对）。
        </p>
      </div>
      <router-link to="/quality/foundation" class="std-hero-link">检测基础配置总览 →</router-link>
    </div>

    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="标准号/名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="query.category" placeholder="全部" clearable style="width: 130px">
            <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>标准规范管理</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增标准</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <template #empty>
          <el-empty description="暂无标准数据，请点击「新增标准」或使用工标网爬取" />
        </template>
        <el-table-column prop="standard_no" label="标准号" width="180" />
        <el-table-column prop="name" label="标准名称" min-width="240" show-overflow-tooltip />
        <el-table-column label="分类" width="110">
          <template #default="{ row }">{{ categoryLabel(row.category) }}</template>
        </el-table-column>
        <el-table-column label="实施日期" width="120">
          <template #default="{ row }">{{ row.implement_date ?? row.implementation_date }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="附件" width="120" align="center">
          <template #default="{ row }">
            <el-link
              v-if="row.attachment"
              type="primary"
              :href="encodeURI(row.attachment)"
              target="_blank"
              :underline="false"
            >
              查看/下载
            </el-link>
            <span v-else>—</span>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" destroy-on-close>
      <el-form :model="formData" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="标准号">
              <el-input v-model="formData.standard_no" placeholder="例如：GB/T 50081-2019" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="爬取">
              <el-button type="primary" @click="handleCrawl" style="width: 100%">
                从工标网爬取
              </el-button>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="formData.category" style="width: 100%">
                <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标准名称"><el-input v-model="formData.name" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="发布日期">
              <el-date-picker v-model="formData.publish_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实施日期">
              <el-date-picker v-model="formData.implement_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="替代情况">
          <el-input
            v-model="formData.replaced_case"
            placeholder="从工标网爬取后自动填充，例如：GB/T 50081-2002"
            clearable
          />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="formData.remark" type="textarea" /></el-form-item>
        <el-form-item label="附件">
          <input type="file" @change="onAttachmentChange" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.standard-list-page .std-hero {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px 24px;
  margin-bottom: 16px;
  padding: 18px 20px;
  border-radius: 12px;
  background: linear-gradient(120deg, #f0f9ff 0%, #faf5ff 100%);
  border: 1px solid var(--el-border-color-lighter);
}

.std-hero-title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.std-hero-desc {
  margin: 0;
  max-width: 820px;
  font-size: 13px;
  line-height: 1.65;
  color: var(--el-text-color-regular);
}

.std-hero-link {
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--el-color-primary);
  text-decoration: none;
  white-space: nowrap;
}

.std-hero-link:hover {
  text-decoration: underline;
}
</style>
