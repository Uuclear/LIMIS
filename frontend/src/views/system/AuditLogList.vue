<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import { getAuditLogs, exportAuditLogs } from '@/api/system'
import { hasPermission } from '@/utils/permission'

interface LogRow {
  id: number
  /** 后端 FK，一般为用户 id */
  user?: number | null
  username: string
  method: string
  path: string
  status_code: number | null
  ip_address: string | null
  /** 后端字段名为 timestamp */
  timestamp: string
  idempotency_key?: string
  is_idempotent_replay?: boolean
}

const loading = ref(false)
const tableData = ref<LogRow[]>([])
const total = ref(0)

const query = reactive({
  page: 1,
  page_size: 20,
  /** 对应后端 AuditLogFilter.username（icontains） */
  username: '',
  method: '',
  path: '',
  /** 状态码，空表示不过滤 */
  status_code: '' as string | number,
  date_range: [] as string[],
  idempotency_key: '',
  /** 全部 / 是 / 否 — 对应后端 is_idempotent_replay */
  is_idempotent_replay: '' as '' | 'yes' | 'no',
})

const methodOptions = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

/** 与后端 AuditLogFilter 对齐；`withPagination` 为 true 时附带 page / page_size */
function buildAuditLogParams(withPagination: boolean): Record<string, unknown> {
  const params: Record<string, unknown> = { ...query }
  if (!withPagination) {
    delete params.page
    delete params.page_size
  }
  if (query.date_range?.length === 2) {
    params.start_date = query.date_range[0]
    params.end_date = query.date_range[1]
  }
  delete params.date_range
  const u = String(params.username ?? '').trim()
  if (u) params.username = u
  else delete params.username
  const p = String(params.path ?? '').trim()
  if (p) params.path = p
  else delete params.path
  const sc = params.status_code
  if (sc !== '' && sc !== null && sc !== undefined) {
    const n = typeof sc === 'number' ? sc : parseInt(String(sc).trim(), 10)
    if (!Number.isFinite(n)) delete params.status_code
    else params.status_code = n
  } else {
    delete params.status_code
  }
  const ik = String(params.idempotency_key ?? '').trim()
  if (ik) params.idempotency_key = ik
  else delete params.idempotency_key
  if (params.is_idempotent_replay === 'yes') params.is_idempotent_replay = true
  else if (params.is_idempotent_replay === 'no') params.is_idempotent_replay = false
  else delete params.is_idempotent_replay
  if (!String(params.method ?? '').trim()) delete params.method
  return params
}

async function fetchList() {
  loading.value = true
  try {
    const params = buildAuditLogParams(true)
    const res: any = await getAuditLogs(params)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

const exporting = ref(false)

async function handleExport() {
  exporting.value = true
  try {
    const params = buildAuditLogParams(false)
    const res = await exportAuditLogs(params)
    const blob = new Blob([res as unknown as BlobPart], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const stamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
    a.download = `audit_logs_${stamp}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  } finally {
    exporting.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, {
    page: 1,
    username: '',
    method: '',
    path: '',
    status_code: '',
    date_range: [],
    idempotency_key: '',
    is_idempotent_replay: '',
  })
  fetchList()
}

function methodTagType(method: string) {
  const map: Record<string, string> = {
    GET: 'info', POST: 'success', PUT: 'warning', PATCH: 'warning', DELETE: 'danger',
  }
  return map[method] ?? 'info'
}

function statusTagType(code: number | null | undefined) {
  if (code == null || Number.isNaN(Number(code))) return 'info'
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
          <el-input v-model="query.username" placeholder="用户名（模糊）" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="方法">
          <el-select v-model="query.method" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="m in methodOptions" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="路径">
          <el-input v-model="query.path" placeholder="路径（模糊）" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="状态码">
          <el-input
            v-model="query.status_code"
            placeholder="如 200"
            clearable
            style="width: 100px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="幂等键">
          <el-input
            v-model="query.idempotency_key"
            placeholder="支持模糊匹配"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="是否重放">
          <el-select v-model="query.is_idempotent_replay" placeholder="全部" clearable style="width: 110px">
            <el-option label="全部" value="" />
            <el-option label="是" value="yes" />
            <el-option label="否" value="no" />
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
        <div class="audit-log-card-header">
          <span>操作日志</span>
          <el-button
            v-if="hasPermission('system:export')"
            type="primary"
            plain
            :icon="Download"
            :loading="exporting"
            @click="handleExport"
          >
            导出 CSV
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="timestamp" label="操作时间" width="180" />
        <el-table-column prop="username" label="用户" width="120" show-overflow-tooltip />
        <el-table-column label="操作方法" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="methodTagType(row.method)" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="请求路径" min-width="260" show-overflow-tooltip />
        <el-table-column prop="idempotency_key" label="幂等键" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ row.idempotency_key || '—' }}</template>
        </el-table-column>
        <el-table-column label="是否重放" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_idempotent_replay ? 'warning' : 'info'" size="small">
              {{ row.is_idempotent_replay ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
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

<style scoped>
.audit-log-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}
</style>
