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
