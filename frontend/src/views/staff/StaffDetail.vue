<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, WarningFilled } from '@element-plus/icons-vue'
import {
  getStaff, getCertificates, createCertificate,
  getAuthorizations, createAuthorization,
  getTrainings, createTraining,
  getEvaluations, createEvaluation,
} from '@/api/staff'
import { getTestCategories, getTestParameters } from '@/api/testing'

const route = useRoute()
const router = useRouter()
const staffId = computed(() => Number(route.params.id))
const activeTab = ref('basic')
const staff = ref<any>({})

async function fetchStaff() {
  staff.value = await getStaff(staffId.value) as any
}

// --- Certificates ---
const certLoading = ref(false)
const certList = ref<any[]>([])
const certDialogVisible = ref(false)
const certForm = reactive({
  cert_type: '', cert_no: '', issuing_authority: '', issue_date: '', expiry_date: '',
})

async function fetchCerts() {
  certLoading.value = true
  try {
    const res: any = await getCertificates(staffId.value)
    certList.value = res.results ?? res.list ?? res ?? []
  } finally {
    certLoading.value = false
  }
}

function openCertCreate() {
  Object.assign(certForm, { cert_type: '', cert_no: '', issuing_authority: '', issue_date: '', expiry_date: '' })
  certDialogVisible.value = true
}

async function handleCertSubmit() {
  await createCertificate(staffId.value, certForm)
  ElMessage.success('创建成功')
  certDialogVisible.value = false
  fetchCerts()
}

function expiryTagType(date: string) {
  if (!date) return 'info'
  const days = (new Date(date).getTime() - Date.now()) / 86400000
  if (days < 0) return 'danger'
  if (days < 30) return 'warning'
  return 'success'
}

// --- Shared options ---
const categoryOptions = ref<{ id: number; name: string }[]>([])
const parameterOptions = ref<{ id: number; name: string; code: string }[]>([])

async function fetchOptions() {
  const [catRes, paramRes]: any[] = await Promise.all([
    getTestCategories(),
    getTestParameters({ page_size: 500 }),
  ])
  categoryOptions.value = (catRes.results ?? catRes.list ?? catRes ?? [])
  parameterOptions.value = (paramRes.results ?? paramRes.list ?? paramRes ?? [])
}

// --- Authorizations ---
const authLoading = ref(false)
const authList = ref<any[]>([])
const authDialogVisible = ref(false)
const authForm = reactive({
  test_category: null as number | null, parameters: [] as number[], authorized_date: '', is_active: true,
})

async function fetchAuths() {
  authLoading.value = true
  try {
    const res: any = await getAuthorizations(staffId.value)
    authList.value = res.results ?? res.list ?? res ?? []
  } finally {
    authLoading.value = false
  }
}

function openAuthCreate() {
  Object.assign(authForm, { test_category: null, parameters: [], authorized_date: '', is_active: true })
  authDialogVisible.value = true
}

async function handleAuthSubmit() {
  await createAuthorization(staffId.value, authForm)
  ElMessage.success('创建成功')
  authDialogVisible.value = false
  fetchAuths()
}

// --- Trainings ---
const trainLoading = ref(false)
const trainList = ref<any[]>([])
const trainDialogVisible = ref(false)
const trainForm = reactive({
  title: '', training_date: '', hours: 0, trainer: '', assessment_result: 'pass',
})

const trainResultOptions = [
  { label: '合格', value: 'pass' },
  { label: '不合格', value: 'fail' },
  { label: '未考核', value: 'na' },
]

async function fetchTrainings() {
  trainLoading.value = true
  try {
    const res: any = await getTrainings(staffId.value)
    trainList.value = res.results ?? res.list ?? res ?? []
  } finally {
    trainLoading.value = false
  }
}

function openTrainCreate() {
  Object.assign(trainForm, {
    title: '', training_date: '', hours: 0, trainer: '', assessment_result: 'pass',
  })
  trainDialogVisible.value = true
}

async function handleTrainSubmit() {
  await createTraining(staffId.value, trainForm)
  ElMessage.success('创建成功')
  trainDialogVisible.value = false
  fetchTrainings()
}

