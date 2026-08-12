<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { generateImage } from '../api'
import { ElMessage } from 'element-plus'

/* ================= 生成参数 ================= */
const prompt = ref('细雨中的宏村马头墙，白墙黛瓦')
const mode = ref('quick')              // quick 快速单张 | batch 四宫格
const aspect = ref('1:1')
const styleKey = ref('ink')
const advanced = ref(false)
const negative = ref('')
const seedRandom = ref(true)
const seedVal = ref(42)

const STYLES = [
  { key: 'ink',    label: '水墨', prefix: '徽派水墨画，墨韵淋漓，浓淡相宜，' },
  { key: 'gongbi', label: '工笔', prefix: '徽州工笔画，线条细腻，设色清雅，' },
  { key: 'green',  label: '青绿', prefix: '青绿山水画，色彩明丽，' },
  { key: 'photo',  label: '写实', prefix: '高清写实摄影，真实光影与质感，' },
  { key: 'print',  label: '版画', prefix: '徽州木刻版画，黑白分明，刀味十足，' },
]
const ASPECTS = {
  '1:1': [1024, 1024],
  '3:4': [768, 1024],
  '4:5': [832, 1024],
  '9:16': [576, 1024],
  '16:9': [1024, 576],
}

/* ================= 灵感提示词 ================= */
const inspireCat = ref('徽派建筑')
const INSPIRE = {
  '徽派建筑': [
    '细雨中的宏村马头墙，白墙黛瓦',
    '西递古村月沼倒影，青瓦白墙',
    '徽州祠堂门楼砖雕，庄重肃穆',
    '棠樾牌坊群黄昏剪影',
    '渔梁坝老街石板巷，烟雨朦胧',
    '呈坎古村晒秋，五彩缤纷的瓦上人家',
  ],
  '山水烟雨': [
    '黄山云海松石，新安画派意境',
    '齐云山晨雾中的道观飞檐',
    '新安江山水画廊晨雾渔舟',
    '太平湖碧水青山，轻舟泛波',
    '塔川秋色，红叶乌桕染霜林',
  ],
  '器物文房': [
    '徽墨与歙砚的文房清供',
    '竹雕笔筒与青花瓷瓶案头',
    '宣纸晒纸工坊的阳光下',
    '油纸伞下的徽州雨巷',
    '镂空砖雕花窗前的桌案',
  ],
  '民俗人物': [
    '徽剧戏台上演出的旦角',
    '闹花灯节上提鱼灯的孩童',
    '制茶工坊里焙茶的匠人',
    '腊月里打年糕的热闹街巷',
  ],
}

/* ================= 画布状态 ================= */
const loading = ref(false)
const single = ref(null)
const grid = ref([null, null, null, null])
const gridLoading = ref([false, false, false, false])
const lightbox = ref(null)             // 放大的图片 src
const history = ref([])                // { prompt, style, aspect, src, thumb }

const allEmpty = computed(() => single.value === null && grid.value.every((c) => c === null))
const currentStyle = computed(() => STYLES.find((s) => s.key === styleKey.value))

function buildPrompt() {
  return (currentStyle.value ? currentStyle.value.prefix : '') + prompt.value.trim()
}
function nextSeed() {
  return seedRandom.value ? Math.floor(Math.random() * 100000) + 1 : seedVal.value
}

