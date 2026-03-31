<script setup lang="ts">
import { Notebook, Warning } from '@element-plus/icons-vue'

/** 与后端 Report.report_type / template_name 字段对应的业务约定（便于编制报告时选用） */
const presets = [
  {
    reportType: 'material',
    templateName: '混凝土抗压检测报告（演示）',
    scope: '混凝土试块强度',
    standardRef: 'GB/T 50081-2019',
  },
  {
    reportType: 'material',
    templateName: '钢筋拉伸检测报告（演示）',
    scope: '热轧钢筋力学性能',
    standardRef: 'GB/T 228.1-2021',
  },
  {
    reportType: 'aggregate',
    templateName: '骨料筛分检测报告（演示）',
    scope: '砂、石',
    standardRef: 'JGJ 52-2006',
  },
  {
    reportType: 'material',
    templateName: '通用材料检测报告',
    scope: '其他材料类',
    standardRef: '按委托项目',
  },
]

const techNotes = [
  {
    title: 'PDF 生成',
    body: '系统使用 Django 模板渲染 HTML，再由 WeasyPrint 转为 PDF（见后端 reports/generator.py）。若未安装 WeasyPrint，将退回占位二进制流。',
  },
  {
    title: 'template_name 字段',
    body: '在「报告」编制或编辑时填写「报告模板」名称，用于区分版式与结论表述；与原始记录模板（JSON）为不同概念。',
  },
  {
    title: '与原始记录的关系',
    body: '原始记录模板绑定检测方法/参数；报告模板名称用于报告实体展示。建议先完成原始记录模板，再统一报告命名规范。',
  },
]
</script>

<template>
  <div class="page-container report-tpl-guide">
    <div class="guide-hero">
      <el-icon class="guide-hero-icon" :size="36" color="#d97706"><Notebook /></el-icon>
      <div>
        <h1 class="guide-title">报告模板说明</h1>
        <p class="guide-lead">
          本模块说明<strong>检测报告实体</strong>中「报告类型」「报告模板名称」的填写约定。实际 PDF 版式由服务端 HTML 模板与生成器决定，不在此页单独维护 Word 文件。
        </p>
      </div>
    </div>

    <el-alert type="warning" :closable="false" show-icon class="guide-alert">
      <template #title>
        <span class="guide-alert-title"><el-icon><Warning /></el-icon> 先决条件</span>
      </template>
      建议在<strong>标准规范</strong>、<strong>项目参数库</strong>、<strong>原始记录模板</strong>就绪后，再统一编制报告并选用下表中的模板名称，避免报告结论与检测方法不一致。
    </el-alert>

    <el-card shadow="never" class="guide-card">
      <template #header>
        <span class="card-header-text">推荐「报告类型」与「报告模板名称」示例</span>
      </template>
      <p class="guide-table-hint">编制报告时在表单中填写 <code>report_type</code> 与 <code>template_name</code>，可与下表对齐；便于检索与统计。</p>
      <el-table :data="presets" stripe border style="width: 100%">
        <el-table-column prop="reportType" label="报告类型 (report_type)" width="200" />
        <el-table-column prop="templateName" label="报告模板名称 (template_name)" min-width="220" />
        <el-table-column prop="scope" label="适用范围" width="160" />
        <el-table-column prop="standardRef" label="常用标准引用" min-width="160" />
      </el-table>
    </el-card>

    <el-card shadow="never" class="guide-card">
      <template #header>
        <span class="card-header-text">技术说明</span>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="(n, i) in techNotes"
          :key="i"
          :timestamp="n.title"
          placement="top"
          type="info"
        >
          <p class="tech-note-body">{{ n.body }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<style scoped>
.report-tpl-guide {
  max-width: 1000px;
}

.guide-hero {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 20px 22px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fffbeb 0%, #fff 50%);
  border: 1px solid var(--el-border-color-lighter);
}

.guide-hero-icon {
  flex-shrink: 0;
  margin-top: 4px;
}

.guide-title {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 700;
}

.guide-lead {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--el-text-color-regular);
}

.guide-alert {
  margin-bottom: 20px;
  border-radius: 10px;
}

.guide-alert-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.guide-card {
  margin-bottom: 16px;
  border-radius: 12px;
}

.card-header-text {
  font-weight: 600;
  font-size: 15px;
}

.guide-table-hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.guide-table-hint code {
  font-size: 12px;
  padding: 2px 6px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.tech-note-body {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
  color: var(--el-text-color-regular);
}
</style>
