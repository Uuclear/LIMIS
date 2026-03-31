import request from '@/utils/request'

export function getUserList(params?: any) { return request.get('/v1/system/users/', { params }) }
export function createUser(data: any) { return request.post('/v1/system/users/', data) }
export function updateUser(id: number, data: any) { return request.put(`/v1/system/users/${id}/`, data) }
export function deleteUser(id: number) { return request.delete(`/v1/system/users/${id}/`) }
export function resetPassword(id: number, data: any) { return request.post(`/v1/system/users/${id}/reset_password/`, data) }
export function toggleUserActive(id: number) { return request.post(`/v1/system/users/${id}/toggle_active/`) }
export function kickoutUserSessions(id: number) { return request.post(`/v1/system/users/${id}/kickout-sessions/`) }
export function getRoleList(params?: any) { return request.get('/v1/system/roles/', { params }) }
export function createRole(data: any) { return request.post('/v1/system/roles/', data) }
export function updateRole(id: number, data: any) { return request.put(`/v1/system/roles/${id}/`, data) }
export function deleteRole(id: number) { return request.delete(`/v1/system/roles/${id}/`) }
export function getPermissionList(params?: any) { return request.get('/v1/system/permissions/', { params }) }
/** 按 module 分组的权限列表（用于角色分配） */
export function getPermissionGrouped() { return request.get('/v1/system/permissions/grouped/') }
export function getAuditLogs(params?: any) { return request.get('/v1/system/audit-logs/', { params }) }
/** 审计日志 CSV，与列表相同的 query 筛选（不含分页）；需 system:export */
export function exportAuditLogs(params?: Record<string, unknown>) {
  return request.get('/v1/system/audit-logs/export/', {
    params,
    responseType: 'blob',
  } as any)
}
