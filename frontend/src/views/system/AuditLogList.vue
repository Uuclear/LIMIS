<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getAuditLogs } from '@/api/system'

interface LogRow {
  id: number
  user: string
  method: string
  path: string
  status_code: number
  ip_address: string
  created_at: string
}

const loading = ref(false)
const tableData = ref<LogRow[]>([])
const total = ref(0)

const query = reactive({
  page: 1,
  page_size: 20,
  user: '',
  method: '',
  date_range: [] as string[],
})

const methodOptions = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

async function fetchList() {
  loading.value = true
  try {
    const params: any = { ...query }
    if (query.date_range?.length === 2) {
      params.start_date = query.date_range[0]
      params.end_date = query.date_range[1]
    }
    delete params.date_range
    const res: any = await getAuditLogs(params)
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
  Object.assign(query, { page: 1, user: '', method: '', date_range: [] })
  fetchList()
}

function methodTagType(method: string) {
  const map: Record<string, string> = {
    GET: 'info', POST: 'success', PUT: 'warning', PATCH: 'warning', DELETE: 'danger',
  }
  return map[method] ?? 'info'
}

function statusTagType(code: number) {
  if (code >= 200 && code < 300) return 'success'
  if (code >= 400 && code < 500) return 'warning'
  return 'danger'
}

onMounted(fetchList)
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="操作时间">
          <el-date-picker
            v-model="query.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item label="用户">
          <el-input v-model="query.user" placeholder="请输入" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="方法">
          <el-select v-model="query.method" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="m in methodOptions" :key="m" :label="m" :value="m" />
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
        <span>操作日志</span>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="created_at" label="操作时间" width="180" />
        <el-table-column prop="user" label="用户" width="120" />
        <el-table-column label="操作方法" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="methodTagType(row.method)" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="请求路径" min-width="260" show-overflow-tooltip />
        <el-table-column label="状态码" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status_code)" size="small">{{ row.status_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="150" />
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
