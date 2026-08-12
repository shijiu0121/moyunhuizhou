<script setup>
import { ref, computed } from 'vue'
import { exportProduct } from '../api'
import { ElMessage } from 'element-plus'

/* ---------------- 成品模板 ---------------- */
const TEMPLATES = [
  { value: 'postcard', label: '明信片', desc: '竖版卡片 · 宣纸纸面', tn: 'pc' },
  { value: 'poster',   label: '海报',   desc: '竖版挂画 · 装裱入框', tn: 'po' },
  { value: 'bookmark', label: '书签',   desc: '竖条书签 · 朱砂题签', tn: 'bm' },
]

const EXAMPLES = [
  '宏村月沼的水墨画，白墙黛瓦，倒影入水',
  '黄山云海，群峰浮沉，墨色晕染',
  '徽派马头墙村落，晨雾缭绕',
]

/* ---------------- 表单状态 ---------------- */
const prompt = ref('宏村月沼的水墨画，白墙黛瓦，倒影入水')
const title = ref('墨蕴徽州')
const subtitle = ref('宏村 · 月沼')
const template = ref('postcard')
const loading = ref(false)
const imageUrl = ref('')
const seed = ref(null) // 首次生成时取随机种子；换模板/改版式复用同画

const templateLabel = computed(() => TEMPLATES.find(t => t.value === template.value)?.label || '')

function randSeed() {
  return Math.floor(Math.random() * 100000)
}

async function onExport(forceNew = false) {
  if (!prompt.value.trim()) { ElMessage.warning('请输入画面描述'); return }
  if (forceNew || seed.value === null) seed.value = randSeed()
  loading.value = true
  try {
    imageUrl.value = await exportProduct(prompt.value, {
      title: title.value,
      subtitle: subtitle.value,
      template: template.value,
      seed: seed.value,
    })
  } catch (e) {
    ElMessage.error('文创生成失败，请确认后端已启动且图像服务已配置')
  } finally {
    loading.value = false
  }
}

function onReroll() { onExport(true) }

function download() {
  if (!imageUrl.value) return
  const a = document.createElement('a')
  a.href = imageUrl.value
  a.download = `${templateLabel.value}-${title.value || '徽州文创'}.png`
  a.click()
}
</script>

<template>
  <div class="page craft-page">
    <div class="page-head">
      <h2>文创印务局</h2>
      <p>把 AI 画作一键制成文创成品 —— 明信片 / 海报 / 书签，让徽州之美被带走</p>
    </div>

    <div class="craft-layout">
      <!-- 左侧：设计台 -->
      <div class="ink-card craft-console">
        <div class="sec-label">一 · 成稿画面</div>
        <el-input
          v-model="prompt"
          type="textarea"
          :rows="3"
          resize="none"
          placeholder="描述想要的徽州画面…"
        />
        <div class="exam-chips">
          <span v-for="ex in EXAMPLES" :key="ex" @click="prompt = ex">{{ ex }}</span>
        </div>

        <div class="sec-label sec-gap">二 · 成品类型</div>
        <div class="tpl-grid">
          <div
            v-for="t in TEMPLATES"
            :key="t.value"
            class="tpl-card"
            :class="{ active: template === t.value }"
            @click="template = t.value"
          >
            <span class="tpl-thumb" :class="`tn-${t.tn}`">
              <i class="tt-img"></i><i class="tt-bar"></i>
            </span>
            <b>{{ t.label }}</b>
            <em>{{ t.desc }}</em>
          </div>
        </div>

        <div class="sec-label sec-gap">三 · 版式定制</div>
        <div class="form-grid">
          <label class="f-item">
            <span>成品标题</span>
            <el-input v-model="title" maxlength="10" show-word-limit placeholder="墨蕴徽州" />
          </label>
          <label class="f-item">
            <span>落款副题</span>
            <el-input v-model="subtitle" maxlength="16" placeholder="宏村 · 月沼" />
          </label>
        </div>

        <div class="console-actions">
          <button class="gen-btn" :disabled="loading" @click="onExport()">
            {{ loading ? '排版中…' : (imageUrl ? '重新生成' : '生成文创成品') }}
          </button>
          <button class="ghost-btn" :disabled="loading || !imageUrl" @click="onReroll">
            换一幅画
          </button>
        </div>
        <p class="engine-tip">同 seed 复用同一幅画 · 切换模板或改版式后点「重新生成」即可重排</p>
      </div>

      <!-- 右侧：实景展示台 -->
      <div class="ink-card craft-scene" :class="`scene-${template}`">
        <!-- 场景道具（纯装饰） -->
        <template v-if="template === 'postcard'">
          <div class="pen"></div>
          <div class="inkstone"></div>
        </template>
        <template v-else-if="template === 'poster'">
          <div class="wire"></div>
          <div class="nail"></div>
          <div class="floor"></div>
        </template>
        <template v-else>
          <div class="book">
            <div class="page-left"><div class="lines"></div></div>
            <div class="page-right"><div class="lines"></div></div>
            <div class="spine"></div>
          </div>
        </template>

        <!-- 成品 -->
        <div v-if="imageUrl" class="scene-product" :class="`product-${template}`">
          <img :src="imageUrl" :alt="`${title} · ${templateLabel}`" />
        </div>

        <!-- 空态 -->
        <div v-else class="scene-empty">
          <div class="empty-seal">印</div>
          <p>文创成品将在此呈现</p>
          <span>选择模板、写上标题，一键制成实物</span>
        </div>

        <!-- 生成中遮罩 -->
        <div v-if="loading" class="scene-loading">
          <div class="ld-ring"></div>
          <span>正在生成与排版…</span>
        </div>
      </div>
    </div>

    <!-- 底部操作条 -->
    <div v-if="imageUrl && !loading" class="craft-foot">
      <div class="foot-info">
        <span class="foot-tag">{{ templateLabel }}</span>
        <span class="foot-seed">seed {{ seed }}</span>
        <span class="foot-tip">已生成成品 · 可直接下载 PNG</span>
      </div>
      <button class="dl-btn" @click="download">下载成品</button>
    </div>
  </div>
