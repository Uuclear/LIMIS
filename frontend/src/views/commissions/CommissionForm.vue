<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { getCommission, createCommission, updateCommission, submitCommission } from '@/api/commissions'
import { getProjectList, getSubProjects, getWitnesses, getSamplers, getOrganizations } from '@/api/projects'
import { getStandardList } from '@/api/standards'
import { getTestMethods, getTestParameters } from '@/api/testing'
import { batchCreateSamples } from '@/api/samples'
import { useActionLock } from '@/composables/useActionLock'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const commissionId = computed(() => Number(route.params.id) || 0)
const formRef = ref()
const { isLocked, runLocked } = useActionLock()

interface CommissionItemRow {
  standard_id: number | null
  test_method_id: number | null
  test_parameter_id: number | null
  test_object: string
  specification: string
  grade: string
  quantity: number
  unit: string
}

interface SampleRow {
  name: string
  specification: string
  grade: string
  quantity: number
  unit: string
  sampling_date: string
  received_date: string
  production_date: string
  sampling_location: string
  remark: string
}

const form = reactive({
  project_code: '',
  project: null as number | null,
  sub_project: null as number | null,
  unit_sub_project: null as number | null,
  division_sub_project: null as number | null,
  item_sub_project: null as number | null,
  construction_part: '',
  commission_date: '',
  client_unit: '',
  client_contact: '',
  client_phone: '',
  witness: null as number | null,
  sampler: null as number | null,
  is_witnessed: false,
  items: [] as CommissionItemRow[],
  samples: [] as SampleRow[],
})

const rules = {
  project: [{ required: true, message: '请选择工程项目', trigger: 'change' }],
  commission_date: [{ required: true, message: '请选择委托日期', trigger: 'change' }],
}

const projectOptions = ref<Array<{ id: number; name: string; code?: string }>>([])
const subProjectOptions = ref<any[]>([])
const unitProjectOptions = ref<{ id: number; name: string }[]>([])
const divisionProjectOptions = ref<{ id: number; name: string }[]>([])
const itemProjectOptions = ref<{ id: number; name: string }[]>([])
const witnessOptions = ref<{ id: number; name: string }[]>([])
const samplerOptions = ref<{ id: number; name: string }[]>([])
const orgOptions = ref<{ id: number; name: string; contact_person?: string; contact_phone?: string }[]>([])
const clientContactOptions = ref<string[]>([])
const clientPhoneOptions = ref<string[]>([])
const standardOptions = ref<any[]>([])

/** 每行缓存：标准号 -> 方法列表；方法 id -> 参数列表；标准号 -> 参数列表(聚合) */
const methodCache = ref<Record<string, any[]>>({})
const paramCache = ref<Record<number, any[]>>({})
const standardParamCache = ref<Record<string, Array<{ id: number; name: string; method_id: number; method_name: string }>>>({})

async function fetchProjects() {
  const res: any = await getProjectList({ page_size: 500 })
  projectOptions.value = res.results ?? res.list ?? []
}

async function fetchStandards() {
  const res: any = await getStandardList({ page_size: 500 })
  standardOptions.value = res.results ?? res.list ?? []
}

async function handleProjectChange(projectId: number) {
  form.unit_sub_project = null
  form.division_sub_project = null
  form.item_sub_project = null
  form.sub_project = null
  form.witness = null
  form.sampler = null
  form.client_unit = ''
  form.client_contact = ''
  form.client_phone = ''
  if (!projectId) return
  const selected = projectOptions.value.find((p) => p.id === projectId)
  form.project_code = selected?.code || ''
  const [subRes, witRes, samplerRes, orgRes]: any[] = await Promise.all([
    getSubProjects(projectId),
    getWitnesses(projectId),
    getSamplers(projectId),
    getOrganizations(projectId),
  ])
  subProjectOptions.value = subRes.results ?? subRes.list ?? subRes ?? []
  unitProjectOptions.value = (subProjectOptions.value ?? []).map((x: any) => ({ id: x.id, name: x.name }))
  divisionProjectOptions.value = []
  itemProjectOptions.value = []
  witnessOptions.value = witRes.results ?? witRes.list ?? witRes ?? []
  samplerOptions.value = samplerRes.results ?? samplerRes.list ?? samplerRes ?? []
  orgOptions.value = orgRes.results ?? orgRes.list ?? orgRes ?? []
  clientContactOptions.value = []
  clientPhoneOptions.value = []
}

