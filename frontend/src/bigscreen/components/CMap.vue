<template>
  <div class="ink-map">
    <!-- 中央题字 -->
    <div class="map-seal-title">
      <span>徽</span><span>州</span><span>文</span><span>化</span><span>核</span><span>心</span><span>区</span>
    </div>
    <!-- 图例 -->
    <div class="map-legend">
      <span class="legend-title">景点分类</span>
      <span v-for="(color, key) in legendItems" :key="key" class="legend-item">
        <i :style="{ background: color }"></i>{{ key }}
      </span>
    </div>

    <CEcharts :option="mapOption" @click="onSiteClick" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as echarts from 'echarts'
import CEcharts from './CEcharts.vue'
import anhuiGeo from '../../assets/anhui.geo.json'
import { CULTURE_SITES, CATEGORY_COLORS, HUIZHOU_CIRCLE_CITIES, OTHER_CITY_SITES } from '../data/huizhouData'
import { INK } from '../modules/inkTheme'

echarts.registerMap('anhui', anhuiGeo)

const CAT_NAME = { nature: '山水自然', village: '徽州古村', culture: '人文古迹', leisure: '主题乐园' }
const legendItems = {
  山水自然: CATEGORY_COLORS.nature,
  徽州古村: CATEGORY_COLORS.village,
  人文古迹: CATEGORY_COLORS.culture,
  主题乐园: CATEGORY_COLORS.leisure,
}

// 徽州文化圈 8 市：暖色宣纸圈定 + 鎏金描边；其余 8 市：淡墨留白
function buildRegions() {
  return anhuiGeo.features.map((f) => {
    const name = f.properties.name
    const inCircle = HUIZHOU_CIRCLE_CITIES.includes(name)
    return {
      name,
      itemStyle: {
        areaColor: inCircle ? 'rgba(197,123,58,0.20)' : 'rgba(106,71,53,0.07)',
        borderColor: inCircle ? 'rgba(160,58,46,0.55)' : 'rgba(106,71,53,0.35)',
        borderWidth: inCircle ? 1.6 : 1,
        shadowColor: inCircle ? 'rgba(197,123,58,0.4)' : 'rgba(106,71,53,0.2)',
        shadowBlur: inCircle ? 12 : 2,
      },
      label: {
        show: true,
        fontSize: 11,
        color: inCircle ? INK.inkSoft : 'rgba(106,71,53,0.55)',
        fontWeight: inCircle ? 700 : 400,
        fontFamily: '"Kaiti SC","STKaiti","楷体",serif',
      },
      emphasis: {
        itemStyle: { areaColor: inCircle ? 'rgba(197,123,58,0.38)' : 'rgba(106,71,53,0.18)' },
      },
    }
  })
}

// 43 处景点：按类别着色（彩点）
const scatterData = CULTURE_SITES.map((s) => ({
  name: s.name,
  city: s.city,
  county: s.county,
  level: s.level,
  cat: s.cat,
  catName: CAT_NAME[s.cat] || s.cat,
  desc: s.desc,
  value: [s.lng, s.lat, s.value],
}))

// 徽州文化圈外 8 市：简略标注（淡墨灰点 + 小字）
const sparseData = OTHER_CITY_SITES.map((s) => ({
  name: s.name,
  tag: s.tag,
  value: [s.lng, s.lat],
}))

