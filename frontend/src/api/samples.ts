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
export function createTestingTasksForSample(id: number) {
  return request.post(`${S}/${id}/create-testing-tasks/`, {})
}
export function exportSamples(params?: any) {
  return request.get(`${S}/export/`, { params, responseType: 'blob' } as any)
}

/** GET：批量登记 Excel 模板（表头与 batch-register 行字段一致） */
export function downloadSampleImportTemplate() {
  return request.get(`${S}/import-template/`, { responseType: 'blob' } as any)
}

/** POST：multipart，字段 commission_id + file（.xlsx） */
export function batchImportSamples(commissionId: number, file: File) {
  const fd = new FormData()
  fd.append('commission_id', String(commissionId))
  fd.append('file', file)
  return request.post(`${S}/batch-import/`, fd, { skipGlobalError: true } as any)
}

/** 无需登录：公开样品/委托进度查询（与标签二维码 `/verify/sample/<no>` 一致） */
export const verifySamplePublic = (sampleNo: string) =>
  request.get(`${S}/public/verify/${encodeURIComponent(sampleNo)}/`, {
    skipGlobalError: true,
  } as Record<string, unknown>)