/* ================= 生成 ================= */
async function onGenerate() {
  if (!prompt.value.trim()) { ElMessage.warning('请输入画面描述'); return }
  if (loading.value) return
  loading.value = true
  const [w, h] = ASPECTS[aspect.value]
  const finalPrompt = buildPrompt()
  const opts = { negative_prompt: negative.value || null, width: w, height: h }

  if (mode.value === 'quick') {
    single.value = null
    try {
      const url = await generateImage(finalPrompt, { ...opts, seed: nextSeed() })
      single.value = url
      pushHistory({ prompt: prompt.value, style: styleKey.value, aspect: aspect.value, src: url })
    } catch (e) {
      ElMessage.error('生成失败，请确认图像生成服务已配置')
    } finally {
      loading.value = false
    }
  } else {
    // 四宫格：逐个 seed 生成，逐格填入（排队出图，不挤爆 GPU）
    grid.value = [null, null, null, null]
    gridLoading.value = [true, true, true, true]
    const base = seedRandom.value ? Math.floor(Math.random() * 100000) + 1 : seedVal.value
    for (let i = 0; i < 4; i++) {
      try {
        const url = await generateImage(finalPrompt, { ...opts, seed: base + i })
        grid.value[i] = url
        pushHistory({ prompt: prompt.value, style: styleKey.value, aspect: aspect.value, src: url })
      } catch (e) {
        grid.value[i] = null
      } finally {
        gridLoading.value[i] = false
      }
    }
    loading.value = false
  }
}

async function regenerateCell(i) {
  const [w, h] = ASPECTS[aspect.value]
  gridLoading.value[i] = true
  try {
    grid.value[i] = await generateImage(buildPrompt(), {
      negative_prompt: negative.value || null, width: w, height: h, seed: nextSeed(),
    })
  } catch (e) {
    ElMessage.error('重画失败，请稍后再试')
  } finally {
    gridLoading.value[i] = false
  }
}

async function regenerateSingle() {
  single.value = null
  loading.value = true
  const [w, h] = ASPECTS[aspect.value]
  try {
    single.value = await generateImage(buildPrompt(), {
      negative_prompt: negative.value || null, width: w, height: h, seed: nextSeed(),
    })
  } catch (e) {
    ElMessage.error('重画失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

function download(url) {
  const a = document.createElement('a')
  a.href = url
  a.download = 'huizhou_work.png'
  a.click()
}

function openLightbox(url) { lightbox.value = url }

/* ================= 历史带（缩略图存 localStorage，跨刷新可回看） ================= */
const HISTORY_KEY = 'mojyun_studio_history'

function makeThumb(url, size = 168, cb) {
  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    const r = size / Math.max(img.width, img.height)
    canvas.width = Math.max(1, Math.round(img.width * r))
    canvas.height = Math.max(1, Math.round(img.height * r))
    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
    cb(canvas.toDataURL('image/jpeg', 0.6))
  }
  img.onerror = () => cb('')
  img.src = url
}

function persistHistory() {
  const meta = history.value.map((h) => ({ prompt: h.prompt, style: h.style, aspect: h.aspect, thumb: h.thumb }))
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(meta)) } catch (e) { /* 超限则忽略 */ }
}

function pushHistory(item) {
  makeThumb(item.src, 168, (thumb) => {
    history.value.unshift({ ...item, thumb })
    history.value = history.value.slice(0, 12)
    persistHistory()
  })
}

function onHistoryClick(i) {
  const h = history.value[i]
  prompt.value = h.prompt
  styleKey.value = h.style
  if (h.aspect && ASPECTS[h.aspect]) aspect.value = h.aspect
  ElMessage.success('已载入「' + h.prompt.slice(0, 14) + '…」的创作参数，可点击生成重现')
  if (h.src) openLightbox(h.src)
}

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]')
    history.value = saved.map((h) => ({ ...h, src: null }))
  } catch (e) {
    history.value = []
  }
})

// 从四宫格切回快速单张时，若单张为空则复用已生成的格子，避免空白画布
watch(mode, (m) => {
  if (m === 'quick' && single.value === null) {
    const found = grid.value.find(Boolean)
    if (found) single.value = found
  }
})
</script>