function handleProjectCodeChange(code: string) {
  const target = projectOptions.value.find((p) => p.code === code)
  if (!target) return
  form.project = target.id
  handleProjectChange(target.id)
}

function handleUnitProjectChange(unitId: number) {
  form.division_sub_project = null
  form.item_sub_project = null
  const unit = subProjectOptions.value.find((x: any) => x.id === unitId)
  divisionProjectOptions.value = (unit?.children ?? []).map((x: any) => ({ id: x.id, name: x.name }))
  itemProjectOptions.value = []
  form.sub_project = unitId || null
}

function handleDivisionProjectChange(divisionId: number) {
  form.item_sub_project = null
  const division = (subProjectOptions.value.flatMap((x: any) => x.children ?? [])).find((x: any) => x.id === divisionId)
  itemProjectOptions.value = (division?.children ?? []).map((x: any) => ({ id: x.id, name: x.name }))
  form.sub_project = divisionId || form.unit_sub_project || null
}

function handleItemProjectChange(itemId: number) {
  form.sub_project = itemId || form.division_sub_project || form.unit_sub_project || null
}

function handleClientUnitChange(name: string) {
  const org = orgOptions.value.find((o) => o.name === name)
  if (!org) return
  clientContactOptions.value = org.contact_person ? [org.contact_person] : []
  clientPhoneOptions.value = org.contact_phone ? [org.contact_phone] : []
  form.client_contact = clientContactOptions.value[0] || ''
  form.client_phone = clientPhoneOptions.value[0] || ''
}

watch(() => form.is_witnessed, (v) => {
  if (!v) {
    form.witness = null
    form.sampler = null
  }
})

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
    if (standardParamCache.value[std.standard_no] === undefined) {
      const methods = methodCache.value[std.standard_no] ?? []
      const merged: Array<{ id: number; name: string; method_id: number; method_name: string }> = []
      for (const m of methods) {
        await ensureParametersForMethod(m.id)
        const params = paramCache.value[m.id] ?? []
        for (const p of params) {
          merged.push({ id: p.id, name: p.name, method_id: m.id, method_name: m.name })
        }
      }
      standardParamCache.value[std.standard_no] = merged
    }
  }
}

function methodsForRow(row: CommissionItemRow) {
  const std = standardOptions.value.find((s) => s.id === row.standard_id)
  if (!std?.standard_no) return []
  return methodCache.value[std.standard_no] ?? []
}

function parametersForRow(row: CommissionItemRow) {
  const std = standardOptions.value.find((s) => s.id === row.standard_id)
  if (!std?.standard_no) return []
  return standardParamCache.value[std.standard_no] ?? []
}

function onRowParameterChange(row: CommissionItemRow) {
  const p = parametersForRow(row).find((x: any) => x.id === row.test_parameter_id) as any
  row.test_method_id = p?.method_id ?? null
}

