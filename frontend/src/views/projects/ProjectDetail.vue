<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Document,
  Box,
  Notebook,
  Tickets,
  List,
  Clock,
  Flag,
  Loading,
  CircleCheck,
  OfficeBuilding,
  User,
} from '@element-plus/icons-vue'
import {
  getProject, getOrganizations, createOrganization, updateOrganization, deleteOrganization,
  getSubProjects, createSubProject, updateSubProject, deleteSubProject,
  getContracts, createContract, updateContract, deleteContract,
  getWitnesses, createWitness, updateWitness, deleteWitness, getProjectStats,
} from '@/api/projects'
import type { Project, Organization, SubProject, Contract, Witness } from '@/types/project'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => {
  const n = Number(route.params.id)
  return Number.isFinite(n) ? n : 0
})
const activeTab = ref('basic')
const project = ref<Project>({} as Project)

// --- Basic Info ---
async function fetchProject() {
  try {
    if (!projectId.value) return
    project.value = (await getProject(projectId.value)) as any
  } catch (e: any) {
    // request.ts 通常已弹出后端 message/detail；这里不重复弹框
    project.value = {} as Project
  }
}

// --- Organizations ---
const orgLoading = ref(false)
const orgList = ref<Organization[]>([])
const orgDialogVisible = ref(false)
const orgForm = reactive({
  id: 0, name: '', role: '', contact_person: '', contact_phone: '',
})
const orgRoleOptions = [
  { label: '建设单位', value: 'builder' },
  { label: '施工单位', value: 'contractor' },
  { label: '监理单位', value: 'supervisor' },
  { label: '设计单位', value: 'designer' },
  { label: '检测单位', value: 'inspector' },
]

async function fetchOrgs() {
  orgLoading.value = true
  try {
    const res: any = await getOrganizations(projectId.value)
    orgList.value = res.results ?? res.list ?? res ?? []
  } finally {
    orgLoading.value = false
  }
}

function openOrgCreate() {
  Object.assign(orgForm, { id: 0, name: '', role: '', contact_person: '', contact_phone: '' })
  orgDialogVisible.value = true
}

function openOrgEdit(row: Organization) {
  Object.assign(orgForm, {
    id: row.id,
    name: row.name,
    role: (row as any).role ?? (row as any).type ?? '',
    contact_person: row.contact_person ?? '',
    contact_phone: row.contact_phone ?? '',
  })
  orgDialogVisible.value = true
}

function buildOrgPayload() {
  return {
    name: orgForm.name,
    role: orgForm.role,
    contact_person: orgForm.contact_person,
    contact_phone: orgForm.contact_phone,
  }
}

async function handleOrgSubmit() {
  const payload = buildOrgPayload()
  if (orgForm.id) {
    await updateOrganization(projectId.value, orgForm.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createOrganization(projectId.value, payload)
    ElMessage.success('创建成功')
  }
  orgDialogVisible.value = false
  fetchOrgs()
}

async function handleOrgDelete(row: Organization) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await deleteOrganization(projectId.value, row.id)
  ElMessage.success('删除成功')
  fetchOrgs()
}

// --- SubProjects ---
const subLoading = ref(false)
const subList = ref<SubProject[]>([])
const subDialogVisible = ref(false)
const subForm = reactive({
  id: 0,
  name: '',
  code: '',
  parent: null as number | null,
  description: '',
})

async function fetchSubs() {
  subLoading.value = true
  try {
    const res: any = await getSubProjects(projectId.value)
    subList.value = res.results ?? res.list ?? res ?? []
  } finally {
    subLoading.value = false
  }
}

function openSubCreate() {
  Object.assign(subForm, { id: 0, name: '', code: '', parent: null, description: '' })
  subDialogVisible.value = true
}

function openSubEdit(row: SubProject) {
  Object.assign(subForm, {
    id: row.id,
    name: row.name,
    code: row.code || '',
    parent: (row as any).parent ?? null,
    description: row.description || '',
  })
  subDialogVisible.value = true
}

