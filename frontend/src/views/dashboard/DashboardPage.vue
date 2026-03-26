<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Document, List, Notebook, WarningFilled,
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getDashboardData, getTestVolume, getQualificationRate } from '@/api/statistics'

use([BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])

interface StatCard {
  title: string
  value: number
  icon: typeof Document
  color: string
  bg: string
}

const stats = ref<StatCard[]>([
  { title: '今日委托', value: 0, icon: Document, color: '#2563eb', bg: '#eff6ff' },
  { title: '待检任务', value: 0, icon: List, color: '#f59e0b', bg: '#fffbeb' },
  { title: '本月报告', value: 0, icon: Notebook, color: '#10b981', bg: '#ecfdf5' },
  { title: '设备预警', value: 0, icon: WarningFilled, color: '#ef4444', bg: '#fef2f2' },
])

const volumeData = ref<any>({})
const qualData = ref<any[]>([])

const recentTasks = ref<any[]>([])

async function fetchDashboard() {
  try {
    const res: any = await getDashboardData()
    stats.value[0].value = res?.today_commissions ?? 0
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
    qualData.value = res?.items ?? res ?? []
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

function statusType(status: string) {
  const map: Record<string, string> = {
    '检测中': 'primary', '待检测': 'warning', '已完成': 'success',
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchDashboard()
  fetchVolume()
  fetchQualRate()
})
</script>

<template>
  <div class="dashboard">
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

    <el-card shadow="hover" class="task-card">
      <template #header>
        <div class="card-header">
          <span>最近检测任务</span>
          <el-button type="primary" text>查看全部</el-button>
        </div>
      </template>
      <el-table :data="recentTasks" stripe>
        <el-table-column prop="id" label="任务编号" width="160" />
        <el-table-column prop="sample" label="样品名称" />
        <el-table-column prop="type" label="检测类型" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="检测人员" width="120" />
        <el-table-column prop="date" label="日期" width="120" />
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

.task-card {
  border-radius: 10px;
}
</style>
