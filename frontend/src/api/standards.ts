import request from '@/utils/request'

export function getStandardList(params?: Record<string, unknown>) {
  return request.get('/v1/standards/', { params })
}

export function getStandard(id: number) {
  return request.get(`/v1/standards/${id}/`)
}
