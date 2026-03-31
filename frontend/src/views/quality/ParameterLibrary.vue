<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Setting } from '@element-plus/icons-vue'
import { getStandardList } from '@/api/standards'
import {
  getTestCategories,
  getTestMethods,
  createTestMethod,
  getTestParameters,
  createTestParameter,
  updateTestParameter,
} from '@/api/testing'

const loading = ref(false)
const standards = ref<any[]>([])
const selectedStandard = ref<any>(null)

const methodLoading = ref(false)
const methods = ref<any[]>([])
const selectedMethod = ref<any>(null)

const paramLoading = ref(false)
const parameters = ref<any[]>([])

const categoryId = ref<number | null>(null)
const categories = ref<{ id: number; name: string; code: string }[]>([])

const methodDialog = ref(false)
const methodForm = ref({
  name: '',
  description: '',
})

const paramDialog = ref(false)
const paramForm = ref({
  id: 0,
  name: '',
  code: '',
  unit: '',
  precision: 1,
  is_required: true,
})

const standardTitle = computed(() =>
  selectedStandard.value
    ? `${selectedStandard.value.standard_no} ${selectedStandard.value.name}`
    : '请选择左侧标准',
)

async function fetchStandards() {
  loading.value = true
  try {
    const res: any = await getStandardList({ page_size: 500, scope: 'all' })
    standards.value = res.results ?? res.list ?? []
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  const res: any = await getTestCategories()
  const list = res.results ?? res.list ?? res ?? []
  categories.value = list
  if (list.length && categoryId.value == null) {
    categoryId.value = list[0].id
  }
}

function selectStandard(row: any) {
  selectedStandard.value = row
  selectedMethod.value = null
  parameters.value = []
  loadMethods()
}

async function loadMethods() {
  if (!selectedStandard.value) return
  methodLoading.value = true
  try {
    const res: any = await getTestMethods({
      standard_no: selectedStandard.value.standard_no,
      page_size: 200,
      scope: 'all',
    })
    methods.value = res.results ?? res.list ?? []
  } finally {
    methodLoading.value = false
  }
}

function selectMethod(row: any) {
  selectedMethod.value = row
  loadParameters()
}

async function loadParameters() {
  if (!selectedMethod.value) return
  paramLoading.value = true
  try {
    const res: any = await getTestParameters({
      method: selectedMethod.value.id,
      page_size: 200,
      scope: 'all',
    })
    parameters.value = res.results ?? res.list ?? []
  } finally {
    paramLoading.value = false
  }
}

function openMethodDialog() {
  if (!selectedStandard.value) {
    ElMessage.warning('请先选择标准')
    return
  }
  if (!categoryId.value) {
    ElMessage.warning('缺少检测类别，请先在后台创建检测类别')
    return
  }
  methodForm.value = { name: '', description: '' }
  methodDialog.value = true
}

async function submitMethod() {
  if (!selectedStandard.value || !categoryId.value) return
  await createTestMethod({
    category: categoryId.value,
    name: methodForm.value.name,
    standard_no: selectedStandard.value.standard_no,
    standard_name: selectedStandard.value.name,
    description: methodForm.value.description,
    is_active: true,
  })
  ElMessage.success('检测方法已创建')
  methodDialog.value = false
  loadMethods()
}

function openParamDialog(row?: any) {
  if (!selectedMethod.value) {
    ElMessage.warning('请先选择检测方法')
    return
  }
  if (row?.id) {
    paramForm.value = {
      id: row.id,
      name: row.name,
      code: row.code,
      unit: row.unit || '',
      precision: row.precision ?? 1,
      is_required: row.is_required,
    }
  } else {
    paramForm.value = {
      id: 0,
      name: '',
      code: '',
      unit: '',
      precision: 1,
      is_required: true,
    }
  }
  paramDialog.value = true
}

async function submitParam() {
  if (!selectedMethod.value) return
  const payload = {
    method: selectedMethod.value.id,
    name: paramForm.value.name,
    code: paramForm.value.code,
    unit: paramForm.value.unit,
    precision: paramForm.value.precision,
    is_required: paramForm.value.is_required,
  }
  if (paramForm.value.id) {
    await updateTestParameter(paramForm.value.id, payload)
    ElMessage.success('参数已更新')
  } else {
    await createTestParameter(payload)
    ElMessage.success('参数已添加')
  }
  paramDialog.value = false
  loadParameters()
}

onMounted(async () => {
  await fetchCategories()
  await fetchStandards()
})
</script>

<template>
  <div class="page-container param-lib">
    <div class="page-header">
      <h2 class="title">项目参数库</h2>
      <p class="hint">
        为「标准规范」中的标准配置检测方法（TestMethod）及参数（TestParameter），供委托单选择检测标准与项目时使用。
      </p>
    </div>

    <el-alert type="info" :closable="false" show-icon class="param-alert">
      <template #title>与委托的衔接</template>
      左侧选中标准后维护「检测方法」与「检测参数」。新建方法时需指定<strong>检测类别</strong>（与系统「检测类别」主数据一致）。
    </el-alert>

    <el-card v-if="categories.length" shadow="never" class="category-bar">
      <span class="category-bar-label">新建检测方法时归属类别</span>
      <el-select
        v-model="categoryId"
        placeholder="选择类别"
        filterable
        style="width: min(100%, 320px)"
      >
        <el-option
          v-for="c in categories"
          :key="c.id"
          :label="`${c.name}（${c.code}）`"
          :value="c.id"
        />
      </el-select>
    </el-card>

    <div class="layout">
      <el-card shadow="never" class="panel">
        <template #header>
          <span>标准规范</span>
        </template>
        <el-table
          v-loading="loading"
          :data="standards"
          highlight-current-row
          height="420"
          empty-text="暂无标准，请先在「标准规范」中录入"
          @row-click="selectStandard"
        >
          <el-table-column prop="standard_no" label="标准号" width="140" />
          <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        </el-table>
      </el-card>

      <el-card shadow="never" class="panel">
        <template #header>
          <div class="card-header">
            <span>检测方法 — {{ standardTitle }}</span>
            <el-button type="primary" size="small" :icon="Plus" @click="openMethodDialog">新增方法</el-button>
          </div>
        </template>
        <el-table
          v-loading="methodLoading"
          :data="methods"
          highlight-current-row
          height="420"
          @row-click="selectMethod"
        >
          <el-table-column prop="name" label="方法名称" min-width="200" />
          <el-table-column prop="standard_no" label="标准号" width="120" />
        </el-table>
      </el-card>

      <el-card shadow="never" class="panel wide">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><Setting /></el-icon>
              检测参数
              <template v-if="selectedMethod"> — {{ selectedMethod.name }}</template>
            </span>
            <el-button type="primary" size="small" :icon="Plus" @click="openParamDialog()">新增参数</el-button>
          </div>
        </template>
        <el-table v-loading="paramLoading" :data="parameters" border stripe height="420">
          <el-table-column prop="code" label="代码" width="100" />
          <el-table-column prop="name" label="参数名称" min-width="160" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="precision" label="精度" width="70" />
          <el-table-column label="必填" width="70" align="center">
            <template #default="{ row }">{{ row.is_required ? '是' : '否' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="90" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" :icon="Plus" @click="openParamDialog(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <el-dialog v-model="methodDialog" title="新增检测方法" width="480px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="方法名称" required>
          <el-input v-model="methodForm.name" placeholder="如：混凝土抗压强度" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="methodForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="methodDialog = false">取消</el-button>
        <el-button type="primary" @click="submitMethod">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="paramDialog" :title="paramForm.id ? '编辑参数' : '新增参数'" width="560px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="参数代码" required>
          <el-input v-model="paramForm.code" placeholder="英文或拼音缩写" />
        </el-form-item>
        <el-form-item label="参数名称" required>
          <el-input v-model="paramForm.name" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="paramForm.unit" placeholder="如 MPa" />
        </el-form-item>
        <el-form-item label="修约精度">
          <el-input-number v-model="paramForm.precision" :min="0" :max="6" />
        </el-form-item>
        <el-form-item label="必填">
          <el-switch v-model="paramForm.is_required" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="paramDialog = false">取消</el-button>
        <el-button type="primary" @click="submitParam">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.param-lib .param-alert {
  margin-bottom: 16px;
  border-radius: 10px;
}

.param-lib .category-bar {
  margin-bottom: 16px;
  border-radius: 10px;
}

.param-lib .category-bar :deep(.el-card__body) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 20px;
}

.param-lib .category-bar-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.param-lib .page-header {
  margin-bottom: 16px;
}
.param-lib .title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
}
.param-lib .hint {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.param-lib .layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 16px;
}
.param-lib .panel.wide {
  grid-column: 1 / -1;
}
.param-lib .card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
</style>
