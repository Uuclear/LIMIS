import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo, Role } from '@/types/user'
import { getToken, setToken, removeToken } from '@/utils/auth'
import * as authApi from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string | null>(getToken())
  const permissions = ref<string[]>([])
  const roles = ref<Role[]>([])

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => {
    if (!userInfo.value) return ''
    const u = userInfo.value
    // 后端 UserSerializer 使用 realName 字段（或保证接口返回一致）
    return u.realName || u.username
  })
  const userRoles = computed(() => roles.value.map((r) => r.code))

  async function login(username: string, password: string) {
    const res = await authApi.login(username, password)
    token.value = res.access
    setToken(res.access, res.refresh)
    if (res.user) {
      userInfo.value = res.user
      roles.value = res.user.roles || []
    }
    await getUserInfo()
  }

  async function getUserInfo() {
    try {
      const res = await authApi.getCurrentUser()
      userInfo.value = res as unknown as UserInfo
      permissions.value = (res as any).permissions || []
      roles.value = (res as any).roles || []
    } catch {
      // silently fail if not logged in yet
    }
  }

  async function logout() {
    try {
      const refreshTk = localStorage.getItem('lims_refresh_token')
      if (refreshTk) {
        await authApi.logout()
      }
    } finally {
      resetState()
    }
  }

  async function refreshUserToken() {
    const refreshTk = localStorage.getItem('lims_refresh_token')
    if (!refreshTk) {
      resetState()
      return
    }
    try {
      const res = await authApi.refreshToken(refreshTk)
      token.value = (res as any).access
      setToken((res as any).access, refreshTk)
    } catch {
      resetState()
    }
  }

  function resetState() {
    token.value = null
    userInfo.value = null
    permissions.value = []
    roles.value = []
    removeToken()
  }

  return {
    userInfo,
    token,
    permissions,
    roles,
    isAuthenticated,
    userName,
    userRoles,
    login,
    logout,
    getUserInfo,
    refreshUserToken,
  }
})
