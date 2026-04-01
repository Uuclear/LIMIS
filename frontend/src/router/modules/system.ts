import type { RouteRecordRaw } from 'vue-router'

const systemRoutes: RouteRecordRaw[] = [
  {
    path: '/system/users',
    name: 'UserManagement',
    component: () => import('@/views/system/UserList.vue'),
    meta: { title: '用户管理', permission: 'system:view' },
  },
  {
    path: '/system/roles',
    name: 'RoleManagement',
    component: () => import('@/views/system/RoleList.vue'),
    meta: { title: '角色管理', permission: 'system:view' },
  },
  {
    path: '/system/audit-logs',
    name: 'AuditLogs',
    component: () => import('@/views/system/AuditLogList.vue'),
    meta: { title: '操作日志', permission: 'system:view' },
  },
]

export default systemRoutes
