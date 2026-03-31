import request from '@/utils/request'

export function getEquipmentList(params?: any) { return request.get('/v1/equipment/', { params }) }
export function getEquipment(id: number) { return request.get(`/v1/equipment/${id}/`) }
export function createEquipment(data: any) { return request.post('/v1/equipment/', data) }
export function updateEquipment(id: number, data: any) { return request.put(`/v1/equipment/${id}/`, data) }
export function deleteEquipment(id: number) { return request.delete(`/v1/equipment/${id}/`) }

export function getCalibrations(equipmentId: number, params?: any) {
  return request.get(`/v1/equipment/${equipmentId}/calibrations/`, { params })
}
export function createCalibration(equipmentId: number, data: any) {
  return request.post(`/v1/equipment/${equipmentId}/calibrations/`, data)
}

export function getPeriodChecks(equipmentId: number, params?: any) {
  return request.get(`/v1/equipment/${equipmentId}/period-checks/`, { params })
}
export function createPeriodCheck(equipmentId: number, data: any) {
  return request.post(`/v1/equipment/${equipmentId}/period-checks/`, data)
}

export function getMaintenances(equipmentId: number, params?: any) {
  return request.get(`/v1/equipment/${equipmentId}/maintenances/`, { params })
}
export function createMaintenance(equipmentId: number, data: any) {
  return request.post(`/v1/equipment/${equipmentId}/maintenances/`, data)
}

export function getExpiringEquipment(params?: any) {
  return request.get('/v1/equipment/expiring/', { params })
}
export function getTraceability(id: number) {
  return request.get(`/v1/equipment/${id}/traceability/`)
}

export function getUsageLogs(equipmentId: number, params?: any) {
  return request.get(`/v1/equipment/${equipmentId}/usage-logs/`, { params })
}
