import request from '@/utils/request'

export function getConsumableList(params?: any) { return request.get('/v1/consumables/', { params }) }
export function createConsumable(data: any) { return request.post('/v1/consumables/', data) }
export function consumableIn(id: number, data: any) {
  return request.post(`/v1/consumables/${id}/in/`, data)
}
export function consumableOut(id: number, data: any) {
  return request.post(`/v1/consumables/${id}/out/`, data)
}
export function getLowStock(params?: any) {
  return request.get('/v1/consumables/low-stock/', { params })
}
export function getExpiring(params?: any) {
  return request.get('/v1/consumables/expiring/', { params })
}
