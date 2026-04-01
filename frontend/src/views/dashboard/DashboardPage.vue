<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Document, List, Notebook, WarningFilled,
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import {
  getDashboardData,
  getTestVolume,
  getQualificationRate,
  getStrengthCurve,
  getCycleAnalysis,
  getWorkload,
  getEquipmentUsage,
  getTaskByProject,
  getTaskByMethod,
  getFlowKpis,
  exportOperationalReporting,
} from '@/api/statistics'

use([
  BarChart, PieChart, LineChart,
  GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer,
])

const router = useRouter()

interface StatCard {
  title: string
  value: number
  icon: typeof Document
  color: string
  bg: string
}

const stats = ref<StatCard[]>([
  { title: '本月委托', value: 0, icon: Document, color: '#2563eb', bg: '#eff6ff' },
  { title: '待分配任务', value: 0, icon: List, color: '#f59e0b', bg: '#fffbeb' },
  { title: '本月报告', value: 0, icon: Notebook, color: '#10b981', bg: '#ecfdf5' },
  { title: '设备预警', value: 0, icon: WarningFilled, color: '#ef4444', bg: '#fef2f2' },
])

const volumeData = ref<any>({})
const qualData = ref<any[]>([])
const kpi = ref({
  avg_cycle_days: 0,
  workload_top_tester: '',
  workload_top_total: 0,
  equipment_usage_rate: 0,
  task_return_rate: 0,
  pending_audit: 0,
  pending_approve: 0,
})

const recentTasks = ref<any[]>([])
const strengthRows = ref<{ age_days: number; avg_strength: number }[]>([])
const projectDim = ref<{ label: string; count: number }[]>([])
const methodDim = ref<{ label: string; count: number }[]>([])

async function fetchDashboard() {
  try {
    const res: any = await getDashboardData()
    stats.value[0].value = res?.month_commissions ?? res?.today_commissions ?? 0
    stats.value[1].value = res?.pending_tasks ?? 0
    stats.value[2].value = res?.month_reports ?? 0
    stats.value[3].value = res?.equipment_warnings ?? 0
    recentTasks.value = res?.recent_tasks ?? []
  } catch { /* ignore */ }
}

async function fetchVolume() {
  try {
    const res: any = await getTestVolume()
    volumeData.value = res ?? {}
  } catch { /* ignore */ }
}

async function fetchQualRate() {
  try {
    const res: any = await getQualificationRate()
    const raw = res?.items ?? res ?? []
    qualData.value = (Array.isArray(raw) ? raw : []).map((item: any) => ({
      name: item.category ?? item.name ?? item.label ?? '—',
      value: item.qualified ?? item.value ?? item.count ?? 0,
    }))
  } catch { /* ignore */ }
}

async function fetchDimStats() {
  try {
    const [p, m]: any[] = await Promise.all([
      getTaskByProject(),
      getTaskByMethod(),
    ])
    projectDim.value = Array.isArray(p) ? p : []
    methodDim.value = Array.isArray(m) ? m : []
  } catch {
    projectDim.value = []
    methodDim.value = []
  }
}

async function fetchStrength() {
  try {
    const res: any = await getStrengthCurve()
    const raw = Array.isArray(res) ? res : []
    strengthRows.value = raw.map((r: any) => ({
      age_days: Number(r.age_days ?? 0),
      avg_strength: Number(r.avg_strength ?? 0),
    }))
  } catch {
    strengthRows.value = []
  }
}

async function fetchKpi() {
  try {
    const [cycleRes, workloadRes, equipmentRes, flowKpiRes]: any[] = await Promise.all([
      getCycleAnalysis(),
      getWorkload(),
      getEquipmentUsage(),
      getFlowKpis(),
    ])
    const cycle = cycleRes ?? {}
    const workload = workloadRes ?? []
    const equipment = equipmentRes ?? {}
    const top = workload[0] ?? {}
    const totalEq = Number(equipment.total_equipment ?? 0)
    const usedEq = Number(equipment.used_equipment ?? 0)
    kpi.value = {
      avg_cycle_days: Number(cycle.avg_days ?? 0),
      workload_top_tester: top.tester_name ?? '-',
      workload_top_total: Number(top.total ?? 0),
      equipment_usage_rate: totalEq > 0 ? Math.round((usedEq / totalEq) * 1000) / 10 : 0,
      task_return_rate: Number(flowKpiRes?.task_return_rate ?? 0),
      pending_audit: Number(flowKpiRes?.pending_audit ?? 0),
      pending_approve: Number(flowKpiRes?.pending_approve ?? 0),
    }
  } catch { /* ignore */ }
}

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: volumeData.value.dates ?? [],
  },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: volumeData.value.values ?? [],
    itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] },
  }],
}))

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '65%'],
    center: ['50%', '45%'],
    data: qualData.value.map((item: any) => ({
      name: item.name ?? item.label,
      value: item.value ?? item.count,
    })),
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.2)' } },
  }],
}))

const projectDimBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 44, right: 16, top: 28, bottom: 72 },
  xAxis: {
    type: 'category',
    data: projectDim.value.map((r) => r.label),
    axisLabel: { rotate: 32, interval: 0, fontSize: 11 },
  },
  yAxis: { type: 'value', name: '任务数' },
  series: [{
    type: 'bar',
    data: projectDim.value.map((r) => r.count),
    itemStyle: { color: '#64748b', borderRadius: [4, 4, 0, 0] },
  }],
}))

const methodDimBarOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 44, right: 16, top: 28, bottom: 72 },
  xAxis: {
    type: 'category',
    data: methodDim.value.map((r) => r.label),
    axisLabel: { rotate: 32, interval: 0, fontSize: 11 },
  },
  yAxis: { type: 'value', name: '任务数' },
  series: [{
    type: 'bar',
    data: methodDim.value.map((r) => r.count),
    itemStyle: { color: '#d97706', borderRadius: [4, 4, 0, 0] },
  }],
}))

const strengthLineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    name: '龄期(天)',
    data: strengthRows.value.map((r) => String(r.age_days)),
  },
  yAxis: { type: 'value', name: '强度' },
  series: [{
    type: 'line',
    smooth: true,
    data: strengthRows.value.map((r) => r.avg_strength),
    itemStyle: { color: '#67c23a' },
    areaStyle: { color: 'rgba(103, 194, 58, 0.12)' },
  }],
}))

const taskStatusMap: Record<string, string> = {
  unassigned: '待分配',
  in_progress: '检测中',
  completed: '已完成',
  abnormal: '异常',
}

function statusType(status: string) {
  const map: Record<string, string> = {
    unassigned: 'info',
    in_progress: 'primary',
    completed: 'success',
    abnormal: 'danger',
  }
  return map[status] || 'info'
}

function taskStatusLabel(status: string) {
  return taskStatusMap[status] ?? status
}

onMounted(() => {
  fetchDashboard()
  fetchVolume()
  fetchQualRate()
  fetchDimStats()
  fetchStrength()
  fetchKpi()
})

async function handleExportOperationalReporting() {
  const res: any = await exportOperationalReporting()
  const blob = new Blob([res], { type: 'text/csv;charset=utf-8;' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'operational_reporting.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="dashboard">
    <div style="display:flex;justify-content:flex-end;margin-bottom:12px;">
      <el-button type="primary" plain @click="handleExportOperationalReporting">导出运营报表</el-button>
    </div>
    <el-row :gutter="20" class="stat-row">
      <el-col v-for="item in stats" :key="item.title" :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-card-body">
            <div class="stat-info">
              <div class="stat-title">{{ item.title }}</div>
              <div class="stat-value">{{ item.value }}</div>
            </div>
            <div class="stat-icon" :style="{ background: item.bg }">
              <el-icon :size="28" :color="item.color">
                <component :is="item.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header"><span>检测量趋势</span></div>
          </template>
          <v-chart :option="barOption" style="height: 280px; width: 100%" autoresize />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header"><span>合格率分布</span></div>
          </template>
          <v-chart :option="pieOption" style="height: 280px; width: 100%" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header"><span>强度发展曲线（按龄期均值）</span></div>
          </template>
          <v-chart :option="strengthLineOption" style="height: 260px; width: 100%" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>各项目任务数</span>
              <span class="chart-sub">近30天</span>
            </div>
          </template>
          <v-chart :option="projectDimBarOption" style="height: 280px; width: 100%" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>各检测方法任务数</span>
              <span class="chart-sub">近30天</span>
            </div>
          </template>
          <v-chart :option="methodDimBarOption" style="height: 280px; width: 100%" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><div class="card-header"><span>平均流转周期</span></div></template>
          <div class="kpi-value">{{ kpi.avg_cycle_days }} 天</div>
          <div class="kpi-sub">委托到批准的平均耗时；待审核 {{ kpi.pending_audit }} / 待批准 {{ kpi.pending_approve }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><div class="card-header"><span>最高工作量人员</span></div></template>
          <div class="kpi-value">{{ kpi.workload_top_tester || '-' }}</div>
          <div class="kpi-sub">近30天任务数：{{ kpi.workload_top_total }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><div class="card-header"><span>设备利用率与退回率</span></div></template>
          <div class="kpi-value">{{ kpi.equipment_usage_rate }}%</div>
          <div class="kpi-sub">近30天设备利用率；任务退回率 {{ kpi.task_return_rate }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="task-card">
      <template #header>
        <div class="card-header">
          <span>最近检测任务</span>
          <el-button type="primary" text @click="router.push('/testing/tasks')">查看全部</el-button>
        </div>
      </template>
      <el-table :data="recentTasks" stripe>
        <el-table-column prop="task_no" label="任务编号" width="200" />
        <el-table-column prop="sample_name" label="样品" min-width="160" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ taskStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tester" label="检测人员" width="120" />
        <el-table-column label="计划日期" width="120">
          <template #default="{ row }">{{ row.planned_date ?? '—' }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 10px;
}

.stat-card-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-title {
  font-size: 14px;
  color: var(--lims-text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--lims-text-primary);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-row {
  margin-bottom: 20px;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.kpi-sub {
  margin-top: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.task-card {
  border-radius: 10px;
}

.chart-sub {
  font-size: 12px;
  font-weight: normal;
  color: var(--el-text-color-secondary);
}
</style>
