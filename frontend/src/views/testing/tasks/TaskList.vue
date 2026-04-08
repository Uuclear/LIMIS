<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, Refresh, Grid, List } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTestTaskList, assignTask, completeTask, returnTask, returnTaskToCommission } from '@/api/testing'
import { getAssignableTesters } from '@/api/staff'
import type { TestTask } from '@/types/testing'
import { useActionLock } from '@/composables/useActionLock'

const { isLocked, runLocked } = useActionLock()

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const tableData = ref<TestTask[]>([])
const total = ref(0)
const viewMode = ref<'kanban' | 'table'>('kanban')

const query = reactive({
  page: 1,
  page_size: 50,
  status: '',
  tester_name: '',
  date_range: [] as string[],
  sample: null as number | null,
})

const statusColumns = [
  { key: 'unassigned', label: '待分配', type: 'info' as const },
  { key: 'in_progress', label: '检测中', type: '' as const },
  { key: 'completed', label: '已完成', type: 'success' as const },
  { key: 'abnormal', label: '异常', type: 'danger' as const },
]

const statusMap: Record<string, string> = {
  unassigned: '待分配',
  in_progress: '检测中',
  completed: '已完成',
  abnormal: '异常',
}

const statusTagType: Record<string, string> = {
  unassigned: 'info',
  in_progress: '',
  completed: 'success',
  abnormal: 'danger',
}

const kanbanData = computed(() => {
  const grouped: Record<string, TestTask[]> = {
    unassigned: [], in_progress: [], completed: [], abnormal: [],
  }
  for (const task of tableData.value) {
    if (grouped[task.status]) {
      grouped[task.status].push(task)
    }
  }
  return grouped
})
const hasSampleFilter = computed(() => !!query.sample)

const assignDialogVisible = ref(false)
const currentTask = ref<TestTask | null>(null)
const assignForm = reactive({ tester_id: null as number | null, tester_name: '' })
const testerOptions = ref<{ value: number; label: string }[]>([])
const testerLoading = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: query.page,
      page_size: query.page_size,
    }
    if (query.status) params.status = query.status
    if (query.sample) params.sample = query.sample
    if (query.date_range?.length === 2) {
      params.planned_date_from = query.date_range[0]
      params.planned_date_to = query.date_range[1]
    }
    const tn = (query.tester_name || '').trim()
    if (tn) params.search = tn
    const res: any = await getTestTaskList(params)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

async function fetchTesterOptions(methodId?: number) {
  testerLoading.value = true
  try {
    const res: any = await getAssignableTesters(methodId)
    const rows = res.results ?? res.list ?? res ?? []
    const seen = new Set<number>()
    testerOptions.value = rows
      .map((r: any) => {
        const uid = Number(r.user)
        const name = r.name || r.user_name || r.staff_no || ''
        return Number.isFinite(uid) && uid > 0 ? {
          value: uid,
          label: `${name} (${r.staff_no || r.employee_no || uid})`,
        } : null
      })
      .filter((x: any) => x && !seen.has(x.value) && seen.add(x.value))
  } finally {
    testerLoading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, {
    page: 1, status: '', tester_name: '', date_range: [], sample: null,
  })
  fetchList()
}

function goDetail(task: TestTask) {
  router.push(`/testing/tasks/${task.id}`)
}

function goSampleDetail() {
  if (!query.sample) return
  router.push(`/sample/${query.sample}`)
}

function openAssignDialog(task: TestTask) {
  currentTask.value = task
  assignForm.tester_id = null
  assignForm.tester_name = ''
  fetchTesterOptions((task as any).test_parameter)
  assignDialogVisible.value = true
}

async function handleAssign() {
  if (!currentTask.value || !assignForm.tester_id) return
  await runLocked(`assign_task_${currentTask.value.id}`, async () => {
    try {
      await assignTask(currentTask.value!.id, {
        tester: assignForm.tester_id,
      })
      ElMessage.success('分配成功')
      assignDialogVisible.value = false
      fetchList()
    } catch {
      ElMessage.error('分配失败')
    }
  })
}

async function handleComplete(task: TestTask) {
  await runLocked(`complete_task_${task.id}`, async () => {
    try {
      await ElMessageBox.confirm('确认完成检测？', '提示')
      await completeTask(task.id)
      ElMessage.success('检测已完成')
      fetchList()
    } catch { /* cancelled */ }
  })
}

