<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Printer, DocumentAdd } from '@element-plus/icons-vue'
import { getCommission, reviewCommission } from '@/api/commissions'
import { createReport } from '@/api/reports'
import type { Commission } from '@/types/commission'
import { useActionLock } from '@/composables/useActionLock'

const route = useRoute()
const router = useRouter()
const commissionId = computed(() => Number(route.params.id))
const { isLocked, runLocked } = useActionLock()

const detail = ref<Commission>({} as Commission)
const loading = ref(false)

async function fetchDetail() {
  loading.value = true
  try {
    detail.value = await getCommission(commissionId.value) as any
  } finally {
    loading.value = false
  }
}

const canReview = computed(() => detail.value.status === 'pending_review')
const canCreateReport = computed(() => detail.value.status === 'reviewed')

const reviewDialogVisible = ref(false)
// 后端评审接口字段：approved（bool） + comment（string）
const reviewForm = reactive({ approved: true as boolean, comment: '' })

function openReviewDialog() {
  reviewForm.approved = true
  reviewForm.comment = ''
  reviewDialogVisible.value = true
}

async function handleReview() {
  await runLocked('commission_review', async () => {
    await reviewCommission(commissionId.value, {
      approved: reviewForm.approved,
      comment: reviewForm.comment,
    })
    ElMessage.success('评审完成')
    reviewDialogVisible.value = false
    fetchDetail()
  })
}

async function handleCreateReport() {
  await runLocked('create_report', async () => {
    try {
      const res: any = await createReport({ commission: commissionId.value })
      const reportId = res.id ?? res.data?.id
      ElMessage.success('报告已创建')
      if (reportId) {
        router.push(`/reports/${reportId}`)
      } else {
        router.push('/reports')
      }
    } catch {
      ElMessage.error('创建报告失败')
    }
  })
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    draft: '草稿', pending_review: '待评审', reviewed: '已评审', rejected: '已退回',
    cancelled: '已终止',
  }
  return map[status] ?? status
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    draft: 'info', pending_review: 'warning', reviewed: 'success', rejected: 'danger',
    cancelled: 'info',
  }
  return map[status] ?? 'info'
}

function handlePrint() {
  window.print()
}

onMounted(fetchDetail)
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/entrustment')">
      <template #content>
        <div style="display: flex; align-items: center; gap: 12px">
          <span style="font-size: 18px; font-weight: 600">委托详情</span>
          <el-tag :type="statusTagType(detail.status)">{{ statusLabel(detail.status) }}</el-tag>
        </div>
      </template>
      <template #extra>
        <el-button :icon="Printer" @click="handlePrint">打印委托单</el-button>
        <el-button
          v-if="canCreateReport"
          v-permission="'report:create'"
          type="success"
          :icon="DocumentAdd"
          :loading="isLocked('create_report')"
          @click="handleCreateReport"
        >
          新建报告
        </el-button>
        <el-button
          v-if="canReview"
          v-permission="'commission:approve'"
          type="primary"
          @click="openReviewDialog"
        >
          合同评审
        </el-button>
      </template>
    </el-page-header>

    <el-card v-loading="loading" shadow="never" style="margin-top: 20px">
      <el-descriptions title="基本信息" :column="2" border>
        <el-descriptions-item label="委托编号">{{ detail.commission_no }}</el-descriptions-item>
        <el-descriptions-item label="委托日期">{{ detail.commission_date }}</el-descriptions-item>
        <el-descriptions-item label="工程名称">{{ detail.project_name }}</el-descriptions-item>
        <el-descriptions-item label="分部工程">{{ detail.sub_project_name }}</el-descriptions-item>
        <el-descriptions-item label="工程部位">{{ detail.construction_part }}</el-descriptions-item>
        <el-descriptions-item label="见证取样">
          <el-tag :type="detail.is_witnessed ? 'success' : 'info'" size="small">
            {{ detail.is_witnessed ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="委托单位">{{ detail.client_unit }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ detail.client_contact }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detail.client_phone }}</el-descriptions-item>
        <el-descriptions-item label="见证人">{{ detail.witness_name }}</el-descriptions-item>
        <el-descriptions-item label="取样人">{{ (detail as any).sampler_name || '—' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header><span>检测项目</span></template>
      <el-table :data="detail.items ?? []" border stripe>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="test_object" label="检测对象" min-width="140" />
        <el-table-column prop="test_item" label="检测项目" min-width="140" />
        <el-table-column prop="test_standard" label="检测标准" min-width="180" show-overflow-tooltip />
        <el-table-column prop="parameter_name" label="检测参数" min-width="160" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格型号" width="130" />
        <el-table-column prop="grade" label="设计强度/等级" width="120" />
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column prop="unit" label="单位" width="80" align="center" />
      </el-table>
    </el-card>

    <el-card v-if="detail.contract_review" shadow="never" style="margin-top: 16px">
      <template #header><span>合同评审信息</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="评审结论">
          <el-tag
            :type="detail.contract_review.conclusion === 'accept' ? 'success' : 'warning'"
            size="small"
          >
            {{ detail.contract_review.conclusion === 'accept' ? '接受' : (detail.contract_review.conclusion === 'reject' ? '拒绝' : '有条件接受') }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="评审人">{{ detail.contract_review.reviewer_name }}</el-descriptions-item>
        <el-descriptions-item label="评审时间">{{ detail.contract_review.review_date }}</el-descriptions-item>
        <el-descriptions-item label="评审意见" :span="2">{{ detail.contract_review.comment }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Review Dialog -->
    <el-dialog v-model="reviewDialogVisible" title="合同评审" width="480px" destroy-on-close>
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="评审结果">
          <el-radio-group v-model="reviewForm.approved">
            <el-radio :value="true">通过</el-radio>
            <el-radio :value="false">退回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="评审意见">
          <el-input v-model="reviewForm.comment" type="textarea" :rows="4" placeholder="请输入评审意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button
          v-permission="'commission:approve'"
          type="primary"
          :loading="isLocked('commission_review')"
          @click="handleReview"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style>
@media print {
  .sidebar, .navbar, .page-header .el-button, .el-dialog, .el-page-header__back {
    display: none !important;
  }
  .page-container {
    padding: 0 !important;
    margin: 0 !important;
  }
}
</style>