async function handleSubSubmit() {
  const payload = {
    name: subForm.name,
    code: subForm.code || '',
    parent: subForm.parent,
    description: subForm.description || '',
  }
  if (subForm.id) {
    await updateSubProject(projectId.value, subForm.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createSubProject(projectId.value, payload)
    ElMessage.success('创建成功')
  }
  subDialogVisible.value = false
  fetchSubs()
}

async function handleSubDelete(row: SubProject) {
  await ElMessageBox.confirm('确认删除该分部分项？', '提示', { type: 'warning' })
  await deleteSubProject(projectId.value, row.id)
  ElMessage.success('删除成功')
  fetchSubs()
}

// --- Contracts ---
const contractLoading = ref(false)
const contractList = ref<Contract[]>([])
const contractDialogVisible = ref(false)
const contractForm = reactive({
  id: 0,
  contract_no: '',
  title: '',
  amount: 0 as number | null,
  sign_date: '',
  start_date: '',
  end_date: '',
  scope: '',
})

async function fetchContracts() {
  contractLoading.value = true
  try {
    const res: any = await getContracts(projectId.value)
    contractList.value = res.results ?? res.list ?? res ?? []
  } finally {
    contractLoading.value = false
  }
}

function openContractCreate() {
  Object.assign(contractForm, {
    id: 0,
    contract_no: '',
    title: '',
    amount: null,
    sign_date: '',
    start_date: '',
    end_date: '',
    scope: '',
  })
  contractDialogVisible.value = true
}

function openContractEdit(row: Contract) {
  const r = row as any
  Object.assign(contractForm, {
    id: r.id,
    contract_no: r.contract_no,
    title: r.title,
    amount: r.amount ?? null,
    sign_date: r.sign_date || '',
    start_date: r.start_date || '',
    end_date: r.end_date || '',
    scope: r.scope || '',
  })
  contractDialogVisible.value = true
}

async function handleContractSubmit() {
  const payload = {
    contract_no: contractForm.contract_no,
    title: contractForm.title,
    amount: contractForm.amount,
    sign_date: contractForm.sign_date || null,
    start_date: contractForm.start_date || null,
    end_date: contractForm.end_date || null,
    scope: contractForm.scope || '',
  }
  if (contractForm.id) {
    await updateContract(projectId.value, contractForm.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createContract(projectId.value, payload)
    ElMessage.success('创建成功')
  }
  contractDialogVisible.value = false
  fetchContracts()
}

async function handleContractDelete(row: Contract) {
  await ElMessageBox.confirm('确认删除该合同？', '提示', { type: 'warning' })
  await deleteContract(projectId.value, (row as any).id)
  ElMessage.success('删除成功')
  fetchContracts()
}

// --- Witnesses ---
const witnessLoading = ref(false)
const witnessList = ref<Witness[]>([])
const witnessDialogVisible = ref(false)
const witnessIdTypeOptions = [
  { label: '居民身份证', value: 'id_card' },
  { label: '护照', value: 'passport' },
  { label: '港澳居民来往内地通行证', value: 'hk_macao' },
  { label: '台湾居民来往大陆通行证', value: 'taiwan' },
  { label: '其他', value: 'other' },
]

const witnessForm = reactive({
  id: 0,
  name: '',
  phone: '',
  id_type: 'id_card',
  id_number: '',
  organization: null as number | null,
  certificate_no: '',
})

async function fetchWitnesses() {
  witnessLoading.value = true
  try {
    const res: any = await getWitnesses(projectId.value)
    witnessList.value = res.results ?? res.list ?? res ?? []
  } finally {
    witnessLoading.value = false
  }
}

async function openWitnessCreate() {
  if (!orgList.value.length) await fetchOrgs()
  Object.assign(witnessForm, {
    id: 0,
    name: '',
    phone: '',
    id_type: 'id_card',
    id_number: '',
    organization: null,
    certificate_no: '',
  })
  witnessDialogVisible.value = true
}

function openWitnessEdit(row: Witness) {
  const r = row as any
  Object.assign(witnessForm, {
    id: r.id,
    name: r.name,
    phone: r.phone || '',
    id_type: r.id_type || 'id_card',
    id_number: r.id_number || '',
    organization: r.organization ?? null,
    certificate_no: r.certificate_no || '',
  })
  witnessDialogVisible.value = true
}

async function handleWitnessSubmit() {
  const payload = {
    name: witnessForm.name,
    phone: witnessForm.phone || '',
    id_type: witnessForm.id_type || 'id_card',
    id_number: witnessForm.id_number || '',
    organization: witnessForm.organization,
    certificate_no: witnessForm.certificate_no || '',
  }
  if (witnessForm.id) {
    await updateWitness(projectId.value, witnessForm.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createWitness(projectId.value, payload)
    ElMessage.success('创建成功')
  }
  witnessDialogVisible.value = false
  fetchWitnesses()
}

async function handleWitnessDelete(row: Witness) {
  await ElMessageBox.confirm('确认删除该见证人？', '提示', { type: 'warning' })
  await deleteWitness(projectId.value, (row as any).id)
  ElMessage.success('删除成功')
  fetchWitnesses()
}

// --- Stats ---
const stats = ref<any>({})
async function fetchStats() {
  try {
    const raw = (await getProjectStats(projectId.value)) as any
    const r = raw || {}
    // axios 拦截器会把 data 转成 camelCase，这里统一成模板使用的 snake_case
    stats.value = {
      commission_count: r.commissionCount ?? r.commission_count ?? 0,
      sample_count: r.sampleCount ?? r.sample_count ?? 0,
      report_count: r.reportCount ?? r.report_count ?? 0,
      contract_count: r.contractCount ?? r.contract_count ?? 0,
      task_total: r.taskTotal ?? r.task_total ?? 0,
      unassigned_count: r.unassignedCount ?? r.unassigned_count ?? 0,
      assigned_count: r.assignedCount ?? r.assigned_count ?? 0,
      in_progress_count: r.inProgressCount ?? r.in_progress_count ?? 0,
      completed_count: r.completedCount ?? r.completed_count ?? 0,
      organization_count: r.organizationCount ?? r.organization_count ?? 0,
      witness_count: r.witnessCount ?? r.witness_count ?? 0,
    }
  } catch {
    stats.value = {}
  }
}

/** 统计页卡片：与仪表盘风格一致，分组展示 */
const overviewStatCards = computed(() => {
  const s = stats.value
  return [
    { title: '委托总数', sub: '已受理委托单', value: s.commission_count ?? 0, icon: Document, color: '#2563eb', bg: '#eff6ff' },
    { title: '样品总数', sub: '收样登记', value: s.sample_count ?? 0, icon: Box, color: '#7c3aed', bg: '#f5f3ff' },
    { title: '报告总数', sub: '已出具报告', value: s.report_count ?? 0, icon: Notebook, color: '#059669', bg: '#ecfdf5' },
    { title: '检测合同', sub: '项目关联合同', value: s.contract_count ?? 0, icon: Tickets, color: '#d97706', bg: '#fffbeb' },
  ]
})

const taskStatCards = computed(() => {
  const s = stats.value
  return [
    { title: '任务总数', sub: '检测任务', value: s.task_total ?? 0, icon: List, color: '#334155', bg: '#f1f5f9' },
    { title: '待分配', sub: '未指派检测员', value: s.unassigned_count ?? 0, icon: Clock, color: '#64748b', bg: '#f8fafc' },
    { title: '待检', sub: '已分配待开始', value: s.assigned_count ?? 0, icon: Flag, color: '#ca8a04', bg: '#fefce8' },
    { title: '检测中', sub: '正在检测', value: s.in_progress_count ?? 0, icon: Loading, color: '#2563eb', bg: '#eff6ff' },
    { title: '已完成', sub: '已闭环', value: s.completed_count ?? 0, icon: CircleCheck, color: '#16a34a', bg: '#f0fdf4' },
  ]
})

const orgStatCards = computed(() => {
  const s = stats.value
  return [
    { title: '参建单位', sub: '建设/施工/监理等', value: s.organization_count ?? 0, icon: OfficeBuilding, color: '#0369a1', bg: '#e0f2fe' },
    { title: '见证人', sub: '在岗见证', value: s.witness_count ?? 0, icon: User, color: '#a21caf', bg: '#fdf4ff' },
  ]
})

/** 任务完成占比（已完成 / 任务总数） */
const taskCompletedPercent = computed(() => {
  const t = stats.value.task_total ?? 0
  const c = stats.value.completed_count ?? 0
  if (!t) return 0
  return Math.min(100, Math.round((c / t) * 100))
})

function handleTabChange(tab: string) {
  const loaders: Record<string, () => void> = {
    orgs: fetchOrgs,
    subs: fetchSubs,
    contracts: fetchContracts,
    witnesses: async () => {
      await fetchOrgs()
      await fetchWitnesses()
    },
    stats: fetchStats,
  }
  loaders[tab]?.()
}

function orgRoleLabel(val: string) {
  return orgRoleOptions.find(o => o.value === val)?.label ?? val
}

const typeLabels: Record<string, string> = {
  building: '房建工程',
  municipal: '市政工程',
  transport: '交通工程',
  water: '水利工程',
  airport: '机场工程',
  other: '其他',
}

/** axios 对非信封 JSON 会 camelCase，项目详情需同时读 snake / camel */
function projField(snake: string): unknown {
  const x = project.value as Record<string, unknown> | null
  if (!x) return undefined
  const camel = snake.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase())
  return x[camel] ?? x[snake]
}

onMounted(fetchProject)
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/project')">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">{{ (projField('name') as string) || project.name || '项目详情' }}</span>
      </template>
    </el-page-header>

    <el-tabs v-model="activeTab" style="margin-top: 20px" @tab-change="handleTabChange">
      <!-- Basic Info -->
      <el-tab-pane label="基本信息" name="basic">
        <el-card shadow="never">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目编号">{{ projField('code') || project.project_no }}</el-descriptions-item>
            <el-descriptions-item label="工程名称">{{ projField('name') }}</el-descriptions-item>
            <el-descriptions-item label="工程类型">
              {{ projField('project_type_display') || typeLabels[String(projField('project_type') ?? '')] || projField('project_type') }}
            </el-descriptions-item>
            <el-descriptions-item label="项目状态">
              {{ projField('status_display') || project.status }}
            </el-descriptions-item>
            <el-descriptions-item label="工程地址" :span="2">{{ projField('address') }}</el-descriptions-item>
            <el-descriptions-item label="开工日期">{{ projField('start_date') }}</el-descriptions-item>
            <el-descriptions-item label="竣工日期">{{ projField('end_date') }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ projField('description') }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>

      <!-- Organizations -->
      <el-tab-pane label="参建单位" name="orgs">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>参建单位</span>
              <el-button type="primary" :icon="Plus" size="small" @click="openOrgCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="orgLoading" :data="orgList" stripe border>
            <el-table-column prop="name" label="单位名称" min-width="180" />
            <el-table-column label="单位角色" width="120">
              <template #default="{ row }">{{ orgRoleLabel((row as any).role || (row as any).type) }}</template>
            </el-table-column>
            <el-table-column prop="contact_person" label="联系人" width="120" />
            <el-table-column prop="contact_phone" label="联系电话" width="140" />
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button link type="primary" @click="openOrgEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="handleOrgDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Sub Projects -->
      <el-tab-pane label="分部分项工程" name="subs">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>分部分项工程</span>
              <el-button type="primary" :icon="Plus" size="small" @click="openSubCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="subLoading" :data="subList" stripe border row-key="id" default-expand-all>
            <el-table-column prop="code" label="编码" width="160" />
            <el-table-column prop="name" label="名称" min-width="200" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openSubEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="handleSubDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Contracts -->
      <el-tab-pane label="检测合同" name="contracts">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>检测合同</span>
              <el-button type="primary" :icon="Plus" size="small" @click="openContractCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="contractLoading" :data="contractList" stripe border>
            <el-table-column prop="contract_no" label="合同编号" width="160" />
            <el-table-column label="合同名称" min-width="200">
              <template #default="{ row }">{{ (row as any).title || (row as any).name }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="金额(元)" width="120" align="right" />
            <el-table-column prop="sign_date" label="签订日期" width="120" />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openContractEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="handleContractDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Witnesses -->
      <el-tab-pane label="见证人" name="witnesses">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>见证人</span>
              <el-button type="primary" :icon="Plus" size="small" @click="openWitnessCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="witnessLoading" :data="witnessList" stripe border>
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column label="证件类型" width="120">
              <template #default="{ row }">{{ (row as any).id_type_display || '—' }}</template>
            </el-table-column>
            <el-table-column prop="phone" label="电话" width="140" />
            <el-table-column prop="id_number" label="证件号" width="200" />
            <el-table-column label="所属单位" min-width="180">
              <template #default="{ row }">{{ (row as any).organization_name || '—' }}</template>
            </el-table-column>
            <el-table-column prop="certificate_no" label="证书编号" width="160" />
            <el-table-column label="操作" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openWitnessEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="handleWitnessDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Stats -->
      <el-tab-pane label="统计信息" name="stats">
        <div class="project-stats">
          <section class="stats-block">
            <h4 class="stats-block-title">业务概况</h4>
            <el-row :gutter="16">
              <el-col v-for="item in overviewStatCards" :key="item.title" :xs="24" :sm="12" :lg="6">
                <el-card shadow="hover" class="stats-kpi-card">
                  <div class="stats-kpi-body">
                    <div class="stats-kpi-text">
                      <div class="stats-kpi-label">{{ item.title }}</div>
                      <div class="stats-kpi-hint">{{ item.sub }}</div>
                      <div class="stats-kpi-value">{{ item.value }}</div>
                    </div>
                    <div class="stats-kpi-icon" :style="{ background: item.bg }">
                      <el-icon :size="26" :color="item.color">
                        <component :is="item.icon" />
                      </el-icon>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </section>

          <section class="stats-block">
            <div class="stats-block-head">
              <h4 class="stats-block-title">检测任务</h4>
              <div v-if="(stats.task_total ?? 0) > 0" class="stats-progress-wrap">
                <span class="stats-progress-label">任务完成度</span>
                <el-progress
                  :percentage="taskCompletedPercent"
                  :stroke-width="8"
                  color="#16a34a"
                />
                <span class="stats-progress-meta">
                  已完成 {{ stats.completed_count ?? 0 }} / 共 {{ stats.task_total ?? 0 }} 个任务
                </span>
              </div>
            </div>
            <div class="task-stat-grid">
              <el-card
                v-for="item in taskStatCards"
                :key="item.title"
                shadow="hover"
                class="stats-kpi-card stats-kpi-card--compact"
              >
                <div class="stats-kpi-body">
                  <div class="stats-kpi-text">
                    <div class="stats-kpi-label">{{ item.title }}</div>
                    <div class="stats-kpi-hint">{{ item.sub }}</div>
                    <div class="stats-kpi-value stats-kpi-value--md">{{ item.value }}</div>
                  </div>
                  <div class="stats-kpi-icon stats-kpi-icon--sm" :style="{ background: item.bg }">
                    <el-icon :size="22" :color="item.color">
                      <component :is="item.icon" />
                    </el-icon>
                  </div>
                </div>
              </el-card>
            </div>
          </section>

          <section class="stats-block">
            <h4 class="stats-block-title">组织与人员</h4>
            <el-row :gutter="16">
              <el-col v-for="item in orgStatCards" :key="item.title" :xs="24" :sm="12" :lg="8">
                <el-card shadow="hover" class="stats-kpi-card">
                  <div class="stats-kpi-body">
                    <div class="stats-kpi-text">
                      <div class="stats-kpi-label">{{ item.title }}</div>
                      <div class="stats-kpi-hint">{{ item.sub }}</div>
                      <div class="stats-kpi-value">{{ item.value }}</div>
                    </div>
                    <div class="stats-kpi-icon" :style="{ background: item.bg }">
                      <el-icon :size="26" :color="item.color">
                        <component :is="item.icon" />
                      </el-icon>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </section>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Organization Dialog -->
    <el-dialog v-model="orgDialogVisible" :title="orgForm.id ? '编辑参建单位' : '新增参建单位'" width="520px" destroy-on-close>
      <el-form :model="orgForm" label-width="80px">
        <el-form-item label="单位名称"><el-input v-model="orgForm.name" /></el-form-item>
        <el-form-item label="单位角色">
          <el-select v-model="orgForm.role" style="width: 100%">
            <el-option v-for="o in orgRoleOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人"><el-input v-model="orgForm.contact_person" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="orgForm.contact_phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orgDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleOrgSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- SubProject Dialog -->
    <el-dialog v-model="subDialogVisible" :title="subForm.id ? '编辑分部分项' : '新增分部分项'" width="480px" destroy-on-close>
      <el-form :model="subForm" label-width="80px">
        <el-form-item label="编码"><el-input v-model="subForm.code" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="subForm.name" /></el-form-item>
        <el-form-item label="上级">
          <el-select v-model="subForm.parent" placeholder="无（顶级）" clearable style="width: 100%">
            <el-option v-for="s in subList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="subForm.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Contract Dialog -->
    <el-dialog v-model="contractDialogVisible" :title="contractForm.id ? '编辑检测合同' : '新增检测合同'" width="520px" destroy-on-close>
      <el-form :model="contractForm" label-width="80px">
        <el-form-item label="合同编号"><el-input v-model="contractForm.contract_no" /></el-form-item>
        <el-form-item label="合同名称"><el-input v-model="contractForm.title" /></el-form-item>
        <el-form-item label="金额"><el-input-number v-model="contractForm.amount" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="签订日期">
          <el-date-picker v-model="contractForm.sign_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始">
              <el-date-picker v-model="contractForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束">
              <el-date-picker v-model="contractForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="检测范围"><el-input v-model="contractForm.scope" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="contractDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleContractSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Witness Dialog -->
    <el-dialog v-model="witnessDialogVisible" :title="witnessForm.id ? '编辑见证人' : '新增见证人'" width="480px" destroy-on-close>
      <el-form :model="witnessForm" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="witnessForm.name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="witnessForm.phone" /></el-form-item>
        <el-form-item label="证件类型">
          <el-select v-model="witnessForm.id_type" placeholder="请选择" style="width: 100%">
            <el-option v-for="o in witnessIdTypeOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="证件号"><el-input v-model="witnessForm.id_number" /></el-form-item>
        <el-form-item label="所属参建单位">
          <el-select v-model="witnessForm.organization" placeholder="可选" clearable filterable style="width: 100%">
            <el-option v-for="o in orgList" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="证书编号"><el-input v-model="witnessForm.certificate_no" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="witnessDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleWitnessSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.project-stats {
  max-width: 1200px;
}

.stats-block {
  margin-bottom: 28px;
}

.stats-block:last-child {
  margin-bottom: 0;
}

.stats-block-title {
  margin: 0 0 14px;
  font-size: 15px;
  font-weight: 600;
  color: var(--lims-text-primary);
  letter-spacing: 0.02em;
}

.stats-block-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 16px 24px;
  margin-bottom: 14px;
}

