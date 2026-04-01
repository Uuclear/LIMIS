import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { ElMessage } from 'element-plus'
import { isAuthenticated } from '@/utils/auth'
import { useUserStore } from '@/stores/user'
import { canAccessRoutePermission, getRoutePermission } from '@/utils/permission'
import systemRoutes from './modules/system'
import projectRoutes from './modules/projects'
import commissionRoutes from './modules/commissions'
import sampleRoutes from './modules/samples'
import equipmentRoutes from './modules/equipment'
import staffRoutes from './modules/staff'
import environmentRoutes from './modules/environment'
import qualityRoutes from './modules/quality'
import testingRoutes from './modules/testing'
import reportRoutes from './modules/reports'

NProgress.configure({ showSpinner: false })

const routes: RouteRecordRaw[] = [
  {
    path: '/standard',
    redirect: '/quality/foundation',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginPage.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/verify/report/:id',
    name: 'ReportVerify',
    component: () => import('@/views/reports/ReportVerifyPage.vue'),
    meta: { public: true, title: '报告防伪查询' },
  },
  {
    path: '/verify/sample/:sampleNo',
    name: 'SampleVerify',
    component: () => import('@/views/samples/SampleVerifyPage.vue'),
    meta: { public: true, title: '样品进度查询' },
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
      ...testingRoutes,
      ...reportRoutes,
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

router.beforeEach(async (to, _from, next) => {
  NProgress.start()

  if (to.matched.some((r) => r.meta.public)) {
    next()
    return
  }

  if (!isAuthenticated()) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  const userStore = useUserStore()
  await userStore.ensureProfile()

  const required = getRoutePermission(to.matched)
  if (!canAccessRoutePermission(required)) {
    ElMessage.warning('无权访问该页面')
    next({ path: '/dashboard' })
    return
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
