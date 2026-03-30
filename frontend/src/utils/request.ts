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
    const resData = response.data

    if (resData && typeof resData === 'object' && 'code' in resData) {
      if (resData.code === 200 || resData.code === 201) {
        return resData.data as unknown as AxiosResponse
      }
      if (resData.code === 401) {
        handleUnauthorized()
        return Promise.reject(new Error(resData.message))
      }
      ElMessage.error(resData.message || '请求失败')
      return Promise.reject(new Error(resData.message))
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
