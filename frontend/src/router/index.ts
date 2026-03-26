import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { isAuthenticated } from '@/utils/auth'
import systemRoutes from './modules/system'
import projectRoutes from './modules/projects'
import commissionRoutes from './modules/commissions'
import sampleRoutes from './modules/samples'
import equipmentRoutes from './modules/equipment'
import staffRoutes from './modules/staff'
import environmentRoutes from './modules/environment'
import qualityRoutes from './modules/quality'
import consumableRoutes from './modules/consumables'
import standardRoutes from './modules/standards'

NProgress.configure({ showSpinner: false })

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginPage.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/components/Layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardPage.vue'),
        meta: { title: '首页' },
      },
      ...systemRoutes,
      ...projectRoutes,
      ...commissionRoutes,
      ...sampleRoutes,
      ...equipmentRoutes,
      ...staffRoutes,
      ...environmentRoutes,
      ...qualityRoutes,
      ...consumableRoutes,
      ...standardRoutes,
      {
        path: 'task',
        name: 'TestTask',
        component: () => import('@/views/placeholder/PlaceholderPage.vue'),
        meta: { title: '检测任务', permission: 'task:list' },
      },
      {
        path: 'record',
        name: 'OriginalRecord',
        component: () => import('@/views/placeholder/PlaceholderPage.vue'),
        meta: { title: '原始记录', permission: 'record:list' },
      },
      {
        path: 'result',
        name: 'TestResult',
        component: () => import('@/views/placeholder/PlaceholderPage.vue'),
        meta: { title: '检测结果', permission: 'result:list' },
      },
      {
        path: 'report',
        name: 'ReportList',
        component: () => import('@/views/placeholder/PlaceholderPage.vue'),
        meta: { title: '报告列表', permission: 'report:list' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const PUBLIC_ROUTES = ['/login']

router.beforeEach((to, _from, next) => {
  NProgress.start()

  if (PUBLIC_ROUTES.includes(to.path)) {
    next()
    return
  }

  if (!isAuthenticated()) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
