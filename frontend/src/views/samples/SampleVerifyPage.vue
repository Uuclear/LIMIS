<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { verifySamplePublic } from '@/api/samples'

const route = useRoute()
const loading = ref(true)
const data = ref<Record<string, unknown> | null>(null)
const err = ref('')

const sampleNo = computed(() => {
  const raw = route.params.sampleNo
  if (typeof raw === 'string' && raw.trim()) return raw.trim()
  if (Array.isArray(raw) && raw[0]) return String(raw[0]).trim()
  return ''
})

onMounted(async () => {
  if (!sampleNo.value) {
    err.value = '无效的样品编号'
    loading.value = false
    return
  }
  try {
    const res = (await verifySamplePublic(sampleNo.value)) as unknown as Record<string, unknown>
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
      <h1 class="verify-title">样品进度查询</h1>
      <p class="verify-sub">本页由 LIMIS 提供，用于核对样品编号与系统登记状态是否一致。</p>

      <el-skeleton v-if="loading" :rows="5" animated />

      <el-result
        v-else-if="err"
        icon="warning"
        title="无法查询"
        :sub-title="err"
      />

      <template v-else-if="data">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="样品编号">{{ data.sample_no }}</el-descriptions-item>
          <el-descriptions-item label="样品名称">{{ data.name ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ data.status_display ?? data.status }}</el-descriptions-item>
          <el-descriptions-item label="委托单号">{{ data.commission_no ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="工程/项目">{{ data.project_name ?? '—' }}</el-descriptions-item>
        </el-descriptions>
        <p class="verify-foot">
          说明：本结果仅作进度核对参考；详细数据以实验室系统登记为准。
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
