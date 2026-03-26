<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => (route.meta.title as string) || '页面开发中')
</script>

<template>
  <div class="placeholder-page">
    <el-empty :description="`${title} - 功能开发中`">
      <el-button type="primary" @click="$router.back()">返回上一页</el-button>
    </el-empty>
  </div>
</template>

<style scoped>
.placeholder-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}
</style>
