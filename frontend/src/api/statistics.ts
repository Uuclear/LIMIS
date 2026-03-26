import request from '@/utils/request'

export function getDashboardData() { return request.get('/v1/statistics/dashboard/') }
export function getTestVolume(params?: any) { return request.get('/v1/statistics/test-volume/', { params }) }
export function getQualificationRate(params?: any) {
  return request.get('/v1/statistics/qualification-rate/', { params })
}
export function getStrengthCurve(params?: any) {
  return request.get('/v1/statistics/strength-curve/', { params })
}
export function getCycleAnalysis(params?: any) {
  return request.get('/v1/statistics/cycle-analysis/', { params })
}
export function getWorkload(params?: any) { return request.get('/v1/statistics/workload/', { params }) }
export function getEquipmentUsage(params?: any) {
  return request.get('/v1/statistics/equipment-usage/', { params })
}
