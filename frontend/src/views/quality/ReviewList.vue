<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getReviewList, createReview } from '@/api/quality'
import { getUserList } from '@/api/system'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const query = reactive({ page: 1, page_size: 20, keyword: '', status: '' })

const statusOptions = [
  { label: '计划中', value: 'planned' },
  { label: '已完成', value: 'completed' },
  { label: '已关闭', value: 'closed' },
]

const userOptions = ref<{ id: number; username: string }[]>([])

const dialogVisible = ref(false)
const formData = reactive({
  review_no: '',
  title: '',
  review_date: '',
  chairperson: null as number | null,
  participants: '',
  minutes: '',
  status: 'planned',
})

async function loadUsers() {
  const res: any = await getUserList({ page_size: 500 })
  const rows = res.results ?? res.list ?? []
  userOptions.value = rows.map((u: any) => ({
    id: u.id,
    username: u.username || u.first_name || String(u.id),
  }))
}

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getReviewList(query)
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
  Object.assign(query, { page: 1, keyword: '', status: '' })
  fetchList()
}

function openCreate() {
  Object.assign(formData, {
    review_no: '',
    title: '',
    review_date: '',
    chairperson: null,
    participants: '',
    minutes: '',
    status: 'planned',
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formData.title?.trim()) {
    ElMessage.warning('请填写评审主题')
    return
  }
  if (!formData.review_date) {
    ElMessage.warning('请选择评审日期')
    return
  }
  if (!formData.chairperson) {
    ElMessage.warning('请选择主持人')
    return
  }
  await createReview({
    review_no: formData.review_no || undefined,
    title: formData.title,
    review_date: formData.review_date,
    chairperson: formData.chairperson,
    participants: formData.participants || '',
    input_materials: '',
    minutes: formData.minutes || '',
    status: formData.status,
  })
  ElMessage.success('创建成功')
  dialogVisible.value = false
  fetchList()
}

function statusTagType(status: string) {
  const map: Record<string, string> = { planned: 'info', completed: 'success', closed: '' }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  return statusOptions.find(o => o.value === status)?.label ?? status
}

onMounted(() => {
  fetchList()
  loadUsers()
})
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="评审编号/主题" clearable style="width: 200px" />
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
          <span>管理评审</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增评审</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="review_no" label="评审编号" width="150" />
        <el-table-column prop="title" label="评审主题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="review_date" label="评审日期" width="120" />
        <el-table-column prop="chairperson_name" label="主持人" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
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

    <el-dialog v-model="dialogVisible" title="新增管理评审" width="600px" destroy-on-close>
      <el-form :model="formData" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="评审编号"><el-input v-model="formData.review_no" placeholder="可留空" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评审日期">
              <el-date-picker v-model="formData.review_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="评审主题" required><el-input v-model="formData.title" /></el-form-item>
        <el-form-item label="主持人" required>
          <el-select v-model="formData.chairperson" placeholder="选择用户" filterable style="width: 100%">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="参会人员"><el-input v-model="formData.participants" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="会议纪要"><el-input v-model="formData.minutes" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="formData.status" style="width: 200px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
