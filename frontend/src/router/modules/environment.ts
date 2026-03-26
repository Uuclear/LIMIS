import type { RouteRecordRaw } from 'vue-router'

const environmentRoutes: RouteRecordRaw[] = [
  {
    path: '/environment',
    name: 'EnvironmentMonitor',
    component: () => import('@/views/environment/EnvironmentMonitor.vue'),
    meta: { title: '环境监控', permission: 'environment:list' },
  },
]

export default environmentRoutes
