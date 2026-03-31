<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getOriginalRecord,
  createOriginalRecord,
  updateOriginalRecord,
  submitRecord,
  calculateResult,
} from '@/api/testing'
import type { OriginalRecord } from '@/types/testing'
import { useActionLock } from '@/composables/useActionLock'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const { isLocked, runLocked } = useActionLock()

const recordId = computed(() => {
  const id = route.params.id as string
  return id === 'new' ? null : Number(id)
})

const isEdit = computed(() => recordId.value != null)
const taskId = computed(() => Number(route.query.task_id) || null)

const form = ref({
  task_id: null as number | null,
  template_id: null as number | null,
  environment_temp: null as number | null,
  environment_humidity: null as number | null,
  equipment_ids: [] as number[],
  data: {
    rows: [] as DataRow[],
  },
})

interface DataRow {
  parameter_name: string
  unit: string
  value_1: string
  value_2: string
  value_3: string
  average: string
  remark: string
}

const record = ref<OriginalRecord | null>(null)

const calculatedResults = ref<Array<{
  parameter_name: string
  value: string
  unit: string
  is_qualified: boolean | null
}>>([])

const isReadonly = computed(() => {
  if (!record.value) return false
  // 仅草稿可编辑；提交后进入待复核/已复核/已退回，前端锁定编辑。
  return record.value.status !== 'draft'
})

const saveLockKey = computed(() => `save_record_${recordId.value ?? 'new'}`)
const submitLockKey = computed(() => {
  const id = recordId.value ?? record.value?.id
  return id != null ? `submit_record_${id}` : 'submit_record_none'
})

async function fetchRecord() {
  if (!recordId.value) return
  loading.value = true
  try {
    const res: any = await getOriginalRecord(recordId.value)
    record.value = res
    form.value = {
      task_id: res.task_id,
      template_id: res.template_id,
      environment_temp: res.environment_temp,
      environment_humidity: res.environment_humidity,
      equipment_ids: res.equipment_ids ?? [],
      data: res.data ?? { rows: [] },
    }
    if (!form.value.data.rows?.length) {
      form.value.data.rows = []
    }
  } finally {
    loading.value = false
  }
}

function initNewRecord() {
  form.value.task_id = taskId.value
  addRow()
}

function addRow() {
  form.value.data.rows.push({
    parameter_name: '',
    unit: '',
    value_1: '',
    value_2: '',
    value_3: '',
    average: '',
    remark: '',
  })
}

function removeRow(index: number) {
  form.value.data.rows.splice(index, 1)
}

async function handleSave() {
  const key = `save_record_${recordId.value ?? 'new'}`
  await runLocked(key, async () => {
    try {
      if (isEdit.value && recordId.value) {
        await updateOriginalRecord(recordId.value, form.value)
        ElMessage.success('保存成功')
      } else {
        const res: any = await createOriginalRecord(form.value)
        ElMessage.success('创建成功')
        router.replace(`/testing/records/${res.id}`)
      }
    } catch {
      ElMessage.error('保存失败')
    }
  })
}

async function handleSubmit() {
  const id = recordId.value ?? (record.value?.id)
  if (!id) {
    ElMessage.warning('请先保存记录')
    return
  }
  await runLocked(`submit_record_${id}`, async () => {
    try {
      await ElMessageBox.confirm('确认提交审核？提交后不可修改。', '提示')
      await submitRecord(id)
      ElMessage.success('提交成功')
      router.push('/testing/records')
    } catch { /* cancelled */ }
  })
}

async function handleCalculate() {
  await runLocked('calculate_result', async () => {
    try {
      const res: any = await calculateResult({
        task_id: form.value.task_id,
        rows: form.value.data.rows,
      })
      calculatedResults.value = res.results ?? res ?? []
      ElMessage.success('计算完成')
    } catch {
      ElMessage.error('计算失败')
    }
  })
}

function goBack() {
  router.push('/testing/records')
}

onMounted(() => {
  if (isEdit.value) {
    fetchRecord()
  } else {
    initNewRecord()
  }
})
</script>

