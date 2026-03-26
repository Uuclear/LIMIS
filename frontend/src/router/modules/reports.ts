import type { RouteRecordRaw } from 'vue-router'

const reportRoutes: RouteRecordRaw[] = [
  {
    path: '/reports',
    name: 'ReportList',
    component: () => import('@/views/reports/ReportList.vue'),
    meta: { title: '报告列表', permission: 'report:list' },
  },
  {
    path: '/reports/:id',
    name: 'ReportDetail',
    component: () => import('@/views/reports/ReportDetail.vue'),
    meta: { title: '报告详情', permission: 'report:list' },
  },
]

export default reportRoutes
