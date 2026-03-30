<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getNcList, createNc, getComplaintList, createComplaint } from '@/api/quality'
import { getUserList } from '@/api/system'

const activeTab = ref('nc')

// --- NonConformity ---
const ncLoading = ref(false)
const ncData = ref<any[]>([])
const ncTotal = ref(0)
const ncQuery = reactive({ page: 1, page_size: 20, keyword: '', status: '' })

const ncStatusOptions = [
  { label: '待处理', value: 'open' },
  { label: '处理中', value: 'in_progress' },
  { label: '已关闭', value: 'closed' },
]

const ncSourceOptions = [
  { label: '内部发现', value: 'internal' },
  { label: '审核发现', value: 'audit' },
  { label: '投诉', value: 'complaint' },
  { label: '能力验证', value: 'proficiency' },
  { label: '其他', value: 'other' },
]

const userOptions = ref<{ id: number; username: string }[]>([])

const ncDialogVisible = ref(false)
const ncForm = reactive({
  nc_no: '',
  source: 'internal',
  description: '',
  impact_assessment: '',
  corrective_action: '',
  responsible_person: null as number | null,
  status: 'open',
})

async function fetchNcList() {
  ncLoading.value = true
  try {
    const res: any = await getNcList(ncQuery)
    ncData.value = res.results ?? res.list ?? []
    ncTotal.value = res.total ?? res.count ?? 0
  } finally {
    ncLoading.value = false
  }
}

async function loadUsers() {
  const res: any = await getUserList({ page_size: 500 })
  const rows = res.results ?? res.list ?? []
  userOptions.value = rows.map((u: any) => ({
    id: u.id,
    username: u.username || u.first_name || String(u.id),
  }))
}

function openNcCreate() {
  Object.assign(ncForm, {
    nc_no: '',
    source: 'internal',
    description: '',
    impact_assessment: '',
    corrective_action: '',
    responsible_person: null,
    status: 'open',
  })
  ncDialogVisible.value = true
}

async function handleNcSubmit() {
  if (!ncForm.nc_no?.trim()) {
    ElMessage.warning('请填写不符合项编号')
    return
  }
  if (!ncForm.description?.trim()) {
    ElMessage.warning('请填写描述')
    return
  }
  if (!ncForm.responsible_person) {
    ElMessage.warning('请选择责任人')
    return
  }
  await createNc({
    nc_no: ncForm.nc_no,
    source: ncForm.source,
    description: ncForm.description,
    impact_assessment: ncForm.impact_assessment || '',
    corrective_action: ncForm.corrective_action || '',
    responsible_person: ncForm.responsible_person,
    status: ncForm.status,
  })
  ElMessage.success('创建成功')
  ncDialogVisible.value = false
  fetchNcList()
}

function ncStatusTagType(status: string) {
  const map: Record<string, string> = {
    open: 'danger', in_progress: 'warning', closed: 'info',
  }
  return map[status] ?? 'info'
}

function ncStatusLabel(status: string) {
  return ncStatusOptions.find(o => o.value === status)?.label ?? status
}

// --- Complaints ---
const cmpLoading = ref(false)
const cmpData = ref<any[]>([])
const cmpTotal = ref(0)
const cmpQuery = reactive({ page: 1, page_size: 20, keyword: '' })

const cmpDialogVisible = ref(false)
const cmpForm = reactive({
  complaint_no: '',
  complainant: '',
  content: '',
  complaint_date: '',
  handler: null as number | null,
  investigation: '',
  handling_result: '',
  status: 'received',
})

const cmpStatusOptions = [
  { label: '已接收', value: 'received' },
  { label: '调查中', value: 'investigating' },
  { label: '已处理', value: 'resolved' },
  { label: '已关闭', value: 'closed' },
]

async function fetchCmpList() {
  cmpLoading.value = true
  try {
    const res: any = await getComplaintList(cmpQuery)
    cmpData.value = res.results ?? res.list ?? []
    cmpTotal.value = res.total ?? res.count ?? 0
  } finally {
    cmpLoading.value = false
  }
}

function openCmpCreate() {
  Object.assign(cmpForm, {
    complaint_no: '',
    complainant: '',
    content: '',
    complaint_date: '',
    handler: null,
    investigation: '',
    handling_result: '',
    status: 'received',
  })
  cmpDialogVisible.value = true
}

async function handleCmpSubmit() {
  if (!cmpForm.complaint_no?.trim() || !cmpForm.complainant?.trim()) {
    ElMessage.warning('请填写投诉编号与投诉人')
    return
  }
  if (!cmpForm.complaint_date || !cmpForm.content?.trim()) {
    ElMessage.warning('请填写投诉日期与内容')
    return
  }
  await createComplaint({
    complaint_no: cmpForm.complaint_no,
    complainant: cmpForm.complainant,
    complaint_date: cmpForm.complaint_date,
    content: cmpForm.content,
    investigation: cmpForm.investigation || '',
    handling_result: cmpForm.handling_result || '',
    handler: cmpForm.handler,
    status: cmpForm.status,
  })
  ElMessage.success('创建成功')
  cmpDialogVisible.value = false
  fetchCmpList()
}

function cmpStatusTagType(status: string) {
  const map: Record<string, string> = {
    received: 'info', investigating: 'warning', resolved: 'success', closed: '',
  }
  return map[status] ?? 'info'
}

function cmpStatusLabel(status: string) {
  return cmpStatusOptions.find(o => o.value === status)?.label ?? status
}

