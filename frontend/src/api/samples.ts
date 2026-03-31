import request from '@/utils/request'

/** 与后端路由一致：projects.urls 下挂载为 samples/ + router.register('samples', …) */
const S = '/v1/samples/samples'

export function getSampleList(params?: any) { return request.get(`${S}/`, { params }) }
export function getSample(id: number) { return request.get(`${S}/${id}/`) }
export function createSample(data: any) { return request.post(`${S}/`, data) }
export function batchCreateSamples(data: any) { return request.post(`${S}/batch-register/`, data) }
export function changeSampleStatus(id: number, data: any) {
  return request.post(`${S}/${id}/change-status/`, data)
}
export function getSampleTimeline(id: number) { return request.get(`${S}/${id}/timeline/`) }
export function getSampleLabel(id: number) { return request.get(`${S}/${id}/label/`) }
export function getRetentionSamples(params?: any) { return request.get(`${S}/retention-list/`, { params }) }
export function disposeSample(id: number, data: any) { return request.post(`${S}/${id}/dispose/`, data) }
export function exportSamples(params?: any) {
  return request.get(`${S}/export/`, { params, responseType: 'blob' } as any)
}
