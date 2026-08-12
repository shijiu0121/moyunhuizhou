<template>
  <footer class="ink-footer">
    <div class="footer-line"></div>
    <div class="stat-row">
      <div v-for="s in stats" :key="s.title" class="stat-item">
        <span class="stat-icon">{{ s.icon }}</span>
        <div class="stat-main">
          <div class="stat-title">{{ s.title }}</div>
          <div class="stat-number">
            <Vue3Odometer :value="s.value" :duration="1600" />
            <span class="stat-unit">{{ s.unit }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="footer-line"></div>
    <div class="footer-slogan">— 让 AI 画徽州 · 讲徽州 · 造徽州文创 —</div>
  </footer>
</template>

<script setup>
import Vue3Odometer from 'vue3-odometer'
import { FOOTER_STATS } from '../data/huizhouData'

const stats = FOOTER_STATS
</script>

<style lang="scss" scoped>
.ink-footer {
  position: absolute;
  left: 22px;
  right: 22px;
  bottom: 16px;
  height: 96px;
  text-align: center;
  z-index: 6;
}
.footer-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(106, 71, 53, 0.5), rgba(160, 58, 46, 0.7), rgba(106, 71, 53, 0.5), transparent);
}
.stat-row {
  display: flex;
  justify-content: center;
  gap: 48px;
  padding: 10px 0 6px;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.stat-icon {
  width: 38px;
  height: 38px;
  border-radius: 4px;
  background: linear-gradient(150deg, #a03a2e, #6a4735);
  color: #f3ece3;
  font-family: 'STKaiti', '楷体', serif;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(74, 58, 42, 0.35);
}
.stat-main { text-align: left; }
.stat-title { font-size: 12px; color: #6a4735; letter-spacing: 2px; margin-bottom: 2px; }
.stat-number { font-size: 26px; color: #241b15; display: flex; align-items: baseline; gap: 6px; }
.stat-number :deep(.odometer) {
  display: inline-block;
  font-family: 'Georgia', 'Times New Roman', serif;
  color: #a03a2e;
  font-weight: 700;
  letter-spacing: 1px;
}
.stat-number :deep(.odometer-digit) {
  display: inline-block;
  vertical-align: middle;
  position: relative;
  margin-right: 1px;
}
.stat-number :deep(.odometer-digit-spacer) {
  display: inline-block;
  vertical-align: middle;
  visibility: hidden;
}
.stat-number :deep(.odometer-digit-inner) {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  text-align: left;
}
.stat-number :deep(.odometer-digit .odometer-value) {
  display: block;
  transition: transform 0.5s ease;
}

.stat-unit { font-size: 12px; color: #6a4735; }
.footer-slogan {
  margin-top: 4px;
  font-size: 13px;
  letter-spacing: 4px;
  color: rgba(106, 71, 53, 0.75);
  font-family: 'STKaiti', '楷体', serif;
}
</style>
