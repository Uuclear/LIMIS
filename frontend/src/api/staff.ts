import request from '@/utils/request'

// staff profile（人员档案）
export function getStaffList(params?: any) { return request.get('/v1/staff/profiles/', { params }) }
export function getStaff(id: number) { return request.get(`/v1/staff/profiles/${id}/`) }
export function createStaff(data: any) { return request.post('/v1/staff/profiles/', data) }
export function updateStaff(id: number, data: any) { return request.put(`/v1/staff/profiles/${id}/`, data) }

// certificates/trainings/authorizations/evaluations：后端是非嵌套路由，靠 query/filter 过滤 staff_id
export function getCertificates(staffId: number, params?: any) {
  return request.get('/v1/staff/certificates/', { params: { ...(params || {}), staff: staffId } })
}
export function createCertificate(staffId: number, data: any) {
  return request.post('/v1/staff/certificates/', { ...data, staff: staffId })
}

export function getAuthorizations(staffId: number, params?: any) {
  return request.get('/v1/staff/authorizations/', { params: { ...(params || {}), staff: staffId } })
}
export function createAuthorization(staffId: number, data: any) {
  return request.post('/v1/staff/authorizations/', { ...data, staff: staffId })
}

export function getTrainings(staffId: number, params?: any) {
  return request.get('/v1/staff/trainings/', { params: { ...(params || {}), staff: staffId } })
}
export function createTraining(staffId: number, data: any) {
  return request.post('/v1/staff/trainings/', { ...data, staff: staffId })
}

export function getEvaluations(staffId: number, params?: any) {
  return request.get('/v1/staff/evaluations/', { params: { ...(params || {}), staff: staffId } })
}
export function createEvaluation(staffId: number, data: any) {
  return request.post('/v1/staff/evaluations/', { ...data, staff: staffId })
}

export function getExpiringCerts(params?: any) {
  return request.get('/v1/staff/expiring-certs/', { params })
}

export function getAssignableTesters(parameterId?: number) {
  return request.get('/v1/staff/profiles/assignable-testers/', {
    params: parameterId ? { parameter_id: parameterId } : {},
  })
}