function handleTabChange(tab: string) {
  if (tab === 'nc') fetchNcList()
  else fetchCmpList()
}

onMounted(() => {
  fetchNcList()
  loadUsers()
})
</script>

<template>
  <div class="page-container">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <!-- NonConformity -->
      <el-tab-pane label="不符合项" name="nc">
        <el-card shadow="never">
          <el-form inline @submit.prevent="() => { ncQuery.page = 1; fetchNcList() }">
            <el-form-item label="关键词">
              <el-input v-model="ncQuery.keyword" placeholder="编号/描述" clearable style="width: 200px" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="ncQuery.status" placeholder="全部" clearable style="width: 120px">
                <el-option v-for="s in ncStatusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Search" @click="() => { ncQuery.page = 1; fetchNcList() }">搜索</el-button>
              <el-button :icon="Refresh" @click="() => { Object.assign(ncQuery, { page: 1, keyword: '', status: '' }); fetchNcList() }">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" style="margin-top: 16px">
          <template #header>
            <div class="card-header">
              <span>不符合项管理</span>
              <el-button type="primary" :icon="Plus" @click="openNcCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="ncLoading" :data="ncData" stripe border>
            <el-table-column prop="nc_no" label="编号" width="150" />
            <el-table-column label="来源" width="120">
              <template #default="{ row }">{{ row.source_display || row.source }}</template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="responsible_person_name" label="责任人" width="120" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="ncStatusTagType(row.status)" size="small">{{ ncStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="ncTotal > 0"
            style="margin-top: 16px; justify-content: flex-end"
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="ncTotal"
            :page-size="ncQuery.page_size"
            :current-page="ncQuery.page"
            :page-sizes="[20, 50, 100]"
            @current-change="(p: number) => { ncQuery.page = p; fetchNcList() }"
            @size-change="(s: number) => { ncQuery.page_size = s; ncQuery.page = 1; fetchNcList() }"
          />
        </el-card>
      </el-tab-pane>

      <!-- Complaints -->
      <el-tab-pane label="投诉处理" name="complaints">
        <el-card shadow="never">
          <el-form inline @submit.prevent="() => { cmpQuery.page = 1; fetchCmpList() }">
            <el-form-item label="关键词">
              <el-input v-model="cmpQuery.keyword" placeholder="编号/投诉人" clearable style="width: 200px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Search" @click="() => { cmpQuery.page = 1; fetchCmpList() }">搜索</el-button>
              <el-button :icon="Refresh" @click="() => { Object.assign(cmpQuery, { page: 1, keyword: '' }); fetchCmpList() }">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" style="margin-top: 16px">
          <template #header>
            <div class="card-header">
              <span>投诉处理</span>
              <el-button type="primary" :icon="Plus" @click="openCmpCreate">新增</el-button>
            </div>
          </template>
          <el-table v-loading="cmpLoading" :data="cmpData" stripe border>
            <el-table-column prop="complaint_no" label="投诉编号" width="150" />
            <el-table-column prop="complainant" label="投诉人" width="100" />
            <el-table-column prop="content" label="投诉内容" min-width="200" show-overflow-tooltip />
            <el-table-column prop="complaint_date" label="投诉日期" width="120" />
            <el-table-column prop="handler_name" label="处理人" width="120" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="cmpStatusTagType(row.status)" size="small">{{ cmpStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="cmpTotal > 0"
            style="margin-top: 16px; justify-content: flex-end"
            background
            layout="total, sizes, prev, pager, next, jumper"
            :total="cmpTotal"
            :page-size="cmpQuery.page_size"
            :current-page="cmpQuery.page"
            :page-sizes="[20, 50, 100]"
            @current-change="(p: number) => { cmpQuery.page = p; fetchCmpList() }"
            @size-change="(s: number) => { cmpQuery.page_size = s; cmpQuery.page = 1; fetchCmpList() }"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- NC Dialog -->
    <el-dialog v-model="ncDialogVisible" title="新增不符合项" width="620px" destroy-on-close>
      <el-form :model="ncForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="编号" required><el-input v-model="ncForm.nc_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="来源">
              <el-select v-model="ncForm.source" style="width: 100%">
                <el-option v-for="t in ncSourceOptions" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" required><el-input v-model="ncForm.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="影响评价"><el-input v-model="ncForm.impact_assessment" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="纠正措施"><el-input v-model="ncForm.corrective_action" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="责任人" required>
          <el-select v-model="ncForm.responsible_person" placeholder="选择用户" filterable style="width: 100%">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="ncForm.status" style="width: 200px">
            <el-option v-for="s in ncStatusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ncDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleNcSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Complaint Dialog -->
    <el-dialog v-model="cmpDialogVisible" title="新增投诉" width="560px" destroy-on-close>
      <el-form :model="cmpForm" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="投诉编号"><el-input v-model="cmpForm.complaint_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="投诉日期">
              <el-date-picker v-model="cmpForm.complaint_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="投诉人"><el-input v-model="cmpForm.complainant" /></el-form-item>
        <el-form-item label="投诉内容"><el-input v-model="cmpForm.content" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="处理人">
          <el-select v-model="cmpForm.handler" placeholder="可选" clearable filterable style="width: 100%">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="调查"><el-input v-model="cmpForm.investigation" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="处理意见"><el-input v-model="cmpForm.handling_result" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="cmpForm.status" style="width: 200px">
            <el-option v-for="s in cmpStatusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cmpDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCmpSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
