import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/stores/user'

type PermissionValue = string | string[]

/**
 * 检查用户是否拥有指定权限
 * @param permission 权限字符串或数组
 * @param requireAll 是否需要满足所有权限（默认false，满足任一即可）
 */
export function hasPermission(permission: PermissionValue, requireAll: boolean = false): boolean {
  const userStore = useUserStore()
  const permissions = userStore.permissions || []
  
  if (!permissions || permissions.length === 0) {
    return false
  }
  
  // 超级管理员拥有所有权限
  if (userStore.user?.is_superuser) {
    return true
  }
  
  const permissionList = Array.isArray(permission) ? permission : [permission]
  
  if (requireAll) {
    return permissionList.every(perm => checkSinglePermission(permissions, perm))
  } else {
    return permissionList.some(perm => checkSinglePermission(permissions, perm))
  }
}

/**
 * 检查单个权限
 * 支持通配符匹配
 */
function checkSinglePermission(permissions: string[], requiredPerm: string): boolean {
  // 精确匹配
  if (permissions.includes(requiredPerm)) {
    return true
  }
  
  // 通配符匹配
  const [module, action] = requiredPerm.split(':')
  
  // 检查模块级别通配符 'module:*'
  if (permissions.includes(`${module}:*`)) {
    return true
  }
  
  // 检查全局通配符 '*'
  if (permissions.includes('*')) {
    return true
  }
  
  return false
}

/**
 * 检查用户是否拥有指定角色
 */
export function hasRole(role: string | string[], requireAll: boolean = false): boolean {
  const userStore = useUserStore()
  const userRoles = userStore.roles || []
  
  if (!userRoles || userRoles.length === 0) {
    return false
  }
  
  // 超级管理员拥有所有角色
  if (userStore.user?.is_superuser) {
    return true
  }
  
  const roleCodes = userRoles.map(r => r.code)
  const roleList = Array.isArray(role) ? role : [role]
  
  if (requireAll) {
    return roleList.every(r => roleCodes.includes(r))
  } else {
    return roleList.some(r => roleCodes.includes(r))
  }
}

/**
 * 权限指令处理函数
 */
function checkPermission(el: HTMLElement, binding: DirectiveBinding<PermissionValue>) {
  const { value, arg } = binding
  const requireAll = arg === 'all'
  
  if (!value) {
    console.warn('v-permission directive requires a permission value')
    return
  }
  
  if (!hasPermission(value, requireAll)) {
    el.parentNode?.removeChild(el)
  }
}

/**
 * 权限指令
 * 
 * 使用方式：
 * v-permission="'user:create'"                    // 单个权限
 * v-permission="['user:create', 'user:edit']"     // 多个权限（满足任一）
 * v-permission:all="['user:create', 'user:edit']" // 多个权限（需全部满足）
 */
export const vPermission: Directive<HTMLElement, PermissionValue> = {
  mounted: checkPermission,
  updated: checkPermission,
}

/**
 * 权限禁用指令
 * 不移除元素，而是禁用
 */
export const vPermissionDisabled: Directive<HTMLElement, PermissionValue> = {
  mounted(el: HTMLElement, binding: DirectiveBinding<PermissionValue>) {
    const { value, arg } = binding
    const requireAll = arg === 'all'
    
    if (!value) {
      return
    }
    
    if (!hasPermission(value, requireAll)) {
      el.setAttribute('disabled', 'true')
      el.classList.add('is-disabled')
      el.style.cursor = 'not-allowed'
      el.style.opacity = '0.5'
    }
  },
  updated(el: HTMLElement, binding: DirectiveBinding<PermissionValue>) {
    const { value, arg } = binding
    const requireAll = arg === 'all'
    
    if (!value) {
      return
    }
    
    if (!hasPermission(value, requireAll)) {
      el.setAttribute('disabled', 'true')
      el.classList.add('is-disabled')
    } else {
      el.removeAttribute('disabled')
      el.classList.remove('is-disabled')
      el.style.cursor = ''
      el.style.opacity = ''
    }
  },
}
