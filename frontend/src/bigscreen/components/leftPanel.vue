<template>
  <aside class="left-column">
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
import CPanel from './CPanel.vue'

// ---------- 平台数据 ----------
const stats = [
  { label: '知识库条目', value: '60' },
  { label: '徽州景点', value: '43' },
  { label: '非遗名录', value: '10' },
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
