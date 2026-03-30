import request from '@/utils/request'

// 后端路由：points / records / alarms
export function getMonitoringPoints(params?: any) {
  return request.get('/v1/environment/points/', { params })
}

// MonitoringPointViewSet.latest_records：GET /v1/environment/points/{id}/latest-records/?limit=50
export function getLatestRecords(pointId: number, params?: any) {
  return request.get(`/v1/environment/points/${pointId}/latest-records/`, { params })
}

export function getAlarms(params?: any) {
  return request.get('/v1/environment/alarms/', { params })
}

export function resolveAlarm(id: number, data?: any) {
  return request.post(`/v1/environment/alarms/${id}/resolve/`, data)
}
