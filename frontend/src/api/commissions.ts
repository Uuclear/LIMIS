import request from '@/utils/request'

export function getCommissionList(params?: any) { return request.get('/v1/commissions/', { params }) }
export function getCommission(id: number) { return request.get(`/v1/commissions/${id}/`) }
export function createCommission(data: any) { return request.post('/v1/commissions/', data) }
export function updateCommission(id: number, data: any) { return request.put(`/v1/commissions/${id}/`, data) }
export function deleteCommission(id: number) { return request.delete(`/v1/commissions/${id}/`) }
export function submitCommission(id: number) { return request.post(`/v1/commissions/${id}/submit/`) }
export function terminateCommission(id: number, data?: { reason?: string }) {
  return request.post(`/v1/commissions/${id}/terminate/`, data || {})
}
export function reviewCommission(id: number, data: any) { return request.post(`/v1/commissions/${id}/review/`, data) }
export function getCommissionItems(commissionId: number, params?: any) {
  return request.get(`/v1/commissions/${commissionId}/items/`, { params })
}
