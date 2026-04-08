<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Download, Printer, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getReport,
  generateReport,
  submitForAudit,
  auditReport,
  approveReport,
  issueReport,
  archiveReport,
  getReportTimeline,
  downloadReport,
  previewReport,
  distributeReport,
  uploadReportPdf,
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
  archived: '已归档',
  voided: '已作废',
}

const statusTagType: Record<string, string> = {
  draft: 'info',
  pending_audit: 'warning',
  pending_approve: '',
  approved: 'success',
  issued: 'success',
  archived: 'success',
  voided: 'danger',
}

const approvalStepMap: Record<string, string> = {
  audit: '审核',
  approve: '批准',
}

const approvalActionMap: Record<string, string> = {
  approve: '通过',
  pass: '通过',
  reject: '驳回',
}

const pdfUrl = ref('')
const timeline = ref<Array<{ time: string; label: string; actor: string; detail: string }>>([])

async function fetchReport() {
  loading.value = true
  try {
    report.value = await getReport(reportId.value) as any
  } finally {
    loading.value = false
  }
}

async function fetchTimeline() {
  try {
    const res: any = await getReportTimeline(reportId.value)
    timeline.value = Array.isArray(res) ? res : (res?.data ?? res ?? [])
  } catch {
    timeline.value = []
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
  if (auditAction.value === 'reject' && (auditComment.value || '').trim().length < 4) {
    ElMessage.warning('退回原因至少4个字符')
    return
  }
  const payload = {
    approved: auditAction.value === 'approve',
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
      fetchTimeline()
    } catch {
      ElMessage.error('操作失败')
    }
  })
}