<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <span class="page-title">
        {{ isEdit ? '编辑原始记录' : '新建原始记录' }}
        <template v-if="record"> - {{ record.record_no }}</template>
      </span>
      <el-tag v-if="record" :type="record.status === 'draft' ? 'info' : 'success'" effect="dark">
        {{
          record.status === 'draft'
            ? '草稿'
            : record.status === 'pending_review'
              ? '待复核'
              : record.status === 'reviewed'
                ? '已复核'
                : record.status === 'returned'
                  ? '已退回'
                  : record.status
        }}
      </el-tag>
    </div>

    <!-- Header Info -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header><span>基本信息</span></template>
      <el-form :model="form" label-width="100px" :disabled="isReadonly">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="任务ID">
              <el-input v-model.number="form.task_id" placeholder="关联任务ID" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="环境温度(℃)">
              <el-input-number
                v-model="form.environment_temp"
                :precision="1"
                :step="0.5"
                placeholder="温度"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="环境湿度(%)">
              <el-input-number
                v-model="form.environment_humidity"
                :precision="1"
                :step="1"
                placeholder="湿度"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- Data Entry -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>检测数据</span>
          <div v-if="!isReadonly">
            <el-button type="primary" size="small" :icon="Plus" @click="addRow">
              添加行
            </el-button>
            <el-button
              size="small"
              :loading="isLocked('calculate_result')"
              @click="handleCalculate"
            >
              计算结果
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="form.data.rows" border stripe>
        <el-table-column label="检测参数" min-width="140">
          <template #default="{ row }">
            <el-input
              v-if="!isReadonly"
              v-model="row.parameter_name"
              placeholder="参数名称"
              size="small"
            />
            <span v-else>{{ row.parameter_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="单位" width="90">
          <template #default="{ row }">
            <el-input
              v-if="!isReadonly"
              v-model="row.unit"
              placeholder="单位"
              size="small"
            />
            <span v-else>{{ row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column label="测量值1" width="120">
          <template #default="{ row }">
            <el-input
              v-if="!isReadonly"
              v-model="row.value_1"
              placeholder="值1"
              size="small"
            />
            <span v-else>{{ row.value_1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="测量值2" width="120">
          <template #default="{ row }">
            <el-input
              v-if="!isReadonly"
              v-model="row.value_2"
              placeholder="值2"
              size="small"
            />
            <span v-else>{{ row.value_2 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="测量值3" width="120">
          <template #default="{ row }">
            <el-input
              v-if="!isReadonly"
              v-model="row.value_3"
              placeholder="值3"
              size="small"
            />
            <span v-else>{{ row.value_3 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="平均值" width="120">
          <template #default="{ row }">
            <el-input
              v-if="!isReadonly"
              v-model="row.average"
              placeholder="平均"
              size="small"
            />
            <span v-else>{{ row.average }}</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="120">
          <template #default="{ row }">
            <el-input
              v-if="!isReadonly"
              v-model="row.remark"
              placeholder="备注"
              size="small"
            />
            <span v-else>{{ row.remark }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="!isReadonly" label="操作" width="70" fixed="right">
          <template #default="{ $index }">
            <el-button
              :icon="Delete"
              link
              type="danger"
              @click="removeRow($index)"
            />
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!form.data.rows.length" description="暂无数据，请添加检测数据行" />
    </el-card>

    <!-- Calculated Results -->
    <el-card v-if="calculatedResults.length" shadow="never" style="margin-top: 16px">
      <template #header><span>计算结果</span></template>
      <el-table :data="calculatedResults" border stripe>
        <el-table-column prop="parameter_name" label="参数" min-width="140" />
        <el-table-column prop="value" label="结果" width="140" />
        <el-table-column prop="unit" label="单位" width="100" />
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
      </el-table>
    </el-card>

    <!-- Review Info (readonly) -->
    <el-card
      v-if="record && record.reviewer_name"
      shadow="never"
      style="margin-top: 16px"
    >
      <template #header><span>审核信息</span></template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="审核人">
          {{ record.reviewer_name }}
        </el-descriptions-item>
        <el-descriptions-item label="审核日期">
          {{ record.review_date ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="审核意见">
          {{ record.review_comment || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Actions -->
    <div v-if="!isReadonly" class="action-bar">
      <el-button @click="goBack">取消</el-button>
      <el-button type="primary" :loading="isLocked(saveLockKey)" @click="handleSave">
        保存草稿
      </el-button>
      <el-button type="success" :loading="isLocked(submitLockKey)" @click="handleSubmit">
        提交审核
      </el-button>
    </div>
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
