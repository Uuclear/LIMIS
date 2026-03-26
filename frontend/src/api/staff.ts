import request from '@/utils/request'

export function getStaffList(params?: any) { return request.get('/v1/staff/', { params }) }
export function getStaff(id: number) { return request.get(`/v1/staff/${id}/`) }
export function createStaff(data: any) { return request.post('/v1/staff/', data) }
export function updateStaff(id: number, data: any) { return request.put(`/v1/staff/${id}/`, data) }

export function getCertificates(staffId: number, params?: any) {
  return request.get(`/v1/staff/${staffId}/certificates/`, { params })
}
export function createCertificate(staffId: number, data: any) {
  return request.post(`/v1/staff/${staffId}/certificates/`, data)
}

export function getAuthorizations(staffId: number, params?: any) {
  return request.get(`/v1/staff/${staffId}/authorizations/`, { params })
}
export function createAuthorization(staffId: number, data: any) {
  return request.post(`/v1/staff/${staffId}/authorizations/`, data)
}

export function getTrainings(staffId: number, params?: any) {
  return request.get(`/v1/staff/${staffId}/trainings/`, { params })
}
export function createTraining(staffId: number, data: any) {
  return request.post(`/v1/staff/${staffId}/trainings/`, data)
}

export function getEvaluations(staffId: number, params?: any) {
  return request.get(`/v1/staff/${staffId}/evaluations/`, { params })
}
export function createEvaluation(staffId: number, data: any) {
  return request.post(`/v1/staff/${staffId}/evaluations/`, data)
}

export function getExpiringCerts(params?: any) {
  return request.get('/v1/staff/expiring-certs/', { params })
}
