<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getProject, getOrganizations, createOrganization, updateOrganization, deleteOrganization,
  getSubProjects, createSubProject, getContracts, createContract,
  getWitnesses, createWitness, getProjectStats,
} from '@/api/projects'
import type { Project, Organization, SubProject, Contract, Witness } from '@/types/project'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.id))
const activeTab = ref('basic')
const project = ref<Project>({} as Project)

// --- Basic Info ---
async function fetchProject() {
  try {
    project.value = (await getProject(projectId.value)) as any
  } catch {
    ElMessage.error('加载项目失败')
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
  Object.assign(subForm, { name: '', code: '', parent: null, description: '' })
  subDialogVisible.value = true
}

async function handleSubSubmit() {
  await createSubProject(projectId.value, {
    name: subForm.name,
    code: subForm.code || '',
    parent: subForm.parent,
    description: subForm.description || '',
  })
  ElMessage.success('创建成功')
  subDialogVisible.value = false
  fetchSubs()
}

// --- Contracts ---
const contractLoading = ref(false)
const contractList = ref<Contract[]>([])
const contractDialogVisible = ref(false)
const contractForm = reactive({
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

async function handleContractSubmit() {
  await createContract(projectId.value, {
    contract_no: contractForm.contract_no,
    title: contractForm.title,
    amount: contractForm.amount,
    sign_date: contractForm.sign_date || null,
    start_date: contractForm.start_date || null,
    end_date: contractForm.end_date || null,
    scope: contractForm.scope || '',
  })
  ElMessage.success('创建成功')
  contractDialogVisible.value = false
  fetchContracts()
}

// --- Witnesses ---
const witnessLoading = ref(false)
const witnessList = ref<Witness[]>([])
const witnessDialogVisible = ref(false)
const witnessForm = reactive({
  name: '',
  phone: '',
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
    name: '',
    phone: '',
    id_number: '',
    organization: null,
    certificate_no: '',
  })
  witnessDialogVisible.value = true
}

async function handleWitnessSubmit() {
  await createWitness(projectId.value, {
    name: witnessForm.name,
    phone: witnessForm.phone || '',
    id_number: witnessForm.id_number || '',
    organization: witnessForm.organization,
    certificate_no: witnessForm.certificate_no || '',
  })
  ElMessage.success('创建成功')
  witnessDialogVisible.value = false
  fetchWitnesses()
}

// --- Stats ---
const stats = ref<any>({})
async function fetchStats() {
  try {
    stats.value = (await getProjectStats(projectId.value)) as any
  } catch {
    stats.value = {}
  }
}

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

onMounted(fetchProject)
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/project')">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">{{ project.name || '项目详情' }}</span>
      </template>
    </el-page-header>

    <el-tabs v-model="activeTab" style="margin-top: 20px" @tab-change="handleTabChange">
      <!-- Basic Info -->
      <el-tab-pane label="基本信息" name="basic">
        <el-card shadow="never">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目编号">{{ (project as any).code || project.project_no }}</el-descriptions-item>
            <el-descriptions-item label="工程名称">{{ project.name }}</el-descriptions-item>
            <el-descriptions-item label="工程类型">
              {{ (project as any).project_type_display || typeLabels[(project as any).project_type] || (project as any).project_type }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">{{ project.status }}</el-descriptions-item>
            <el-descriptions-item label="工程地址" :span="2">{{ project.address }}</el-descriptions-item>
            <el-descriptions-item label="开工日期">{{ project.start_date }}</el-descriptions-item>
            <el-descriptions-item label="竣工日期">{{ project.end_date }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ project.description }}</el-descriptions-item>
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
            <el-table-column prop="phone" label="电话" width="140" />
            <el-table-column prop="id_number" label="证件号" width="200" />
            <el-table-column label="所属单位" min-width="180">
              <template #default="{ row }">{{ (row as any).organization_name || '—' }}</template>
            </el-table-column>
            <el-table-column prop="certificate_no" label="证书编号" width="160" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Stats -->
      <el-tab-pane label="统计信息" name="stats">
        <el-card shadow="never">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="委托总数" :value="stats.commission_count ?? 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="样品总数" :value="stats.sample_count ?? 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="检测完成数" :value="stats.completed_count ?? 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="合同数量" :value="stats.contract_count ?? 0" />
            </el-col>
          </el-row>
        </el-card>
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
    <el-dialog v-model="subDialogVisible" title="新增分部分项" width="480px" destroy-on-close>
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
    <el-dialog v-model="contractDialogVisible" title="新增检测合同" width="520px" destroy-on-close>
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
    <el-dialog v-model="witnessDialogVisible" title="新增见证人" width="480px" destroy-on-close>
      <el-form :model="witnessForm" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="witnessForm.name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="witnessForm.phone" /></el-form-item>
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
