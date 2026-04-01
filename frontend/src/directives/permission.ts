/**
 * 权限指令 v-permission
 * 用于控制按钮级别的权限显示
 * 
 * 使用方式：
 * v-permission="'user:create'"           // 单个权限
 * v-permission="['user:create', 'user:edit']"  // 多个权限（满足任一即可）
 * v-permission:all="['user:create', 'user:edit']"  // 多个权限（需全部满足）
 */

import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/stores/user'

type PermissionValue = string | string[]

/**
 * 检查用户是否拥有指定权限
 */
function checkPermission(value: PermissionValue, requireAll: boolean = false): boolean {
  const userStore = useUserStore()
  const permissions = userStore.permissions || []
  
  if (!permissions || permissions.length === 0) {
    return false
  }
  
  // 超级管理员拥有所有权限
  if (userStore.user?.is_superuser) {
    return true
  }
  
  // 权限字符串格式: module:action，如 'user:create', 'report:approve'
  const permissionList = Array.isArray(value) ? value : [value]
  
  if (requireAll) {
    // 需要满足所有权限
    return permissionList.every(perm => {
      return checkSinglePermission(permissions, perm)
    })
  } else {
    // 满足任一权限即可
    return permissionList.some(perm => {
      return checkSinglePermission(permissions, perm)
    })
  }
}

/**
 * 检查单个权限
 * 支持通配符匹配，如 'user:*' 匹配所有user模块权限
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
 * 权限指令
 */
export const permission: Directive<HTMLElement, PermissionValue> = {
  mounted(el: HTMLElement, binding: DirectiveBinding<PermissionValue>) {
    const { value, arg } = binding
    const requireAll = arg === 'all'
    
    if (!value) {
      console.warn('v-permission directive requires a permission value')
      return
    }
    
    const hasPermission = checkPermission(value, requireAll)
    
    if (!hasPermission) {
      // 移除元素
      el.parentNode?.removeChild(el)
    }
  },
}

/**
 * 权限禁用指令 v-permission-disabled
 * 与 v-permission 类似，但不移除元素，而是禁用
 */
export const permissionDisabled: Directive<HTMLElement, PermissionValue> = {
  mounted(el: HTMLElement, binding: DirectiveBinding<PermissionValue>) {
    const { value, arg } = binding
    const requireAll = arg === 'all'
    
    if (!value) {
      console.warn('v-permission-disabled directive requires a permission value')
      return
    }
    
    const hasPermission = checkPermission(value, requireAll)
    
    if (!hasPermission) {
      // 禁用元素
      el.setAttribute('disabled', 'true')
      el.classList.add('is-disabled')
      el.style.cursor = 'not-allowed'
      el.style.opacity = '0.5'
    }
  },
}

/**
 * 安装权限指令
 */
export function setupPermissionDirectives(app: any) {
  app.directive('permission', permission)
  app.directive('permission-disabled', permissionDisabled)
}

export default {
  permission,
  permissionDisabled,
  setupPermissionDirectives,
}