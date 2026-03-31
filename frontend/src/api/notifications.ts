import request from '@/utils/request'

export const getNotifications = (params?: any) =>
  request.get('/v1/system/notifications/', { params })

export const getUnreadCount = () =>
  request.get('/v1/system/notifications/unread_count/')

export const markAllRead = () =>
  request.post('/v1/system/notifications/mark_all_read/')

export const markRead = (id: number) =>
  request.post(`/v1/system/notifications/${id}/mark_read/`)