async function handleReturn(task: TestTask) {
  let reason = ''
  try {
    const prompt = await ElMessageBox.prompt('请输入退回原因（至少4个字符）', '退回待分配', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^.{4,}$/,
      inputErrorMessage: '原因至少4个字符',
    })
    reason = prompt.value
  } catch {
    return
  }
  await runLocked(`return_task_${task.id}`, async () => {
    try {
      await returnTask(task.id, { reason })
      ElMessage.success('已退回待分配')
      fetchList()
    } catch { /* cancelled */ }
  })
}



async function handleReturnCommission(task: TestTask) {
  let reason = ''
  try {
    const prompt = await ElMessageBox.prompt('请输入退回委托原因（至少4个字符）', '退回委托提交', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^.{4,}$/,
      inputErrorMessage: '原因至少4个字符',
    })
    reason = prompt.value
  } catch {
    return
  }
  await runLocked(`return_commission_${task.id}`, async () => {
    try {
      await returnTaskToCommission(task.id, { reason })
      ElMessage.success('已退回委托提交流程')
      fetchList()
    } catch { /* cancelled */ }
  })
}

function handleChangeCommission(task: TestTask) {
  const cid = (task as any).commission
  if (!cid) return
  router.push(`/entrustment/${cid}/edit`)
}

function isOverdue(task: TestTask) {
  if (task.status === 'completed') return false
  return new Date(task.planned_date) < new Date()
}

