import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/stores/user'

export function hasPermission(permission: string): boolean {
  const userStore = useUserStore()
  return userStore.permissions.includes(permission)
}

export function hasRole(role: string): boolean {
  const userStore = useUserStore()
  return userStore.roles.some((r) => r.code === role)
}

function checkPermission(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
  const userStore = useUserStore()
  // admin 角色跳过权限检查
  if (userStore.userRoles.includes('admin')) return

  const required = Array.isArray(binding.value) ? binding.value : [binding.value]
  if (required.length && !required.some((p) => hasPermission(p))) {
    el.parentNode?.removeChild(el)
  }
}

export const vPermission: Directive<HTMLElement, string | string[]> = {
  mounted: checkPermission,
  updated: checkPermission,
}
