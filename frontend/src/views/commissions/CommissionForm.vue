<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getCommission, createCommission, updateCommission, submitCommission } from '@/api/commissions'
import { getProjectList, getSubProjects, getWitnesses } from '@/api/projects'
import type { CommissionItem } from '@/types/commission'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const commissionId = computed(() => Number(route.params.id) || 0)

const formRef = ref()
const saving = ref(false)

const form = reactive({
  project_id: null as number | null,
  sub_project_id: null as number | null,
  construction_part: '',
  commission_date: '',
  client_name: '',
  client_phone: '',
  witness_id: null as number | null,
  witness_sampling: false,
  items: [] as CommissionItem[],
})

const rules = {
  project_id: [{ required: true, message: '请选择工程项目', trigger: 'change' }],
  commission_date: [{ required: true, message: '请选择委托日期', trigger: 'change' }],
}

const projectOptions = ref<{ id: number; name: string }[]>([])
const subProjectOptions = ref<{ id: number; name: string }[]>([])
const witnessOptions = ref<{ id: number; name: string }[]>([])

async function fetchProjects() {
  const res: any = await getProjectList({ page_size: 500 })
  projectOptions.value = res.results ?? res.list ?? []
}

async function handleProjectChange(projectId: number) {
  form.sub_project_id = null
  form.witness_id = null
  if (!projectId) return
  const [subRes, witRes]: any[] = await Promise.all([
    getSubProjects(projectId),
    getWitnesses(projectId),
  ])
  subProjectOptions.value = subRes.results ?? subRes.list ?? subRes ?? []
  witnessOptions.value = witRes.results ?? witRes.list ?? witRes ?? []
}

async function fetchDetail() {
  if (!commissionId.value) return
  const res: any = await getCommission(commissionId.value)
  Object.assign(form, {
    project_id: res.project_id,
    sub_project_id: res.sub_project_id,
    construction_part: res.construction_part,
    commission_date: res.commission_date,
    client_name: res.client_name,
    client_phone: res.client_phone,
    witness_id: res.witness_id,
    witness_sampling: res.witness_sampling,
    items: res.items ?? [],
  })
  if (res.project_id) await handleProjectChange(res.project_id)
}

function addItem() {
  form.items.push({
    test_object: '', test_item: '', test_standard: '',
    specification: '', design_grade: '', quantity: 1, unit: '组',
  })
}

function removeItem(index: number) {
  form.items.splice(index, 1)
}

async function handleSave() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await updateCommission(commissionId.value, form)
    } else {
      await createCommission(form)
    }
    ElMessage.success('保存成功')
    router.push('/entrustment')
  } finally {
    saving.value = false
  }
}

async function handleSaveAndSubmit() {
  await formRef.value?.validate()
  saving.value = true
  try {
    let id = commissionId.value
    if (isEdit.value) {
      await updateCommission(id, form)
    } else {
      const res: any = await createCommission(form)
      id = res.id ?? res
    }
    await submitCommission(id)
    ElMessage.success('已提交评审')
    router.push('/entrustment')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchProjects()
  if (isEdit.value) await fetchDetail()
})
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/entrustment')">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">{{ isEdit ? '编辑委托' : '新增委托' }}</span>
      </template>
    </el-page-header>

    <el-card shadow="never" style="margin-top: 20px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工程项目" prop="project_id">
              <el-select
                v-model="form.project_id"
                placeholder="请选择"
                filterable
                style="width: 100%"
                @change="handleProjectChange"
              >
                <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分部工程">
              <el-select v-model="form.sub_project_id" placeholder="请选择" clearable style="width: 100%">
                <el-option v-for="s in subProjectOptions" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="施工部位">
              <el-input v-model="form.construction_part" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="委托日期" prop="commission_date">
              <el-date-picker v-model="form.commission_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="委托人">
              <el-input v-model="form.client_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="form.client_phone" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="见证人">
              <el-select v-model="form.witness_id" placeholder="请选择" clearable style="width: 100%">
                <el-option v-for="w in witnessOptions" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="见证取样">
              <el-switch v-model="form.witness_sampling" active-text="是" inactive-text="否" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">检测项目</el-divider>
        <div style="margin-bottom: 12px">
          <el-button type="primary" :icon="Plus" size="small" @click="addItem">添加项目</el-button>
        </div>

        <el-table :data="form.items" border>
          <el-table-column label="检测对象" min-width="140">
            <template #default="{ row }">
              <el-input v-model="row.test_object" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="检测项目" min-width="140">
            <template #default="{ row }">
              <el-input v-model="row.test_item" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="检测标准" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.test_standard" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="规格型号" width="130">
            <template #default="{ row }">
              <el-input v-model="row.specification" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="设计等级" width="120">
            <template #default="{ row }">
              <el-input v-model="row.design_grade" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="数量" width="90">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" size="small" controls-position="right" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="单位" width="90">
            <template #default="{ row }">
              <el-input v-model="row.unit" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button link type="danger" :icon="Delete" @click="removeItem($index)" />
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 24px; text-align: right">
          <el-button @click="router.push('/entrustment')">取消</el-button>
          <el-button type="info" :loading="saving" @click="handleSave">保存草稿</el-button>
          <el-button type="primary" :loading="saving" @click="handleSaveAndSubmit">提交评审</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>
