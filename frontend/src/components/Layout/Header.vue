<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ArrowDown, Bell, User, Lock, SwitchButton } from '@element-plus/icons-vue'
import { getDashboardData } from '@/api/statistics'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

/** 与仪表盘 /statistics/dashboard 一致的待办类提醒（非站内信系统） */
type NotifItem = { id: string; title: string; desc: string; path: string; count: number }
const notifications = ref<NotifItem[]>([])

const unreadCount = computed(() =>
  notifications.value.reduce((s, n) => s + n.count, 0),
)

async function loadNotifications() {
  try {
    const res: any = await getDashboardData()
    const items: NotifItem[] = []
    const n = (v: unknown) => (typeof v === 'number' && !Number.isNaN(v) ? v : 0)

    const pc = n(res?.pending_commission_reviews)
    if (pc > 0) {
      items.push({
        id: 'commission_review',
        title: '委托待评审',
        desc: `共 ${pc} 条委托单待评审`,
        path: '/entrustment',
        count: pc,
      })
    }
    const pt = n(res?.pending_tasks)
    if (pt > 0) {
      items.push({
        id: 'pending_tasks',
        title: '检测任务待办',
        desc: `共 ${pt} 个任务待分配或待检`,
        path: '/testing/tasks',
        count: pt,
      })
    }
    const rr = n(res?.records_pending_review)
    if (rr > 0) {
      items.push({
        id: 'record_review',
        title: '原始记录待复核',
        desc: `共 ${rr} 条记录待复核`,
        path: '/testing/records',
        count: rr,
      })
    }
    const pr = n(res?.pending_report_reviews)
    if (pr > 0) {
      items.push({
        id: 'report_review',
        title: '检测报告审批',
        desc: `共 ${pr} 份报告待审核/批准`,
        path: '/reports',
        count: pr,
      })
    }
    const ew = n(res?.equipment_warnings)
    if (ew > 0) {
      items.push({
        id: 'equipment_cal',
        title: '设备校准提醒',
        desc: `共 ${ew} 台设备需关注校准/检定`,
        path: '/equipment',
        count: ew,
      })
    }
    notifications.value = items
  } catch {
    notifications.value = []
  }
}

onMounted(() => {
  loadNotifications()
})

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
      <el-popover placement="bottom-end" :width="340" trigger="click" @show="loadNotifications">
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
