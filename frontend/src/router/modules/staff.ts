import type { RouteRecordRaw } from 'vue-router'

const staffRoutes: RouteRecordRaw[] = [
  {
    path: '/staff',
    name: 'StaffList',
    component: () => import('@/views/staff/StaffList.vue'),
    meta: { title: '人员管理', permission: 'staff:view' },
  },
  {
    path: '/staff/:id',
    name: 'StaffDetail',
    component: () => import('@/views/staff/StaffDetail.vue'),
    meta: { title: '人员详情', permission: 'staff:view' },
  },
]

export default staffRoutes
