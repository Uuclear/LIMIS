import type { RouteRecordRaw } from 'vue-router'

const qualityRoutes: RouteRecordRaw[] = [
  {
    path: '/quality/audit',
    name: 'AuditList',
    component: () => import('@/views/quality/AuditList.vue'),
    meta: { title: '内部审核', permission: 'quality:audit:list' },
  },
  {
    path: '/quality/review',
    name: 'ReviewList',
    component: () => import('@/views/quality/ReviewList.vue'),
    meta: { title: '管理评审', permission: 'quality:review:list' },
  },
  {
    path: '/quality/nonconformity',
    name: 'NonConformityList',
    component: () => import('@/views/quality/NonConformityList.vue'),
    meta: { title: '不符合项', permission: 'quality:nonconformity:list' },
  },
]

export default qualityRoutes
