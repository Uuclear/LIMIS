<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getReviewList, createReview } from '@/api/quality'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const query = reactive({ page: 1, page_size: 20, keyword: '', status: '' })

const statusOptions = [
  { label: '准备中', value: 'preparing' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
]

const dialogVisible = ref(false)
const formData = reactive({
  review_no: '', topic: '', review_date: '', chairperson: '',
  participants: '', agenda: '', status: 'preparing', remark: '',
})

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getReviewList(query)
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
    review_no: '', topic: '', review_date: '', chairperson: '',
    participants: '', agenda: '', status: 'preparing', remark: '',
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await createReview(formData)
  ElMessage.success('创建成功')
  dialogVisible.value = false
  fetchList()
}

function statusTagType(status: string) {
  const map: Record<string, string> = { preparing: 'info', in_progress: 'warning', completed: 'success' }
  return map[status] ?? 'info'
}

function statusLabel(status: string) {
  return statusOptions.find(o => o.value === status)?.label ?? status
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="评审编号/主题" clearable style="width: 200px" />
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
          <span>管理评审</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增评审</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="review_no" label="评审编号" width="150" />
        <el-table-column prop="topic" label="评审主题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="review_date" label="评审日期" width="120" />
        <el-table-column prop="chairperson" label="主持人" width="100" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" title="新增管理评审" width="600px" destroy-on-close>
      <el-form :model="formData" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="评审编号"><el-input v-model="formData.review_no" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评审日期">
              <el-date-picker v-model="formData.review_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="评审主题"><el-input v-model="formData.topic" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="主持人"><el-input v-model="formData.chairperson" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参加人员"><el-input v-model="formData.participants" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="议程"><el-input v-model="formData.agenda" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="formData.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
