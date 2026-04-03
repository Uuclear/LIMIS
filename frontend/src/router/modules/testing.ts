import type { RouteRecordRaw } from 'vue-router'

const testingRoutes: RouteRecordRaw[] = [
  {
    path: '/testing/tasks',
    name: 'TestTaskList',
    component: () => import('@/views/testing/tasks/TaskList.vue'),
    meta: { title: '检测任务', permission: 'task:view' },
  },
  {
    path: '/testing/tasks/:id',
    name: 'TestTaskDetail',
    component: () => import('@/views/testing/tasks/TaskDetail.vue'),
    meta: { title: '任务详情', permission: 'task:view' },
  },
  {
    path: '/testing/records',
    name: 'RecordList',
    component: () => import('@/views/testing/records/RecordList.vue'),
    meta: { title: '原始记录', permission: 'testing:view' },
  },
  {
    path: '/testing/records/new',
    name: 'RecordCreate',
    component: () => import('@/views/testing/records/RecordForm.vue'),
    meta: { title: '新建记录', permission: 'testing:create' },
  },
  {
    path: '/testing/records/:id',
    name: 'RecordEdit',
    component: () => import('@/views/testing/records/RecordForm.vue'),
    meta: { title: '编辑记录', permission: 'testing:view' },
  },
]

export default testingRoutes
