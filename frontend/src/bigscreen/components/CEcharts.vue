<template>
  <div ref="el" class="ink-chart"></div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['click', 'ready'])
const el = ref(null)
let chart = null

function render() {
  if (!chart) {
    chart = echarts.init(el.value)
    chart.on('click', (p) => emit('click', p))
    emit('ready', chart)
  }
  chart.setOption(props.option, true)
}
watch(() => props.option, render, { deep: true })
onMounted(render)
function onResize() { chart && chart.resize() }
window.addEventListener('resize', onResize)
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart && chart.dispose()
  chart = null
})
defineExpose({ getChart: () => chart })
</script>

<style lang="scss" scoped>
.ink-chart { width: 100%; height: 100%; }
</style>
