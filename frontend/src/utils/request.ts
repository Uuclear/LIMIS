import axios from 'axios'
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'
import router from '@/router'

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
    // blob/arraybuffer 等：直接返回 data，避免被当作 JSON 信封处理
    if (response.config.responseType && response.config.responseType !== 'json') {
      return response.data as unknown as AxiosResponse
    }

    const resData = response.data

    // 业务信封 { code, message, data }：code 需为数字 200/201/401/4xx（兼容字符串 "200"，避免网关改类型导致不解包）
    if (resData && typeof resData === 'object' && 'code' in (resData as object)) {
      const o = resData as { code?: unknown; message?: string; data?: unknown }
      const raw = o.code
      let code: number | null = null
      if (typeof raw === 'number' && Number.isFinite(raw)) {
        code = raw
      } else if (typeof raw === 'string' && /^\d+$/.test(raw.trim())) {
        const n = parseInt(raw.trim(), 10)
        if (Number.isFinite(n)) code = n
      }
      if (code == null) {
        return resData as unknown as AxiosResponse
      }
      if (code === 200 || code === 201) {
        return (o.data !== undefined ? o.data : resData) as unknown as AxiosResponse
      }
      if (code === 401) {
        handleUnauthorized()
        return Promise.reject(new Error(o.message))
      }
      ElMessage.error(o.message || '请求失败')
      return Promise.reject(new Error(o.message || '请求失败'))
    }

    return resData as unknown as AxiosResponse
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