</template>

<style scoped>
.craft-page { max-width: 1180px; }
.craft-layout {
  display: grid;
  grid-template-columns: 5fr 7fr;
  gap: 20px;
  align-items: stretch;
}
@media (max-width: 900px) {
  .craft-layout { grid-template-columns: 1fr; }
}

/* ============ 左侧设计台 ============ */
.craft-console { display: flex; flex-direction: column; }
.sec-label {
  font-family: var(--zh-font);
  font-size: 14px;
  letter-spacing: 3px;
  color: var(--brown);
  margin-bottom: 10px;
  padding-left: 10px;
  border-left: 3px solid var(--red);
}
.sec-gap { margin-top: 20px; }

.exam-chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.exam-chips span {
  padding: 4px 10px;
  font-size: 12px;
  color: var(--brown);
  border: 1px dashed rgba(106, 71, 53, 0.4);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all .2s;
}
.exam-chips span:hover { color: var(--red); border-color: var(--red); background: rgba(160, 58, 46, 0.06); }

/* 模板卡片 */
.tpl-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.tpl-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 14px 6px 12px;
  border: 1px solid rgba(106, 71, 53, 0.28);
  border-radius: 6px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.5);
  transition: all .2s;
}
.tpl-card:hover { border-color: rgba(160, 58, 46, 0.5); transform: translateY(-2px); }
.tpl-card.active {
  border-color: var(--red);
  background: rgba(160, 58, 46, 0.06);
  box-shadow: 0 0 0 2px rgba(160, 58, 46, 0.16);
}
.tpl-card b { font-family: var(--zh-font); font-size: 14px; letter-spacing: 2px; color: var(--ink); }
.tpl-card em { font-style: normal; font-size: 11px; color: var(--ink-line); }

