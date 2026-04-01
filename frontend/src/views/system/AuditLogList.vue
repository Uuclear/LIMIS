<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Search, Refresh, View, Download } from '@element-plus/icons-vue'
import { getAuditLogs, exportAuditLogs } from '@/api/system'
import { ElMessage } from 'element-plus'

interface LogRow {
  id: number
  user: { id: number; username: string; first_name: string; last_name: string } | string
  method: string
  path: string
  query_string: string
  body: string
  status_code: number
  ip_address: string
  user_agent: string
  response_time: number
  timestamp: string
  created_at: string
}

const loading = ref(false)
const tableData = ref<LogRow[]>([])
const total = ref(0)
const detailVisible = ref(false)
const currentLog = ref<LogRow | null>(null)

const query = reactive({
  page: 1,
  page_size: 20,
  user: '',
  method: '',
  path: '',
  status_code: '',
  date_range: [] as string[],
})

const methodOptions = [
  { value: 'GET', label: 'GET', type: 'info' },
  { value: 'POST', label: 'POST', type: 'success' },
  { value: 'PUT', label: 'PUT', type: 'warning' },
  { value: 'PATCH', label: 'PATCH', type: 'warning' },
  { value: 'DELETE', label: 'DELETE', type: 'danger' },
]

const statusOptions = [
  { value: '2xx', label: '2xx 成功' },
  { value: '4xx', label: '4xx 客户端错误' },
  { value: '5xx', label: '5xx 服务器错误' },
]

// 操作类型映射
const operationMap: Record<string, string> = {
  'POST /api/v1/commissions': '创建委托',
  'PUT /api/v1/commissions': '更新委托',
  'DELETE /api/v1/commissions': '删除委托',
  'POST /api/v1/samples': '登记样品',
  'POST /api/v1/reports': '创建报告',
  'POST /api/v1/reports/.*audit': '审核报告',
  'POST /api/v1/reports/.*approve': '批准报告',
  'POST /api/v1/reports/.*issue': '发放报告',
}

// 获取操作类型
function getOperationType(row: LogRow): string {
  const key = `${row.method} ${row.path}`
  for (const [pattern, label] of Object.entries(operationMap)) {
    if (key.match(new RegExp(pattern))) {
      return label
    }
  }
  return row.method === 'GET' ? '查询' : '操作'
}

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
  } catch (error) {
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, { page: 1, user: '', method: '', path: '', status_code: '', date_range: [] })
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

// 查看详情
function handleViewDetail(row: LogRow) {
  currentLog.value = row
  detailVisible.value = true
}

// 格式化用户显示
function formatUser(user: LogRow['user']): string {
  if (typeof user === 'string') return user
  if (user.first_name || user.last_name) {
    return `${user.first_name || ''}${user.last_name || ''} (${user.username})`
  }
  return user.username
}

// 导出日志
async function handleExport() {
  try {
    ElMessage.info('正在导出...')
    const params: any = { ...query }
    if (query.date_range?.length === 2) {
      params.start_date = query.date_range[0]
      params.end_date = query.date_range[1]
    }
    delete params.date_range
    delete params.page
    delete params.page_size
    
    const res: any = await exportAuditLogs(params)
    if (res instanceof Blob) {
      const url = window.URL.createObjectURL(res)
      const a = document.createElement('a')
      a.href = url
      a.download = `审计日志_${new Date().toISOString().slice(0, 10)}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    }
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 格式化JSON显示
function formatJson(str: string): string {
  try {
    return JSON.stringify(JSON.parse(str), null, 2)
  } catch {
    return str
  }
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
          <el-input v-model="query.user" placeholder="用户名/姓名" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="query.method" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="m in methodOptions" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="请求路径">
          <el-input v-model="query.path" placeholder="路径关键字" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="状态码">
          <el-select v-model="query.status_code" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Download" @click="handleExport">导出</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>操作日志</span>
          <span style="color: #909399; font-size: 12px;">共 {{ total }} 条记录</span>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="timestamp" label="操作时间" width="180">
          <template #default="{ row }">
            {{ row.timestamp || row.created_at }}
          </template>
        </el-table-column>
        <el-table-column label="操作用户" width="150">
          <template #default="{ row }">
            {{ formatUser(row.user) }}
          </template>
        </el-table-column>
        <el-table-column label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="methodTagType(row.method)">
              {{ getOperationType(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="请求方法" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="methodTagType(row.method)" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="请求路径" min-width="240" show-overflow-tooltip />
        <el-table-column label="状态码" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status_code)" size="small">{{ row.status_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column label="响应时间" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.response_time">{{ row.response_time }}ms</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="handleViewDetail(row)">详情</el-button>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="日志详情" width="700px" destroy-on-close>
      <el-descriptions v-if="currentLog" :column="2" border>
        <el-descriptions-item label="操作时间" :span="2">
          {{ currentLog.timestamp || currentLog.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="操作用户">
          {{ formatUser(currentLog.user) }}
        </el-descriptions-item>
        <el-descriptions-item label="IP地址">
          {{ currentLog.ip_address }}
        </el-descriptions-item>
        <el-descriptions-item label="请求方法">
          <el-tag :type="methodTagType(currentLog.method)" size="small">{{ currentLog.method }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态码">
          <el-tag :type="statusTagType(currentLog.status_code)" size="small">{{ currentLog.status_code }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="请求路径" :span="2">
          {{ currentLog.path }}
        </el-descriptions-item>
        <el-descriptions-item label="查询参数" :span="2">
          <pre style="margin: 0; white-space: pre-wrap; word-break: break-all; max-height: 100px; overflow: auto;">{{ currentLog.query_string || '-' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="请求体" :span="2">
          <pre style="margin: 0; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow: auto;">{{ currentLog.body ? formatJson(currentLog.body) : '-' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="用户代理" :span="2">
          {{ currentLog.user_agent || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="响应时间" v-if="currentLog.response_time">
          {{ currentLog.response_time }}ms
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-container {
  padding: 20px;
}
</style>
