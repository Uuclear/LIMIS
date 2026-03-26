<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus, WarningFilled } from '@element-plus/icons-vue'
import {
  getEquipmentList, createEquipment, updateEquipment, getExpiringEquipment,
} from '@/api/equipment'

const router = useRouter()
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const expiringList = ref<any[]>([])

const query = reactive({
  page: 1, page_size: 20, keyword: '', category: '', status: '',
})

const categoryOptions = [
  { label: 'A类', value: 'A' },
  { label: 'B类', value: 'B' },
  { label: 'C类', value: 'C' },
]

const statusOptions = [
  { label: '在用', value: 'in_use' },
  { label: '停用', value: 'disabled' },
  { label: '送检中', value: 'calibrating' },
  { label: '维修中', value: 'repairing' },
  { label: '报废', value: 'scrapped' },
]

const dialogVisible = ref(false)
const formData = reactive({
  id: 0,
  equipment_no: '',
  name: '',
  model: '',
  category: 'A',
  status: 'in_use',
  manufacturer: '',
  serial_no: '',
  purchase_date: '',
  calibration_due: '',
  location: '',
  custodian: '',
  remark: '',
})

const dialogTitle = computed(() => formData.id ? '编辑设备' : '新增设备')

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getEquipmentList(query)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

async function fetchExpiring() {
  try {
    const res: any = await getExpiringEquipment()
    expiringList.value = res.results ?? res.list ?? res ?? []
  } catch { /* ignore */ }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, { page: 1, keyword: '', category: '', status: '' })
  fetchList()
}

function openCreate() {
  Object.assign(formData, {
    id: 0, equipment_no: '', name: '', model: '', category: 'A',
    status: 'in_use', manufacturer: '', serial_no: '', purchase_date: '',
    calibration_due: '', location: '', custodian: '', remark: '',
  })
  dialogVisible.value = true
}

function openEdit(row: any) {
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (formData.id) {
    await updateEquipment(formData.id, formData)
    ElMessage.success('更新成功')
  } else {
    await createEquipment(formData)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

function goDetail(row: any) {
  router.push(`/equipment/${row.id}`)
}

function categoryTagType(cat: string) {
  const map: Record<string, string> = { A: 'danger', B: 'warning', C: 'info' }
  return map[cat] ?? 'info'
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    in_use: 'success', disabled: 'danger', calibrating: 'warning',
    repairing: '', scrapped: 'info',
  }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  return statusOptions.find(o => o.value === status)?.label ?? status
}

onMounted(() => {
  fetchList()
  fetchExpiring()
})
</script>

<template>
  <div class="page-container">
    <el-alert
      v-if="expiringList.length"
      type="warning"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    >
      <template #title>
        <span>
          <el-icon><WarningFilled /></el-icon>
          有 <strong>{{ expiringList.length }}</strong> 台设备即将到期，请及时安排检定/校准
        </span>
      </template>
    </el-alert>

    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="编号/名称/型号" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="query.category" placeholder="全部" clearable style="width: 100px">
            <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>仪器设备管理</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增设备</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="equipment_no" label="管理编号" width="150" />
        <el-table-column prop="name" label="设备名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="model" label="型号" width="140" show-overflow-tooltip />
        <el-table-column label="分类" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="categoryTagType(row.category)" size="small">{{ row.category }}类</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="calibration_due" label="校准到期日" width="120" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">查看</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        style="margin-top: 16px; justify-content: flex-end"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-size="query.page_size"
        :current-page="query.page"
        :page-sizes="[20, 50, 100]"
        @current-change="(p: number) => { query.page = p; fetchList() }"
        @size-change="(s: number) => { query.page_size = s; query.page = 1; fetchList() }"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form :model="formData" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="管理编号">
              <el-input v-model="formData.equipment_no" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称">
              <el-input v-model="formData.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="formData.model" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="formData.category" style="width: 100%">
                <el-option v-for="c in categoryOptions" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="制造商">
              <el-input v-model="formData.manufacturer" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出厂编号">
              <el-input v-model="formData.serial_no" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="购置日期">
              <el-date-picker v-model="formData.purchase_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="校准到期">
              <el-date-picker v-model="formData.calibration_due" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="存放地点">
              <el-input v-model="formData.location" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保管人">
              <el-input v-model="formData.custodian" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="formData.status" style="width: 100%">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
