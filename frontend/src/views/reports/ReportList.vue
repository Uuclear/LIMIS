<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getReportList,
  submitForAudit,
  issueReport,
  voidReport,
  downloadReport,
  previewReport,
} from '@/api/reports'
import type { Report } from '@/types/report'

const router = useRouter()
const loading = ref(false)
const tableData = ref<Report[]>([])
const total = ref(0)
const activeTab = ref('')

const query = reactive({
  page: 1,
  page_size: 20,
  status: '',
  date_range: [] as string[],
})

const statusTabs = [
  { label: '全部', value: '' },
  { label: '草稿', value: 'draft' },
  { label: '待审核', value: 'pending_audit' },
  { label: '待批准', value: 'pending_approve' },
  { label: '已批准', value: 'approved' },
  { label: '已发放', value: 'issued' },
  { label: '已归档', value: 'archived' },
]

const statusMap: Record<string, string> = {
  draft: '草稿',
  pending_audit: '待审核',
  pending_approve: '待批准',
  approved: '已批准',
  issued: '已发放',
  archived: '已归档',
  voided: '已作废',
}

const statusTagType: Record<string, string> = {
  draft: 'info',
  pending_audit: 'warning',
  pending_approve: '',
  approved: 'success',
  issued: 'success',
  archived: 'info',
  voided: 'danger',
}

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, any> = { ...query }
    if (query.date_range?.length === 2) {
      params.start_date = query.date_range[0]
      params.end_date = query.date_range[1]
    }
    delete params.date_range
    if (activeTab.value) {
      params.status = activeTab.value
    }
    const res: any = await getReportList(params)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

function handleTabChange(tab: string) {
  activeTab.value = tab
  query.page = 1
  fetchList()
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, { page: 1, status: '', date_range: [] })
  fetchList()
}

function goDetail(row: Report) {
  router.push(`/reports/${row.id}`)
}

async function handlePreview(row: Report) {
  try {
    const res: any = await previewReport(row.id)
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank')
  } catch {
    ElMessage.error('预览失败')
  }
}

async function handleSubmitAudit(row: Report) {
  try {
    await ElMessageBox.confirm('确认提交审核？', '提示')
    await submitForAudit(row.id)
    ElMessage.success('已提交审核')
    fetchList()
  } catch { /* cancelled */ }
}

async function handleIssue(row: Report) {
  try {
    await ElMessageBox.confirm('确认发放报告？', '提示')
    await issueReport(row.id)
    ElMessage.success('报告已发放')
    fetchList()
  } catch { /* cancelled */ }
}

async function handleDownload(row: Report) {
  try {
    const res: any = await downloadReport(row.id)
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${row.report_no}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}

const voidDialogVisible = ref(false)
const voidTarget = ref<Report | null>(null)
const voidReason = ref('')

function openVoidDialog(row: Report) {
  voidTarget.value = row
  voidReason.value = ''
  voidDialogVisible.value = true
}

async function handleVoid() {
  if (!voidTarget.value) return
  try {
    await voidReport(voidTarget.value.id, { reason: voidReason.value })
    ElMessage.success('报告已作废')
    voidDialogVisible.value = false
    fetchList()
  } catch {
    ElMessage.error('作废失败')
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="query.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <span>检测报告</span>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane
          v-for="tab in statusTabs"
          :key="tab.value"
          :label="tab.label"
          :name="tab.value"
        />
      </el-tabs>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="report_no" label="报告编号" width="180" />
        <el-table-column prop="commission_no" label="委托编号" width="180" />
        <el-table-column prop="client_name" label="委托单位" min-width="160" show-overflow-tooltip />
        <el-table-column prop="compiler_name" label="编制人" width="100" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType[row.status]" size="small" effect="dark">
              {{ statusMap[row.status] ?? row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="compile_date" label="编制日期" width="120" />
        <el-table-column label="CMA" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_cma" type="success" size="small">CMA</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">查看</el-button>
            <el-button link type="primary" @click="handlePreview(row)">预览</el-button>
            <el-button
              v-if="row.status === 'draft'"
              link type="warning"
              @click="handleSubmitAudit(row)"
            >
              提交审核
            </el-button>
            <el-button
              v-if="row.status === 'pending_audit'"
              link type="primary"
              @click="goDetail(row)"
            >
              审核
            </el-button>
            <el-button
              v-if="row.status === 'pending_approve'"
              link type="primary"
              @click="goDetail(row)"
            >
              批准
            </el-button>
            <el-button
              v-if="row.status === 'approved'"
              link type="success"
              @click="handleIssue(row)"
            >
              发放
            </el-button>
            <el-button
              v-if="row.status === 'issued'"
              link type="primary"
              :icon="Download"
              @click="handleDownload(row)"
            >
              下载
            </el-button>
            <el-button
              v-if="row.status !== 'voided' && row.status !== 'issued'"
              link type="danger"
              @click="openVoidDialog(row)"
            >
              作废
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

    <!-- Void Dialog -->
    <el-dialog v-model="voidDialogVisible" title="作废报告" width="450px">
      <el-form label-width="80px">
        <el-form-item label="作废原因">
          <el-input
            v-model="voidReason"
            type="textarea"
            :rows="3"
            placeholder="请输入作废原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="voidDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleVoid">确认作废</el-button>
      </template>
    </el-dialog>
  </div>
</template>
