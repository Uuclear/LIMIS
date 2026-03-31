<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Download, Printer } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getReport,
  generateReport,
  submitForAudit,
  auditReport,
  approveReport,
  issueReport,
  downloadReport,
  previewReport,
} from '@/api/reports'
import type { Report } from '@/types/report'
import { useActionLock } from '@/composables/useActionLock'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const report = ref<Report | null>(null)
const { isLocked, runLocked } = useActionLock()

const reportId = computed(() => Number(route.params.id))

const statusMap: Record<string, string> = {
  draft: '草稿',
  pending_audit: '待审核',
  pending_approve: '待批准',
  approved: '已批准',
  issued: '已发放',
  voided: '已作废',
}

const statusTagType: Record<string, string> = {
  draft: 'info',
  pending_audit: 'warning',
  pending_approve: '',
  approved: 'success',
  issued: 'success',
  voided: 'danger',
}

const approvalStepMap: Record<string, string> = {
  audit: '审核',
  approve: '批准',
}

const approvalActionMap: Record<string, string> = {
  approve: '通过',
  reject: '驳回',
}

const pdfUrl = ref('')

async function fetchReport() {
  loading.value = true
  try {
    report.value = await getReport(reportId.value) as any
  } finally {
    loading.value = false
  }
}

async function handleGenerate() {
  await runLocked('generate', async () => {
    try {
      await ElMessageBox.confirm('确认生成报告PDF？', '提示')
      await generateReport(reportId.value)
      ElMessage.success('报告生成成功')
      fetchReport()
    } catch { /* cancelled */ }
  })
}

async function handleSubmitAudit() {
  await runLocked('submit_audit', async () => {
    try {
      await ElMessageBox.confirm('确认提交审核？', '提示')
      await submitForAudit(reportId.value)
      ElMessage.success('已提交审核')
      fetchReport()
    } catch { /* cancelled */ }
  })
}

const auditDialogVisible = ref(false)
const auditAction = ref<'approve' | 'reject'>('approve')
const auditComment = ref('')
const auditType = ref<'audit' | 'approve'>('audit')

function openAuditDialog(type: 'audit' | 'approve') {
  auditType.value = type
  auditAction.value = 'approve'
  auditComment.value = ''
  auditDialogVisible.value = true
}

async function handleAuditSubmit() {
  const payload = {
    action: auditAction.value,
    comment: auditComment.value,
  }
  await runLocked('audit_submit', async () => {
    try {
      if (auditType.value === 'audit') {
        await auditReport(reportId.value, payload)
      } else {
        await approveReport(reportId.value, payload)
      }
      ElMessage.success('操作成功')
      auditDialogVisible.value = false
      fetchReport()
    } catch {
      ElMessage.error('操作失败')
    }
  })
}

async function handleIssue() {
  await runLocked('issue', async () => {
    try {
      await ElMessageBox.confirm('确认发放报告？', '提示')
      await issueReport(reportId.value)
      ElMessage.success('报告已发放')
      fetchReport()
    } catch { /* cancelled */ }
  })
}

