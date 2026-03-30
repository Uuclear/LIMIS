import request from '@/utils/request'

export function getConsumableList(params?: any) { return request.get('/v1/consumables/items/', { params }) }
export function createConsumable(data: any) { return request.post('/v1/consumables/items/', data) }

// 入/出库：后端路由为 in-records/out-records，需要在 payload 里带 consumable
export function consumableIn(consumableId: number, data: any) {
  const today = new Date().toISOString().slice(0, 10)
  return request.post('/v1/consumables/in-records/', {
    consumable: consumableId,
    quantity: data?.quantity,
    batch_no: data?.batch_no ?? '',
    purchase_date: data?.purchase_date ?? today,
    expiry_date: data?.expiry_date ?? null,
  })
}
export function consumableOut(consumableId: number, data: any) {
  const today = new Date().toISOString().slice(0, 10)
  return request.post('/v1/consumables/out-records/', {
    consumable: consumableId,
    quantity: data?.quantity,
    purpose: data?.purpose ?? data?.remark ?? '出库',
    out_date: data?.out_date ?? today,
    recipient: data?.recipient ?? null,
  })
}

export function getLowStock(params?: any) {
  return request.get('/v1/consumables/items/low-stock/', { params })
}
export function getExpiring(params?: any) {
  return request.get('/v1/consumables/items/expiring/', { params })
}
