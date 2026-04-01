import type { RouteRecordRaw } from 'vue-router'

const equipmentRoutes: RouteRecordRaw[] = [
  {
    path: '/equipment',
    name: 'EquipmentList',
    component: () => import('@/views/equipment/EquipmentList.vue'),
    meta: { title: '仪器设备', permission: 'equipment:view' },
  },
  {
    path: '/equipment/:id',
    name: 'EquipmentDetail',
    component: () => import('@/views/equipment/EquipmentDetail.vue'),
    meta: { title: '设备详情', permission: 'equipment:view' },
  },
]

export default equipmentRoutes
