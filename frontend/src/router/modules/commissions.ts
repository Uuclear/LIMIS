import type { RouteRecordRaw } from 'vue-router'

const commissionRoutes: RouteRecordRaw[] = [
  {
    path: '/entrustment',
    name: 'CommissionList',
    component: () => import('@/views/commissions/CommissionList.vue'),
    meta: { title: '委托管理', permission: 'entrustment:list' },
  },
  {
    path: '/entrustment/create',
    name: 'CommissionCreate',
    component: () => import('@/views/commissions/CommissionForm.vue'),
    meta: { title: '新增委托', permission: 'entrustment:create' },
  },
  {
    path: '/entrustment/:id',
    name: 'CommissionDetail',
    component: () => import('@/views/commissions/CommissionDetail.vue'),
    meta: { title: '委托详情', permission: 'entrustment:list' },
  },
  {
    path: '/entrustment/:id/edit',
    name: 'CommissionEdit',
    component: () => import('@/views/commissions/CommissionForm.vue'),
    meta: { title: '编辑委托', permission: 'entrustment:edit' },
  },
]

export default commissionRoutes
