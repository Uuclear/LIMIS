import type { RouteRecordRaw } from 'vue-router'

const standardRoutes: RouteRecordRaw[] = [
  {
    path: '/standard',
    name: 'StandardList',
    component: () => import('@/views/standards/StandardList.vue'),
    meta: { title: '标准规范', permission: 'system:standard:list' },
  },
]

export default standardRoutes
