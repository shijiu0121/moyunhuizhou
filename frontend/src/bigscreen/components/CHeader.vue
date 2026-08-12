<template>
  <header class="ink-header">
    <!-- 沉浸式导航行：印章 + 全局菜单 + 时钟 -->
    <div class="header-nav">
      <div class="nav-left">
        <span class="seal">墨蕴<br />徽州</span>
        <span class="nav-brand">墨蕴徽州 <i>· 徽文化数字文创智造平台</i></span>
      </div>
      <nav class="nav-menu">
        <router-link
          v-for="m in menus"
          :key="m.path"
          :to="m.path"
          class="nav-item"
          :class="{ active: route.path === m.path }"
        >{{ m.label }}</router-link>
      </nav>
      <div class="nav-right">
        <div class="clock">{{ clock }}</div>
        <div class="date">{{ dateText }}</div>
      </div>
    </div>

    <!-- 大标题行 -->
    <div class="header-main">
      <span class="ornament">—◆—</span>
      <h1 class="main-title">徽州意象馆</h1>
      <span class="ornament">—◆—</span>
    </div>

    <!-- 滚动资讯（位置后续再议，暂留） -->
    <div class="ticker">
      <span class="ticker-label">徽州要闻</span>
      <div class="ticker-viewport">
        <div class="ticker-track" :style="{ transform: `translateY(-${index * 100}%)` }">
          <div v-for="(n, i) in news" :key="i" class="ticker-item">{{ n }}</div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { NEWS_TICKER } from '../data/huizhouData'

const route = useRoute()
const menus = [
  { path: '/', label: '首页' },
  { path: '/bigscreen', label: '徽州意象馆' },
  { path: '/studio', label: 'AI徽画工坊' },
  { path: '/ask', label: '徽史问答官' },
  { path: '/craft', label: '文创印务局' },
]

const news = NEWS_TICKER
const index = ref(0)
const clock = ref('')
const dateText = ref('')
let timer = null
let clockTimer = null

function pad(n) { return String(n).padStart(2, '0') }
function tick() {
  const d = new Date()
  clock.value = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  dateText.value = `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${'日一二三四五六'[d.getDay()]}`
}
onMounted(() => {
  tick()
  clockTimer = setInterval(tick, 1000)
  timer = setInterval(() => { index.value = (index.value + 1) % news.length }, 4200)
})
onBeforeUnmount(() => {
  clearInterval(timer); clearInterval(clockTimer)
})
</script>

<style lang="scss" scoped>
.ink-header {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 136px;
  display: flex;
  flex-direction: column;
  z-index: 10;
}

/* ---------- 沉浸式导航行 ---------- */
.header-nav {
  height: 54px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 44px;
  background: rgba(250, 245, 236, 0.72);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  border-bottom: 1px solid rgba(106, 71, 53, 0.18);
  box-shadow: 0 2px 10px rgba(36, 27, 21, 0.06);
}
.nav-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.seal {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  background: #a03a2e;
  color: #f3ece3;
  font-family: 'STKaiti', 'KaiTi', '楷体', serif;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.2;
  text-align: center;
  padding-top: 8px;
  box-sizing: border-box;
  border-radius: 3px;
  box-shadow:
    inset 0 0 0 2px rgba(243, 236, 227, 0.45),
    inset 0 0 0 3px rgba(160, 58, 46, 0.9);
  transform: rotate(-4deg);
}
.nav-brand {
  font-family: 'STKaiti', '楷体', serif;
  font-size: 17px;
  font-weight: 800;
  letter-spacing: 3px;
  color: #241b15;
  white-space: nowrap;
}
.nav-brand i {
  font-style: normal;
  font-size: 11px;
  color: #8a7462;
  letter-spacing: 1px;
  margin-left: 6px;
}
.nav-menu {
  display: flex;
  gap: 8px;
}
.nav-item {
  color: #6a4735;
  text-decoration: none;
  padding: 6px 15px;
  font-size: 14px;
  letter-spacing: 2px;
  border-radius: 3px;
  position: relative;
  transition: all .22s;
}
.nav-item:hover {
  color: #a03a2e;
  background: rgba(160, 58, 46, 0.08);
}
.nav-item.active {
  color: #fff;
  background: linear-gradient(120deg, #a03a2e, #6a4735);
  box-shadow: 0 2px 8px rgba(160, 58, 46, 0.35);
}
.nav-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.clock {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 21px;
  color: #241b15;
  letter-spacing: 1px;
  line-height: 1.1;
}
.date { font-size: 12px; color: #6a4735; letter-spacing: 1px; }

/* ---------- 大标题行 ---------- */
.header-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
}
.ornament { color: #a03a2e; font-size: 12px; letter-spacing: 0; }
.main-title {
  margin: 0;
  font-size: 42px;
  font-weight: 900;
  letter-spacing: 16px;
  color: #241b15;
  font-family: 'STXingkai', 'KaiTi', '楷体', serif;
  text-shadow: 0 2px 0 rgba(160, 58, 46, 0.18);
}

/* ---------- 滚动资讯（位置后续再议，暂留） ---------- */
.ticker {
  position: absolute;
  bottom: -34px;
  left: 50%;
  transform: translateX(-50%);
  width: 900px;
  height: 34px;
  display: flex;
  align-items: center;
  background: rgba(36, 27, 21, 0.82);
  border-radius: 3px;
  overflow: hidden;
}
.ticker-label {
  flex-shrink: 0;
  padding: 0 14px;
  height: 100%;
  display: flex;
  align-items: center;
  color: #f3ece3;
  background: #a03a2e;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 3px;
}
.ticker-viewport { flex: 1; height: 100%; overflow: hidden; }
.ticker-track {
  transition: transform 0.6s ease;
  height: 100%;
}
.ticker-item {
  height: 34px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  color: #e9dcc5;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
