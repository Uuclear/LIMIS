import type { RouteRecordRaw } from 'vue-router'

const consumableRoutes: RouteRecordRaw[] = [
  {
    path: '/consumable',
    name: 'ConsumableList',
    component: () => import('@/views/consumables/ConsumableList.vue'),
    meta: { title: '耗材管理', permission: 'consumable:list' },
  },
]

export default consumableRoutes
