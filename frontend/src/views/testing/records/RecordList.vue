<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOriginalRecordList, submitRecord, reviewRecord } from '@/api/testing'
import type { OriginalRecord } from '@/types/testing'
import { useActionLock } from '@/composables/useActionLock'

const router = useRouter()
const loading = ref(false)
const tableData = ref<OriginalRecord[]>([])
const total = ref(0)
const { isLocked, runLocked } = useActionLock()

const query = reactive({
  page: 1,
  page_size: 20,
  status: '',
  recorder_name: '',
})

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '待复核', value: 'pending_review' },
  { label: '已复核', value: 'reviewed' },
  { label: '已退回', value: 'returned' },
]

const statusMap: Record<string, string> = {
  draft: '草稿',
  pending_review: '待复核',
  reviewed: '已复核',
  returned: '已退回',
}

const statusTagType: Record<string, string> = {
  draft: 'info',
  pending_review: 'warning',
  reviewed: 'success',
  returned: 'danger',
}

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getOriginalRecordList(query)
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
  Object.assign(query, { page: 1, status: '', recorder_name: '' })
  fetchList()
}

function goEdit(record: OriginalRecord) {
  router.push(`/testing/records/${record.id}`)
}

function goView(record: OriginalRecord) {
  router.push(`/testing/records/${record.id}`)
}

async function handleSubmit(record: OriginalRecord) {
  await runLocked(`submit_record_${record.id}`, async () => {
    try {
      await ElMessageBox.confirm('确认提交该原始记录？提交后不可修改。', '提示')
      await submitRecord(record.id)
      ElMessage.success('提交成功')
      fetchList()
    } catch { /* cancelled */ }
  })
}

// Review (复核) dialog
const reviewDialogVisible = ref(false)
const reviewTarget = ref<OriginalRecord | null>(null)
const reviewForm = reactive({ approved: true as boolean, comment: '' })

function openReviewDialog(record: OriginalRecord) {
  reviewTarget.value = record
  reviewForm.approved = true
  reviewForm.comment = ''
  reviewDialogVisible.value = true
}

async function handleReview() {
  if (!reviewTarget.value) return
  if (!reviewForm.approved && (reviewForm.comment || '').trim().length < 4) {
    ElMessage.warning('退回原因至少4个字符')
    return
  }
  await runLocked(`review_record_${reviewTarget.value.id}`, async () => {
    try {
      await reviewRecord(reviewTarget.value!.id, {
        approved: reviewForm.approved,
        comment: reviewForm.comment,
      })
      ElMessage.success(reviewForm.approved ? '复核通过' : '已退回')
      reviewDialogVisible.value = false
      fetchList()
    } catch {
      ElMessage.error('操作失败')
    }
  })
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 120px">
            <el-option
              v-for="s in statusOptions"
              :key="s.value"
              :label="s.label"
              :value="s.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="记录人">
          <el-input
            v-model="query.recorder_name"
            placeholder="记录人姓名"
            clearable
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <span>原始记录管理</span>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="record_no" label="记录编号" width="180" />
        <el-table-column prop="task_no" label="任务编号" width="180" />
        <el-table-column prop="template_name" label="模板名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="recorder_name" label="记录人" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType[row.status]" size="small">
              {{ statusMap[row.status] ?? row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="review_date" label="审核日期" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'draft'"
              v-permission="'testing:edit'"
              link
              type="primary"
              @click="goEdit(row)"
            >
              填写
            </el-button>
            <el-button
              v-else
              v-permission="'testing:view'"
              link
              type="primary"
              @click="goView(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="row.status === 'draft'"
              v-permission="'testing:edit'"
              link
              type="success"
              :loading="isLocked(`submit_record_${row.id}`)"
              @click="handleSubmit(row)"
            >
              提交审核
            </el-button>
            <el-button
              v-if="row.status === 'pending_review'"
              v-permission="'testing:approve'"
              link
              type="warning"
              :loading="isLocked(`review_record_${row.id}`)"
              @click="openReviewDialog(row)"
            >
              复核
            </el-button>
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

    <!-- Review Dialog -->
    <el-dialog v-model="reviewDialogVisible" title="原始记录复核" width="450px" destroy-on-close>
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="复核结果">
          <el-radio-group v-model="reviewForm.approved">
            <el-radio :value="true">通过</el-radio>
            <el-radio :value="false">退回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="复核意见">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="3"
            placeholder="请输入复核意见（退回时必填，至少4个字符）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button
          v-permission="'testing:approve'"
          type="primary"
          :loading="reviewTarget ? isLocked(`review_record_${reviewTarget.id}`) : false"
          @click="handleReview"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>
