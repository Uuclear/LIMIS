<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus, WarningFilled } from '@element-plus/icons-vue'
import {
  getConsumableList, createConsumable, consumableIn, consumableOut,
  getLowStock,
} from '@/api/consumables'
import { useActionLock } from '@/composables/useActionLock'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const lowStockList = ref<any[]>([])
const { isLocked, runLocked } = useActionLock()
// 后端目前仅实现了 low-stock，无 expiring 接口

const query = reactive({ page: 1, page_size: 20, keyword: '' })

// --- Create ---
const createVisible = ref(false)
const createForm = reactive({
  code: '', name: '', spec: '', unit: '', category: '',
  stock: 0, safety_stock: 10, expiry_date: '', supplier: '', remark: '',
})

// --- In / Out ---
const ioVisible = ref(false)
const ioType = ref<'in' | 'out'>('in')
const ioTarget = ref<any>(null)
const ioForm = reactive({ quantity: 1, batch_no: '', operator: '', remark: '' })

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getConsumableList(query)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

async function fetchAlerts() {
  try {
    const lowRes: any = await getLowStock()
    lowStockList.value = lowRes?.results ?? lowRes?.list ?? lowRes ?? []
  } catch { /* ignore */ }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, { page: 1, keyword: '' })
  fetchList()
}

function openCreate() {
  Object.assign(createForm, {
    code: '', name: '', spec: '', unit: '', category: '',
    stock: 0, safety_stock: 10, expiry_date: '', supplier: '', remark: '',
  })
  createVisible.value = true
}

async function handleCreateSubmit() {
  // 后端 Consumable 模型字段为 name/code/specification/unit/safety_stock 等
  // 前端表单存在 spec/stock/supplier(字符串)/remark 等差异，这里做一次 payload 映射，避免 422/400
  const payload: Record<string, unknown> = {
    code: createForm.code,
    name: createForm.name,
    specification: createForm.spec || '',
    unit: createForm.unit,
    category: createForm.category || '',
    manufacturer: '',
    safety_stock: createForm.safety_stock ?? 10,
    expiry_date: createForm.expiry_date || null,
    storage_location: '',
  }
  await runLocked('consumable_create', async () => {
    await createConsumable(payload)
    ElMessage.success('创建成功')
    createVisible.value = false
    fetchList()
  })
}

function openInOut(row: any, type: 'in' | 'out') {
  ioTarget.value = row
  ioType.value = type
  Object.assign(ioForm, { quantity: 1, batch_no: '', operator: '', remark: '' })
  ioVisible.value = true
}

async function handleIoSubmit() {
  await runLocked(`consumable_io_${ioType.value}_${ioTarget.value?.id ?? 0}`, async () => {
    const fn = ioType.value === 'in' ? consumableIn : consumableOut
    await fn(ioTarget.value.id, ioForm)
    ElMessage.success(ioType.value === 'in' ? '入库成功' : '出库成功')
    ioVisible.value = false
    fetchList()
    fetchAlerts()
  })
}

function stockColor(row: any) {
  if (row.stock <= 0) return '#f56c6c'
  if (row.stock <= row.safety_stock) return '#e6a23c'
  return ''
}

onMounted(() => {
  fetchList()
  fetchAlerts()
})
</script>

<template>
  <div class="page-container">
    <el-row :gutter="16" v-if="lowStockList.length" style="margin-bottom: 16px">
      <el-col :span="12" v-if="lowStockList.length">
        <el-alert type="warning" :closable="false" show-icon>
          <template #title>
            <el-icon><WarningFilled /></el-icon>
            <strong>{{ lowStockList.length }}</strong> 种耗材库存不足
          </template>
        </el-alert>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="编码/名称" clearable style="width: 200px" />
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
          <span>耗材管理</span>
          <el-button v-permission="'consumables:create'" type="primary" :icon="Plus" @click="openCreate">新增耗材</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="code" label="编码" width="130" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="spec" label="规格" width="120" />
        <el-table-column label="库存量" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: stockColor(row), fontWeight: stockColor(row) ? '700' : 'normal' }">
              {{ row.stock }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" width="90" align="center" />
        <el-table-column prop="expiry_date" label="有效期" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'consumables:create'" link type="success" @click="openInOut(row, 'in')">入库</el-button>
            <el-button v-permission="'consumables:create'" link type="warning" @click="openInOut(row, 'out')">出库</el-button>
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

    <!-- Create Dialog -->
    <el-dialog v-model="createVisible" title="新增耗材" width="580px" destroy-on-close>
      <el-form :model="createForm" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="编码"><el-input v-model="createForm.code" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名称"><el-input v-model="createForm.name" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="规格"><el-input v-model="createForm.spec" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位"><el-input v-model="createForm.unit" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="初始库存">
              <el-input-number v-model="createForm.stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安全库存">
              <el-input-number v-model="createForm.safety_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="有效期">
              <el-date-picker v-model="createForm.expiry_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商"><el-input v-model="createForm.supplier" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="分类"><el-input v-model="createForm.category" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="createForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button v-permission="'consumables:create'" type="primary" :loading="isLocked('consumable_create')" @click="handleCreateSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- In/Out Dialog -->
    <el-dialog
      v-model="ioVisible"
      :title="ioType === 'in' ? '耗材入库' : '耗材出库'"
      width="440px"
      destroy-on-close
    >
      <div v-if="ioTarget" style="margin-bottom: 12px; color: #606266">
        {{ ioTarget.name }}（{{ ioTarget.code }}），当前库存: <strong>{{ ioTarget.stock }}</strong>
      </div>
      <el-form :model="ioForm" label-width="80px">
        <el-form-item label="数量">
          <el-input-number v-model="ioForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="批次号"><el-input v-model="ioForm.batch_no" /></el-form-item>
        <el-form-item label="操作人"><el-input v-model="ioForm.operator" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="ioForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ioVisible = false">取消</el-button>
        <el-button
          v-permission="'consumables:create'"
          type="primary"
          :loading="isLocked(`consumable_io_${ioType}_${ioTarget?.id ?? 0}`)"
          @click="handleIoSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>
