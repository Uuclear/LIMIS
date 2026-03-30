<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getCommission, createCommission, updateCommission, submitCommission } from '@/api/commissions'
import { getProjectList, getSubProjects, getWitnesses } from '@/api/projects'
import { getStandardList } from '@/api/standards'
import { getTestMethods, getTestParameters } from '@/api/testing'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const commissionId = computed(() => Number(route.params.id) || 0)

const formRef = ref()
const saving = ref(false)

export interface CommissionItemRow {
  standard_id: number | null
  test_method_id: number | null
  test_parameter_id: number | null
  test_object: string
  specification: string
  grade: string
  quantity: number
  unit: string
}

const form = reactive({
  project: null as number | null,
  sub_project: null as number | null,
  construction_part: '',
  commission_date: '',
  client_unit: '',
  client_phone: '',
  witness: null as number | null,
  is_witnessed: false,
  items: [] as CommissionItemRow[],
})

const rules = {
  project: [{ required: true, message: '请选择工程项目', trigger: 'change' }],
  commission_date: [{ required: true, message: '请选择委托日期', trigger: 'change' }],
}

const projectOptions = ref<{ id: number; name: string }[]>([])
const subProjectOptions = ref<{ id: number; name: string }[]>([])
const witnessOptions = ref<{ id: number; name: string }[]>([])
const standardOptions = ref<any[]>([])

/** 每行缓存：标准号 -> 方法列表；方法 id -> 参数列表 */
const methodCache = ref<Record<string, any[]>>({})
const paramCache = ref<Record<number, any[]>>({})

async function fetchProjects() {
  const res: any = await getProjectList({ page_size: 500 })
  projectOptions.value = res.results ?? res.list ?? []
}

async function fetchStandards() {
  const res: any = await getStandardList({ page_size: 500 })
  standardOptions.value = res.results ?? res.list ?? []
}

async function handleProjectChange(projectId: number) {
  form.sub_project = null
  form.witness = null
  if (!projectId) return
  const [subRes, witRes]: any[] = await Promise.all([
    getSubProjects(projectId),
    getWitnesses(projectId),
  ])
  subProjectOptions.value = subRes.results ?? subRes.list ?? subRes ?? []
  witnessOptions.value = witRes.results ?? witRes.list ?? witRes ?? []
}

async function ensureMethodsForStandard(standardNo: string) {
  if (!standardNo || methodCache.value[standardNo] !== undefined) return
  const res: any = await getTestMethods({ standard_no: standardNo, page_size: 200 })
  methodCache.value[standardNo] = res.results ?? res.list ?? []
}

async function ensureParametersForMethod(methodId: number) {
  if (!methodId || paramCache.value[methodId] !== undefined) return
  const res: any = await getTestParameters({ method: methodId, page_size: 200 })
  paramCache.value[methodId] = res.results ?? res.list ?? []
}

async function onRowStandardChange(row: CommissionItemRow) {
  row.test_method_id = null
  row.test_parameter_id = null
  const std = standardOptions.value.find((s) => s.id === row.standard_id)
  if (std?.standard_no) {
    await ensureMethodsForStandard(std.standard_no)
  }
}

async function onRowMethodChange(row: CommissionItemRow) {
  row.test_parameter_id = null
  if (row.test_method_id) {
    await ensureParametersForMethod(row.test_method_id)
  }
}

function methodsForRow(row: CommissionItemRow) {
  const std = standardOptions.value.find((s) => s.id === row.standard_id)
  if (!std?.standard_no) return []
  return methodCache.value[std.standard_no] ?? []
}

function parametersForRow(row: CommissionItemRow) {
  if (!row.test_method_id) return []
  return paramCache.value[row.test_method_id] ?? []
}

async function fetchDetail() {
  if (!commissionId.value) return
  const res: any = await getCommission(commissionId.value)
  Object.assign(form, {
    project: res.project,
    sub_project: res.sub_project,
    construction_part: res.construction_part,
    commission_date: res.commission_date,
    client_unit: res.client_unit,
    client_phone: res.client_phone,
    witness: res.witness,
    is_witnessed: res.is_witnessed,
    items: (res.items ?? []).map((it: any) => ({
      standard_id: null,
      test_method_id: null,
      test_parameter_id: null,
      test_object: it.test_object,
      specification: it.specification ?? '',
      grade: it.grade ?? '',
      quantity: it.quantity ?? 1,
      unit: it.unit ?? '组',
    })),
  })
  if (res.project) await handleProjectChange(res.project)
}