/* 模板缩略小样 */
.tpl-thumb {
  position: relative;
  display: block;
  background: #f6f1e8;
  border: 1px solid rgba(106, 71, 53, 0.35);
  border-radius: 2px;
  margin-bottom: 2px;
  overflow: hidden;
}
.tpl-thumb .tt-img {
  position: absolute;
  top: 4px; left: 4px; right: 4px;
  background: linear-gradient(135deg, #c9c0b2, #8a8476);
  display: block;
}
.tpl-thumb .tt-bar {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  background: rgba(106, 71, 53, 0.65);
  display: block;
}
.tn-pc { width: 34px; height: 48px; }
.tn-pc .tt-img { height: 62%; }
.tn-pc .tt-bar { height: 22%; }
.tn-po { width: 36px; height: 52px; }
.tn-po .tt-img { top: 20%; height: 60%; }
.tn-po .tt-bar { height: 12%; background: var(--red); }
.tn-bm { width: 20px; height: 52px; }
.tn-bm .tt-img { top: 20%; height: 56%; }
.tn-bm .tt-bar { height: 16%; background: var(--red); }

/* 版式表单 */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.f-item { display: flex; flex-direction: column; gap: 6px; }
.f-item span { font-size: 12px; color: var(--ink-soft); letter-spacing: 1px; }

/* 按钮 */
.console-actions { display: flex; gap: 10px; margin-top: 18px; }
.gen-btn {
  flex: 1;
  padding: 11px 0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--paper-light);
  font-family: var(--zh-font);
  font-size: 15px;
  letter-spacing: 4px;
  background: linear-gradient(120deg, var(--red), #6a4735);
  box-shadow: 0 2px 10px rgba(160, 58, 46, 0.3);
  transition: all .2s;
}
.gen-btn:hover:not(:disabled) { filter: brightness(1.08); }
.gen-btn:disabled { opacity: .5; cursor: not-allowed; }
.ghost-btn {
  padding: 11px 18px;
  border: 1px solid rgba(106, 71, 53, 0.4);
  border-radius: 4px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.6);
  color: var(--brown);
  font-family: var(--zh-font);
  font-size: 14px;
  letter-spacing: 2px;
  transition: all .2s;
}
.ghost-btn:hover:not(:disabled) { color: var(--red); border-color: var(--red); background: rgba(160, 58, 46, 0.06); }
.ghost-btn:disabled { opacity: .4; cursor: not-allowed; }
.engine-tip { margin: 10px 0 0; font-size: 11px; color: var(--ink-line); letter-spacing: 1px; }

/* ============ 右侧实景展示台 ============ */
.craft-scene {
  position: relative;
  overflow: hidden;
  min-height: 560px;
  padding: 0;
  display: flex;
  align-items: stretch;
}