async function handleDownload() {
  try {
    const res: any = await downloadReport(reportId.value)
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${report.value?.report_no ?? 'report'}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}

async function handlePreview() {
  try {
    const res: any = await previewReport(reportId.value)
    const blob = new Blob([res], { type: 'application/pdf' })
    pdfUrl.value = window.URL.createObjectURL(blob)
  } catch {
    ElMessage.error('预览失败')
  }
}

function handlePrint() {
  if (pdfUrl.value) {
    const w = window.open(pdfUrl.value, '_blank')
    w?.print()
  } else {
    handlePreview()
  }
}

function goBack() {
  router.push('/reports')
}

function approvalTagType(action: string) {
  return action === 'approve' ? 'success' : 'danger'
}

onMounted(fetchReport)
</script>

<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <span v-if="report" class="page-title">报告详情 - {{ report.report_no }}</span>
    </div>

    <template v-if="report">
      <!-- Report Info -->
      <el-card shadow="never" style="margin-top: 16px">
        <template #header>
          <div class="card-header">
            <span>报告信息</span>
            <el-tag :type="statusTagType[report.status]" effect="dark">
              {{ statusMap[report.status] ?? report.status }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="报告编号">{{ report.report_no }}</el-descriptions-item>
          <el-descriptions-item label="报告标题">{{ report.title }}</el-descriptions-item>
          <el-descriptions-item label="编制日期">{{ report.compile_date }}</el-descriptions-item>
          <el-descriptions-item label="编制人">{{ report.compiler_name }}</el-descriptions-item>
          <el-descriptions-item label="CMA标志">
            <el-tag v-if="report.has_cma" type="success" size="small">CMA</el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="CNAS标志">
            <el-tag v-if="report.has_cnas" type="success" size="small">CNAS</el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="结论" :span="3">
            {{ report.conclusion || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="3">
            {{ report.remark || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Commission & Sample Info -->
      <el-card shadow="never" style="margin-top: 16px">
        <template #header><span>委托及样品信息</span></template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="委托编号">{{ report.commission_no }}</el-descriptions-item>
          <el-descriptions-item label="项目名称">{{ report.project_name }}</el-descriptions-item>
          <el-descriptions-item label="委托单位">{{ report.client_name }}</el-descriptions-item>
          <el-descriptions-item label="相关样品" :span="3">
            <el-tag
              v-for="(name, idx) in report.sample_names"
              :key="idx"
              style="margin-right: 6px; margin-bottom: 4px"
            >
              {{ name }}
            </el-tag>
            <span v-if="!report.sample_names?.length">-</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Approval History -->
      <el-card shadow="never" style="margin-top: 16px">
        <template #header><span>审批记录</span></template>
        <el-timeline v-if="report.approvals?.length">
          <el-timeline-item
            v-for="approval in report.approvals"
            :key="approval.id"
            :timestamp="approval.created_at"
            placement="top"
            :type="approval.action === 'approve' ? 'success' : 'danger'"
          >
            <div class="approval-item">
              <div>
                <el-tag :type="approvalTagType(approval.action)" size="small">
                  {{ approvalStepMap[approval.step] }} - {{ approvalActionMap[approval.action] }}
                </el-tag>
                <span class="approval-operator">{{ approval.operator_name }}</span>
              </div>
              <div v-if="approval.comment" class="approval-comment">
                {{ approval.comment }}
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无审批记录" :image-size="60" />
      </el-card>

      <!-- Distribution Records -->
      <el-card
        v-if="report.distributions?.length"
        shadow="never"
        style="margin-top: 16px"
      >
        <template #header><span>发放记录</span></template>
        <el-table :data="report.distributions" border stripe>
          <el-table-column prop="recipient" label="接收人" min-width="140" />
          <el-table-column prop="method" label="发放方式" width="120">
            <template #default="{ row }">
              {{ { email: '邮件', print: '打印', pickup: '自取' }[row.method as string] ?? row.method }}
            </template>
          </el-table-column>
          <el-table-column prop="operator_name" label="操作人" width="120" />
          <el-table-column prop="distributed_at" label="发放时间" width="180" />
          <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        </el-table>
      </el-card>

      <!-- PDF Preview -->
      <el-card v-if="pdfUrl" shadow="never" style="margin-top: 16px">
        <template #header>
          <div class="card-header">
            <span>报告预览</span>
            <el-button size="small" @click="pdfUrl = ''">关闭预览</el-button>
          </div>
        </template>
        <iframe :src="pdfUrl" class="pdf-preview" />
      </el-card>

      <!-- Actions -->
      <div class="action-bar">
        <el-button @click="handlePreview">预览</el-button>

        <template v-if="report.status === 'draft'">
          <el-button type="primary" :loading="isLocked('generate')" @click="handleGenerate">生成PDF</el-button>
          <el-button type="warning" :loading="isLocked('submit_audit')" @click="handleSubmitAudit">提交审核</el-button>
        </template>

        <template v-if="report.status === 'pending_audit'">
          <el-button type="success" @click="openAuditDialog('audit')">审核</el-button>
        </template>

        <template v-if="report.status === 'pending_approve'">
          <el-button type="success" @click="openAuditDialog('approve')">批准</el-button>
        </template>

        <template v-if="report.status === 'approved'">
          <el-button type="success" :loading="isLocked('issue')" @click="handleIssue">发放</el-button>
        </template>

        <template v-if="report.status === 'issued'">
          <el-button :icon="Download" @click="handleDownload">下载</el-button>
          <el-button :icon="Printer" @click="handlePrint">打印</el-button>
        </template>
      </div>
    </template>

    <!-- Audit/Approve Dialog -->
    <el-dialog
      v-model="auditDialogVisible"
      :title="auditType === 'audit' ? '审核报告' : '批准报告'"
      width="500px"
    >
      <el-form label-width="80px">
        <el-form-item label="操作">
          <el-radio-group v-model="auditAction">
            <el-radio value="approve">通过</el-radio>
            <el-radio value="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="意见">
          <el-input
            v-model="auditComment"
            type="textarea"
            :rows="3"
            placeholder="请输入审核/批准意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auditDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="isLocked('audit_submit')" @click="handleAuditSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-bar {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.approval-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.approval-operator {
  margin-left: 8px;
  color: var(--el-text-color-regular);
  font-size: 13px;
}

.approval-comment {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  padding: 4px 0;
}

.pdf-preview {
  width: 100%;
  height: 600px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}
</style>
