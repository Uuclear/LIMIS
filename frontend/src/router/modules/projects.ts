import type { RouteRecordRaw } from 'vue-router'

const projectRoutes: RouteRecordRaw[] = [
  {
    path: '/project',
    name: 'ProjectList',
    component: () => import('@/views/projects/ProjectList.vue'),
    meta: { title: '工程项目', permission: 'project:view' },
  },
  {
    path: '/project/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/projects/ProjectDetail.vue'),
    meta: { title: '项目详情', permission: 'project:view' },
  },
]

export default projectRoutes
