<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const query = reactive({ page: 1, page_size: 20, keyword: '', status: '', category: '' })

const statusOptions = [
  { label: '现行', value: 'active' },
  { label: '即将实施', value: 'upcoming' },
  { label: '已废止', value: 'abolished' },
  { label: '被替代', value: 'replaced' },
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
  id: 0, standard_no: '', name: '', category: 'GB',
  implementation_date: '', status: 'active',
  replaced_by: '', remark: '',
})
const dialogTitle = computed(() => formData.id ? '编辑标准' : '新增标准')

async function fetchList() {
  loading.value = true
  try {
    const res: any = await request.get('/v1/standards/', { params: query })
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
    id: 0, standard_no: '', name: '', category: 'GB',
    implementation_date: '', status: 'active', replaced_by: '', remark: '',
  })
  dialogVisible.value = true
}

function openEdit(row: any) {
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (formData.id) {
    await request.put(`/v1/standards/${formData.id}/`, formData)
    ElMessage.success('更新成功')
  } else {
    await request.post('/v1/standards/', formData)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    active: 'success', upcoming: 'warning', abolished: 'danger', replaced: 'info',
  }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  return statusOptions.find(o => o.value === status)?.label ?? status
}

function categoryLabel(cat: string) {
  return categoryOptions.find(o => o.value === cat)?.label ?? cat
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
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
        <el-table-column prop="standard_no" label="标准号" width="180" />
        <el-table-column prop="name" label="标准名称" min-width="240" show-overflow-tooltip />
        <el-table-column label="分类" width="110">
          <template #default="{ row }">{{ categoryLabel(row.category) }}</template>
        </el-table-column>
        <el-table-column prop="implementation_date" label="实施日期" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
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
            <el-form-item label="标准号"><el-input v-model="formData.standard_no" /></el-form-item>
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
            <el-form-item label="实施日期">
              <el-date-picker v-model="formData.implementation_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="替代标准"><el-input v-model="formData.replaced_by" placeholder="被替代时填写新标准号" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="formData.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