<template>
  <div class="page">
    <div class="page-head">
      <h2>AI 徽画工坊</h2>
      <p>输入画面描述，选择画幅与风格，一键生成徽派水墨作品 —— 自研徽派 LoRA 模型 · 本地推理</p>
    </div>

    <div class="workbench">
      <!-- ===== 左：控制台 ===== -->
      <aside class="console">
        <div class="console-block">
          <label class="cb-label">画面描述</label>
          <el-input v-model="prompt" type="textarea" :rows="3" placeholder="例如：细雨中的宏村马头墙，白墙黛瓦" />
          <div class="style-chips">
            <button
              v-for="s in STYLES"
              :key="s.key"
              class="chip"
              :class="{ on: styleKey === s.key }"
              @click="styleKey = s.key"
            >{{ s.label }}</button>
          </div>
        </div>

        <div class="console-block inspire">
          <label class="cb-label">灵感提示词 · 点击填入上方描述</label>
          <div class="inspire-cats">
            <button
              v-for="c in Object.keys(INSPIRE)"
              :key="c"
              class="cat-btn"
              :class="{ on: inspireCat === c }"
              @click="inspireCat = c"
            >{{ c }}</button>
          </div>
          <div class="inspire-list">
            <span v-for="t in INSPIRE[inspireCat]" :key="t" class="inspire-item" @click="prompt = t">{{ t }}</span>
          </div>
        </div>

        <div class="console-block">
          <label class="cb-label">出图模式</label>
          <div class="mode-toggle">
            <button class="mode-btn" :class="{ on: mode === 'quick' }" @click="mode = 'quick'">
              <span class="mode-ico">⚡</span>快速 · 1 张<span class="mode-sub">约 30 秒</span>
            </button>
            <button class="mode-btn" :class="{ on: mode === 'batch' }" @click="mode = 'batch'">
              <span class="mode-ico">🖼</span>四宫格 · 4 张<span class="mode-sub">逐格出图</span>
            </button>
          </div>
        </div>

        <div class="console-block">
          <label class="cb-label">画幅</label>
          <div class="aspect-grid">
            <button
              v-for="(wh, k) in ASPECTS"
              :key="k"
              class="aspect-btn"
              :class="{ on: aspect === k }"
              @click="aspect = k"
            >
              <i class="ratio-box" :style="{ width: 18, height: 18 / (wh[0] / wh[1]) }"></i>{{ k }}
            </button>
          </div>
        </div>

        <div class="console-block">
          <button class="adv-toggle" @click="advanced = !advanced">
            <span class="adv-arrow" :class="{ open: advanced }">▸</span>高级选项
            <span class="adv-hint" v-if="!advanced">负面提示词 · seed</span>
          </button>
          <div v-if="advanced" class="adv-body">
            <label class="mini-label">负面提示词（不想出现的内容）</label>
            <el-input v-model="negative" type="textarea" :rows="2" placeholder="低质量、模糊、水印、畸形……" />
            <div class="seed-row">
              <label class="mini-label">随机 seed</label>
              <el-switch v-model="seedRandom" />
              <template v-if="!seedRandom">
                <label class="mini-label seed-val-label">固定</label>
                <el-input-number v-model="seedVal" :min="1" :max="999999" size="small" controls-position="right" />
              </template>
            </div>
          </div>
        </div>

        <button class="gen-btn" :class="{ busy: loading }" @click="onGenerate" :disabled="loading">
          <span class="gen-ink" v-if="loading"></span>
          <span>{{ loading ? '水墨晕染中…' : '🎨 生 成 作 品' }}</span>
        </button>
        <p class="engine-tip">引擎：本地 SDXL + 徽派 LoRA · 画幅 {{ aspect }} · {{ currentStyle.label }}风格</p>
      </aside>

      <!-- ===== 右：作品画布 ===== -->
      <section class="canvas">
        <div class="canvas-head">
          <span class="canvas-title">作品画布</span>
          <span class="canvas-status">
            <template v-if="loading">{{ mode === 'batch' ? '四宫格 · 逐格生成' : '快速 · 生成中' }}</template>
            <template v-else-if="single || grid.some(Boolean)">已生成 · 点击可放大</template>
            <template v-else>等待创作</template>
          </span>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && allEmpty" class="canvas-empty">
          <div class="empty-ink">🖌️</div>
          <p>你的水墨徽州将在此呈现</p>
          <span>输入描述 → 选择画幅风格 → 点击生成</span>
        </div>

        <!-- 四宫格 -->
        <div v-else-if="mode === 'batch'" class="grid">
          <div
            v-for="(cell, i) in 4"
            :key="i"
            class="grid-cell"
            :class="{ busy: gridLoading[i] }"
          >
            <div v-if="gridLoading[i]" class="ink-load">
              <span class="ink-drop"></span>
              <span class="ink-ring"></span>
              <span class="ink-text">水墨晕染中 · 第 {{ i + 1 }}/4</span>
            </div>
            <template v-else-if="cell">
              <img :src="cell" class="cell-img" alt="" @click="openLightbox(cell)" />
              <div class="cell-actions">
                <button @click="openLightbox(cell)">放大</button>
                <button @click="regenerateCell(i)">重画</button>
                <button @click="download(cell)">下载</button>
              </div>
            </template>
            <div v-else class="cell-slot">
              <span class="cell-badge">{{ aspect }}</span>
              <span class="cell-tip">待生成</span>
            </div>
          </div>
        </div>

        <!-- 快速单张 -->
        <div v-else class="single-wrap">
          <div v-if="loading && !single" class="ink-load big">
            <span class="ink-drop"></span>
            <span class="ink-ring"></span>
            <span class="ink-text">水墨晕染中…</span>
          </div>
          <template v-else-if="single">
            <img :src="single" class="single-img" alt="" @click="openLightbox(single)" />
            <div class="single-actions">
              <button @click="openLightbox(single)">放大</button>
              <button @click="regenerateSingle">换个想法重画</button>
              <button @click="download(single)">下载作品</button>
            </div>
          </template>
        </div>
      </section>
    </div>

    <!-- ===== 历史带 ===== -->
    <div v-if="history.length" class="history-band">
      <div class="hb-head"><span class="hb-title">最近创作</span><span class="hb-tip">点击回看参数，可一键重现</span></div>
      <div class="hb-track">
        <div v-for="(h, i) in history" :key="i" class="hb-item" @click="onHistoryClick(i)">
          <img v-if="h.thumb" :src="h.thumb" class="hb-thumb" alt="" />
          <div v-else class="hb-place">🖌️</div>
          <span class="hb-caption">{{ h.prompt }}</span>
        </div>
      </div>
    </div>

    <!-- ===== 放大灯箱 ===== -->
    <div v-if="lightbox" class="lightbox" @click.self="lightbox = null">
      <div class="lb-frame" @click.self="lightbox = null">
        <img :src="lightbox" class="lb-img" alt="" />
        <div class="lb-actions">
          <button @click="download(lightbox)">💾 下载</button>
          <button class="lb-close" @click="lightbox = null">✕ 关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ================= 布局 ================= */
