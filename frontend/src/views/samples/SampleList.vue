<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Refresh, Plus, Download } from '@element-plus/icons-vue'
import { getSampleList, exportSamples } from '@/api/samples'
import type { Sample } from '@/types/sample'

const router = useRouter()
const loading = ref(false)
const tableData = ref<Sample[]>([])
const total = ref(0)

const query = reactive({
  page: 1, page_size: 20, keyword: '', status: '', date_range: [] as string[],
})

const statusOptions = [
  { label: '待检', value: 'pending' },
  { label: '检测中', value: 'testing' },
  { label: '已检', value: 'tested' },
  { label: '留样', value: 'retained' },
  { label: '已处置', value: 'disposed' },
]

async function fetchList() {
  loading.value = true
  try {
    const params: any = {
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
      status: query.status || undefined,
    }
    if (query.date_range?.length === 2) {
      params.sampling_date_start = query.date_range[0]
      params.sampling_date_end = query.date_range[1]
    }
    const res: any = await getSampleList(params)
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
  Object.assign(query, { page: 1, keyword: '', status: '', date_range: [] })
  fetchList()
}

function goDetail(row: Sample) {
  router.push(`/sample/${row.id}`)
}

function goRegister() {
  router.push('/sample/register')
}

async function handleExport() {
  const res: any = await exportSamples(query)
  const url = window.URL.createObjectURL(new Blob([res]))
  const a = document.createElement('a')
  a.href = url
  a.download = '样品列表.xlsx'
  a.click()
  window.URL.revokeObjectURL(url)
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    pending: 'info', testing: 'warning', tested: 'success', retained: 'warning', disposed: 'danger',
  }
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
          <el-input v-model="query.keyword" placeholder="样品编号/名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="取样日期">
          <el-date-picker
            v-model="query.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD"
            style="width: 260px"
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
        <div class="card-header">
          <span>样品管理</span>
          <div>
            <el-button :icon="Download" @click="handleExport">导出</el-button>
            <el-button type="primary" :icon="Plus" @click="goRegister">样品登记</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="sample_no" label="样品编号" width="180" />
        <el-table-column prop="name" label="样品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格型号" width="140" show-overflow-tooltip />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sampling_date" label="取样日期" width="120" />
        <el-table-column prop="commission_no" label="委托编号" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">查看</el-button>
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
  </div>
</template>
