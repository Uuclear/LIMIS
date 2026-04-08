import request from '@/utils/request'

export const getReportList = (params?: any) => request.get('/v1/reports/', { params })
export const getReport = (id: number) => request.get(`/v1/reports/${id}/`)
export const createReport = (data: any) => request.post('/v1/reports/', data)
export const generateReport = (id: number) => request.post(`/v1/reports/${id}/generate/`)
export const submitForAudit = (id: number) => request.post(`/v1/reports/${id}/submit_audit/`)
export const auditReport = (id: number, data: any) => request.post(`/v1/reports/${id}/audit/`, data)
export const approveReport = (id: number, data: any) => request.post(`/v1/reports/${id}/approve/`, data)
export const issueReport = (id: number) => request.post(`/v1/reports/${id}/issue/`)
export const archiveReport = (id: number) => request.post(`/v1/reports/${id}/archive/`)
export const getReportTimeline = (id: number) => request.get(`/v1/reports/${id}/timeline/`)
export const voidReport = (id: number, data: any) => request.post(`/v1/reports/${id}/void/`, data)
export const previewReport = (id: number) => request.get(`/v1/reports/${id}/preview/`, { responseType: 'blob' } as any)
export const downloadReport = (id: number) => request.get(`/v1/reports/${id}/download/`, { responseType: 'blob' } as any)
export const uploadReportPdf = (id: number, file: File) => {
  const form = new FormData()
  form.append('pdf_file', file)
  return request.post(`/v1/reports/${id}/upload_pdf/`, form)
}
export const distributeReport = (id: number, data: any) => request.post(`/v1/reports/${id}/distribute/`, data)
export const getReportDistributions = (id: number) => request.get(`/v1/reports/${id}/distributions/`)
export const verifyReport = (id: number) => request.get(`/v1/reports/${id}/verify/`)
/** 无需登录：公开防伪查询（与二维码 URL 一致） */
export const verifyReportPublic = (id: number) =>
  request.get(`/v1/reports/public/verify/${id}/`, { skipGlobalError: true } as Record<string, unknown>)
