import type { Directive, DirectiveBinding } from 'vue'
import type { RouteRecordNormalized } from 'vue-router'
import { useUserStore } from '@/stores/user'

export function hasPermission(permission: string): boolean {
  const userStore = useUserStore()
  const perms = userStore.permissions
  if (perms.includes('*')) return true
  return perms.includes(permission)
}

/** 自最深匹配向父级查找首个 meta.permission（与路由守卫一致） */
export function getRoutePermission(matched: RouteRecordNormalized[]): string | undefined {
  for (let i = matched.length - 1; i >= 0; i--) {
    const p = matched[i].meta.permission as string | undefined
    if (p) return p
  }
  return undefined
}

/** 无 permission 的路由视为不限制；否则走 hasPermission（含 *） */
export function canAccessRoutePermission(permission: string | undefined): boolean {
  if (!permission) return true
  return hasPermission(permission)
}

export function hasRole(role: string): boolean {
  const userStore = useUserStore()
  return userStore.roles.some((r) => r.code === role)
}

function checkPermission(el: HTMLElement, binding: DirectiveBinding<string>) {
  const permission = binding.value
  if (permission && !hasPermission(permission)) {
    el.parentNode?.removeChild(el)
  }
}

export const vPermission: Directive<HTMLElement, string> = {
  mounted: checkPermission,
  updated: checkPermission,
}
