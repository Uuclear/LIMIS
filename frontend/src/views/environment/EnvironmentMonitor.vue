<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getMonitoringPoints, getLatestRecords, getAlarms, resolveAlarm } from '@/api/environment'

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const points = ref<any[]>([])
const realtimeData = ref<any[]>([])
const historyData = ref<any>({ times: [], temperatures: [], humidities: [] })
const alarmList = ref<any[]>([])
const selectedPoint = ref<number | null>(null)
let timer: ReturnType<typeof setInterval> | null = null

async function fetchPoints() {
  try {
    const res: any = await getMonitoringPoints()
    const list = res.results ?? res.list ?? res ?? []
    points.value = (list || []).map((p: any) => ({
      ...p,
      temp_range: p.temp_min != null && p.temp_max != null ? `${p.temp_min}~${p.temp_max}` : '',
      humid_range: p.humidity_min != null && p.humidity_max != null ? `${p.humidity_min}~${p.humidity_max}` : '',
    }))
    if (points.value.length && !selectedPoint.value) {
      selectedPoint.value = points.value[0].id
    }
  } catch { /* ignore */ }
}

async function fetchRealtime() {
  if (!points.value.length) return
  try {
    const list = await Promise.all(
      points.value.map(async (p: any) => {
        const recsRes: any = await getLatestRecords(p.id, { limit: 1 })
        const recs: any[] = Array.isArray(recsRes) ? recsRes : []
        const latest = recs.length ? recs[0] : null
        return {
          point_id: p.id,
          temperature: latest?.temperature ?? null,
          humidity: latest?.humidity ?? null,
          recorded_at: latest?.recorded_at ?? null,
          is_alarm: latest?.is_alarm ?? false,
        }
      }),
    )
    realtimeData.value = list
  } catch { /* ignore */ }
}

async function fetchHistory() {
  if (!selectedPoint.value) return
  try {
    const recsRes: any = await getLatestRecords(selectedPoint.value, { limit: 24 })
    const recs: any[] = Array.isArray(recsRes) ? recsRes : []
    historyData.value = {
      times: (recs ?? []).map((r) => r.recorded_at ?? ''),
      temperatures: (recs ?? []).map((r) => r.temperature ?? null),
      humidities: (recs ?? []).map((r) => r.humidity ?? null),
    }
  } catch { /* ignore */ }
}

async function fetchAlarms() {
  try {
    const res: any = await getAlarms({ is_resolved: false })
    const list = res.results ?? res.list ?? res ?? []
    alarmList.value = (list || []).map((a: any) => ({
      ...a,
      type: a.alarm_type_display || a.alarm_type || '',
      message: a.alarm_type_display ? `${a.alarm_type_display}告警` : '告警',
      value: a.alarm_value ?? '',
      threshold: a.threshold ?? '',
      created_at: a.alarm_time ?? a.created_at ?? '',
    }))
  } catch { /* ignore */ }
}

async function handleResolve(alarm: any) {
  await resolveAlarm(alarm.id)
  ElMessage.success('已处理')
  fetchAlarms()
}

function pointStatus(data: any) {
  if (!data) return 'info'
  if (data.is_alarm) return 'danger'
  return 'success'
}

function pointStatusText(data: any) {
  if (!data) return '离线'
  if (data.is_alarm) return '异常'
  return '正常'
}

function getPointRealtime(pointId: number) {
  return realtimeData.value.find((d: any) => d.point_id === pointId)
}

const chartOption = computed(() => {
  const times = historyData.value.times ?? []
  const temps = historyData.value.temperatures ?? []
  const humids = historyData.value.humidities ?? []
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['温度(°C)', '湿度(%RH)'] },
    grid: { left: 50, right: 30, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: times, boundaryGap: false },
    yAxis: [
      { type: 'value', name: '温度(°C)', position: 'left' },
      { type: 'value', name: '湿度(%RH)', position: 'right' },
    ],
    series: [
      { name: '温度(°C)', type: 'line', data: temps, smooth: true, yAxisIndex: 0 },
      { name: '湿度(%RH)', type: 'line', data: humids, smooth: true, yAxisIndex: 1 },
    ],
  }
})

function onPointChange() {
  fetchHistory()
}

function startPolling() {
  timer = setInterval(() => {
    fetchRealtime()
  }, 30000)
}

onMounted(async () => {
  await fetchPoints()
  await Promise.all([fetchRealtime(), fetchHistory(), fetchAlarms()])
  startPolling()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="page-container">
    <el-row :gutter="16">
      <el-col v-for="point in points" :key="point.id" :xs="12" :sm="8" :md="6">
        <el-card shadow="hover" style="margin-bottom: 16px" :body-style="{ padding: '16px' }">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px">
            <span style="font-weight: 600">{{ point.name }}</span>
            <el-tag :type="pointStatus(getPointRealtime(point.id))" size="small">
              {{ pointStatusText(getPointRealtime(point.id)) }}
            </el-tag>
          </div>
          <div style="display: flex; gap: 20px">
            <div>
              <div style="font-size: 12px; color: #909399">温度</div>
              <div style="font-size: 24px; font-weight: 700; color: #409eff">
                {{ getPointRealtime(point.id)?.temperature ?? '--' }}
                <span style="font-size: 14px">°C</span>
              </div>
            </div>
            <div>
              <div style="font-size: 12px; color: #909399">湿度</div>
              <div style="font-size: 24px; font-weight: 700; color: #67c23a">
                {{ getPointRealtime(point.id)?.humidity ?? '--' }}
                <span style="font-size: 14px">%RH</span>
              </div>
            </div>
          </div>
          <div v-if="point.temp_range || point.humid_range" style="font-size: 12px; color: #909399; margin-top: 8px">
            范围: {{ point.temp_range }} / {{ point.humid_range }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" style="margin-bottom: 16px">
      <template #header>
        <div class="card-header">
          <span>历史趋势（最近24小时）</span>
          <el-select v-model="selectedPoint" placeholder="选择监测点" style="width: 200px" @change="onPointChange">
            <el-option v-for="p in points" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </div>
      </template>
      <v-chart :option="chartOption" style="height: 320px; width: 100%" autoresize />
    </el-card>

    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>告警列表</span>
          <el-badge :value="alarmList.length" :hidden="!alarmList.length" type="danger">
            <el-tag type="danger" size="small">未处理</el-tag>
          </el-badge>
        </div>
      </template>
      <el-table :data="alarmList" stripe border>
        <el-table-column prop="point_name" label="监测点" width="140" />
        <el-table-column prop="type" label="告警类型" width="120" />
        <el-table-column prop="message" label="告警信息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="value" label="当前值" width="100" />
        <el-table-column prop="threshold" label="阈值" width="100" />
        <el-table-column prop="created_at" label="告警时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'environment:create'" link type="primary" @click="handleResolve(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
