<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadInstance } from 'element-plus'
import printJS from 'print-js'
import { Search, Refresh, Plus, Download, Printer, Upload } from '@element-plus/icons-vue'
import { getSampleList, exportSamples, getSampleLabel, downloadSampleImportTemplate, batchImportSamples } from '@/api/samples'
import { getCommissionList } from '@/api/commissions'
import { hasPermission } from '@/utils/permission'
import type { Sample } from '@/types/sample'

const router = useRouter()
const loading = ref(false)
const printLoading = ref(false)
const selectedRows = ref<Sample[]>([])
const tableData = ref<Sample[]>([])
const total = ref(0)

const query = reactive({
  page: 1, page_size: 20, keyword: '', status: '', date_range: [] as string[],
})

const canBatchImport = computed(
  () => hasPermission('sample:create') || hasPermission('sample:edit'),
)

const importDialogVisible = ref(false)
const importCommissionId = ref<number | null>(null)
const importFile = ref<File | null>(null)
const importSubmitting = ref(false)
const importUploadRef = ref<UploadInstance>()
const commissionOptions = ref<{ id: number; commission_no: string; project_name: string }[]>([])

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

async function handleDownloadTemplate() {
  const res: any = await downloadSampleImportTemplate()
  const url = window.URL.createObjectURL(new Blob([res]))
  const a = document.createElement('a')
  a.href = url
  a.download = '样品批量导入模板.xlsx'
  a.click()
  window.URL.revokeObjectURL(url)
}

async function openImportDialog() {
  importCommissionId.value = null
  importFile.value = null
  importUploadRef.value?.clearFiles()
  importDialogVisible.value = true
  try {
    const res: any = await getCommissionList({ page_size: 500, status: 'reviewed' })
    commissionOptions.value = res.results ?? res.list ?? []
  } catch {
    commissionOptions.value = []
  }
}

function onImportFileChange(uploadFile: UploadFile) {
  importFile.value = uploadFile.raw ?? null
}

async function submitBatchImport() {
  if (!importCommissionId.value) {
    ElMessage.warning('请选择委托单')
    return
  }
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的 Excel 文件')
    return
  }
  importSubmitting.value = true
  try {
    await batchImportSamples(importCommissionId.value, importFile.value)
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    fetchList()
  } catch (e: unknown) {
    const err = e as { response?: { data?: { message?: string; data?: { errors?: { row: number; message: string }[] } } } }
    const d = err.response?.data
    const msg = d?.message ?? '导入失败'
    const errs = d?.data?.errors
    if (Array.isArray(errs) && errs.length) {
      const preview = errs
        .slice(0, 5)
        .map((x) => (x.row ? `第${x.row}行: ${x.message}` : x.message))
        .join('；')
      ElMessage.error(`${msg}（${preview}${errs.length > 5 ? '…' : ''}）`)
    } else {
      ElMessage.error(msg)
    }
  } finally {
    importSubmitting.value = false
  }
}

function onSelectionChange(rows: Sample[]) {
  selectedRows.value = rows
}

function escapeHtml(s: string) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/"/g, '&quot;')
}

async function batchPrintLabels() {
  const rows = selectedRows.value
  if (!rows.length) {
    ElMessage.warning('请先勾选要打印的样品')
    return
  }
  if (rows.length > 30) {
    ElMessage.warning('一次最多打印 30 条')
    return
  }
  printLoading.value = true
  try {
    const blocks: string[] = []
    for (const row of rows) {
      const data: any = await getSampleLabel(row.id)
      blocks.push(
        `<div class="label-block" style="page-break-inside:avoid;border:1px solid #ddd;padding:12px;margin-bottom:12px;text-align:center;width:200px;display:inline-block;vertical-align:top;margin-right:12px;">
          <div style="font-weight:600;font-size:14px;">${escapeHtml(String(data.sample_no ?? ''))}</div>
          <div style="font-size:12px;color:#666;margin:4px 0;">${escapeHtml(String(data.name ?? ''))}</div>
          <img src="${data.qr_code}" width="160" height="160" alt="" />
        </div>`,
      )
    }
    const html = `<div style="font-family:sans-serif;">${blocks.join('')}</div>`
    printJS({
      printable: html,
      type: 'raw-html',
      scanStyles: false,
      style: '@page { margin: 12mm; } .label-block { box-sizing: border-box; }',
    })
  } finally {
    printLoading.value = false
  }
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
            <el-button
              v-permission="'sample:view'"
              :icon="Printer"
              :disabled="!selectedRows.length"
              :loading="printLoading"
              @click="batchPrintLabels"
            >批量打印标签</el-button>
            <el-button v-permission="'sample:view'" :icon="Download" @click="handleExport">导出</el-button>
            <template v-if="canBatchImport">
              <el-button :icon="Download" @click="handleDownloadTemplate">下载模板</el-button>
              <el-button type="primary" plain :icon="Upload" @click="openImportDialog">批量导入</el-button>
            </template>
            <el-button v-permission="'sample:create'" type="primary" :icon="Plus" @click="goRegister">样品登记</el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="48" align="center" />
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
            <el-button v-permission="'sample:view'" link type="primary" @click="goDetail(row)">查看</el-button>
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

    <el-dialog v-model="importDialogVisible" title="批量导入样品" width="520px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="委托单" required>
          <el-select
            v-model="importCommissionId"
            placeholder="请选择已评审的委托"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="c in commissionOptions"
              :key="c.id"
              :label="`${c.commission_no} - ${c.project_name}`"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Excel 文件" required>
          <el-upload
            ref="importUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="onImportFileChange"
            :on-exceed="() => ElMessage.warning('一次只能上传一个文件')"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">请先下载模板，按表头填写后上传（.xlsx）</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importSubmitting" @click="submitBatchImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>
