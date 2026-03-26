<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

const collapsed = ref(false)
</script>

<template>
  <div class="main-layout">
    <aside
      class="layout-sidebar"
      :style="{ width: collapsed ? '64px' : '220px' }"
    >
      <Sidebar v-model:collapsed="collapsed" />
    </aside>

    <div
      class="layout-main"
      :style="{ marginLeft: collapsed ? '64px' : '220px' }"
    >
      <Header />
      <main class="layout-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.main-layout {
  width: 100%;
  height: 100%;
}

.layout-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  transition: width 0.2s;
  overflow: hidden;
}

.layout-main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.2s;
}

.layout-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
}
</style>
