import request from '@/utils/request'

export function getUserList(params?: any) { return request.get('/v1/system/users/', { params }) }
export function createUser(data: any) { return request.post('/v1/system/users/', data) }
export function updateUser(id: number, data: any) { return request.put(`/v1/system/users/${id}/`, data) }
export function deleteUser(id: number) { return request.delete(`/v1/system/users/${id}/`) }
export function resetPassword(id: number, data: any) { return request.post(`/v1/system/users/${id}/reset_password/`, data) }
export function toggleUserActive(id: number) { return request.post(`/v1/system/users/${id}/toggle_active/`) }
export function getRoleList(params?: any) { return request.get('/v1/system/roles/', { params }) }
export function createRole(data: any) { return request.post('/v1/system/roles/', data) }
export function updateRole(id: number, data: any) { return request.put(`/v1/system/roles/${id}/`, data) }
export function deleteRole(id: number) { return request.delete(`/v1/system/roles/${id}/`) }
export function getPermissionList(params?: any) { return request.get('/v1/system/permissions/', { params }) }
export function getAuditLogs(params?: any) { return request.get('/v1/system/audit-logs/', { params }) }
