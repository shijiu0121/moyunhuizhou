<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const menus = [
  { path: '/', label: '首页' },
  { path: '/bigscreen', label: '徽州意象馆' },
  { path: '/studio', label: 'AI徽画工坊' },
  { path: '/ask', label: '徽史问答官' },
  { path: '/craft', label: '文创印务局' },
]
</script>

<template>
  <router-view v-if="route.meta.fullscreen" />
  <el-container v-else class="app-shell">
    <el-header class="navbar" height="64px">
      <div class="navbar-inner">
        <span class="logo-seal">墨蕴<br />徽州</span>
        <span class="logo-text">墨蕴徽州 <i>· 徽文化数字文创智造平台</i></span>
        <nav class="menu">
          <router-link v-for="m in menus" :key="m.path" :to="m.path" class="menu-item"
                       :class="{ active: route.path === m.path }">
            {{ m.label }}
          </router-link>
        </nav>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: transparent;
}
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0;
  background: rgba(250, 245, 236, 0.85);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 2px 12px rgba(74, 58, 42, 0.08);
  border-bottom: 1px solid rgba(106, 71, 53, 0.18);
}
.navbar-inner {
  max-width: 1100px;
  height: 64px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.logo-seal {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  background: #a03a2e;
  color: #f3ece3;
  font-family: var(--zh-font);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  text-align: center;
  padding-top: 8px;
  border-radius: 3px;
  box-shadow: inset 0 0 0 2px rgba(243, 236, 227, 0.45);
}
.logo-text {
  color: #241b15;
  font-family: var(--zh-font);
  font-size: 19px;
  font-weight: 800;
  letter-spacing: 4px;
  white-space: nowrap;
}
.logo-text i {
  font-style: normal;
  font-size: 12px;
  color: #8a7462;
  letter-spacing: 1px;
  margin-left: 8px;
}
.menu {
  margin-left: auto;
  display: flex;
  gap: 6px;
}
.menu-item {
  color: #6a4735;
  text-decoration: none;
  padding: 7px 14px;
  font-size: 14px;
  letter-spacing: 2px;
  border-radius: 3px;
  position: relative;
  transition: all .22s;
}
.menu-item:hover {
  color: #a03a2e;
  background: rgba(160, 58, 46, 0.08);
}
.menu-item.active {
  color: #a03a2e;
  background: rgba(160, 58, 46, 0.10);
}
.menu-item.active::after {
  content: '';
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 3px;
  height: 2px;
  background: #c57b3a;
}
.app-main {
  padding: 0;
}
</style>
