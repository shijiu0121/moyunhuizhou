<template>
  <aside class="left-column">
    <!-- 徽文化目的地 TOP8 -->
    <CPanel class="col-panel">
      <template #title>徽文化目的地 TOP8</template>
      <template #content>
        <CEcharts :option="rankOption" @ready="startRankLoop" />
      </template>
    </CPanel>

    <!-- 游客画像 -->
    <CPanel class="col-panel">
      <template #title>游客画像</template>
      <template #content>
        <div class="age-wrap">
          <CEcharts :option="ageOption" />
          <div class="source-box">
            <div class="source-title">客源构成</div>
            <div class="source-chips">
              <span v-for="s in sourceList" :key="s.name" class="chip">
                {{ s.name }} <b>{{ s.value }}%</b>
              </span>
            </div>
          </div>
        </div>
      </template>
    </CPanel>

    <!-- 知识库 / 平台统计 -->
    <CPanel class="col-panel">
      <template #title>平台数据</template>
      <template #content>
        <div class="stat-grid">
          <div class="stat-item" v-for="s in stats" :key="s.label">
            <div class="stat-num">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
      </template>
    </CPanel>
  </aside>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import CPanel from './CPanel.vue'
import CEcharts from './CEcharts.vue'
import { SITE_RANKING, VISITOR_AGE, VISITOR_SOURCE } from '../data/huizhouData'
import { INK, inkAxisLabel } from '../modules/inkTheme'

// ---------- 目的地排行 ----------
const rankData = SITE_RANKING
const topValue = rankData[0].value
const rankOption = ref({
  grid: { left: 10, right: 44, top: 4, bottom: 4, containLabel: true },
  xAxis: { type: 'value', show: false, max: (v) => Math.ceil(v.max * 1.12) },
  yAxis: {
    type: 'category',
    inverse: true,
    data: rankData.map((d) => d.label),
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: inkAxisLabel('#241b15'),
  },
  series: [{
    type: 'bar',
    barWidth: 11,
    data: rankData.map((d) => ({
      value: d.value,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: 'rgba(36,27,21,0.35)' },
          { offset: 1, color: d.value === topValue ? 'rgba(160,58,46,0.9)' : 'rgba(106,71,53,0.85)' },
        ]),
        borderRadius: [0, 7, 7, 0],
      },
    })),
    label: {
      show: true,
      position: 'right',
      formatter: '{c} 万',
      color: '#6a4735',
      fontSize: 12,
    },
    backgroundStyle: { color: 'rgba(106,71,53,0.08)', borderRadius: 7 },
    showBackground: true,
  }],
})
let rankTimer = null
let rankIdx = 0
function startRankLoop(chart) {
  if (rankTimer) return
  rankTimer = setInterval(() => {
    chart.dispatchAction({ type: 'downplay', seriesIndex: 0 })
    chart.dispatchAction({ type: 'highlight', seriesIndex: 0, dataIndex: rankIdx })
    rankIdx = (rankIdx + 1) % rankData.length
  }, 1800)
}
onUnmounted(() => {
  if (rankTimer) clearInterval(rankTimer)
  rankTimer = null
})

// ---------- 游客画像：年龄环形 ----------
const ageOption = ref({
  tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
  legend: {
    orient: 'vertical',
    right: 4,
    top: 'middle',
    itemWidth: 10,
    itemHeight: 10,
    itemGap: 8,
    textStyle: { color: '#4a3a2a', fontSize: 12 },
  },
  series: [{
    type: 'pie',
    radius: ['52%', '72%'],
    center: ['32%', '50%'],
    avoidLabelOverlap: true,
    itemStyle: { borderRadius: 5, borderColor: '#faf5ec', borderWidth: 2 },
    label: { show: true, position: 'center', formatter: '游客\n画像', color: '#6a4735', fontSize: 13, fontWeight: 700, lineHeight: 18 },
    emphasis: { label: { show: true, fontSize: 15 } },
    data: VISITOR_AGE.map((a, i) => ({
      ...a,
      itemStyle: { color: [INK.brown, INK.orange, INK.blue, INK.inkSoft][i] },
    })),
  }],
})
const sourceList = VISITOR_SOURCE

// ---------- 平台数据 ----------
const stats = [
  { label: '知识库条目', value: '1,280' },
  { label: '徽州景点', value: '120+' },
  { label: '非遗名录', value: '38' },
]
</script>

<style lang="scss" scoped>
.left-column {
  position: absolute;
  left: 22px;
  top: 96px;
  bottom: 108px;
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  z-index: 5;
}
.col-panel { flex: 1; min-height: 0; }

.age-wrap { height: 100%; display: flex; flex-direction: column; }
.source-box { padding: 4px 2px 0; }
.source-title {
  font-size: 12px;
  color: #6a4735;
  margin-bottom: 6px;
  letter-spacing: 2px;
  border-left: 3px solid #a03a2e;
  padding-left: 6px;
}
.source-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  font-size: 12px;
  color: #4a3a2a;
  background: rgba(106, 71, 53, 0.10);
  border: 1px solid rgba(106, 71, 53, 0.2);
  border-radius: 3px;
  padding: 2px 8px;
  b { color: #a03a2e; margin-left: 2px; }
}

.stat-grid { height: 100%; display: flex; flex-direction: column; justify-content: space-around; gap: 8px; }
.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: linear-gradient(90deg, rgba(106,71,53,0.10), rgba(106,71,53,0.02));
  border-left: 3px solid #6a4735;
}
.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #241b15;
  font-family: 'Georgia', 'Times New Roman', serif;
}
.stat-label { font-size: 13px; color: #6a4735; letter-spacing: 1px; }
</style>