function addItem() {
  form.items.push({
    standard_id: null,
    test_method_id: null,
    test_parameter_id: null,
    test_object: '',
    specification: '',
    grade: '',
    quantity: 1,
    unit: '组',
  })
}

function removeItem(index: number) {
  form.items.splice(index, 1)
}

function buildItemPayload(row: CommissionItemRow) {
  const std = standardOptions.value.find((s) => s.id === row.standard_id)
  const method = methodsForRow(row).find((m: any) => m.id === row.test_method_id)
  const param = parametersForRow(row).find((p: any) => p.id === row.test_parameter_id)
  return {
    test_object: row.test_object || '—',
    test_item: param?.name || method?.name || '—',
    test_standard: std?.standard_no || '',
    test_method: method?.name || '',
    specification: row.specification || '',
    grade: row.grade || '',
    quantity: row.quantity || 1,
    unit: row.unit || '组',
    remark: '',
  }
}

function buildCreatePayload() {
  return {
    project: form.project,
    sub_project: form.sub_project,
    construction_part: form.construction_part || '—',
    commission_date: form.commission_date,
    client_unit: form.client_unit || '未填写',
    client_contact: '',
    client_phone: form.client_phone || '',
    witness: form.witness,
    is_witnessed: form.is_witnessed,
    remark: '',
    items: form.items.map((row) => buildItemPayload(row)),
  }
}

function buildUpdatePayload() {
  return {
    sub_project: form.sub_project,
    construction_part: form.construction_part || '—',
    commission_date: form.commission_date,
    client_unit: form.client_unit || '未填写',
    client_contact: '',
    client_phone: form.client_phone || '',
    witness: form.witness,
    is_witnessed: form.is_witnessed,
    remark: '',
  }
}

async function handleSave() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await updateCommission(commissionId.value, buildUpdatePayload())
    } else {
      await createCommission(buildCreatePayload())
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
      await updateCommission(id, buildUpdatePayload())
    } else {
      const res: any = await createCommission(buildCreatePayload())
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
  await fetchStandards()
  if (isEdit.value) await fetchDetail()
  else addItem()
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
            <el-form-item label="工程项目" prop="project">
              <el-select
                v-model="form.project"
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
              <el-select v-model="form.sub_project" placeholder="请选择" clearable style="width: 100%">
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
            <el-form-item label="委托单位">
              <el-input v-model="form.client_unit" placeholder="委托单位名称" />
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
              <el-select v-model="form.witness" placeholder="请选择" clearable style="width: 100%">
                <el-option v-for="w in witnessOptions" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="见证取样">
              <el-switch v-model="form.is_witnessed" active-text="是" inactive-text="否" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">检测项目（先选标准，再选方法，再选参数）</el-divider>
        <div style="margin-bottom: 12px">
          <el-button type="primary" :icon="Plus" size="small" @click="addItem">添加一行</el-button>
        </div>

        <el-table :data="form.items" border>
          <el-table-column label="检测标准" min-width="200">
            <template #default="{ row }">
              <el-select
                v-model="row.standard_id"
                placeholder="标准规范"
                filterable
                clearable
                style="width: 100%"
                @change="onRowStandardChange(row)"
              >
                <el-option
                  v-for="s in standardOptions"
                  :key="s.id"
                  :label="`${s.standard_no} ${s.name}`"
                  :value="s.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="检测方法" min-width="180">
            <template #default="{ row }">
              <el-select
                v-model="row.test_method_id"
                placeholder="先选标准"
                filterable
                clearable
                style="width: 100%"
                :disabled="!row.standard_id"
                @visible-change="(v: boolean) => v && row.standard_id && onRowStandardChange(row)"
                @change="onRowMethodChange(row)"
              >
                <el-option
                  v-for="m in methodsForRow(row)"
                  :key="m.id"
                  :label="m.name"
                  :value="m.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="检测项目(参数)" min-width="180">
            <template #default="{ row }">
              <el-select
                v-model="row.test_parameter_id"
                placeholder="先选方法"
                filterable
                clearable
                style="width: 100%"
                :disabled="!row.test_method_id"
                @visible-change="(v: boolean) => v && row.test_method_id && onRowMethodChange(row)"
              >
                <el-option
                  v-for="p in parametersForRow(row)"
                  :key="p.id"
                  :label="p.name"
                  :value="p.id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="检测对象" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.test_object" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="规格型号" width="120">
            <template #default="{ row }">
              <el-input v-model="row.specification" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="设计等级" width="100">
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
