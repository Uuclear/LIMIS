<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getEquipment, getCalibrations, createCalibration,
  getPeriodChecks, createPeriodCheck,
  getMaintenances, createMaintenance,
  getUsageLogs,
} from '@/api/equipment'

const route = useRoute()
const router = useRouter()
const equipmentId = computed(() => Number(route.params.id))
const activeTab = ref('basic')
const equipment = ref<any>({})

async function fetchEquipment() {
  equipment.value = await getEquipment(equipmentId.value) as any
}

// --- Calibrations ---
const calLoading = ref(false)
const calList = ref<any[]>([])
const calDialogVisible = ref(false)
const calForm = reactive({
  certificate_no: '', calibration_date: '', valid_until: '',
  institution: '', result: 'qualified', remark: '',
})

async function fetchCalibrations() {
  calLoading.value = true
  try {
    const res: any = await getCalibrations(equipmentId.value)
    calList.value = res.results ?? res.list ?? res ?? []
  } finally {
    calLoading.value = false
  }
}

function openCalCreate() {
  Object.assign(calForm, {
    certificate_no: '', calibration_date: '', valid_until: '',
    institution: '', result: 'qualified', remark: '',
  })
  calDialogVisible.value = true
}

async function handleCalSubmit() {
  await createCalibration(equipmentId.value, {
    certificate_no: calForm.certificate_no,
    calibration_date: calForm.calibration_date,
    valid_until: calForm.valid_until,
    calibration_org: calForm.institution,
    conclusion: calForm.result,
    remark: calForm.remark,
  })
  ElMessage.success('创建成功')
  calDialogVisible.value = false
  fetchCalibrations()
}

function calResultTag(result: string) {
  const map: Record<string, string> = { qualified: 'success', unqualified: 'danger', limited: 'warning' }
  return map[result] ?? 'info'
}

function calResultLabel(result: string) {
  const map: Record<string, string> = { qualified: '合格', unqualified: '不合格', limited: '限用' }
  return map[result] ?? result
}

function validityColor(date: string) {
  if (!date) return ''
  const diff = new Date(date).getTime() - Date.now()
  const days = diff / (1000 * 60 * 60 * 24)
  if (days < 0) return 'danger'
  if (days < 30) return 'warning'
  return 'success'
}

// --- Period Checks ---
const checkLoading = ref(false)
const checkList = ref<any[]>([])
const checkDialogVisible = ref(false)
const checkForm = reactive({
  check_date: '', checker: '', result: 'normal', standard_value: '', measured_value: '', remark: '',
})

async function fetchChecks() {
  checkLoading.value = true
  try {
    const res: any = await getPeriodChecks(equipmentId.value)
    checkList.value = res.results ?? res.list ?? res ?? []
  } finally {
    checkLoading.value = false
  }
}

function openCheckCreate() {
  Object.assign(checkForm, {
    check_date: '', checker: '', result: 'normal',
    standard_value: '', measured_value: '', remark: '',
  })
  checkDialogVisible.value = true
}

async function handleCheckSubmit() {
  await createPeriodCheck(equipmentId.value, {
    check_date: checkForm.check_date,
    check_method: checkForm.standard_value || '-',
    check_result: checkForm.measured_value || '-',
    conclusion: checkForm.result,
  })
  ElMessage.success('创建成功')
  checkDialogVisible.value = false
  fetchChecks()
}

// --- Maintenances ---
const mtLoading = ref(false)
const mtList = ref<any[]>([])
const mtDialogVisible = ref(false)
const mtForm = reactive({
  maintenance_date: '', type: 'routine', content: '', operator: '', remark: '',
})

async function fetchMaintenances() {
  mtLoading.value = true
  try {
    const res: any = await getMaintenances(equipmentId.value)
    mtList.value = res.results ?? res.list ?? res ?? []
  } finally {
    mtLoading.value = false
  }
}

function openMtCreate() {
  Object.assign(mtForm, {
    maintenance_date: '', type: 'routine', content: '', operator: '', remark: '',
  })
  mtDialogVisible.value = true
}

async function handleMtSubmit() {
  await createMaintenance(equipmentId.value, {
    maintenance_date: mtForm.maintenance_date,
    maintenance_type: mtForm.type,
    description: mtForm.content,
    result: mtForm.remark,
  })
  ElMessage.success('创建成功')
  mtDialogVisible.value = false
  fetchMaintenances()
}

// --- Traceability / Usage ---
const usageLoading = ref(false)
const usageList = ref<any[]>([])

async function fetchUsage() {
  usageLoading.value = true
  try {
    const res: any = await getUsageLogs(equipmentId.value, { page_size: 100 })
    usageList.value = res.results ?? res.list ?? res ?? []
  } finally {
    usageLoading.value = false
  }
}

const mtTypeOptions = [
  { label: '日常保养', value: 'routine' },
  { label: '故障维修', value: 'repair' },
  { label: '定期维护', value: 'periodic' },
]

function mtTypeLabel(val: string) {
  return mtTypeOptions.find(o => o.value === val)?.label ?? val
}

function handleTabChange(tab: string) {
  const loaders: Record<string, () => void> = {
    calibrations: fetchCalibrations,
    checks: fetchChecks,
    maintenances: fetchMaintenances,
    usage: fetchUsage,
  }
  loaders[tab]?.()
}

onMounted(fetchEquipment)
</script>

