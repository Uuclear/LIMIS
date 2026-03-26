<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const title = route.meta.title as string
</script>

<template>
  <div class="page-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>{{ title }}</span>
        </div>
      </template>
      <el-empty description="功能开发中" />
    </el-card>
  </div>
</template>
