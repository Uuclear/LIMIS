import axios from 'axios'
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'
import router from '@/router'

function toCamel(s: string): string {
  return s.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
}

function camelizeKeys(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(camelizeKeys)
  if (obj !== null && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [toCamel(k), camelizeKeys(v)])
    )
  }
  return obj
}

const service = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    // blob 等非 JSON 响应直接返回
    if (response.config.responseType && response.config.responseType !== 'json') {
      return response as unknown as AxiosResponse
    }

    const resData = response.data

    // 仅把「数值型 code + 业务信封」当作统一响应；避免与业务字段 code（如项目编号）冲突
    if (
      resData &&
      typeof resData === 'object' &&
      typeof (resData as { code?: unknown }).code === 'number'
    ) {
      const code = (resData as { code: number; message?: string; data?: unknown }).code
      if (code === 200 || code === 201) {
        return camelizeKeys((resData as { data: unknown }).data) as unknown as AxiosResponse
      }
      if (code === 401) {
        handleUnauthorized()
        return Promise.reject(new Error((resData as { message?: string }).message))
      }
      ElMessage.error((resData as { message?: string }).message || '请求失败')
      return Promise.reject(new Error((resData as { message?: string }).message))
    }

    return camelizeKeys(resData) as unknown as AxiosResponse
  },
  (error) => {
    if (error.response?.status === 401) {
      handleUnauthorized()
    } else {
      const msg = error.response?.data?.detail
        || error.response?.data?.message
        || error.message
        || '网络异常'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

function handleUnauthorized() {
  removeToken()
  router.push('/login')
  ElMessage.error('登录已过期，请重新登录')
}

export default service
