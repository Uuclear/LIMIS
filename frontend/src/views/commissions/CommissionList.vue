<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getCommissionList, deleteCommission, submitCommission } from '@/api/commissions'
import type { Commission } from '@/types/commission'

const router = useRouter()
const loading = ref(false)
const tableData = ref<Commission[]>([])
const total = ref(0)
const activeStatus = ref('')

const query = reactive({
  page: 1, page_size: 20, keyword: '', status: '',
})

const statusTabs = [
  { label: '全部', value: '' },
  { label: '草稿', value: 'draft' },
  { label: '待评审', value: 'pending_review' },
  { label: '已评审', value: 'reviewed' },
  { label: '已退回', value: 'rejected' },
]

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getCommissionList({ ...query, status: activeStatus.value || undefined })
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

function handleTabChange(status: string) {
  activeStatus.value = status
  query.page = 1
  fetchList()
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  query.keyword = ''
  handleSearch()
}

function goCreate() {
  router.push('/entrustment/create')
}

function goDetail(row: Commission) {
  router.push(`/entrustment/${row.id}`)
}

function goEdit(row: Commission) {
  router.push(`/entrustment/${row.id}/edit`)
}

async function handleSubmitReview(row: Commission) {
  await ElMessageBox.confirm('确认提交评审？提交后不可编辑。', '提示', { type: 'warning' })
  await submitCommission(row.id)
  ElMessage.success('已提交评审')
  fetchList()
}

async function handleDelete(row: Commission) {
  await ElMessageBox.confirm('确认删除该委托？', '提示', { type: 'warning' })
  await deleteCommission(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    draft: 'info', pending_review: 'warning', reviewed: 'success', rejected: 'danger',
  }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    draft: '草稿', pending_review: '待评审', reviewed: '已评审', rejected: '已退回',
  }
  return map[status] ?? status
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="委托编号/工程名称" clearable style="width: 220px" />
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
          <span>委托管理</span>
          <el-button type="primary" :icon="Plus" @click="goCreate">新增委托</el-button>
        </div>
      </template>

      <el-tabs v-model="activeStatus" @tab-change="handleTabChange">
        <el-tab-pane v-for="t in statusTabs" :key="t.value" :label="t.label" :name="t.value" />
      </el-tabs>

      <el-table v-loading="loading" :data="tableData" stripe border style="margin-top: 8px">
        <el-table-column prop="commission_no" label="委托编号" width="180" />
        <el-table-column prop="project_name" label="工程名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="construction_part" label="施工部位" min-width="140" show-overflow-tooltip />
        <el-table-column prop="commission_date" label="委托日期" width="120" />
        <el-table-column label="见证取样" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.witness_sampling ? 'success' : 'info'" size="small">
              {{ row.witness_sampling ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">查看</el-button>
            <el-button v-if="row.status === 'draft'" link type="primary" @click="goEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" link type="success" @click="handleSubmitReview(row)">
              提交评审
            </el-button>
            <el-button v-if="row.status === 'draft'" link type="danger" @click="handleDelete(row)">删除</el-button>
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
  </div>
</template>
