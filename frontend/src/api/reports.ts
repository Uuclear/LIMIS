import request from '@/utils/request'

export const getReportList = (params?: any) => request.get('/v1/reports/', { params })
export const getReport = (id: number) => request.get(`/v1/reports/${id}/`)
export const createReport = (data: any) => request.post('/v1/reports/', data)
export const generateReport = (id: number) => request.post(`/v1/reports/${id}/generate/`)
export const submitForAudit = (id: number) => request.post(`/v1/reports/${id}/submit_audit/`)
export const auditReport = (id: number, data: any) => request.post(`/v1/reports/${id}/audit/`, data)
export const approveReport = (id: number, data: any) => request.post(`/v1/reports/${id}/approve/`, data)
export const issueReport = (id: number) => request.post(`/v1/reports/${id}/issue/`)
export const voidReport = (id: number, data: any) => request.post(`/v1/reports/${id}/void/`, data)
export const previewReport = (id: number) => request.get(`/v1/reports/${id}/preview/`, { responseType: 'blob' } as any)
export const downloadReport = (id: number) => request.get(`/v1/reports/${id}/download/`, { responseType: 'blob' } as any)
export const verifyReport = (id: number) => request.get(`/v1/reports/${id}/verify/`)
