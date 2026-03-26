<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTestTask, assignTask, startTask, completeTask, getTestResults } from '@/api/testing'
import type { TestTask, TestResult } from '@/types/testing'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const task = ref<TestTask | null>(null)
const results = ref<TestResult[]>([])

const taskId = computed(() => Number(route.params.id))

const statusMap: Record<string, string> = {
  pending: '待分配',
  assigned: '待检',
  testing: '检测中',
  completed: '已完成',
}

const statusTagType: Record<string, string> = {
  pending: 'info',
  assigned: 'warning',
  testing: '',
  completed: 'success',
}

async function fetchTask() {
  loading.value = true
  try {
    task.value = await getTestTask(taskId.value) as any
  } finally {
    loading.value = false
  }
}

async function fetchResults() {
  try {
    const res: any = await getTestResults({ task_id: taskId.value })
    results.value = res.results ?? res.list ?? res ?? []
  } catch { /* ignore */ }
}

const assignDialogVisible = ref(false)
const assignTester = ref<number | null>(null)

async function handleAssign() {
  if (!task.value || !assignTester.value) return
  try {
    await assignTask(task.value.id, { tester_id: assignTester.value })
    ElMessage.success('分配成功')
    assignDialogVisible.value = false
    fetchTask()
  } catch {
    ElMessage.error('分配失败')
  }
}

async function handleStart() {
  if (!task.value) return
  try {
    await ElMessageBox.confirm('确认开始检测？', '提示')
    await startTask(task.value.id)
    ElMessage.success('已开始检测')
    fetchTask()
  } catch { /* cancelled */ }
}

async function handleComplete() {
  if (!task.value) return
  try {
    await ElMessageBox.confirm('确认完成检测？', '提示')
    await completeTask(task.value.id)
    ElMessage.success('检测已完成')
    fetchTask()
  } catch { /* cancelled */ }
}

function goRecord() {
  router.push(`/testing/records/new?task_id=${taskId.value}`)
}

function goBack() {
  router.push('/testing/tasks')
}

onMounted(() => {
  fetchTask()
  fetchResults()
})
</script>

<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <span v-if="task" class="page-title">任务详情 - {{ task.task_no }}</span>
    </div>

    <template v-if="task">
      <!-- Task Info -->
      <el-card shadow="never" style="margin-top: 16px">
        <template #header>
          <div class="card-header">
            <span>任务信息</span>
            <el-tag :type="statusTagType[task.status]" effect="dark">
              {{ statusMap[task.status] ?? task.status }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="任务编号">{{ task.task_no }}</el-descriptions-item>
          <el-descriptions-item label="检测方法">{{ task.method_name }}</el-descriptions-item>
          <el-descriptions-item label="标准编号">{{ task.standard_no }}</el-descriptions-item>
          <el-descriptions-item label="检测人员">
            {{ task.tester_name || '未分配' }}
          </el-descriptions-item>
          <el-descriptions-item label="计划日期">{{ task.planned_date }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ task.started_at ?? '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ task.completed_at ?? '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ task.remark || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Sample Info -->
      <el-card shadow="never" style="margin-top: 16px">
        <template #header><span>样品信息</span></template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="样品编号">{{ task.sample_no }}</el-descriptions-item>
          <el-descriptions-item label="样品名称">{{ task.sample_name }}</el-descriptions-item>
          <el-descriptions-item label="委托编号">{{ task.commission_no }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- Equipment Info -->
      <el-card
        v-if="task.equipment_names?.length"
        shadow="never"
        style="margin-top: 16px"
      >
        <template #header><span>设备信息</span></template>
        <el-tag
          v-for="(name, idx) in task.equipment_names"
          :key="idx"
          style="margin-right: 8px; margin-bottom: 8px"
        >
          {{ name }}
        </el-tag>
      </el-card>

      <!-- Test Results -->
      <el-card shadow="never" style="margin-top: 16px">
        <template #header>
          <div class="card-header">
            <span>检测结果</span>
            <el-button
              v-if="task.status === 'testing'"
              type="primary"
              size="small"
              @click="goRecord"
            >
              填写原始记录
            </el-button>
          </div>
        </template>
        <el-table :data="results" stripe border>
          <el-table-column prop="parameter_name" label="检测参数" min-width="140" />
          <el-table-column prop="value" label="检测值" width="120" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column label="限值范围" width="140">
            <template #default="{ row }">
              <span v-if="row.limit_low != null || row.limit_high != null">
                {{ row.limit_low ?? '-' }} ~ {{ row.limit_high ?? '-' }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="判定" width="100" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="row.is_qualified != null"
                :type="row.is_qualified ? 'success' : 'danger'"
                size="small"
              >
                {{ row.is_qualified ? '合格' : '不合格' }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        </el-table>
        <el-empty v-if="!results.length" description="暂无检测结果" />
      </el-card>

      <!-- Actions -->
      <div class="action-bar">
        <el-button
          v-if="task.status === 'pending'"
          type="primary"
          @click="assignDialogVisible = true"
        >
          分配人员
        </el-button>
        <el-button
          v-if="task.status === 'assigned'"
          type="warning"
          @click="handleStart"
        >
          开始检测
        </el-button>
        <el-button
          v-if="task.status === 'testing'"
          type="success"
          @click="handleComplete"
        >
          完成检测
        </el-button>
        <el-button
          v-if="task.status === 'testing'"
          @click="goRecord"
        >
          填写原始记录
        </el-button>
      </div>
    </template>

    <!-- Assign Dialog -->
    <el-dialog v-model="assignDialogVisible" title="分配检测人员" width="400px">
      <el-form label-width="80px">
        <el-form-item label="检测人员">
          <el-input v-model.number="assignTester" placeholder="请输入检测人员ID" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAssign">确定</el-button>
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
</style>
