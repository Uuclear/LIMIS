<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  HomeFilled,
  Briefcase,
  Document,
  DataAnalysis,
  Notebook,
  Monitor,
  SetUp,
  Setting,
  Fold,
  Expand,
} from '@element-plus/icons-vue'

interface MenuItem {
  index: string
  title: string
  icon?: typeof HomeFilled
  children?: MenuItem[]
}

const props = defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ 'update:collapsed': [value: boolean] }>()

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

const menuItems: MenuItem[] = [
  { index: '/dashboard', title: '首页', icon: HomeFilled },
  {
    index: 'business',
    title: '业务管理',
    icon: Briefcase,
    children: [
      { index: '/project', title: '工程项目' },
      { index: '/entrustment', title: '委托管理' },
      { index: '/sample', title: '样品管理' },
    ],
  },
  {
    index: 'testing',
    title: '检测管理',
    icon: DataAnalysis,
    children: [
      { index: '/testing/tasks', title: '检测任务' },
      { index: '/testing/records', title: '原始记录' },
      { index: '/testing/results', title: '检测结果' },
    ],
  },
  {
    index: 'report',
    title: '报告管理',
    icon: Notebook,
    children: [{ index: '/reports', title: '报告列表' }],
  },
  {
    index: 'resource',
    title: '资源管理',
    icon: Document,
    children: [
      { index: '/equipment', title: '仪器设备' },
      { index: '/staff', title: '人员管理' },
      { index: '/consumable', title: '耗材管理' },
    ],
  },
  {
    index: 'monitor',
    title: '监控管理',
    icon: Monitor,
    children: [{ index: '/environment', title: '环境监控' }],
  },
  {
    index: 'quality',
    title: '质量体系',
    icon: SetUp,
    children: [
      { index: '/quality/foundation', title: '检测基础配置' },
      { index: '/quality/standards', title: '标准规范' },
      { index: '/quality/parameter-library', title: '项目参数库' },
      { index: '/quality/record-templates', title: '原始记录模板' },
      { index: '/quality/report-templates', title: '报告模板' },
      { index: '/quality/qualification-profiles', title: '资质管理' },
      { index: '/quality/audit', title: '内部审核' },
      { index: '/quality/review', title: '管理评审' },
      { index: '/quality/nonconformity', title: '不符合项' },
    ],
  },
  {
    index: 'system',
    title: '系统管理',
    icon: Setting,
    children: [
      { index: '/system/users', title: '用户管理' },
      { index: '/system/roles', title: '角色管理' },
      { index: '/system/audit-logs', title: '操作日志' },
    ],
  },
]

function handleMenuSelect(index: string) {
  if (index.startsWith('/')) {
    router.push(index)
  }
}

function toggleCollapse() {
  emit('update:collapsed', !props.collapsed)
}
</script>

<template>
  <div class="sidebar">
    <div class="sidebar-logo">
      <span v-show="!collapsed" class="sidebar-logo-text">LIMIS</span>
      <span v-show="collapsed" class="sidebar-logo-text">L</span>
    </div>

    <el-scrollbar class="sidebar-menu-wrap">
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        background-color="#001529"
        text-color="#ffffffb3"
        active-text-color="#ffffff"
        :collapse-transition="false"
        @select="handleMenuSelect"
      >
        <template v-for="item in menuItems" :key="item.index">
          <el-menu-item v-if="!item.children" :index="item.index">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>

          <el-sub-menu v-else :index="item.index">
            <template #title>
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </template>
            <el-menu-item
              v-for="child in item.children"
              :key="child.index"
              :index="child.index"
            >
              {{ child.title }}
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-scrollbar>

    <div class="sidebar-toggle" @click="toggleCollapse">
      <el-icon :size="16">
        <Fold v-if="!collapsed" />
        <Expand v-else />
      </el-icon>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #001529;
}

.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-logo-text {
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 2px;
}

.sidebar-menu-wrap {
  flex: 1;
  overflow: hidden;
}

.sidebar-menu-wrap :deep(.el-menu) {
  border-right: none;
}

.sidebar-menu-wrap :deep(.el-menu-item.is-active) {
  background-color: #2563eb !important;
}

.sidebar-menu-wrap :deep(.el-sub-menu__title:hover),
.sidebar-menu-wrap :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.06) !important;
}

.sidebar-toggle {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.65);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  transition: color 0.2s;
}

.sidebar-toggle:hover {
  color: #fff;
}
</style>
