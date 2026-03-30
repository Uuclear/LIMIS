<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ArrowDown, Bell, User, Lock, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

/** 站内提醒（示例数据，后续可对接通知接口） */
const notifications = ref([
  { id: 1, title: '待办：委托评审', desc: '有委托单待您评审', path: '/entrustment' },
  { id: 2, title: '设备校准提醒', desc: '部分设备即将到检', path: '/equipment' },
  { id: 3, title: '质量体系', desc: '内部审核计划请关注', path: '/quality/audit' },
])

const unreadCount = computed(() => notifications.value.length)

const breadcrumbs = computed(() => {
  return route.matched
    .filter((item) => item.meta?.title)
    .map((item) => ({ title: item.meta.title as string, path: item.path }))
})

function openNotification(n: { path?: string }) {
  if (n.path) {
    router.push(n.path)
  }
}

async function handleCommand(command: string) {
  if (command === 'logout') {
    await userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/system/users')
  } else if (command === 'password') {
    router.push('/system/users')
  }
}
</script>

<template>
  <div class="header">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item
          v-for="item in breadcrumbs"
          :key="item.path"
          :to="item.path"
        >
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <el-popover placement="bottom-end" :width="340" trigger="click">
        <template #reference>
          <span class="notif-trigger" role="button" tabindex="0">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="notification-badge">
              <el-icon :size="18" class="header-icon"><Bell /></el-icon>
            </el-badge>
          </span>
        </template>
        <div class="notif-panel">
          <div class="notif-panel-title">消息提醒</div>
          <el-scrollbar max-height="280px">
            <div
              v-for="n in notifications"
              :key="n.id"
              class="notif-item"
              @click="openNotification(n)"
            >
              <div class="notif-item-title">{{ n.title }}</div>
              <div class="notif-item-desc">{{ n.desc }}</div>
            </div>
            <el-empty v-if="!notifications.length" description="暂无消息" :image-size="64" />
          </el-scrollbar>
        </div>
      </el-popover>

      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="28" :icon="User" />
          <span class="user-name">{{ userStore.userName || '用户' }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>个人信息
            </el-dropdown-item>
            <el-dropdown-item command="password">
              <el-icon><Lock /></el-icon>修改密码
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style scoped>
.header {
  height: var(--lims-header-height);
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--lims-header-bg);
  border-bottom: 1px solid var(--lims-border-color);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notif-trigger {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  outline: none;
}

.header-icon {
  cursor: pointer;
  color: var(--lims-text-secondary);
  transition: color 0.2s;
}

.notif-trigger:hover .header-icon {
  color: var(--lims-primary);
}

.notification-badge {
  display: flex;
  align-items: center;
}

.notif-panel-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.notif-item {
  padding: 10px 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.notif-item:hover {
  background: var(--el-fill-color-light);
}

.notif-item-title {
  font-size: 13px;
  color: var(--el-text-color-primary);
}

.notif-item-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.user-info:hover {
  background: var(--lims-bg);
}

.user-name {
  font-size: 14px;
  color: var(--lims-text-primary);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
