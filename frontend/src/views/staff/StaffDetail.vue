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
  name: '', cert_no: '', issuer: '', issue_date: '', expiry_date: '', remark: '',
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
  Object.assign(certForm, { name: '', cert_no: '', issuer: '', issue_date: '', expiry_date: '', remark: '' })
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

// --- Authorizations ---
const authLoading = ref(false)
const authList = ref<any[]>([])
const authDialogVisible = ref(false)
const authForm = reactive({
  method_name: '', method_no: '', scope: '', auth_date: '', expiry_date: '', remark: '',
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
  Object.assign(authForm, { method_name: '', method_no: '', scope: '', auth_date: '', expiry_date: '', remark: '' })
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
  topic: '', type: '', start_date: '', end_date: '', hours: 0, institution: '', result: '', remark: '',
})

const trainTypeOptions = [
  { label: '内部培训', value: 'internal' },
  { label: '外部培训', value: 'external' },
  { label: '自学', value: 'self' },
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
    topic: '', type: 'internal', start_date: '', end_date: '',
    hours: 0, institution: '', result: '', remark: '',
  })
  trainDialogVisible.value = true
}

async function handleTrainSubmit() {
  await createTraining(staffId.value, trainForm)
  ElMessage.success('创建成功')
  trainDialogVisible.value = false
  fetchTrainings()
}

function trainTypeLabel(val: string) {
  return trainTypeOptions.find(o => o.value === val)?.label ?? val
}

// --- Evaluations ---
const evalLoading = ref(false)
const evalList = ref<any[]>([])
const evalDialogVisible = ref(false)
const evalForm = reactive({
  eval_date: '', evaluator: '', type: '', score: 0, conclusion: '', remark: '',
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
  Object.assign(evalForm, { eval_date: '', evaluator: '', type: '', score: 0, conclusion: '', remark: '' })
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
    certs: fetchCerts, auths: fetchAuths,
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
            <el-table-column prop="name" label="证书名称" min-width="160" />
            <el-table-column prop="cert_no" label="证书编号" width="160" />
            <el-table-column prop="issuer" label="发证机构" width="160" />
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
            <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
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
            <el-table-column prop="method_name" label="检测方法" min-width="180" />
            <el-table-column prop="method_no" label="方法标准号" width="160" />
            <el-table-column prop="scope" label="授权范围" min-width="160" show-overflow-tooltip />
            <el-table-column prop="auth_date" label="授权日期" width="120" />
            <el-table-column label="有效期至" width="130">
              <template #default="{ row }">
                <el-tag :type="expiryTagType(row.expiry_date)" size="small">
                  {{ row.expiry_date || '长期' }}
                </el-tag>
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
            <el-table-column prop="topic" label="培训主题" min-width="180" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">{{ trainTypeLabel(row.type) }}</template>
            </el-table-column>
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="结束日期" width="120" />
            <el-table-column prop="hours" label="学时" width="70" align="center" />
            <el-table-column prop="institution" label="培训机构" width="160" />
            <el-table-column prop="result" label="考核结果" width="100" />
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
            <el-table-column prop="evaluator" label="评价人" width="100" />
            <el-table-column prop="type" label="评价类型" width="120" />
            <el-table-column prop="score" label="得分" width="80" align="center" />
            <el-table-column prop="conclusion" label="结论" width="120" />
            <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- Certificate Dialog -->
    <el-dialog v-model="certDialogVisible" title="新增资质证书" width="520px" destroy-on-close>
      <el-form :model="certForm" label-width="90px">
        <el-form-item label="证书名称"><el-input v-model="certForm.name" /></el-form-item>
        <el-form-item label="证书编号"><el-input v-model="certForm.cert_no" /></el-form-item>
        <el-form-item label="发证机构"><el-input v-model="certForm.issuer" /></el-form-item>
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
        <el-form-item label="备注"><el-input v-model="certForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="certDialogVisible = false">取消</el-button>
        <el-button v-permission="'staff:create'" type="primary" @click="handleCertSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Authorization Dialog -->
    <el-dialog v-model="authDialogVisible" title="新增上岗授权" width="520px" destroy-on-close>
      <el-form :model="authForm" label-width="90px">
        <el-form-item label="检测方法"><el-input v-model="authForm.method_name" /></el-form-item>
        <el-form-item label="方法标准号"><el-input v-model="authForm.method_no" /></el-form-item>
        <el-form-item label="授权范围"><el-input v-model="authForm.scope" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="授权日期">
              <el-date-picker v-model="authForm.auth_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至">
              <el-date-picker v-model="authForm.expiry_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="authForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="authDialogVisible = false">取消</el-button>
        <el-button v-permission="'staff:create'" type="primary" @click="handleAuthSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Training Dialog -->
    <el-dialog v-model="trainDialogVisible" title="新增培训记录" width="520px" destroy-on-close>
      <el-form :model="trainForm" label-width="90px">
        <el-form-item label="培训主题"><el-input v-model="trainForm.topic" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="trainForm.type" style="width: 100%">
            <el-option v-for="t in trainTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="trainForm.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker v-model="trainForm.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学时">
              <el-input-number v-model="trainForm.hours" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="考核结果"><el-input v-model="trainForm.result" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="培训机构"><el-input v-model="trainForm.institution" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="trainForm.remark" type="textarea" /></el-form-item>
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
            <el-form-item label="评价人"><el-input v-model="evalForm.evaluator" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评价类型"><el-input v-model="evalForm.type" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="得分">
              <el-input-number v-model="evalForm.score" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结论"><el-input v-model="evalForm.conclusion" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="evalForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="evalDialogVisible = false">取消</el-button>
        <el-button v-permission="'staff:create'" type="primary" @click="handleEvalSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
