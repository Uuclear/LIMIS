<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh, Grid, List } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTestTaskList, assignTask, startTask, completeTask } from '@/api/testing'
import type { TestTask } from '@/types/testing'

const router = useRouter()
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
})

const statusColumns = [
  { key: 'unassigned', label: '待分配', type: 'info' as const },
  { key: 'assigned', label: '待检', type: 'warning' as const },
  { key: 'in_progress', label: '检测中', type: '' as const },
  { key: 'completed', label: '已完成', type: 'success' as const },
  { key: 'abnormal', label: '异常', type: 'danger' as const },
]

const statusMap: Record<string, string> = {
  unassigned: '待分配',
  assigned: '待检',
  in_progress: '检测中',
  completed: '已完成',
  abnormal: '异常',
}

const statusTagType: Record<string, string> = {
  unassigned: 'info',
  assigned: 'warning',
  in_progress: '',
  completed: 'success',
  abnormal: 'danger',
}

const kanbanData = computed(() => {
  const grouped: Record<string, TestTask[]> = {
    unassigned: [], assigned: [], in_progress: [], completed: [], abnormal: [],
  }
  for (const task of tableData.value) {
    if (grouped[task.status]) {
      grouped[task.status].push(task)
    }
  }
  return grouped
})

const assignDialogVisible = ref(false)
const currentTask = ref<TestTask | null>(null)
const assignForm = reactive({ tester_id: null as number | null, tester_name: '' })

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, any> = { ...query }
    if (query.date_range?.length === 2) {
      params.start_date = query.date_range[0]
      params.end_date = query.date_range[1]
    }
    delete params.date_range
    const res: any = await getTestTaskList(params)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, {
    page: 1, status: '', tester_name: '', date_range: [],
  })
  fetchList()
}

function goDetail(task: TestTask) {
  router.push(`/testing/tasks/${task.id}`)
}

function openAssignDialog(task: TestTask) {
  currentTask.value = task
  assignForm.tester_id = null
  assignForm.tester_name = ''
  assignDialogVisible.value = true
}

async function handleAssign() {
  if (!currentTask.value || !assignForm.tester_id) return
  try {
    await assignTask(currentTask.value.id, {
      tester_id: assignForm.tester_id,
    })
    ElMessage.success('分配成功')
    assignDialogVisible.value = false
    fetchList()
  } catch {
    ElMessage.error('分配失败')
  }
}

async function handleStart(task: TestTask) {
  try {
    await ElMessageBox.confirm('确认开始检测？', '提示')
    await startTask(task.id)
    ElMessage.success('已开始检测')
    fetchList()
  } catch { /* cancelled */ }
}

async function handleComplete(task: TestTask) {
  try {
    await ElMessageBox.confirm('确认完成检测？', '提示')
    await completeTask(task.id)
    ElMessage.success('检测已完成')
    fetchList()
  } catch { /* cancelled */ }
}

function isOverdue(task: TestTask) {
  if (task.status === 'completed') return false
  return new Date(task.planned_date) < new Date()
}

onMounted(fetchList)
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
              <div class="kanban-card-info">{{ task.sample_name }}</div>
              <div class="kanban-card-info">{{ task.method_name }}</div>
              <div class="kanban-card-footer">
                <span>{{ task.planned_date }}</span>
                <span v-if="task.tester_name">{{ task.tester_name }}</span>
              </div>
              <div class="kanban-card-actions" @click.stop>
                <el-button
                  v-if="task.status === 'unassigned'"
                  size="small"
                  v-permission="'testing:edit'"
                  type="primary"
                  @click="openAssignDialog(task)"
                >
                  分配
                </el-button>
                <el-button
                  v-if="task.status === 'assigned'"
                  size="small"
                  type="warning"
                  @click="handleStart(task)"
                >
                  开始
                </el-button>
                <el-button
                  v-if="task.status === 'in_progress'"
                  size="small"
                  type="success"
                  @click="handleComplete(task)"
                >
                  完成
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
          <el-table-column prop="method_name" label="检测方法" min-width="160" show-overflow-tooltip />
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
              <el-button link type="primary" @click="goDetail(row)">查看</el-button>
              <el-button
                v-if="row.status === 'unassigned'"
                v-permission="'testing:edit'"
                link type="primary"
                @click="openAssignDialog(row)"
              >
                分配
              </el-button>
              <el-button
                v-if="row.status === 'assigned'"
                link type="warning"
                @click="handleStart(row)"
              >
                开始
              </el-button>
              <el-button
                v-if="row.status === 'in_progress'"
                link type="success"
                @click="handleComplete(row)"
              >
                完成
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
          <el-input v-model.number="assignForm.tester_id" placeholder="请输入检测人员ID" />
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