async function handleArchive() {
  await runLocked('archive', async () => {
    try {
      await ElMessageBox.confirm('确认归档报告？归档后不可修改。', '提示')
      await archiveReport(reportId.value)
      ElMessage.success('报告已归档')
      fetchReport()
      fetchTimeline()
    } catch { /* cancelled */ }
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

// PDF Upload
const uploadInputRef = ref<HTMLInputElement | null>(null)

function triggerUpload() {
  uploadInputRef.value?.click()
}

async function handleUploadPdf(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    ElMessage.warning('请选择PDF格式文件')
    input.value = ''
    return
  }
  await runLocked('upload_pdf', async () => {
    try {
      await uploadReportPdf(reportId.value, file)
      ElMessage.success('PDF上传成功')
      fetchReport()
    } catch {
      ElMessage.error('上传失败')
    } finally {
      input.value = ''
    }
  })
}

// Distribute report
const distributeDialogVisible = ref(false)
const distributeForm = ref({
  recipient: '',
  recipient_unit: '',
  method: 'paper' as 'paper' | 'electronic' | 'both',
  copies: 1,
  distribution_date: '',
  receiver_signature: '',
})

function openDistributeDialog() {
  const today = new Date().toISOString().slice(0, 10)
  distributeForm.value = {
    recipient: '',
    recipient_unit: '',
    method: 'paper',
    copies: 1,
    distribution_date: today,
    receiver_signature: '',
  }
  distributeDialogVisible.value = true
}

async function handleDistributeSubmit() {
  if (!distributeForm.value.recipient.trim()) {
    ElMessage.warning('请填写接收人')
    return
  }
  if (!distributeForm.value.distribution_date) {
    ElMessage.warning('请选择发放日期')
    return
  }
  await runLocked('distribute', async () => {
    try {
      await distributeReport(reportId.value, distributeForm.value)
      ElMessage.success('发放记录已创建')
      distributeDialogVisible.value = false
      fetchReport()
      fetchTimeline()
    } catch {
      ElMessage.error('创建发放记录失败')
    }
  })
}

function approvalTagType(action: string) {
  return action === 'pass' ? 'success' : 'danger'
}

function goBack() {
  router.push('/reports')
}

onMounted(fetchReport)
onMounted(fetchTimeline)
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
          <el-descriptions-item label="报告类型">{{ report.report_type }}</el-descriptions-item>
          <el-descriptions-item label="编制日期">{{ report.compile_date }}</el-descriptions-item>
          <el-descriptions-item label="编制人">{{ report.compiler_name }}</el-descriptions-item>
          <el-descriptions-item label="发放日期">{{ report.issue_date || '-' }}</el-descriptions-item>
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
          <el-descriptions-item label="模板名称">{{ report.template_name || '-' }}</el-descriptions-item>
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
            :type="approval.action === 'pass' ? 'success' : 'danger'"
          >
            <div class="approval-item">
              <div>
                <el-tag :type="approvalTagType(approval.action)" size="small">
                  {{ approvalStepMap[(approval as any).role || (approval as any).step] || '审批' }} - {{ approvalActionMap[approval.action] || approval.action }}
                </el-tag>
                <span class="approval-operator">{{ (approval as any).user_name || (approval as any).operator_name || '' }}</span>
              </div>
              <div v-if="approval.comment" class="approval-comment">
                {{ approval.comment }}
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无审批记录" :image-size="60" />
      </el-card>

      <el-card shadow="never" style="margin-top: 16px">
        <template #header><span>流程时间线</span></template>
        <el-timeline v-if="timeline.length">
          <el-timeline-item v-for="(n, i) in timeline" :key="`${n.time}-${i}`" :timestamp="n.time" placement="top">
            <div>{{ n.label }} <span style="color:#999"> {{ n.actor ? `（${n.actor}）` : '' }}</span></div>
            <div v-if="n.detail" style="color:#666; margin-top:4px">{{ n.detail }}</div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无流程记录" :image-size="56" />
      </el-card>

      <!-- Distribution Records -->
      <el-card
        shadow="never"
        style="margin-top: 16px"
      >
        <template #header>
          <div class="card-header">
            <span>发放记录</span>
            <el-button
              v-if="report.status === 'issued' || report.status === 'archived'"
              v-permission="'report:edit'"
              type="primary"
              size="small"
              @click="openDistributeDialog"
            >
              新增发放记录
            </el-button>
          </div>
        </template>
        <el-table v-if="report.distributions?.length" :data="report.distributions" border stripe>
          <el-table-column prop="recipient" label="接收人" min-width="140" />
          <el-table-column prop="recipient_unit" label="接收单位" min-width="140" show-overflow-tooltip />
          <el-table-column prop="method" label="发放方式" width="120">
            <template #default="{ row }">
              {{ { paper: '纸质', electronic: '电子', both: '纸质+电子' }[row.method as string] ?? row.method }}
            </template>
          </el-table-column>
          <el-table-column prop="copies" label="份数" width="80" align="center" />
          <el-table-column prop="distribution_date" label="发放日期" width="120" />
          <el-table-column prop="receiver_signature" label="签收人" width="120" />
        </el-table>
        <el-empty v-else description="暂无发放记录" :image-size="60" />
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
        <el-button v-permission="'report:view'" @click="handlePreview">预览</el-button>

        <template v-if="report.status === 'draft'">
          <el-button v-permission="'report:edit'" type="primary" :loading="isLocked('generate')" @click="handleGenerate">生成PDF</el-button>
          <el-button v-permission="'report:edit'" :icon="UploadFilled" :loading="isLocked('upload_pdf')" @click="triggerUpload">上传PDF</el-button>
          <el-button v-permission="'report:edit'" type="warning" :loading="isLocked('submit_audit')" @click="handleSubmitAudit">提交审核</el-button>
        </template>

        <template v-if="report.status === 'pending_audit'">
          <el-button v-permission="'report:edit'" :icon="UploadFilled" :loading="isLocked('upload_pdf')" @click="triggerUpload">上传PDF</el-button>
          <el-button v-permission="'report:approve'" type="success" @click="openAuditDialog('audit')">审核</el-button>
        </template>

        <template v-if="report.status === 'pending_approve'">
          <el-button v-permission="'report:approve'" type="success" @click="openAuditDialog('approve')">批准</el-button>
        </template>

        <template v-if="report.status === 'approved'">
          <el-button v-permission="'report:edit'" type="success" :loading="isLocked('issue')" @click="handleIssue">发放</el-button>
        </template>

        <template v-if="report.status === 'issued'">
          <el-button v-permission="'report:edit'" type="primary" @click="openDistributeDialog">分发报告</el-button>
          <el-button v-permission="'report:export'" :icon="Download" @click="handleDownload">下载</el-button>
          <el-button v-permission="'report:view'" :icon="Printer" @click="handlePrint">打印</el-button>
          <el-button v-permission="'report:edit'" type="info" :loading="isLocked('archive')" @click="handleArchive">归档</el-button>
        </template>

        <template v-if="report.status === 'archived'">
          <el-button v-permission="'report:export'" :icon="Download" @click="handleDownload">下载</el-button>
          <el-button v-permission="'report:view'" :icon="Printer" @click="handlePrint">打印</el-button>
        </template>
      </div>
      <!-- Hidden PDF upload input -->
      <input
        ref="uploadInputRef"
        type="file"
        accept=".pdf"
        style="display: none"
        @change="handleUploadPdf"
      />
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
        <el-button v-permission="'report:approve'" type="primary" :loading="isLocked('audit_submit')" @click="handleAuditSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Distribute Report Dialog -->
    <el-dialog v-model="distributeDialogVisible" title="分发报告" width="500px" destroy-on-close>
      <el-form :model="distributeForm" label-width="90px">
        <el-form-item label="接收人" required>
          <el-input v-model="distributeForm.recipient" placeholder="请输入接收人姓名" />
        </el-form-item>
        <el-form-item label="接收单位">
          <el-input v-model="distributeForm.recipient_unit" placeholder="请输入接收单位" />
        </el-form-item>
        <el-form-item label="发放方式" required>
          <el-radio-group v-model="distributeForm.method">
            <el-radio value="paper">纸质</el-radio>
            <el-radio value="electronic">电子</el-radio>
            <el-radio value="both">纸质+电子</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="份数">
          <el-input-number v-model="distributeForm.copies" :min="1" :max="99" />
        </el-form-item>
        <el-form-item label="发放日期" required>
          <el-date-picker
            v-model="distributeForm.distribution_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择发放日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="签收人">
          <el-input v-model="distributeForm.receiver_signature" placeholder="请输入签收人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="distributeDialogVisible = false">取消</el-button>
        <el-button
          v-permission="'report:edit'"
          type="primary"
          :loading="isLocked('distribute')"
          @click="handleDistributeSubmit"
        >
          确定
        </el-button>
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