/* 场景底座 */
.scene-postcard {
  background:
    radial-gradient(ellipse at 50% 118%, rgba(106, 71, 53, 0.28), transparent 58%),
    repeating-linear-gradient(0deg, rgba(106, 71, 53, 0.05) 0 2px, transparent 2px 38px),
    repeating-linear-gradient(90deg, rgba(106, 71, 53, 0.05) 0 2px, transparent 2px 38px),
    linear-gradient(180deg, #efe7d9, #e1d4be);
}
.scene-poster {
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.16) 0, rgba(0, 0, 0, 0.04) 38%, transparent 72%),
    repeating-linear-gradient(0deg, rgba(106, 71, 53, 0.07) 0 3px, transparent 3px 7px),
    linear-gradient(180deg, #e7dbc6, #d8c6a8);
}
.scene-bookmark {
  background:
    radial-gradient(ellipse at 50% 112%, rgba(160, 58, 46, 0.13), transparent 52%),
    linear-gradient(180deg, #efe7d9, #dfd1b8);
}

/* ---- 场景道具：桌面 ---- */
.scene-postcard .pen {
  position: absolute;
  right: 11%;
  top: 22%;
  width: 150px;
  height: 11px;
  border-radius: 6px;
  background: linear-gradient(90deg, #241b15, #6a4735);
  transform: rotate(-30deg);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.25);
  pointer-events: none;
}
.scene-postcard .pen::before {
  content: '';
  position: absolute;
  left: -5px;
  top: -3px;
  width: 20px;
  height: 17px;
  border-radius: 3px;
  background: #c57b3a;
}
.scene-postcard .pen::after {
  content: '';
  position: absolute;
  right: -9px;
  top: -3px;
  width: 0;
  height: 0;
  border-left: 15px solid #a03a2e;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
}
.scene-postcard .inkstone {
  position: absolute;
  left: 9%;
  bottom: 15%;
  width: 74px;
  height: 74px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 34%, #4a3a2a, #1d140f 72%);
  box-shadow: 0 7px 14px rgba(0, 0, 0, 0.3);
  pointer-events: none;
}
.scene-postcard .inkstone::after {
  content: '';
  position: absolute;
  inset: 22%;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 42%, #0a0705, #221812 72%);
}

/* ---- 场景道具：墙面 ---- */
.scene-poster .floor {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 11%;
  background: linear-gradient(180deg, #8a6a4a, #5a4128);
  box-shadow: 0 -6px 18px rgba(0, 0, 0, 0.25);
  pointer-events: none;
}
.scene-poster .wire {
  position: absolute;
  top: 13%;
  left: 22%;
  right: 22%;
  height: 2px;
  background: rgba(36, 27, 21, 0.5);
  pointer-events: none;
}
.scene-poster .nail {
  position: absolute;
  top: 13%;
  left: 50%;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #3a2a1a;
  transform: translate(-50%, -50%);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
  pointer-events: none;
}

/* ---- 场景道具：书本 ---- */
.scene-bookmark .book {
  position: absolute;
  left: 50%;
  bottom: 5%;
  width: 76%;
  height: 46%;
  transform: translateX(-50%);
  pointer-events: none;
}
.book .page-left, .book .page-right {
  position: absolute;
  top: 0;
  width: 49%;
  height: 100%;
  background: linear-gradient(180deg, #fdfbf4, #efe8d8);
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.28);
}
.book .page-left { left: 0; border-radius: 5px 0 0 5px; transform: perspective(600px) rotateY(14deg); transform-origin: right center; }
.book .page-right { right: 0; border-radius: 0 5px 5px 0; transform: perspective(600px) rotateY(-14deg); transform-origin: left center; }
.book .spine {
  position: absolute;
  top: 0; bottom: 0; left: 50%;
  width: 3px;
  background: rgba(106, 71, 53, 0.35);
  transform: translateX(-50%);
}
.book .lines { position: absolute; inset: 14% 12% 12% 12%; }
.book .lines::before, .book .lines::after {
  content: '';
  position: absolute;
  left: 0; right: 0;
  height: 3px;
  border-radius: 2px;
  background: rgba(106, 71, 53, 0.13);
}
.book .lines::before {
  top: 16%;
  box-shadow: 0 20px 0 rgba(106, 71, 53, 0.10), 0 40px 0 rgba(106, 71, 53, 0.08);
}
.book .lines::after {
  top: 62%;
  box-shadow: 0 20px 0 rgba(106, 71, 53, 0.08);
}

/* ---- 成品摆放 ---- */
.scene-product {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.scene-product img {
  max-width: 58%;
  max-height: 86%;
  object-fit: contain;
  border-radius: 3px;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.32);
  pointer-events: auto;
}
.product-postcard img { transform: rotate(-2deg); max-width: 52%; }
.product-poster { align-items: flex-start; padding-top: 20%; }
.product-poster img {
  max-width: 46%;
  border: 10px solid #6a4735;
  border-bottom-width: 16px;
  box-shadow: 0 20px 44px rgba(0, 0, 0, 0.38);
}
.product-bookmark { align-items: flex-end; padding-bottom: 30%; }
.product-bookmark img {
  max-width: 27%;
  max-height: 62%;
  transform: rotate(1.5deg);
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.3);
}

/* ---- 空态 / 加载 ---- */
.scene-empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--ink-line);
  z-index: 1;
}
.empty-seal {
  width: 58px;
  height: 58px;
  border-radius: 6px;
  background: linear-gradient(135deg, var(--red), #6a4735);
  color: var(--paper-light);
  font-family: var(--zh-font);
  font-size: 26px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 2px rgba(243, 236, 227, 0.4);
  margin-bottom: 6px;
}
.scene-empty p { font-family: var(--zh-font); font-size: 17px; letter-spacing: 3px; color: var(--brown); margin: 4px 0; }
.scene-empty span { font-size: 12px; }

.scene-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: rgba(250, 245, 236, 0.72);
  backdrop-filter: blur(2px);
  z-index: 5;
}
.scene-loading span { font-family: var(--zh-font); font-size: 14px; letter-spacing: 3px; color: var(--brown); }
.ld-ring {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: 3px solid rgba(160, 58, 46, 0.2);
  border-top-color: var(--red);
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ============ 底部操作条 ============ */
.craft-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 18px;
  padding: 14px 20px;
  background: var(--paper-light);
  border: 1px solid rgba(106, 71, 53, 0.28);
  border-radius: 6px;
  box-shadow: 0 3px 14px rgba(74, 58, 42, 0.08);
}
.foot-info { display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--ink-soft); }
.foot-tag {
  padding: 3px 12px;
  border-radius: 999px;
  background: rgba(160, 58, 46, 0.10);
  color: var(--red);
  font-family: var(--zh-font);
  letter-spacing: 2px;
}
.foot-seed { font-family: var(--num-font); font-size: 12px; color: var(--ink-line); }
.foot-tip { font-size: 12px; color: var(--ink-line); }
.dl-btn {
  padding: 9px 28px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--paper-light);
  font-family: var(--zh-font);
  font-size: 14px;
  letter-spacing: 3px;
  background: linear-gradient(120deg, #6a4735, #241b15);
  box-shadow: 0 2px 8px rgba(74, 58, 42, 0.25);
  transition: all .2s;
}
.dl-btn:hover { background: linear-gradient(120deg, var(--red), #6a4735); }
</style>
