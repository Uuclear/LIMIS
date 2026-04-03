<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Printer } from '@element-plus/icons-vue'
import {
  getSample,
  changeSampleStatus,
  getSampleTimeline,
  getSampleLabel,
  disposeSample,
  createTestingTasksForSample,
} from '@/api/samples'
import { getTestTaskList } from '@/api/testing'
import type { Sample } from '@/types/sample'
import { useActionLock } from '@/composables/useActionLock'

const route = useRoute()
const router = useRouter()
const sampleId = computed(() => Number(route.params.id))

const detail = ref<Sample>({} as Sample)
const loading = ref(false)
const timeline = ref<{ time: string; status: string; operator: string; remark: string }[]>([])
const { isLocked, runLocked } = useActionLock()

// 检测任务（用于“检测中”的下一步引导）
const tasks = ref<any[]>([])
const tasksLoading = ref(false)
const tasksLoaded = ref(false)

async function fetchTasks() {
  tasksLoading.value = true
  try {
    const res: any = await getTestTaskList({
      sample: sampleId.value,
      page_size: 200,
    })
    tasks.value = res.results ?? res.list ?? res ?? []
  } finally {
    tasksLoading.value = false
    tasksLoaded.value = true
  }
}

const statusSteps = [
  { label: '待检', value: 'pending' },
  { label: '检测中', value: 'testing' },
  { label: '已检', value: 'tested' },
  { label: '留样', value: 'retained' },
  { label: '已处置', value: 'disposed' },
]

const currentStep = computed(() => {
  const idx = statusSteps.findIndex(s => s.value === detail.value.status)
  return idx >= 0 ? idx : 0
})

async function fetchDetail() {
  loading.value = true
  try {
    detail.value = await getSample(sampleId.value) as any
    await fetchTasks()
  } finally {
    loading.value = false
  }
}

async function fetchTimeline() {
  const res: any = await getSampleTimeline(sampleId.value)
  timeline.value = res ?? []
}

async function handleStatusChange(newStatus: string) {
  await runLocked(`sample_status_${newStatus}`, async () => {
    const label = statusSteps.find(s => s.value === newStatus)?.label ?? newStatus
    await ElMessageBox.confirm(`确认将状态变更为"${label}"？`, '提示', { type: 'warning' })
    await changeSampleStatus(sampleId.value, { new_status: newStatus })
    ElMessage.success('状态变更成功')
    fetchDetail()
    fetchTimeline()
  })
}

async function handlePrintLabel() {
  const res: any = await getSampleLabel(sampleId.value)
  if (res?.url) window.open(res.url, '_blank')
  else ElMessage.info('标签生成中，请稍后')
}

const disposeDialogVisible = ref(false)
const disposeForm = reactive({ disposal_method: '', remark: '' })

function openDisposeDialog() {
  disposeForm.disposal_method = ''
  disposeForm.remark = ''
  disposeDialogVisible.value = true
}

async function handleDispose() {
  await runLocked('sample_dispose', async () => {
    if (!disposeForm.disposal_method) return ElMessage.warning('请选择处置方式')
    await disposeSample(sampleId.value, disposeForm)
    ElMessage.success('处置成功')
    disposeDialogVisible.value = false
    fetchDetail()
    fetchTimeline()
  })
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    pending: 'info', testing: 'warning', tested: 'success', retained: '', disposed: 'danger',
  }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  return statusSteps.find(s => s.value === status)?.label ?? status
}

const nextStatus = computed(() => {
  const idx = currentStep.value
  if (idx >= statusSteps.length - 1 || detail.value.status === 'disposed') return null

  const candidate = statusSteps[idx + 1]

  // 样品“检测中”后：必须先生成/分配检测任务并完成，才能变更为“已检”
  if (detail.value.status === 'testing' && candidate?.value === 'tested') {
    if (!tasksLoaded.value) return null
    if (!tasks.value.length) return null
    const allCompleted = tasks.value.every((t) => t.status === 'completed')
    return allCompleted ? candidate : null
  }

  return candidate ?? null
})

function goTasks() {
  router.push(`/testing/tasks?sample=${sampleId.value}`)
}

async function handleCreateTasks() {
  await runLocked('create_tasks', async () => {
    await createTestingTasksForSample(sampleId.value)
    ElMessage.success('检测任务已生成，请继续分配/开始检测')
    await fetchTasks()
    router.push(`/testing/tasks?sample=${sampleId.value}&status=unassigned`)
  })
}