onMounted(() => {
  const s = route.query.sample
  const st = route.query.status
  if (s != null && s !== '') query.sample = Number(s)
  if (st != null && st !== '') query.status = String(st)
  fetchList()
})
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 120px">
            <el-option
              v-for="col in statusColumns"
              :key="col.key"
              :label="col.label"
              :value="col.key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="检测人员">
          <el-input
            v-model="query.tester_name"
            placeholder="检测人员姓名"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item label="计划日期">
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
        <div class="card-header">
          <span>检测任务</span>
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button value="kanban">
              <el-icon><Grid /></el-icon> 看板
            </el-radio-button>
            <el-radio-button value="table">
              <el-icon><List /></el-icon> 列表
            </el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-alert
        v-if="hasSampleFilter && !loading && tableData.length === 0"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 12px"
      >
        <template #title>
          当前样品暂无检测任务。请回到样品详情点击“生成检测任务”后再分配人员。
        </template>
        <template #default>
          <el-button v-permission="'sample:view'" type="primary" link @click="goSampleDetail">返回样品详情</el-button>
        </template>
      </el-alert>

      <!-- Kanban View -->
      <div v-if="viewMode === 'kanban'" v-loading="loading" class="kanban-board">
        <div v-for="col in statusColumns" :key="col.key" class="kanban-column">
          <div class="kanban-column-header">
            <el-tag :type="col.type" effect="dark" round>
              {{ col.label }}
            </el-tag>
            <el-badge :value="kanbanData[col.key]?.length ?? 0" type="info" />
          </div>
          <div class="kanban-column-body">
            <div
              v-for="task in kanbanData[col.key]"
              :key="task.id"
              class="kanban-card"
              :class="{ 'is-overdue': isOverdue(task) }"
              @click="goDetail(task)"
            >
              <div class="kanban-card-title">{{ task.task_no }}</div>
              <div class="kanban-card-info">{{ task.commission_no }} / {{ task.sample_no }}</div>
              <div class="kanban-card-info">{{ task.sample_name }}</div>
              <div class="kanban-card-info" style="color: var(--el-color-primary)">{{ task.parameter_name }}</div>
              <div class="kanban-card-footer">
                <span>{{ task.planned_date || '未排期' }}</span>
                <span v-if="task.tester_name">{{ task.tester_name }}</span>
              </div>
              <div class="kanban-card-actions" @click.stop>
                <el-button
                  v-if="task.status === 'unassigned'"
                  v-permission="'task:edit'"
                  size="small"
                  type="primary"
                  @click="openAssignDialog(task)"
                >
                  分配
                </el-button>
                <el-button
                  v-if="task.status === 'unassigned'"
                  v-permission="'task:edit'"
                  size="small"
                  type="warning"
                  :loading="isLocked(`return_commission_${task.id}`)"
                  @click="handleReturnCommission(task)"
                >
                  退回委托
                </el-button>
                <el-button
                  v-if="task.status === 'unassigned'"
                  v-permission="'commission:edit'"
                  size="small"
                  @click="handleChangeCommission(task)"
                >
                  变更委托
                </el-button>
                <el-button
                  v-if="task.status === 'in_progress'"
                  v-permission="'testing:create'"
                  size="small"
                  type="primary"
                  @click.stop="router.push(`/testing/records/new?task_id=${task.id}`)"
                >
                  填写记录
                </el-button>
                <el-button
                  v-if="task.status === 'in_progress'"
                  v-permission="'task:edit'"
                  size="small"
                  type="success"
                  :loading="isLocked(`complete_task_${task.id}`)"
                  @click="handleComplete(task)"
                >
                  完成
                </el-button>
                <el-button
                  v-if="task.status === 'in_progress'"
                  v-permission="'task:edit'"
                  size="small"
                  type="danger"
                  :loading="isLocked(`return_task_${task.id}`)"
                  @click="handleReturn(task)"
                >
                  退回
                </el-button>
              </div>
            </div>
            <el-empty
              v-if="!kanbanData[col.key]?.length"
              description="暂无任务"
              :image-size="60"
            />
          </div>
        </div>
      </div>

      <!-- Table View -->
      <template v-if="viewMode === 'table'">
        <el-table v-loading="loading" :data="tableData" stripe border>
          <el-table-column prop="task_no" label="任务编号" width="180" />
          <el-table-column prop="sample_name" label="样品" min-width="140" show-overflow-tooltip />
          <el-table-column prop="parameter_name" label="检测参数" min-width="160" show-overflow-tooltip />
          <el-table-column prop="tester_name" label="检测人员" width="120" />
          <el-table-column prop="planned_date" label="计划日期" width="120" />
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType[row.status]" size="small">
                {{ statusMap[row.status] ?? row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button v-permission="'task:view'" link type="primary" @click="goDetail(row)">查看</el-button>
              <el-button
                v-if="row.status === 'unassigned'"
                v-permission="'task:edit'"
                link
                type="primary"
                @click="openAssignDialog(row)"
              >
                分配
              </el-button>
              <el-button
                v-if="row.status === 'unassigned'"
                v-permission="'task:edit'"
                link
                type="warning"
                :loading="isLocked(`return_commission_${row.id}`)"
                @click="handleReturnCommission(row)"
              >
                退回委托
              </el-button>
              <el-button
                v-if="row.status === 'unassigned'"
                v-permission="'commission:edit'"
                link
                @click="handleChangeCommission(row)"
              >
                变更委托
              </el-button>
              <el-button
                v-if="row.status === 'in_progress'"
                v-permission="'task:edit'"
                link
                type="success"
                :loading="isLocked(`complete_task_${row.id}`)"
                @click="handleComplete(row)"
              >
                完成
              </el-button>
              <el-button
                v-if="row.status === 'in_progress'"
                v-permission="'task:edit'"
                link
                type="danger"
                :loading="isLocked(`return_task_${row.id}`)"
                @click="handleReturn(row)"
              >
                退回
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
      </template>
    </el-card>

    <!-- Assign Dialog -->
    <el-dialog v-model="assignDialogVisible" title="分配检测人员" width="400px">
      <el-form label-width="80px">
        <el-form-item label="检测人员">
          <el-select
            v-model="assignForm.tester_id"
            filterable
            clearable
            placeholder="请选择检测人员"
            style="width: 100%"
            :loading="testerLoading"
          >
            <el-option
              v-for="u in testerOptions"
              :key="u.value"
              :label="u.label"
              :value="u.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button
          v-permission="'task:edit'"
          type="primary"
          :loading="currentTask ? isLocked(`assign_task_${currentTask.id}`) : false"
          @click="handleAssign"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kanban-board {
  display: flex;
  gap: 16px;
  min-height: 500px;
  overflow-x: auto;
}

.kanban-column {
  flex: 1;
  min-width: 260px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.kanban-column-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  font-weight: 600;
}

.kanban-column-body {
  flex: 1;
  padding: 0 12px 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.kanban-card {
  background: #fff;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  border: 1px solid var(--el-border-color-lighter);
  transition: box-shadow 0.2s;
}

.kanban-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.kanban-card.is-overdue {
  border-left: 3px solid var(--el-color-danger);
}

.kanban-card-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
  color: var(--el-text-color-primary);
}

.kanban-card-info {
  font-size: 13px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kanban-card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}

.kanban-card-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}
</style>
