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
  /** 本次会话是否已拉取过 /me（含失败），避免刷新后权限为空却误判无权限 */
  const profileFetched = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => {
    if (!userInfo.value) return ''
    const u = userInfo.value as Record<string, unknown>
    return (
      (u.real_name as string)
      || (u.first_name as string)
      || (u.username as string)
    )
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
    profileFetched.value = true
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

  async function ensureProfile() {
    if (!token.value || profileFetched.value) return
    try {
      await getUserInfo()
    } finally {
      profileFetched.value = true
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
    profileFetched.value = false
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
    ensureProfile,
    refreshUserToken,
  }
})
