import request from '@/utils/request'

export function getMonitoringPoints(params?: any) {
  return request.get('/v1/environment/points/', { params })
}
export function getRealtimeData(params?: any) {
  return request.get('/v1/environment/realtime/', { params })
}
export function getHistoryData(params?: any) {
  return request.get('/v1/environment/history/', { params })
}
export function getAlarms(params?: any) {
  return request.get('/v1/environment/alarms/', { params })
}
export function resolveAlarm(id: number, data?: any) {
  return request.post(`/v1/environment/alarms/${id}/resolve/`, data)
}