onMounted(() => { fetchDetail(); fetchTimeline() })
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/sample')">
      <template #content>
        <div style="display: flex; align-items: center; gap: 12px">
          <span style="font-size: 18px; font-weight: 600">样品详情</span>
          <el-tag :type="statusTagType(detail.status)">{{ statusLabel(detail.status) }}</el-tag>
        </div>
      </template>
      <template #extra>
        <el-button v-permission="'sample:view'" :icon="Printer" @click="handlePrintLabel">打印标签</el-button>
        <el-button
          v-if="detail.status === 'testing'"
          v-permission="'testing:view'"
          type="primary"
          @click="goTasks"
        >
          查看检测任务
        </el-button>
        <el-button
          v-if="detail.status === 'testing' && tasksLoaded && !tasks.length"
          v-permission="'sample:edit'"
          type="warning"
          @click="handleCreateTasks"
          :loading="tasksLoading || isLocked('create_tasks')"
        >
          生成检测任务
        </el-button>
        <el-button
          v-if="nextStatus && detail.status !== 'retained'"
          v-permission="'sample:edit'"
          type="primary"
          :loading="nextStatus ? isLocked(`sample_status_${nextStatus.value}`) : false"
          @click="handleStatusChange(nextStatus.value)"
        >
          变更为「{{ nextStatus.label }}」
        </el-button>
        <el-button
          v-if="detail.status === 'retained'"
          v-permission="'sample:create'"
          type="danger"
          @click="openDisposeDialog"
        >
          样品处置
        </el-button>
      </template>
    </el-page-header>

    <!-- Status Steps -->
    <el-card shadow="never" style="margin-top: 20px">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step v-for="s in statusSteps" :key="s.value" :title="s.label" />
      </el-steps>
    </el-card>

    <!-- Info -->
    <el-card v-loading="loading" shadow="never" style="margin-top: 16px">
      <template #header><span>样品信息</span></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="样品编号">{{ detail.sample_no }}</el-descriptions-item>
        <el-descriptions-item label="样品名称">{{ detail.name }}</el-descriptions-item>
        <el-descriptions-item label="规格型号">{{ detail.specification }}</el-descriptions-item>
        <el-descriptions-item label="设计等级">{{ detail.grade }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ detail.quantity }} {{ detail.unit }}</el-descriptions-item>
        <el-descriptions-item label="取样日期">{{ detail.sampling_date }}</el-descriptions-item>
        <el-descriptions-item label="接收日期">{{ detail.received_date }}</el-descriptions-item>
        <el-descriptions-item label="委托编号">{{ detail.commission_no }}</el-descriptions-item>
        <el-descriptions-item label="工程名称" :span="2">{{ detail.project_name }}</el-descriptions-item>
        <el-descriptions-item v-if="detail.retention_deadline" label="留样到期日">
          {{ detail.retention_deadline }}
        </el-descriptions-item>
        <el-descriptions-item v-if="detail.disposal_date" label="处置日期">
          {{ detail.disposal_date }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Testing Tasks -->
    <el-card v-if="tasksLoaded && tasks.length" shadow="never" style="margin-top: 16px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>检测任务</span>
          <el-button type="primary" link @click="goTasks">查看全部</el-button>
        </div>
      </template>
      <el-table :data="tasks" stripe border size="small">
        <el-table-column prop="task_no" label="任务编号" min-width="140">
          <template #default="{ row }">
            <router-link :to="`/testing/tasks/${row.id}`" class="link-primary">{{ row.task_no }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="parameter_name" label="检测参数" min-width="120" />
        <el-table-column prop="standard_no" label="标准编号" min-width="120" />
        <el-table-column prop="tester_name" label="检测人员" width="100">
          <template #default="{ row }">{{ row.tester_name || '未分配' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="{ unassigned: 'info', in_progress: 'warning', completed: 'success' }[row.status as string] ?? 'info'" size="small">
              {{ { unassigned: '待分配', in_progress: '检测中', completed: '已完成' }[row.status as string] ?? row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Timeline -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header><span>状态记录</span></template>
      <el-timeline v-if="timeline.length">
        <el-timeline-item
          v-for="(item, idx) in timeline"
          :key="idx"
          :timestamp="item.time"
          placement="top"
        >
          <p><strong>{{ statusLabel(item.status) }}</strong> — {{ item.operator }}</p>
          <p v-if="item.remark" style="color: var(--el-text-color-secondary); font-size: 13px">{{ item.remark }}</p>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无记录" :image-size="60" />
    </el-card>

    <!-- Dispose Dialog -->
    <el-dialog v-model="disposeDialogVisible" title="样品处置" width="460px" destroy-on-close>
      <el-form :model="disposeForm" label-width="80px">
        <el-form-item label="处置方式">
          <el-select v-model="disposeForm.disposal_method" style="width: 100%">
            <el-option label="退还委托方" value="return" />
            <el-option label="实验室销毁" value="destroy" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="disposeForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="disposeDialogVisible = false">取消</el-button>
        <el-button v-permission="'sample:create'" type="primary" :loading="isLocked('sample_dispose')" @click="handleDispose">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
