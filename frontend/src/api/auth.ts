import request from '@/utils/request'
import type { LoginResponse, UserInfo } from '@/types/user'

export function login(username: string, password: string) {
  return request.post<unknown, LoginResponse>('/v1/system/login/', { username, password })
}

export function logout() {
  return request.post('/v1/system/logout/')
}

export function getCurrentUser() {
  return request.get<unknown, UserInfo>('/v1/system/me/')
}

export function refreshToken(refresh: string) {
  return request.post<unknown, { access: string }>('/v1/system/token/refresh/', { refresh })
}

export function changePassword(oldPassword: string, newPassword: string) {
  return request.put('/v1/system/password/change/', { oldPassword, newPassword })
}
