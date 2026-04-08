<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getCommissionList, deleteCommission, submitCommission, terminateCommission } from '@/api/commissions'
import type { Commission } from '@/types/commission'
import { useActionLock } from '@/composables/useActionLock'

const router = useRouter()
const loading = ref(false)
const tableData = ref<Commission[]>([])
const total = ref(0)
const activeStatus = ref('draft')
const { isLocked, runLocked } = useActionLock()

const query = reactive({
  page: 1, page_size: 20, search: '', status: '',
})

const statusTabs = [
  { label: '草稿', value: 'draft' },
  { label: '待评审', value: 'pending_review' },
  { label: '已评审', value: 'reviewed' },
  { label: '已退回', value: 'rejected' },
  { label: '已终止', value: 'cancelled' },
  { label: '全部', value: '' },
]

async function fetchList() {
  loading.value = true
  try {
    const statusParam = activeStatus.value || undefined
    const res: any = await getCommissionList({ ...query, status: statusParam })
    tableData.value = (res.results ?? res.list ?? []) as Commission[]
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
  query.search = ''
  handleSearch()
}

function goCreate() {
  router.push('/entrustment/create')
}

function goEdit(row: Commission) {
  router.push(`/entrustment/${row.id}/edit`)
}

async function handleSubmitReview(row: Commission) {
  await runLocked(`commission_submit_${row.id}`, async () => {
    await ElMessageBox.confirm('确认提交？提交后不可编辑。', '提示', { type: 'warning' })
    await submitCommission(row.id)
    ElMessage.success('已提交')
    fetchList()
  })
}

async function handleDelete(row: Commission) {
  await ElMessageBox.confirm('确认删除该草稿委托？删除后将级联移除关联数据。', '提示', { type: 'warning' })
  await deleteCommission(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

async function handleTerminate(row: Commission) {
  await runLocked(`commission_terminate_${row.id}`, async () => {
    let reason: string
    try {
      const prompt = await ElMessageBox.prompt('可选填终止原因', '终止委托', {
        confirmButtonText: '确定终止',
        cancelButtonText: '取消',
        inputPlaceholder: '例如：客户撤单、项目取消',
      })
      reason = String(prompt.value || '').trim()
    } catch {
      return
    }
    await terminateCommission(row.id, reason ? { reason } : {})
    ElMessage.success('委托已终止')
    fetchList()
  })
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    draft: 'info', pending_review: 'warning', reviewed: 'success', rejected: 'danger',
    cancelled: 'info',
  }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    draft: '草稿', pending_review: '待评审', reviewed: '已评审', rejected: '已退回',
    cancelled: '已终止',
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
          <el-input v-model="query.search" placeholder="委托编号/工程名称/工程部位" clearable style="width: 220px" />
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
          <el-button v-permission="'commission:create'" type="primary" :icon="Plus" @click="goCreate">新增委托</el-button>
        </div>
      </template>

      <el-tabs v-model="activeStatus" @tab-change="handleTabChange">
        <el-tab-pane v-for="t in statusTabs" :key="t.value" :label="t.label" :name="t.value" />
      </el-tabs>

      <el-table v-loading="loading" :data="tableData" stripe border style="margin-top: 8px">
        <el-table-column prop="commission_no" label="委托编号" width="180">
          <template #default="{ row }">
            <router-link :to="`/entrustment/${row.id}`" class="link-primary">{{ row.commission_no }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="工程名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="sample_names" label="样品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="construction_part" label="工程部位" min-width="140" show-overflow-tooltip />
        <el-table-column prop="commission_date" label="委托日期" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/entrustment/${row.id}`)">查看</el-button>
            <el-button
              v-if="row.status === 'draft' || row.status === 'rejected'"
              v-permission="'commission:edit'"
              link
              type="default"
              @click="goEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'draft' || row.status === 'rejected'"
              v-permission="'commission:edit'"
              link
              type="success"
              :loading="isLocked(`commission_submit_${row.id}`)"
              @click="handleSubmitReview(row)"
            >
              提交
            </el-button>
            <el-button
              v-if="row.status === 'draft'"
              v-permission="'commission:delete'"
              link
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
            <el-button
              v-if="row.status === 'pending_review' || row.status === 'reviewed'"
              v-permission="'commission:edit'"
              link
              type="warning"
              :loading="isLocked(`commission_terminate_${row.id}`)"
              @click="handleTerminate(row)"
            >
              终止
            </el-button>
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
