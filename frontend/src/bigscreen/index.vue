<template>
  <div class="bigscreen" :style="bigscreenStyle">
    <!-- 背景层：宣纸 + 水墨 -->
    <div class="bg bg-paper"></div>
    <div class="bg bg-wash"></div>

    <!-- 内容层 -->
    <CHeader />
    <CMap />
    <LeftPanel />
    <RightPanel />
    <CFooter />

    <!-- 数据声明 -->
    <div class="data-note">{{ dataNote }}</div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import autofit from 'autofit.js'
import CHeader from './components/CHeader.vue'
import CMap from './components/CMap.vue'
import LeftPanel from './components/leftPanel.vue'
import RightPanel from './components/rightPanel.vue'
import CFooter from './components/CFooter.vue'
import { DATA_NOTE } from './data/huizhouData'
import footerBg from '../assets/huizhou-footer.jpg'

const dataNote = DATA_NOTE
// 页脚实拍背景（经 Vite 打包为资源 URL，注入 CSS 变量供 ::after 使用）
const bigscreenStyle = { '--footer-bg': `url(${footerBg})` }

onMounted(() => {
  autofit.init({
    el: '.bigscreen',
    dw: 1920,
    dh: 1080,
    resize: true,
    limit: 0.2,     // 最小缩放 0.2，避免过小失真
    allowScroll: true,
  })
})
onBeforeUnmount(() => {
  autofit.off()
})
</script>

<style lang="scss" scoped>
.bigscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 1920px;
  height: 1080px;
  transform-origin: top left;
  overflow: hidden;
  background: #f3ece3;
}

.bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.bg-paper {
  background:
    radial-gradient(circle at 50% 42%, rgba(255, 255, 255, 0.65), transparent 62%),
    radial-gradient(ellipse at 12% 88%, rgba(106, 71, 53, 0.10), transparent 45%),
    radial-gradient(ellipse at 90% 12%, rgba(197, 123, 58, 0.08), transparent 40%),
    #f3ece3;
}
.bg-wash {
  /* 下方远山 */
  background:
    linear-gradient(180deg, transparent 68%, rgba(106, 71, 53, 0.10) 100%);
  /* 墨晕 */
}
/* 底部实拍图背景：黄山云海（实景照片 · 已做宣纸淡化处理） */
.bigscreen::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 190px;
  pointer-events: none;
  /* 顶部纸色渐隐，与页面宣纸底无缝衔接 */
  background-image: linear-gradient(180deg, rgba(243, 236, 227, 0.88) 0%, rgba(243, 236, 227, 0.25) 28%, rgba(243, 236, 227, 0) 48%), var(--footer-bg);
  background-repeat: no-repeat;
  background-position: center bottom;
  background-size: 100% 100%;
}

.data-note {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 2px;
  text-align: center;
  font-size: 10px;
  letter-spacing: 1px;
  color: rgba(106, 71, 53, 0.45);
  z-index: 20;
  pointer-events: none;
}
</style>