.workbench {
  display: grid;
  grid-template-columns: 390px 1fr;
  gap: 20px;
  /* 两列默认拉伸，初始即等高（以左侧控制台高度为准） */
  align-items: stretch;
}
@media (max-width: 960px) {
  .workbench { grid-template-columns: 1fr; }
}

/* ================= 左：控制台 ================= */
.console {
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0) 45%),
    var(--paper-light);
  border: 1px solid rgba(106, 71, 53, 0.28);
  border-radius: 6px;
  box-shadow: 0 3px 16px rgba(74, 58, 42, 0.08);
  padding: 18px 18px 14px;
  position: sticky;
  top: 80px;
}
.console-block {
  padding: 12px 0;
  border-bottom: 1px dashed rgba(106, 71, 53, 0.22);
}
.console-block:last-child { border-bottom: none; }
.cb-label {
  display: block;
  font-family: var(--zh-font);
  font-size: 13px;
  letter-spacing: 3px;
  color: #6a4735;
  margin-bottom: 9px;
}

/* 风格 chips */
.style-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.chip {
  font-family: var(--zh-font);
  font-size: 13px;
  letter-spacing: 2px;
  color: #6a4735;
  background: rgba(106, 71, 53, 0.06);
  border: 1px dashed rgba(106, 71, 53, 0.4);
  border-radius: 3px;
  padding: 4px 14px;
  cursor: pointer;
  transition: all .2s;
}
.chip:hover { border-color: #a03a2e; color: #a03a2e; }
.chip.on {
  background: linear-gradient(120deg, #a03a2e, #6a4735);
  color: #f3ece3;
  border-style: solid;
  border-color: transparent;
}

/* 出图模式 */
.mode-toggle { display: flex; gap: 10px; }
.mode-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 11px 4px;
  font-family: var(--zh-font);
  font-size: 14px;
  letter-spacing: 1px;
  color: #6a4735;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(106, 71, 53, 0.3);
  border-radius: 5px;
  cursor: pointer;
  transition: all .2s;
}
.mode-btn:hover { border-color: rgba(160, 58, 46, 0.55); }
.mode-btn.on {
  background: linear-gradient(120deg, #a03a2e, #6a4735);
  color: #f3ece3;
  border-color: transparent;
  box-shadow: 0 0 0 2px rgba(160, 58, 46, 0.18);
}
.mode-ico { font-size: 18px; }
.mode-sub { font-size: 11px; opacity: .75; letter-spacing: 0; font-family: inherit; }

/* 画幅 */
.aspect-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.aspect-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  letter-spacing: 1px;
  color: #6a4735;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(106, 71, 53, 0.3);
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  transition: all .2s;
}
.aspect-btn:hover { border-color: rgba(160, 58, 46, 0.55); }
.aspect-btn.on {
  background: rgba(160, 58, 46, 0.12);
  border-color: #a03a2e;
  color: #a03a2e;
  font-weight: 700;
}
.ratio-box {
  display: inline-block;
  border: 1.5px solid currentColor;
  border-radius: 1px;
}

/* 高级选项 */
.adv-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--zh-font);
  font-size: 13px;
  letter-spacing: 2px;
  color: #6a4735;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 2px 0;
}
.adv-toggle:hover { color: #a03a2e; }
.adv-arrow { transition: transform .2s; display: inline-block; }
.adv-arrow.open { transform: rotate(90deg); }
.adv-hint { font-size: 11px; color: #b7a48e; margin-left: auto; letter-spacing: 0; }
.adv-body { margin-top: 10px; }
.mini-label {
  display: block;
  font-size: 12px;
  color: #8a7462;
  margin: 10px 0 5px;
}
.mini-label:first-child { margin-top: 0; }
.seed-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
.seed-val-label { margin: 0; }
.seed-row :deep(.el-input-number) { width: 120px; }

/* 生成按钮 */
.gen-btn {
  position: relative;
  width: 100%;
  margin-top: 16px;
  padding: 13px 0;
  font-family: var(--zh-font);
  font-size: 17px;
  font-weight: 800;
  letter-spacing: 5px;
  color: #f3ece3;
  background: linear-gradient(120deg, #a03a2e, #6a4735);
  border: none;
  border-radius: 5px;
  box-shadow: 0 4px 14px rgba(106, 58, 46, 0.3);
  cursor: pointer;
  transition: all .22s;
  overflow: hidden;
}
.gen-btn:hover { box-shadow: 0 6px 20px rgba(106, 58, 46, 0.4); transform: translateY(-1px); }
.gen-btn:disabled { cursor: not-allowed; transform: none; }
.gen-btn.busy { background: linear-gradient(120deg, #6a4735, #4e3324); }
.gen-ink {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(243, 236, 227, 0.35), transparent 40%),
    radial-gradient(circle at 80% 50%, rgba(243, 236, 227, 0.25), transparent 35%);
  animation: gen-sheen 1.8s ease-in-out infinite;
}
@keyframes gen-sheen {
  0%, 100% { transform: translateX(-40%); }
  50% { transform: translateX(40%); }
}
.engine-tip { font-size: 12px; color: #9a8470; text-align: center; margin: 10px 0 4px; }

/* 灵感 */
.inspire-cats { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.cat-btn {
  font-family: var(--zh-font);
  font-size: 12px;
  letter-spacing: 2px;
  color: #8a7462;
  background: transparent;
  border: 1px solid rgba(106, 71, 53, 0.28);
  border-radius: 3px;
  padding: 3px 12px;
  cursor: pointer;
  transition: all .2s;
}
.cat-btn:hover { color: #a03a2e; border-color: #a03a2e; }
.cat-btn.on {
  color: #f3ece3;
  background: linear-gradient(120deg, #a03a2e, #6a4735);
  border-color: transparent;
}
.inspire-list { display: flex; flex-direction: column; gap: 7px; }
.inspire-item {
  font-size: 13px;
  color: #6a4735;
  padding: 7px 10px;
  background: rgba(106, 71, 53, 0.05);
  border-radius: 4px;
  cursor: pointer;
  transition: all .18s;
  line-height: 1.5;
}
.inspire-item:hover {
  color: #a03a2e;
  background: rgba(160, 58, 46, 0.07);
  transform: translateX(3px);
}

/* ================= 右：画布 ================= */
.canvas {
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0) 45%),
    var(--paper-light);
  border: 1px solid rgba(106, 71, 53, 0.28);
  border-radius: 6px;
  box-shadow: 0 3px 16px rgba(74, 58, 42, 0.08);
  /* 高度随左侧控制台等高（grid 拉伸），画布内容自适应填满 */
  min-height: 0;
  padding: 16px;
  display: flex;
  flex-direction: column;
}
.canvas-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  margin-bottom: 14px;
  border-bottom: 1px dashed rgba(106, 71, 53, 0.25);
}
.canvas-title { font-family: var(--zh-font); font-size: 16px; letter-spacing: 3px; color: #4a3a2a; font-weight: 700; }
.canvas-status { font-size: 12px; color: #9a8470; letter-spacing: 1px; }

/* 空状态 */
.canvas-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9a8470;
}
.empty-ink { font-size: 58px; opacity: .55; animation: float 3.2s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.canvas-empty p { font-family: var(--zh-font); font-size: 19px; letter-spacing: 3px; color: #6a4735; margin: 14px 0 6px; }
.canvas-empty span { font-size: 12px; }

/* 四宫格 */
.grid {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 12px;
}
.grid-cell {
  position: relative;
  border-radius: 5px;
  overflow: hidden;
  background: rgba(230, 218, 199, 0.35);
  border: 1px solid rgba(106, 71, 53, 0.18);
  min-height: 220px;
}
.cell-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: zoom-in;
  display: block;
  animation: fade-in .5s ease;
  transition: transform .3s;
}
.grid-cell:hover .cell-img { transform: scale(1.04); }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
.cell-actions {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  display: flex;
  gap: 6px;
  padding: 8px;
  background: linear-gradient(transparent, rgba(36, 27, 21, 0.65));
  opacity: 0;
  transition: opacity .22s;
}
.grid-cell:hover .cell-actions { opacity: 1; }
.cell-actions button {
  flex: 1;
  font-size: 12px;
  letter-spacing: 1px;
  color: #f3ece3;
  background: rgba(160, 58, 46, 0.75);
  border: none;
  border-radius: 3px;
  padding: 5px 0;
  cursor: pointer;
  transition: background .2s;
}
.cell-actions button:hover { background: #a03a2e; }
.cell-slot {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #b7a48e;
}
.cell-badge {
  font-size: 20px;
  font-weight: 700;
  color: rgba(106, 71, 53, 0.4);
  border: 1.5px solid rgba(106, 71, 53, 0.3);
  border-radius: 4px;
  padding: 2px 10px;
  font-family: var(--num-font);
}
.cell-tip { font-size: 11px; letter-spacing: 1px; }

/* 水墨晕染 loading */
.ink-load {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: rgba(36, 27, 21, 0.6);
  background:
    radial-gradient(circle at 50% 42%, rgba(36, 27, 21, 0.06), transparent 60%),
    rgba(230, 218, 199, 0.35);
}
.ink-load.big { position: static; flex: 1; }
.ink-drop {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(36, 27, 21, 0.9) 0%, rgba(36, 27, 21, 0.3) 45%, transparent 70%);
  filter: blur(0.5px);
  animation: ink-pulse 1.7s ease-in-out infinite;
}
.ink-ring {
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 1.5px solid rgba(36, 27, 21, 0.4);
  animation: ink-ring 1.7s ease-out infinite;
}
@keyframes ink-pulse {
  0%, 100% { transform: scale(0.45); opacity: .5; }
  50% { transform: scale(1.1); opacity: 1; }
}
@keyframes ink-ring {
  0% { transform: scale(0.3); opacity: .9; }
  100% { transform: scale(1.4); opacity: 0; }
}
.ink-text { font-size: 12px; letter-spacing: 3px; }

/* 快速单张 */
.single-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 540px;
  gap: 14px;
}
.single-img {
  max-width: 100%;
  max-height: 520px;
  border-radius: 6px;
  box-shadow: 0 8px 28px rgba(36, 27, 21, 0.25);
  cursor: zoom-in;
  animation: fade-in .5s ease;
}
.single-actions { display: flex; gap: 10px; }
.single-actions button {
  font-size: 13px;
  letter-spacing: 2px;
  color: #f3ece3;
  background: linear-gradient(120deg, #6a4735, #241b15);
  border: none;
  border-radius: 4px;
  padding: 7px 18px;
  cursor: pointer;
  transition: all .2s;
}
.single-actions button:hover { background: linear-gradient(120deg, #a03a2e, #6a4735); }

/* ================= 历史带 ================= */
.history-band { margin-top: 24px; }
.hb-head {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}
.hb-title {
  font-family: var(--zh-font);
  font-size: 15px;
  letter-spacing: 3px;
  color: #4a3a2a;
  font-weight: 700;
  padding-left: 10px;
  border-left: 3px solid #c57b3a;
}
.hb-tip { font-size: 11px; color: #b7a48e; }
.hb-track {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.hb-track::-webkit-scrollbar { height: 6px; }
.hb-track::-webkit-scrollbar-thumb { background: rgba(160, 58, 46, 0.35); border-radius: 3px; }
.hb-item {
  flex: 0 0 128px;
  text-align: center;
  cursor: pointer;
  transition: all .2s;
}
.hb-item:hover { transform: translateY(-3px); }
.hb-thumb {
  width: 128px;
  height: 128px;
  object-fit: cover;
  border-radius: 5px;
  border: 1px solid rgba(106, 71, 53, 0.28);
  box-shadow: 0 3px 10px rgba(74, 58, 42, 0.14);
  display: block;
}
.hb-place {
  width: 128px;
  height: 128px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34px;
  background: rgba(230, 218, 199, 0.4);
  border-radius: 5px;
}
.hb-caption {
  display: block;
  margin-top: 6px;
  font-size: 11px;
  color: #6a4735;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ================= 灯箱 ================= */
.lightbox {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(24, 18, 14, 0.82);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: lb-fade .25s ease;
}
@keyframes lb-fade { from { opacity: 0; } to { opacity: 1; } }
.lb-frame { position: relative; max-width: 86vw; max-height: 86vh; }
.lb-img {
  max-width: 86vw;
  max-height: 78vh;
  border-radius: 4px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}
.lb-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 14px;
}
.lb-actions button {
  font-size: 13px;
  letter-spacing: 2px;
  color: #f3ece3;
  background: linear-gradient(120deg, #a03a2e, #6a4735);
  border: none;
  border-radius: 4px;
  padding: 8px 22px;
  cursor: pointer;
  transition: all .2s;
}
.lb-actions button:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4); }
.lb-actions .lb-close { background: rgba(255, 255, 255, 0.15); }
</style>