const mapOption = ref({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(36,27,21,0.9)',
    borderColor: 'rgba(197,123,58,0.8)',
    borderWidth: 1,
    padding: [8, 12],
    textStyle: { color: '#f3ece3', fontSize: 13, fontFamily: '"Kaiti SC","楷体",serif' },
    formatter: (p) => {
      if (p.seriesName === '徽州文化景点') {
        const d = scatterData[p.dataIndex]
        const c = CATEGORY_COLORS[d.cat]
        return `<b style="color:#fff">${d.name}</b>
                <span style="color:#c9b696">（${d.county} · ${d.level}）</span><br/>
                <span style="color:${c}">●</span> ${d.catName}<br/>
                ${d.desc}<br/>
                <span style="color:#e9b76b">年游客量（示例）${d.value[2]} 万人次</span>`
      }
      if (p.seriesName === '文化圈外标注') {
        const s = sparseData[p.dataIndex]
        return `<b style="color:#fff">${s.name}</b><br/><span style="color:#c9b696">${s.tag}</span>`
      }
      return p.name
    },
  },
  geo: {
    map: 'anhui',
    roam: true,
    zoom: 1.15,
    center: [117.3, 30.4],
    layoutCenter: ['50%', '53%'],
    layoutSize: '92%',
    regions: buildRegions(),
    itemStyle: {
      areaColor: 'rgba(106,71,53,0.07)',
      borderColor: 'rgba(106,71,53,0.35)',
      borderWidth: 1,
    },
    emphasis: {
      label: { show: true, color: '#a03a2e', fontWeight: 700, fontSize: 13 },
      itemStyle: { areaColor: 'rgba(197,123,58,0.38)' },
    },
    select: { disabled: true },
  },
  series: [
    {
      name: '徽州文化景点',
      type: 'scatter',
      coordinateSystem: 'geo',
      data: scatterData,
      symbol: 'circle',
      symbolSize: (val) => 7 + Math.sqrt(val[2]) * 0.45,
      itemStyle: (params) => ({
        color: CATEGORY_COLORS[scatterData[params.dataIndex].cat],
        borderColor: '#f3ece3',
        borderWidth: 1.5,
        shadowBlur: 8,
        shadowColor: 'rgba(36,27,21,0.3)',
      }),
      label: {
        show: true,
        formatter: (p) => scatterData[p.dataIndex].name,
        position: 'right',
        distance: 5,
        fontSize: 12,
        color: '#241b15',
        fontWeight: 700,
        fontFamily: '"STKaiti","楷体",serif',
        textShadowBlur: 4,
        textShadowColor: 'rgba(243,236,227,0.95)',
      },
      emphasis: {
        itemStyle: { scale: 1.6 },
        label: { fontSize: 14 },
      },
    },
    {
      name: '客流脉冲',
      type: 'effectScatter',
      coordinateSystem: 'geo',
      data: scatterData,
      symbolSize: 8,
      rippleEffect: { brushType: 'stroke', scale: 3, period: 3.6 },
      itemStyle: (params) => ({
        color: CATEGORY_COLORS[scatterData[params.dataIndex].cat],
        shadowBlur: 6,
        shadowColor: 'rgba(36,27,21,0.4)',
      }),
      emphasis: { scale: 1.4 },
      zlevel: 2,
    },
    {
      name: '文化圈外标注',
      type: 'scatter',
      coordinateSystem: 'geo',
      data: sparseData,
      symbol: 'circle',
      symbolSize: 5,
      itemStyle: {
        color: 'rgba(106,71,53,0.45)',
        borderColor: '#f3ece3',
        borderWidth: 1,
      },
      label: {
        show: true,
        formatter: (p) => sparseData[p.dataIndex].name,
        position: 'right',
        distance: 4,
        fontSize: 10,
        color: 'rgba(106,71,53,0.62)',
        fontFamily: '"Kaiti SC","STKaiti","楷体",serif',
      },
      emphasis: { label: { fontSize: 11 } },
      zlevel: 1,
    },
  ],
})

function onSiteClick(p) {
  if (p.seriesName !== '徽州文化景点') return
  window.dispatchEvent(new CustomEvent('huizhou:site', { detail: scatterData[p.dataIndex] }))
}
</script>

<style lang="scss" scoped>
.ink-map {
  position: absolute;
  left: 288px;
  top: 88px;
  right: 288px;
  bottom: 112px;
}
.map-seal-title {
  position: absolute;
  bottom: 22px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 3;
  pointer-events: none;
  span {
    font-family: 'STKaiti', '楷体', serif;
    font-size: 24px;
    font-weight: 700;
    color: rgba(36, 27, 21, 0.14);
    letter-spacing: 6px;
  }
}
.map-legend {
  position: absolute;
  top: 8px;
  left: 48px;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(250, 245, 236, 0.85);
  border: 1px solid rgba(106, 71, 53, 0.25);
  border-radius: 4px;
  padding: 5px 12px;
  backdrop-filter: blur(2px);
}
.legend-title {
  font-size: 12px;
  color: #6a4735;
  letter-spacing: 2px;
  border-right: 1px solid rgba(106, 71, 53, 0.3);
  padding-right: 10px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #4a3a2a;
  i {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
    border: 1px solid rgba(255, 255, 255, 0.8);
  }
}
</style>
