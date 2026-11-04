<template>
  <aside class="right-column">
    <!-- 徽州非遗名录 -->
    <CPanel class="col-panel">
      <template #title>徽州非遗名录</template>
      <template #content>
        <div class="heritage-viewport">
          <div class="heritage-track" :style="{ animationDuration: `${heritage.length * 2.2}s` }">
            <div v-for="(h, i) in heritageLoop" :key="i" class="heritage-row">
              <span class="h-name">{{ h.name }}</span>
              <span class="h-type">{{ h.type }}</span>
              <span class="h-level" :class="h.level === '国家级' ? 'nat' : 'prov'">{{ h.level }}</span>
            </div>
          </div>
        </div>
      </template>
    </CPanel>

    <!-- 文创品类 -->
    <CPanel class="col-panel">
      <template #title>文创品类 TOP8</template>
      <template #content>
        <CEcharts :option="craftOption" />
      </template>
    </CPanel>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import * as echarts from 'echarts'
import CPanel from './CPanel.vue'
import CEcharts from './CEcharts.vue'
import { HERITAGE_LIST, CRAFT_CATEGORIES } from '../data/huizhouData'
import { INK, inkAxisLabel } from '../modules/inkTheme'

const heritage = HERITAGE_LIST
// 复制两份实现无缝滚动
const heritageLoop = [...heritage, ...heritage]

const craftData = [...CRAFT_CATEGORIES].sort((a, b) => a.count - b.count).slice(-8)
const craftOption = ref({
  grid: { left: 10, right: 40, top: 8, bottom: 4, containLabel: true },
  xAxis: {
    type: 'value',
    show: false,
    max: (v) => Math.ceil(v.max * 1.2),
  },
  yAxis: {
    type: 'category',
    inverse: true,
    data: craftData.map((c) => c.name),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: inkAxisLabel('#241b15'),
  },
  series: [{
    type: 'bar',
    barWidth: 12,
    data: craftData.map((c, i) => ({
      value: c.count,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: 'rgba(79,118,129,0.35)' },
          { offset: 1, color: INK.blue },
        ]),
        borderRadius: [0, 6, 6, 0],
      },
    })),
    label: { show: true, position: 'right', formatter: '{c} 款', color: '#4a3a2a', fontSize: 12 },
    showBackground: true,
    backgroundStyle: { color: 'rgba(106,71,53,0.07)', borderRadius: 6 },
  }],
})
</script>

<style lang="scss" scoped>
.right-column {
  position: absolute;
  right: 22px;
  top: 96px;
  bottom: 108px;
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  z-index: 5;
}
.col-panel { flex: 1; min-height: 0; }

/* 非遗滚动 */
.heritage-viewport { height: 100%; overflow: hidden; }
.heritage-track {
  animation: scrollUp linear infinite;
}
@keyframes scrollUp {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}
.heritage-row {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 34px;
  padding: 0 8px;
  border-bottom: 1px dashed rgba(106, 71, 53, 0.18);
  font-size: 13px;
}
.h-name { flex: 1; color: #241b15; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.h-type { color: #8a7462; font-size: 12px; }
.h-level { font-size: 12px; padding: 1px 6px; border-radius: 2px; }
.h-level.nat { color: #f3ece3; background: #a03a2e; }
.h-level.prov { color: #6a4735; background: rgba(106, 71, 53, 0.16); }
</style>
