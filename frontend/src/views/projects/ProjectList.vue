<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, View } from '@element-plus/icons-vue'
import { getProjectList, createProject, updateProject, deleteProject } from '@/api/projects'
import type { Project } from '@/types/project'

const router = useRouter()
const loading = ref(false)
const tableData = ref<Project[]>([])
const total = ref(0)

const query = reactive({
  page: 1, page_size: 20, search: '', status: '', project_type: '',
})

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()

const form = reactive({
  id: 0,
  code: '',
  name: '',
  project_type: '',
  status: '',
  address: '',
  start_date: '',
  end_date: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入工程名称', trigger: 'blur' }],
  project_type: [{ required: true, message: '请选择工程类型', trigger: 'change' }],
}

const typeOptions = [
  { label: '房建工程', value: 'building' },
  { label: '市政工程', value: 'municipal' },
  { label: '交通工程', value: 'transport' },
  { label: '水利工程', value: 'water' },
  { label: '机场工程', value: 'airport' },
  { label: '其他', value: 'other' },
]

const statusOptions = [
  { label: '进行中', value: 'active' },
  { label: '已竣工', value: 'completed' },
  { label: '已暂停', value: 'suspended' },
]

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getProjectList(query)
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
  Object.assign(query, { page: 1, search: '', status: '', project_type: '' })
  fetchList()
}

function openCreate() {
  dialogTitle.value = '新增工程项目'
  Object.assign(form, {
    id: 0,
    code: '',
    name: '',
    project_type: '',
    status: 'active',
    address: '',
    start_date: '',
    end_date: '',
    description: '',
  })
  dialogVisible.value = true
}

function openEdit(row: Project) {
  dialogTitle.value = '编辑工程项目'
  Object.assign(form, {
    id: row.id,
    code: (row as any).code ?? row.project_no ?? '',
    name: row.name,
    project_type: (row as any).project_type ?? row.type ?? '',
    status: row.status,
    address: row.address ?? '',
    start_date: row.start_date ?? '',
    end_date: row.end_date ?? '',
    description: row.description ?? '',
  })
  dialogVisible.value = true
}

function buildProjectPayload() {
  const payload: Record<string, unknown> = {
    name: form.name,
    address: form.address || '',
    project_type: form.project_type,
    status: form.status || 'active',
    start_date: form.start_date || null,
    end_date: form.end_date || null,
    description: form.description || '',
  }
  const code = (form.code || '').trim()
  if (code) {
    payload.code = code
  }
  return payload
}

async function handleSubmit() {
  await formRef.value?.validate()
  const payload = buildProjectPayload()
  if (form.id) {
    await updateProject(form.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createProject(payload)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

async function handleDelete(row: Project) {
  await ElMessageBox.confirm('确认删除该项目？', '提示', { type: 'warning' })
  await deleteProject(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

function goDetail(row: Project) {
  router.push(`/project/${row.id}`)
}

function typeLabel(val: string) {
  return typeOptions.find(o => o.value === val)?.label ?? val
}

function rowCode(row: Project) {
  return (row as any).code ?? row.project_no ?? ''
}

function rowProjectType(row: Project) {
  return (row as any).project_type ?? row.type ?? ''
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    active: 'success', completed: 'info', suspended: 'warning',
  }
  return map[status] ?? 'info'
}

function statusLabel(val: string) {
  return statusOptions.find(o => o.value === val)?.label ?? val
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.search" placeholder="项目编号/名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="工程类型">
          <el-select v-model="query.project_type" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
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
          <span>工程项目列表</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增项目</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column label="项目编号" width="160">
          <template #default="{ row }">{{ rowCode(row) }}</template>
        </el-table-column>
        <el-table-column prop="name" label="工程名称" min-width="200" show-overflow-tooltip />
        <el-table-column label="工程类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel(rowProjectType(row)) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开工日期" width="120" />
        <el-table-column prop="end_date" label="竣工日期" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :icon="View" @click="goDetail(row)">查看</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="项目编号">
              <el-input v-model="form.code" placeholder="留空则自动生成" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工程名称" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工程类型" prop="project_type">
              <el-select v-model="form.project_type" placeholder="请选择" style="width: 100%">
                <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" placeholder="请选择" style="width: 100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="工程地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开工日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="竣工日期">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
