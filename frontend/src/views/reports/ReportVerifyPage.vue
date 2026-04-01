<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { verifyReportPublic } from '@/api/reports'

const route = useRoute()
const loading = ref(true)
const data = ref<Record<string, unknown> | null>(null)
const err = ref('')

const reportId = computed(() => {
  const n = Number(route.params.id)
  return Number.isFinite(n) ? n : NaN
})

onMounted(async () => {
  if (!Number.isFinite(reportId.value) || reportId.value <= 0) {
    err.value = '无效的报告编号'
    loading.value = false
    return
  }
  try {
    const res = (await verifyReportPublic(reportId.value)) as unknown as Record<string, unknown>
    data.value = res ?? null
  } catch (e: unknown) {
    const ax = e as { response?: { data?: { message?: string } }; message?: string }
    err.value = ax?.response?.data?.message || ax?.message || '查询失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="verify-wrap">
    <div class="verify-card">
      <h1 class="verify-title">报告防伪查询</h1>
      <p class="verify-sub">本页由 LIMIS 提供，用于核对报告编号与系统登记状态是否一致。</p>

      <el-skeleton v-if="loading" :rows="4" animated />

      <el-result
        v-else-if="err"
        icon="warning"
        title="无法查询"
        :sub-title="err"
      />

      <template v-else-if="data">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="报告编号">{{ data.report_no }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ data.status_display ?? data.status }}</el-descriptions-item>
          <el-descriptions-item label="编制日期">{{ data.compile_date ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="发放日期">{{ data.issue_date ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="CMA 标识">{{ data.has_cma ? '是' : '否' }}</el-descriptions-item>
        </el-descriptions>
        <p class="verify-foot">
          说明：本结果仅作真伪核对参考；如需正式文本请以机构盖章纸质报告为准。
        </p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.verify-wrap {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 48px 16px;
  background: linear-gradient(180deg, #f0f4ff 0%, #f9fafb 40%);
}

.verify-card {
  width: 100%;
  max-width: 520px;
  background: #fff;
  border-radius: 12px;
  padding: 28px 24px 20px;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.08);
}

.verify-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.verify-sub {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 24px;
  line-height: 1.5;
}

.verify-foot {
  margin-top: 20px;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.5;
}
</style>
