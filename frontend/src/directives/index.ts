/**
 * 自定义指令入口
 */

import type { App } from 'vue'
import { setupPermissionDirectives } from './permission'

export function setupDirectives(app: App) {
  // 注册权限指令
  setupPermissionDirectives(app)
}

export * from './permission'