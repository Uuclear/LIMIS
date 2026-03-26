import request from '@/utils/request'

export function getSampleList(params?: any) { return request.get('/v1/samples/', { params }) }
export function getSample(id: number) { return request.get(`/v1/samples/${id}/`) }
export function createSample(data: any) { return request.post('/v1/samples/', data) }
export function batchCreateSamples(data: any) { return request.post('/v1/samples/batch/', data) }
export function changeSampleStatus(id: number, data: any) {
  return request.post(`/v1/samples/${id}/change-status/`, data)
}
export function getSampleTimeline(id: number) { return request.get(`/v1/samples/${id}/timeline/`) }
export function getSampleLabel(id: number) { return request.get(`/v1/samples/${id}/label/`) }
export function getRetentionSamples(params?: any) { return request.get('/v1/samples/retention/', { params }) }
export function disposeSample(id: number, data: any) { return request.post(`/v1/samples/${id}/dispose/`, data) }
export function exportSamples(params?: any) {
  return request.get('/v1/samples/export/', { params, responseType: 'blob' } as any)
}
