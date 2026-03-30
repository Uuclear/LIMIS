import request from '@/utils/request'

export function getStandardList(params?: Record<string, unknown>) {
  return request.get('/v1/standards/', { params })
}

export function getStandard(id: number) {
  return request.get(`/v1/standards/${id}/`)
}

export function deleteStandard(id: number) {
  return request.delete(`/v1/standards/${id}/`)
}
