import type { RouteRecordRaw } from 'vue-router'

const qualityRoutes: RouteRecordRaw[] = [
  {
    path: '/quality/foundation',
    name: 'PrerequisitesHub',
    component: () => import('@/views/quality/PrerequisitesHub.vue'),
    meta: { title: '检测基础配置', permission: 'testing:view' },
  },
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
  {
    path: '/quality/standards',
    name: 'QualityStandardList',
    component: () => import('@/views/standards/StandardList.vue'),
    meta: { title: '标准规范', permission: 'system:standard:list' },
  },
  {
    path: '/quality/parameter-library',
    name: 'ParameterLibrary',
    component: () => import('@/views/quality/ParameterLibrary.vue'),
    meta: { title: '项目参数库', permission: 'quality:parameter:list' },
  },
  {
    path: '/quality/record-templates',
    name: 'RecordTemplateLibrary',
    component: () => import('@/views/quality/RecordTemplateLibrary.vue'),
    meta: { title: '原始记录模板', permission: 'testing:view' },
  },
  {
    path: '/quality/report-templates',
    name: 'ReportTemplateGuide',
    component: () => import('@/views/quality/ReportTemplateGuide.vue'),
    meta: { title: '报告模板', permission: 'testing:view' },
  },
  {
    path: '/quality/qualification-profiles',
    name: 'QualificationProfiles',
    component: () => import('@/views/quality/QualificationProfiles.vue'),
    meta: { title: '资质管理', permission: 'quality:view' },
  },
]

export default qualityRoutes
