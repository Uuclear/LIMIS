<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getAuditList, createAudit } from '@/api/quality'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const query = reactive({ page: 1, page_size: 20, keyword: '', status: '' })

const statusOptions = [
  { label: '计划中', value: 'planned' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
  { label: '已关闭', value: 'closed' },
]

const typeOptions = [
  { label: '内部审核', value: 'internal' },
  { label: '管理层审核', value: 'management' },
  { label: '专项审核', value: 'special' },
]

const dialogVisible = ref(false)
const formData = reactive({
  audit_no: '', topic: '', type: 'internal', planned_date: '',
  lead_auditor: '', scope: '', status: 'planned', remark: '',
})

const detailVisible = ref(false)
const currentAudit = ref<any>(null)

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getAuditList(query)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, { page: 1, keyword: '', status: '' })
  fetchList()
}

function openCreate() {
  Object.assign(formData, {
    audit_no: '', topic: '', type: 'internal', planned_date: '',
    lead_auditor: '', scope: '', status: 'planned', remark: '',
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await createAudit(formData)
  ElMessage.success('创建成功')
  dialogVisible.value = false
  fetchList()
}

function showDetail(row: any) {
  currentAudit.value = row
  detailVisible.value = true
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    planned: 'info', in_progress: 'warning', completed: 'success', closed: '',
  }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  return statusOptions.find(o => o.value === status)?.label ?? status
}

function typeLabel(type: string) {
  return typeOptions.find(o => o.value === type)?.label ?? type
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="审核编号/主题" clearable style="width: 200px" />
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
          <span>内部审核</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增审核</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border @row-click="showDetail">
        <el-table-column prop="audit_no" label="审核编号" width="150" />
        <el-table-column prop="topic" label="主题" min-width="180" show-overflow-tooltip />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">{{ typeLabel(row.type) }}</template>
        </el-table-column>
        <el-table-column prop="planned_date" label="计划日期" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lead_auditor" label="审核组长" width="100" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="showDetail(row)">查看</el-button>
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
    <el-dialog v-model="dialogVisible" title="新增内部审核" width="600px" destroy-on-close>
      <el-form :model="formData" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="审核编号"><el-input v-model="formData.audit_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="formData.type" style="width: 100%">
                <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="审核主题"><el-input v-model="formData.topic" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计划日期">
              <el-date-picker v-model="formData.planned_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="审核组长"><el-input v-model="formData.lead_auditor" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="审核范围"><el-input v-model="formData.scope" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="formData.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="审核详情" width="700px" destroy-on-close>
      <template v-if="currentAudit">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="审核编号">{{ currentAudit.audit_no }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ typeLabel(currentAudit.type) }}</el-descriptions-item>
          <el-descriptions-item label="主题" :span="2">{{ currentAudit.topic }}</el-descriptions-item>
          <el-descriptions-item label="计划日期">{{ currentAudit.planned_date }}</el-descriptions-item>
          <el-descriptions-item label="审核组长">{{ currentAudit.lead_auditor }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTagType(currentAudit.status)" size="small">{{ statusLabel(currentAudit.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审核范围" :span="2">{{ currentAudit.scope }}</el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px">
          <h4 style="margin-bottom: 12px">发现问题及纠正措施</h4>
          <el-table :data="currentAudit.findings ?? []" stripe border>
            <el-table-column prop="clause" label="条款" width="120" />
            <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="severity" label="严重程度" width="100" />
            <el-table-column prop="corrective_action" label="纠正措施" min-width="200" show-overflow-tooltip />
            <el-table-column prop="due_date" label="整改期限" width="120" />
            <el-table-column prop="status" label="状态" width="80" />
          </el-table>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