<template>
  <div class="page-container">
    <el-page-header @back="router.push('/equipment')">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">{{ equipment.name || '设备详情' }}</span>
      </template>
    </el-page-header>

    <el-tabs v-model="activeTab" style="margin-top: 20px" @tab-change="handleTabChange">
      <!-- Basic -->
      <el-tab-pane label="基本信息" name="basic">
        <el-card shadow="never">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="管理编号">{{ equipment.equipment_no }}</el-descriptions-item>
            <el-descriptions-item label="设备名称">{{ equipment.name }}</el-descriptions-item>
            <el-descriptions-item label="型号">{{ equipment.model }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ equipment.category }}类</el-descriptions-item>
            <el-descriptions-item label="制造商">{{ equipment.manufacturer }}</el-descriptions-item>
            <el-descriptions-item label="出厂编号">{{ equipment.serial_no }}</el-descriptions-item>
            <el-descriptions-item label="购置日期">{{ equipment.purchase_date }}</el-descriptions-item>
            <el-descriptions-item label="校准到期">{{ equipment.calibration_due }}</el-descriptions-item>
            <el-descriptions-item label="存放地点">{{ equipment.location }}</el-descriptions-item>
            <el-descriptions-item label="保管人">{{ equipment.custodian }}</el-descriptions-item>
            <el-descriptions-item label="状态">{{ equipment.status }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ equipment.remark }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>

      <!-- Calibrations -->
      <el-tab-pane label="检定/校准记录" name="calibrations">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>检定/校准记录</span>
              <el-button type="primary" :icon="Plus" size="small" @click="openCalCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="calLoading" :data="calList" stripe border>
            <el-table-column prop="certificate_no" label="证书编号" width="160" />
            <el-table-column prop="calibration_date" label="检定日期" width="120" />
            <el-table-column label="有效期至" width="120">
              <template #default="{ row }">
                <el-tag :type="validityColor(row.valid_until)" size="small">{{ row.valid_until }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="institution" label="检定机构" min-width="160" />
            <el-table-column label="结论" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="calResultTag(row.result)" size="small">{{ calResultLabel(row.result) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Period Checks -->
      <el-tab-pane label="期间核查" name="checks">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>期间核查记录</span>
              <el-button type="primary" :icon="Plus" size="small" @click="openCheckCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="checkLoading" :data="checkList" stripe border>
            <el-table-column prop="check_date" label="核查日期" width="120" />
            <el-table-column prop="checker" label="核查人" width="100" />
            <el-table-column prop="standard_value" label="标准值" width="120" />
            <el-table-column prop="measured_value" label="实测值" width="120" />
            <el-table-column label="结论" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.result === 'normal' ? 'success' : 'danger'" size="small">
                  {{ row.result === 'normal' ? '正常' : '异常' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Maintenances -->
      <el-tab-pane label="维护保养" name="maintenances">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>维护保养记录</span>
              <el-button type="primary" :icon="Plus" size="small" @click="openMtCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="mtLoading" :data="mtList" stripe border>
            <el-table-column prop="maintenance_date" label="日期" width="120" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">{{ mtTypeLabel(row.type) }}</template>
            </el-table-column>
            <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="operator" label="操作人" width="100" />
            <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Usage -->
      <el-tab-pane label="使用记录" name="usage">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>使用记录（溯源）</span></div>
          </template>
          <el-table v-loading="usageLoading" :data="usageList" stripe border>
            <el-table-column prop="start_time" label="开始时间" width="180" />
            <el-table-column prop="end_time" label="结束时间" width="180" />
            <el-table-column prop="user_name" label="使用人" width="120" />
            <el-table-column prop="task" label="关联任务" width="120" />
            <el-table-column prop="condition_before" label="使用前状态" min-width="140" />
            <el-table-column prop="condition_after" label="使用后状态" min-width="140" />
            <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- Calibration Dialog -->
    <el-dialog v-model="calDialogVisible" title="新增检定/校准记录" width="520px" destroy-on-close>
      <el-form :model="calForm" label-width="90px">
        <el-form-item label="证书编号"><el-input v-model="calForm.certificate_no" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="检定日期">
              <el-date-picker v-model="calForm.calibration_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至">
              <el-date-picker v-model="calForm.valid_until" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="检定机构"><el-input v-model="calForm.institution" /></el-form-item>
        <el-form-item label="结论">
          <el-radio-group v-model="calForm.result">
            <el-radio value="qualified">合格</el-radio>
            <el-radio value="unqualified">不合格</el-radio>
            <el-radio value="limited">限用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="calForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="calDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCalSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Period Check Dialog -->
    <el-dialog v-model="checkDialogVisible" title="新增期间核查" width="520px" destroy-on-close>
      <el-form :model="checkForm" label-width="80px">
        <el-form-item label="核查日期">
          <el-date-picker v-model="checkForm.check_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="核查人"><el-input v-model="checkForm.checker" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="标准值"><el-input v-model="checkForm.standard_value" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实测值"><el-input v-model="checkForm.measured_value" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="结论">
          <el-radio-group v-model="checkForm.result">
            <el-radio value="normal">正常</el-radio>
            <el-radio value="abnormal">异常</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="checkForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="checkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCheckSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Maintenance Dialog -->
    <el-dialog v-model="mtDialogVisible" title="新增维护保养" width="520px" destroy-on-close>
      <el-form :model="mtForm" label-width="80px">
        <el-form-item label="日期">
          <el-date-picker v-model="mtForm.maintenance_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="mtForm.type" style="width: 100%">
            <el-option v-for="o in mtTypeOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="mtForm.content" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="操作人"><el-input v-model="mtForm.operator" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="mtForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mtDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleMtSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
