<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ArrowDown, Bell, User, Lock, SwitchButton } from '@element-plus/icons-vue'
import { getUnreadCount, getNotifications, markAllRead, markRead } from '@/api/notifications'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

interface NotificationItem {
  id: number
  notificationType: string
  title: string
  content: string
  linkPath: string
  isRead: boolean
  createdAt: string
}
const notifications = ref<NotificationItem[]>([])
const unreadCount = ref(0)

async function fetchUnreadCount() {
  try {
    const res = await getUnreadCount() as any
    unreadCount.value = res?.count ?? 0
  } catch {}
}

async function fetchNotifications() {
  try {
    const res = await getNotifications({ page_size: 10 }) as any
    notifications.value = Array.isArray(res) ? res : (res?.results ?? [])
  } catch {}
}

async function handleMarkAllRead() {
  await markAllRead()
  notifications.value.forEach(n => { n.isRead = true })
  unreadCount.value = 0
}

async function handleMarkRead(notif: NotificationItem) {
  if (!notif.isRead) {
    await markRead(notif.id)
    notif.isRead = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }
  if (notif.linkPath) {
    router.push(notif.linkPath)
  }
}

onMounted(() => {
  fetchUnreadCount()
  fetchNotifications()
})

const pollTimer = setInterval(fetchUnreadCount, 60000)
onUnmounted(() => clearInterval(pollTimer))

const breadcrumbs = computed(() => {
  return route.matched
    .filter((item) => item.meta?.title)
    .map((item) => ({ title: item.meta.title as string, path: item.path }))
})

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
          <div class="notif-panel-header">
            <span class="notif-panel-title">消息提醒</span>
            <el-button link type="primary" size="small" @click="handleMarkAllRead">全部已读</el-button>
          </div>
          <el-scrollbar max-height="280px">
            <div
              v-for="notif in notifications"
              :key="notif.id"
              class="notif-item"
              :class="{ 'notif-item-unread': !notif.isRead }"
              @click="handleMarkRead(notif)"
            >
              <div class="notif-item-title">{{ notif.title }}</div>
              <div class="notif-item-desc">{{ notif.content }}</div>
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

.notif-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.notif-panel-title {
  font-weight: 600;
  font-size: 14px;
}

.notif-item-unread .notif-item-title {
  font-weight: 600;
  color: var(--lims-primary);
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