function trainResultLabel(val: string) {
  return trainResultOptions.find(o => o.value === val)?.label ?? val
}

// --- Evaluations ---
const evalLoading = ref(false)
const evalList = ref<any[]>([])
const evalDialogVisible = ref(false)
const evalForm = reactive({
  eval_date: '', eval_type: '', score: 0, conclusion: 'competent', comment: '',
})

async function fetchEvals() {
  evalLoading.value = true
  try {
    const res: any = await getEvaluations(staffId.value)
    evalList.value = res.results ?? res.list ?? res ?? []
  } finally {
    evalLoading.value = false
  }
}

function openEvalCreate() {
  Object.assign(evalForm, { eval_date: '', eval_type: '', score: 0, conclusion: 'competent', comment: '' })
  evalDialogVisible.value = true
}

async function handleEvalSubmit() {
  await createEvaluation(staffId.value, evalForm)
  ElMessage.success('创建成功')
  evalDialogVisible.value = false
  fetchEvals()
}

function handleTabChange(tab: string) {
  const loaders: Record<string, () => void> = {
    certs: fetchCerts, auths: () => { fetchAuths(); fetchOptions() },
    trainings: fetchTrainings, evals: fetchEvals,
  }
  loaders[tab]?.()
}

onMounted(fetchStaff)
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/staff')">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">{{ staff.name || '人员详情' }}</span>
      </template>
    </el-page-header>

    <el-tabs v-model="activeTab" style="margin-top: 20px" @tab-change="handleTabChange">
      <!-- Basic -->
      <el-tab-pane label="基本信息" name="basic">
        <el-card shadow="never">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="工号">{{ staff.staff_no }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ staff.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ staff.gender }}</el-descriptions-item>
            <el-descriptions-item label="部门">{{ staff.department }}</el-descriptions-item>
            <el-descriptions-item label="职称">{{ staff.title }}</el-descriptions-item>
            <el-descriptions-item label="学历">{{ staff.education }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ staff.phone }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ staff.email }}</el-descriptions-item>
            <el-descriptions-item label="入职日期">{{ staff.entry_date }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>

      <!-- Certificates -->
      <el-tab-pane label="资质证书" name="certs">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>资质证书</span>
              <el-button v-permission="'staff:create'" type="primary" :icon="Plus" size="small" @click="openCertCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="certLoading" :data="certList" stripe border>
            <el-table-column prop="cert_type" label="证书类型" min-width="160" />
            <el-table-column prop="cert_no" label="证书编号" width="160" />
            <el-table-column prop="issuing_authority" label="发证机构" width="160" />
            <el-table-column prop="issue_date" label="发证日期" width="120" />
            <el-table-column label="有效期至" width="130">
              <template #default="{ row }">
                <el-tag :type="expiryTagType(row.expiry_date)" size="small">
                  {{ row.expiry_date || '长期' }}
                </el-tag>
                <el-icon v-if="expiryTagType(row.expiry_date) === 'warning'" color="#e6a23c" style="margin-left: 4px">
                  <WarningFilled />
                </el-icon>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Authorizations -->
      <el-tab-pane label="上岗授权" name="auths">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>上岗授权</span>
              <el-button v-permission="'staff:create'" type="primary" :icon="Plus" size="small" @click="openAuthCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="authLoading" :data="authList" stripe border>
            <el-table-column prop="test_category_name" label="检测类别" min-width="140" />
            <el-table-column prop="authorized_date" label="授权日期" width="120" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '有效' : '已停' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Trainings -->
      <el-tab-pane label="培训记录" name="trainings">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>培训记录</span>
              <el-button v-permission="'staff:create'" type="primary" :icon="Plus" size="small" @click="openTrainCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="trainLoading" :data="trainList" stripe border>
            <el-table-column prop="title" label="培训主题" min-width="180" />
            <el-table-column prop="training_date" label="培训日期" width="120" />
            <el-table-column prop="hours" label="学时" width="70" align="center" />
            <el-table-column prop="trainer" label="培训讲师" width="140" />
            <el-table-column label="考核结果" width="100">
              <template #default="{ row }">{{ row.assessment_result_display || trainResultLabel(row.assessment_result) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Evaluations -->
      <el-tab-pane label="能力评价" name="evals">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>能力评价</span>
              <el-button v-permission="'staff:create'" type="primary" :icon="Plus" size="small" @click="openEvalCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="evalLoading" :data="evalList" stripe border>
            <el-table-column prop="eval_date" label="评价日期" width="120" />
            <el-table-column prop="eval_type" label="评价类型" width="120" />
            <el-table-column prop="score" label="得分" width="80" align="center" />
            <el-table-column prop="conclusion_display" label="结论" width="120" />
            <el-table-column prop="evaluator_name" label="评价人" width="100" />
            <el-table-column prop="comment" label="备注" min-width="140" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- Certificate Dialog -->
    <el-dialog v-model="certDialogVisible" title="新增资质证书" width="520px" destroy-on-close>
      <el-form :model="certForm" label-width="90px">
        <el-form-item label="证书类型"><el-input v-model="certForm.cert_type" placeholder="如：检测员证、见证员证" /></el-form-item>
        <el-form-item label="证书编号"><el-input v-model="certForm.cert_no" /></el-form-item>
        <el-form-item label="发证机构"><el-input v-model="certForm.issuing_authority" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="发证日期">
              <el-date-picker v-model="certForm.issue_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至">
              <el-date-picker v-model="certForm.expiry_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="certDialogVisible = false">取消</el-button>
        <el-button v-permission="'staff:create'" type="primary" @click="handleCertSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Authorization Dialog -->
    <el-dialog v-model="authDialogVisible" title="新增上岗授权" width="560px" destroy-on-close>
      <el-form :model="authForm" label-width="90px">
        <el-form-item label="检测类别">
          <el-select v-model="authForm.test_category" placeholder="选择检测类别" filterable clearable style="width: 100%">
            <el-option v-for="c in categoryOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="授权参数">
          <el-select v-model="authForm.parameters" multiple filterable placeholder="选择检测参数" style="width: 100%">
            <el-option v-for="p in parameterOptions" :key="p.id" :label="`${p.code} ${p.name}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="授权日期">
          <el-date-picker v-model="authForm.authorized_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="是否生效">
          <el-switch v-model="authForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="authDialogVisible = false">取消</el-button>
        <el-button v-permission="'staff:create'" type="primary" @click="handleAuthSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Training Dialog -->
    <el-dialog v-model="trainDialogVisible" title="新增培训记录" width="520px" destroy-on-close>
      <el-form :model="trainForm" label-width="90px">
        <el-form-item label="培训主题"><el-input v-model="trainForm.title" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="培训日期">
              <el-date-picker v-model="trainForm.training_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学时">
              <el-input-number v-model="trainForm.hours" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="培训讲师"><el-input v-model="trainForm.trainer" /></el-form-item>
        <el-form-item label="考核结果">
          <el-select v-model="trainForm.assessment_result" style="width: 100%">
            <el-option v-for="t in trainResultOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="trainDialogVisible = false">取消</el-button>
        <el-button v-permission="'staff:create'" type="primary" @click="handleTrainSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Evaluation Dialog -->
    <el-dialog v-model="evalDialogVisible" title="新增能力评价" width="520px" destroy-on-close>
      <el-form :model="evalForm" label-width="80px">
        <el-form-item label="评价日期">
          <el-date-picker v-model="evalForm.eval_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="评价类型"><el-input v-model="evalForm.eval_type" placeholder="如：年度评价" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="得分">
              <el-input-number v-model="evalForm.score" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="结论">
          <el-select v-model="evalForm.conclusion" style="width: 100%">
            <el-option label="胜任" value="competent" />
            <el-option label="待提高" value="needs_improvement" />
            <el-option label="不胜任" value="incompetent" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="evalForm.comment" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="evalDialogVisible = false">取消</el-button>
        <el-button v-permission="'staff:create'" type="primary" @click="handleEvalSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
