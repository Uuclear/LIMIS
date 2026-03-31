<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { batchCreateSamples } from '@/api/samples'
import { getCommissionList } from '@/api/commissions'

const router = useRouter()
const formRef = ref()
const saving = ref(false)

const commissionOptions = ref<{ id: number; commission_no: string; project_name: string }[]>([])

interface SampleRow {
  name: string
  specification: string
  grade: string
  quantity: number
  unit: string
  sampling_date: string
  received_date: string
}

const form = reactive({
  commission_id: null as number | null,
  samples: [] as SampleRow[],
})

const rules = {
  commission_id: [{ required: true, message: '请选择委托', trigger: 'change' }],
}

const selectedCommission = ref<any>(null)

async function fetchCommissions() {
  const res: any = await getCommissionList({ page_size: 500, status: 'reviewed' })
  commissionOptions.value = res.results ?? res.list ?? []
}

function handleCommissionChange(id: number) {
  selectedCommission.value = commissionOptions.value.find(c => c.id === id) ?? null
}

function addSample() {
  form.samples.push({
    name: '', specification: '', grade: '',
    quantity: 1, unit: '组', sampling_date: '', received_date: '',
  })
}

function removeSample(index: number) {
  form.samples.splice(index, 1)
}

async function handleSubmit() {
  await formRef.value?.validate()
  if (!form.samples.length) {
    return ElMessage.warning('请至少添加一个样品')
  }
  for (let i = 0; i < form.samples.length; i++) {
    if (!form.samples[i].name) {
      return ElMessage.warning(`第${i + 1}行样品名称不能为空`)
    }
  }
  saving.value = true
  try {
    await batchCreateSamples({
      commission_id: form.commission_id,
      samples: form.samples,
    })
    ElMessage.success('样品登记成功')
    router.push('/sample')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchCommissions()
  addSample()
})
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/sample')">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">样品登记</span>
      </template>
    </el-page-header>

    <el-card shadow="never" style="margin-top: 20px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-divider content-position="left">关联委托</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="选择委托" prop="commission_id">
              <el-select
                v-model="form.commission_id"
                placeholder="请选择委托"
                filterable
                style="width: 100%"
                @change="handleCommissionChange"
              >
                <el-option
                  v-for="c in commissionOptions"
                  :key="c.id"
                  :label="`${c.commission_no} - ${c.project_name}`"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工程名称">
              <el-input :model-value="selectedCommission?.project_name ?? ''" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">样品信息</el-divider>
        <div style="margin-bottom: 12px">
          <el-button v-permission="'sample:create'" type="primary" :icon="Plus" size="small" @click="addSample">添加样品</el-button>
        </div>

        <el-table :data="form.samples" border>
          <el-table-column label="样品名称" min-width="140">
            <template #default="{ row }">
              <el-input v-model="row.name" size="small" placeholder="必填" />
            </template>
          </el-table-column>
          <el-table-column label="规格型号" width="140">
            <template #default="{ row }">
              <el-input v-model="row.specification" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="设计等级" width="120">
            <template #default="{ row }">
              <el-input v-model="row.grade" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="数量" width="90">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" size="small" controls-position="right" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="单位" width="80">
            <template #default="{ row }">
              <el-input v-model="row.unit" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="取样日期" width="170">
            <template #default="{ row }">
              <el-date-picker v-model="row.sampling_date" type="date" value-format="YYYY-MM-DD" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="接收日期" width="170">
            <template #default="{ row }">
              <el-date-picker v-model="row.received_date" type="date" value-format="YYYY-MM-DD" size="small" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button v-permission="'sample:create'" link type="danger" :icon="Delete" @click="removeSample($index)" />
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 24px; text-align: right">
          <el-button @click="router.push('/sample')">取消</el-button>
          <el-button v-permission="'sample:create'" type="primary" :loading="saving" @click="handleSubmit">提交登记</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>
