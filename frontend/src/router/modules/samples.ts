import type { RouteRecordRaw } from 'vue-router'

const sampleRoutes: RouteRecordRaw[] = [
  {
    path: '/sample',
    name: 'SampleList',
    component: () => import('@/views/samples/SampleList.vue'),
    meta: { title: '样品管理', permission: 'sample:view' },
  },
  {
    path: '/sample/register',
    name: 'SampleRegister',
    component: () => import('@/views/samples/SampleRegister.vue'),
    meta: { title: '样品登记', permission: 'sample:create' },
  },
  {
    path: '/sample/:id',
    name: 'SampleDetail',
    component: () => import('@/views/samples/SampleDetail.vue'),
    meta: { title: '样品详情', permission: 'sample:view' },
  },
]

export default sampleRoutes
