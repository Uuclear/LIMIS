import request from '@/utils/request'

export function getProjectList(params?: any) { return request.get('/v1/projects/', { params }) }
export function getProject(id: number) { return request.get(`/v1/projects/${id}/`) }
export function createProject(data: any) { return request.post('/v1/projects/', data) }
export function updateProject(id: number, data: any) { return request.put(`/v1/projects/${id}/`, data) }
export function deleteProject(id: number) { return request.delete(`/v1/projects/${id}/`) }

export function getOrganizations(projectId: number, params?: any) {
  return request.get(`/v1/projects/${projectId}/organizations/`, { params })
}
export function createOrganization(projectId: number, data: any) {
  return request.post(`/v1/projects/${projectId}/organizations/`, data)
}
export function updateOrganization(projectId: number, id: number, data: any) {
  return request.put(`/v1/projects/${projectId}/organizations/${id}/`, data)
}
export function deleteOrganization(projectId: number, id: number) {
  return request.delete(`/v1/projects/${projectId}/organizations/${id}/`)
}

export function getSubProjects(projectId: number, params?: any) {
  return request.get(`/v1/projects/${projectId}/sub-projects/`, { params })
}
export function createSubProject(projectId: number, data: any) {
  return request.post(`/v1/projects/${projectId}/sub-projects/`, data)
}
export function updateSubProject(projectId: number, id: number, data: any) {
  return request.put(`/v1/projects/${projectId}/sub-projects/${id}/`, data)
}
export function deleteSubProject(projectId: number, id: number) {
  return request.delete(`/v1/projects/${projectId}/sub-projects/${id}/`)
}

export function getContracts(projectId: number, params?: any) {
  return request.get(`/v1/projects/${projectId}/contracts/`, { params })
}
export function createContract(projectId: number, data: any) {
  return request.post(`/v1/projects/${projectId}/contracts/`, data)
}
export function updateContract(projectId: number, id: number, data: any) {
  return request.put(`/v1/projects/${projectId}/contracts/${id}/`, data)
}
export function deleteContract(projectId: number, id: number) {
  return request.delete(`/v1/projects/${projectId}/contracts/${id}/`)
}

export function getWitnesses(projectId: number, params?: any) {
  return request.get(`/v1/projects/${projectId}/witnesses/`, { params })
}
export function createWitness(projectId: number, data: any) {
  return request.post(`/v1/projects/${projectId}/witnesses/`, data)
}
export function updateWitness(projectId: number, id: number, data: any) {
  return request.put(`/v1/projects/${projectId}/witnesses/${id}/`, data)
}
export function deleteWitness(projectId: number, id: number) {
  return request.delete(`/v1/projects/${projectId}/witnesses/${id}/`)
}

export function getProjectStats(projectId: number) {
  return request.get(`/v1/projects/${projectId}/stats/`)
}