async function fetchDetail() {
  if (!commissionId.value) return
  const res: any = await getCommission(commissionId.value)
  Object.assign(form, {
    project_code: '',
    project: res.project,
    sub_project: res.sub_project,
    unit_sub_project: null,
    division_sub_project: null,
    item_sub_project: null,
    construction_part: res.construction_part,
    commission_date: res.commission_date,
    client_unit: res.client_unit,
    client_contact: res.client_contact ?? '',
    client_phone: res.client_phone,
    witness: res.witness,
    sampler: (res as any).sampler ?? null,
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
  if (res.sub_project) {
    const unit = subProjectOptions.value.find((x: any) => x.id === res.sub_project || (x.children ?? []).some((c: any) => c.id === res.sub_project || (c.children ?? []).some((i: any) => i.id === res.sub_project)))
    if (unit) {
      form.unit_sub_project = unit.id
      handleUnitProjectChange(unit.id)
      const division = (unit.children ?? []).find((c: any) => c.id === res.sub_project || (c.children ?? []).some((i: any) => i.id === res.sub_project))
      if (division) {
        form.division_sub_project = division.id
        handleDivisionProjectChange(division.id)
        const item = (division.children ?? []).find((i: any) => i.id === res.sub_project)
        if (item) form.item_sub_project = item.id
      }
    }
  }
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

function addSample() {
  form.samples.push({
    name: '',
    specification: '',
    grade: '',
    quantity: 1,
    unit: '个',
    sampling_date: form.commission_date || '',
    received_date: form.commission_date || '',
    production_date: '',
    sampling_location: '',
    remark: '',
  })
}

function removeSample(index: number) {
  form.samples.splice(index, 1)
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
    client_contact: form.client_contact || '',
    client_phone: form.client_phone || '',
    witness: form.witness,
    sampler: form.sampler,
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
    client_contact: form.client_contact || '',
    client_phone: form.client_phone || '',
    witness: form.witness,
    sampler: form.sampler,
    is_witnessed: form.is_witnessed,
    remark: '',
  }
}

async function handleSave() {
  await formRef.value?.validate()
  await runLocked('commission_save', async () => {
    let id = commissionId.value
    if (isEdit.value) {
      await updateCommission(id, buildUpdatePayload())
    } else {
      const res: any = await createCommission(buildCreatePayload())
      id = res.id ?? res
    }
    if (form.samples.length && id) {
      await batchCreateSamples({
        commission_id: id,
        samples: form.samples.map((s) => ({
          name: s.name || '未命名样品',
          specification: s.specification || '',
          grade: s.grade || '',
          quantity: s.quantity || 1,
          unit: s.unit || '个',
          sampling_date: s.sampling_date || form.commission_date,
          received_date: s.received_date || form.commission_date,
          production_date: s.production_date || null,
          sampling_location: s.sampling_location || '',
          remark: s.remark || '',
        })),
      })
    }
    ElMessage.success('保存成功')
    router.push('/entrustment')
  })
}

async function handleSaveAndSubmit() {
  await formRef.value?.validate()
  await runLocked('commission_submit', async () => {
    let id = commissionId.value
    if (isEdit.value) {
      await updateCommission(id, buildUpdatePayload())
    } else {
      const res: any = await createCommission(buildCreatePayload())
      id = res.id ?? res
    }
    await submitCommission(id)
    if (form.samples.length) {
      await batchCreateSamples({
        commission_id: id,
        samples: form.samples.map((s) => ({
          name: s.name || '未命名样品',
          specification: s.specification || '',
          grade: s.grade || '',
          quantity: s.quantity || 1,
          unit: s.unit || '个',
          sampling_date: s.sampling_date || form.commission_date,
          received_date: s.received_date || form.commission_date,
          production_date: s.production_date || null,
          sampling_location: s.sampling_location || '',
          remark: s.remark || '',
        })),
      })
    }
    ElMessage.success('已提交')
    router.push('/entrustment')
  })
}

onMounted(async () => {
  await fetchProjects()
  await fetchStandards()
  if (isEdit.value) await fetchDetail()
  else {
    addItem()
    addSample()
  }
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
            <el-form-item label="工程项目编号">
              <el-select v-model="form.project_code" placeholder="请选择项目编号" clearable filterable style="width: 100%" @change="handleProjectCodeChange">
                <el-option v-for="p in projectOptions" :key="`code-${p.id}`" :label="p.code || ''" :value="p.code || ''" />
              </el-select>
            </el-form-item>
          </el-col>
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
          <el-col :span="8">
            <el-form-item label="单位工程">
              <el-select v-model="form.unit_sub_project" placeholder="请选择" clearable style="width: 100%" @change="handleUnitProjectChange">
                <el-option v-for="s in unitProjectOptions" :key="`u-${s.id}`" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分部工程">
              <el-select v-model="form.division_sub_project" placeholder="请选择" clearable style="width: 100%" :disabled="!form.unit_sub_project" @change="handleDivisionProjectChange">
                <el-option v-for="s in divisionProjectOptions" :key="`d-${s.id}`" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分项工程">
              <el-select v-model="form.item_sub_project" placeholder="请选择" clearable style="width: 100%" :disabled="!form.division_sub_project" @change="handleItemProjectChange">
                <el-option v-for="s in itemProjectOptions" :key="`i-${s.id}`" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工程部位">
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
              <el-select v-model="form.client_unit" placeholder="可选（来自参建单位）" clearable filterable style="width: 100%" @change="handleClientUnitChange">
                <el-option v-for="o in orgOptions" :key="o.id" :label="o.name" :value="o.name" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-select v-model="form.client_contact" placeholder="可选" clearable allow-create filterable default-first-option style="width: 100%">
                <el-option v-for="c in clientContactOptions" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-select v-model="form.client_phone" placeholder="可选" clearable allow-create filterable default-first-option style="width: 100%">
                <el-option v-for="p in clientPhoneOptions" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="见证人">
              <el-select v-model="form.witness" placeholder="请选择" clearable :disabled="!form.is_witnessed" style="width: 100%">
                <el-option v-for="w in witnessOptions" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="见证取样">
              <el-switch v-model="form.is_witnessed" active-text="是" inactive-text="否" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="取样人">
              <el-select v-model="form.sampler" placeholder="请选择" clearable :disabled="!form.is_witnessed" style="width: 100%">
                <el-option v-for="w in samplerOptions" :key="`sampler-${w.id}`" :label="w.name" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">检测项目（先选标准，再选参数）</el-divider>
        <div style="margin-bottom: 12px">
          <el-button
            v-permission="isEdit ? 'commission:edit' : 'commission:create'"
            type="primary"
            :icon="Plus"
            size="small"
            @click="addItem"
          >
            添加一行
          </el-button>
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
          <el-table-column label="检测项目(参数)" min-width="180">
            <template #default="{ row }">
              <el-select
                v-model="row.test_parameter_id"
                placeholder="先选标准"
                filterable
                clearable
                style="width: 100%"
                :disabled="!row.standard_id"
                @visible-change="(v: boolean) => v && row.standard_id && onRowStandardChange(row)"
                @change="onRowParameterChange(row)"
              >
                <el-option
                  v-for="p in parametersForRow(row)"
                  :key="p.id"
                  :label="`${p.name}${p.method_name ? `（${p.method_name}）` : ''}`"
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
              <el-button
                v-permission="isEdit ? 'commission:edit' : 'commission:create'"
                link
                type="danger"
                :icon="Delete"
                @click="removeItem($index)"
              />
            </template>
          </el-table-column>
        </el-table>

        <el-divider content-position="left">样品登记（随委托一并登记）</el-divider>
        <div style="margin-bottom: 12px">
          <el-button type="primary" :icon="Plus" size="small" @click="addSample">添加样品</el-button>
        </div>
        <el-table :data="form.samples" border>
          <el-table-column prop="name" label="样品名称" min-width="120">
            <template #default="{ row }"><el-input v-model="row.name" size="small" /></template>
          </el-table-column>
          <el-table-column prop="specification" label="规格型号" min-width="120">
            <template #default="{ row }"><el-input v-model="row.specification" size="small" /></template>
          </el-table-column>
          <el-table-column prop="grade" label="设计等级" width="100">
            <template #default="{ row }"><el-input v-model="row.grade" size="small" /></template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="90">
            <template #default="{ row }"><el-input-number v-model="row.quantity" :min="1" size="small" style="width: 100%" /></template>
          </el-table-column>
          <el-table-column prop="unit" label="单位" width="80">
            <template #default="{ row }"><el-input v-model="row.unit" size="small" /></template>
          </el-table-column>
          <el-table-column label="取样日期" width="130">
            <template #default="{ row }"><el-date-picker v-model="row.sampling_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></template>
          </el-table-column>
          <el-table-column label="收样日期" width="130">
            <template #default="{ row }"><el-date-picker v-model="row.received_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button link type="danger" :icon="Delete" @click="removeSample($index)" />
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 24px; text-align: right">
          <el-button @click="router.push('/entrustment')">取消</el-button>
          <el-button
            v-permission="isEdit ? 'commission:edit' : 'commission:create'"
            type="info"
            :loading="isLocked('commission_save')"
            @click="handleSave"
          >
            保存
          </el-button>
          <el-button
            v-permission="isEdit ? 'commission:edit' : 'commission:create'"
            type="primary"
            :loading="isLocked('commission_submit')"
            @click="handleSaveAndSubmit"
          >
            提交
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>
