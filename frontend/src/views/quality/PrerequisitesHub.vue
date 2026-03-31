<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  Document, Connection, Tickets, Notebook,
  Right, CircleCheck,
} from '@element-plus/icons-vue'

const router = useRouter()

const steps = [
  { order: 1, title: '标准规范', desc: '录入现行标准号、名称、实施日期，可爬取工标网辅助填写', path: '/quality/standards' },
  { order: 2, title: '项目参数库', desc: '为每本标准建立检测方法（TestMethod）与检测参数（TestParameter）', path: '/quality/parameter-library' },
  { order: 3, title: '原始记录模板', desc: '按检测方法/参数绑定 JSON 表单结构，供任务录入原始数据', path: '/quality/record-templates' },
  { order: 4, title: '报告模板', desc: '了解报告类型与模板名称约定，编制报告时选用', path: '/quality/report-templates' },
]

const cards = [
  {
    title: '标准规范',
    sub: '标准号、名称、日期、附件',
    icon: Document,
    color: '#2563eb',
    bg: '#eff6ff',
    path: '/quality/standards',
  },
  {
    title: '项目参数库',
    sub: '标准 → 方法 → 参数',
    icon: Connection,
    color: '#7c3aed',
    bg: '#f5f3ff',
    path: '/quality/parameter-library',
  },
  {
    title: '原始记录模板',
    sub: 'JSON 表单与检测方法绑定',
    icon: Tickets,
    color: '#059669',
    bg: '#ecfdf5',
    path: '/quality/record-templates',
  },
  {
    title: '报告模板',
    sub: '类型与模板名称说明',
    icon: Notebook,
    color: '#d97706',
    bg: '#fffbeb',
    path: '/quality/report-templates',
  },
]

function go(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="page-container prereq-hub">
    <div class="hub-hero">
      <h1 class="hub-title">检测基础配置</h1>
      <p class="hub-lead">
        以下四项在<strong>受理委托、下达任务</strong>之前应配置完成，保证委托单可选标准、检测项目可落到方法与参数，并具备原始记录与报告输出依据。
      </p>
      <el-space wrap>
        <el-tag type="success" effect="plain" round>
          <el-icon style="vertical-align: middle; margin-right: 4px"><CircleCheck /></el-icon>
          推荐顺序：标准 → 参数库 → 原始记录模板 → 报告模板
        </el-tag>
        <el-tag type="info" effect="plain" round>与「委托管理」无直接冲突，可随时补录</el-tag>
      </el-space>
    </div>

    <el-row :gutter="16" class="hub-cards">
      <el-col v-for="c in cards" :key="c.path" :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="hub-card" @click="go(c.path)">
          <div class="hub-card-inner">
            <div class="hub-card-icon" :style="{ background: c.bg }">
              <el-icon :size="28" :color="c.color">
                <component :is="c.icon" />
              </el-icon>
            </div>
            <div class="hub-card-text">
              <div class="hub-card-title">{{ c.title }}</div>
              <div class="hub-card-sub">{{ c.sub }}</div>
            </div>
            <el-icon class="hub-card-arrow" :size="18"><Right /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="hub-steps-card">
      <template #header>
        <span class="hub-steps-header">配置顺序说明</span>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="s in steps"
          :key="s.order"
          :timestamp="`步骤 ${s.order}`"
          placement="top"
          type="primary"
        >
          <div class="hub-step-body">
            <div class="hub-step-title">{{ s.title }}</div>
            <p class="hub-step-desc">{{ s.desc }}</p>
            <el-button type="primary" link @click="go(s.path)">
              去配置 <el-icon><Right /></el-icon>
            </el-button>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<style scoped>
.prereq-hub {
  max-width: 1400px;
}

.hub-hero {
  margin-bottom: 24px;
  padding: 20px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 60%, #f5f3ff 100%);
  border: 1px solid var(--el-border-color-lighter);
}

.hub-title {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  letter-spacing: 0.02em;
}

.hub-lead {
  margin: 0 0 14px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--el-text-color-regular);
  max-width: 920px;
}

.hub-cards {
  margin-bottom: 24px;
}

.hub-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.hub-card:hover {
  transform: translateY(-2px);
}

.hub-card :deep(.el-card__body) {
  padding: 16px 18px;
}

.hub-card-inner {
  display: flex;
  align-items: center;
  gap: 14px;
}

.hub-card-icon {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hub-card-text {
  flex: 1;
  min-width: 0;
}

.hub-card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.hub-card-sub {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.hub-card-arrow {
  color: var(--el-text-color-placeholder);
  flex-shrink: 0;
}

.hub-steps-card {
  border-radius: 12px;
}

.hub-steps-header {
  font-weight: 600;
  font-size: 15px;
}

.hub-step-body {
  padding-bottom: 4px;
}

.hub-step-title {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 6px;
}

.hub-step-desc {
  margin: 0 0 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.55;
}
</style>
