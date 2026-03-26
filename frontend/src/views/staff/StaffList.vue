<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getStaffList, createStaff, updateStaff } from '@/api/staff'

const router = useRouter()
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const query = reactive({
  page: 1, page_size: 20, keyword: '', department: '', title: '',
})

const departmentOptions = [
  { label: '检测一室', value: '检测一室' },
  { label: '检测二室', value: '检测二室' },
  { label: '检测三室', value: '检测三室' },
  { label: '综合管理部', value: '综合管理部' },
  { label: '质量管理部', value: '质量管理部' },
  { label: '技术管理部', value: '技术管理部' },
]

const titleOptions = [
  { label: '高级工程师', value: '高级工程师' },
  { label: '工程师', value: '工程师' },
  { label: '助理工程师', value: '助理工程师' },
  { label: '技术员', value: '技术员' },
]

const educationOptions = [
  { label: '博士', value: '博士' },
  { label: '硕士', value: '硕士' },
  { label: '本科', value: '本科' },
  { label: '大专', value: '大专' },
  { label: '中专', value: '中专' },
]

const dialogVisible = ref(false)
const formData = reactive({
  id: 0, staff_no: '', name: '', gender: '男', department: '',
  title: '', education: '', phone: '', email: '', entry_date: '',
})
const dialogTitle = computed(() => formData.id ? '编辑人员' : '新增人员')

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getStaffList(query)
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
  Object.assign(query, { page: 1, keyword: '', department: '', title: '' })
  fetchList()
}

function openCreate() {
  Object.assign(formData, {
    id: 0, staff_no: '', name: '', gender: '男', department: '',
    title: '', education: '', phone: '', email: '', entry_date: '',
  })
  dialogVisible.value = true
}

function openEdit(row: any) {
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (formData.id) {
    await updateStaff(formData.id, formData)
    ElMessage.success('更新成功')
  } else {
    await createStaff(formData)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

function goDetail(row: any) {
  router.push(`/staff/${row.id}`)
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="工号/姓名" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="query.department" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="d in departmentOptions" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="职称">
          <el-select v-model="query.title" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="t in titleOptions" :key="t.value" :label="t.label" :value="t.value" />
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
          <span>人员管理</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增人员</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="staff_no" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="title" label="职称" width="120" />
        <el-table-column prop="education" label="学历" width="80" />
        <el-table-column prop="cert_count" label="证书数" width="80" align="center" />
        <el-table-column prop="auth_count" label="授权项目数" width="100" align="center" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">查看</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form :model="formData" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工号"><el-input v-model="formData.staff_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名"><el-input v-model="formData.name" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-radio-group v-model="formData.gender">
                <el-radio value="男">男</el-radio>
                <el-radio value="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门">
              <el-select v-model="formData.department" style="width: 100%">
                <el-option v-for="d in departmentOptions" :key="d.value" :label="d.label" :value="d.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="职称">
              <el-select v-model="formData.title" style="width: 100%">
                <el-option v-for="t in titleOptions" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学历">
              <el-select v-model="formData.education" style="width: 100%">
                <el-option v-for="e in educationOptions" :key="e.value" :label="e.label" :value="e.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="电话"><el-input v-model="formData.phone" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱"><el-input v-model="formData.email" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="入职日期">
          <el-date-picker v-model="formData.entry_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
