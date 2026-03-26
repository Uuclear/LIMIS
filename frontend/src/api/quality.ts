import request from '@/utils/request'

// Audit
export function getAuditList(params?: any) { return request.get('/v1/quality/audits/', { params }) }
export function getAudit(id: number) { return request.get(`/v1/quality/audits/${id}/`) }
export function createAudit(data: any) { return request.post('/v1/quality/audits/', data) }

// Review
export function getReviewList(params?: any) { return request.get('/v1/quality/reviews/', { params }) }
export function getReview(id: number) { return request.get(`/v1/quality/reviews/${id}/`) }
export function createReview(data: any) { return request.post('/v1/quality/reviews/', data) }

// NonConformity
export function getNcList(params?: any) { return request.get('/v1/quality/nonconformities/', { params }) }
export function getNc(id: number) { return request.get(`/v1/quality/nonconformities/${id}/`) }
export function createNc(data: any) { return request.post('/v1/quality/nonconformities/', data) }

// Complaint
export function getComplaintList(params?: any) { return request.get('/v1/quality/complaints/', { params }) }
export function createComplaint(data: any) { return request.post('/v1/quality/complaints/', data) }

// Proficiency Test
export function getPtList(params?: any) { return request.get('/v1/quality/proficiency-tests/', { params }) }
export function createPt(data: any) { return request.post('/v1/quality/proficiency-tests/', data) }

// Supervision
export function getSupervisionList(params?: any) { return request.get('/v1/quality/supervisions/', { params }) }
export function createSupervision(data: any) { return request.post('/v1/quality/supervisions/', data) }