.stats-block-head .stats-block-title {
  margin-bottom: 0;
  flex-shrink: 0;
}

.stats-progress-wrap {
  flex: 1;
  min-width: 220px;
  max-width: 480px;
}

.stats-progress-label {
  display: block;
  font-size: 13px;
  color: var(--lims-text-secondary);
  margin-bottom: 6px;
}

.stats-progress-meta {
  display: block;
  font-size: 12px;
  color: var(--lims-text-secondary);
  margin-top: 6px;
}

.stats-kpi-card {
  border-radius: 10px;
  margin-bottom: 16px;
}

.stats-kpi-card :deep(.el-card__body) {
  padding: 16px 18px;
}

.stats-kpi-card--compact :deep(.el-card__body) {
  padding: 12px 14px;
}

.stats-kpi-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.stats-kpi-text {
  min-width: 0;
}

.stats-kpi-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--lims-text-primary);
  line-height: 1.3;
}

.stats-kpi-hint {
  font-size: 12px;
  color: var(--lims-text-secondary);
  margin-top: 4px;
  line-height: 1.35;
}

.stats-kpi-value {
  font-size: 30px;
  font-weight: 700;
  color: var(--lims-text-primary);
  margin-top: 8px;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.stats-kpi-value--md {
  font-size: 24px;
  margin-top: 6px;
}

.stats-kpi-icon {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-kpi-icon--sm {
  width: 44px;
  height: 44px;
  border-radius: 10px;
}

.task-stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.task-stat-grid .stats-kpi-card {
  margin-bottom: 0;
}
</style>
