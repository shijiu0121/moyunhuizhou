<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import anhuiGeo from '../assets/anhui.geo.json'
import { CULTURE_SITES, HUIZHOU_CIRCLE_CITIES } from '../bigscreen/data/huizhouData'
import g1 from '../assets/home/gallery-1.jpg'
import g2 from '../assets/home/gallery-2.jpg'
import g3 from '../assets/home/gallery-3.jpg'
import g4 from '../assets/home/gallery-4.jpg'
import g5 from '../assets/home/gallery-5.jpg'
import g6 from '../assets/home/gallery-6.jpg'
import g7 from '../assets/home/gallery-7.jpg'

const router = useRouter()
function go(path) { router.push(path) }

/* ================= 数据信任条 ================= */
const stats = [
  { label: '知识库条目', value: 1280 },
  { label: '徽州文化景点', value: 43 },
  { label: '非遗名录', value: 38 },
  { label: '文化圈城市', value: 8 },
]
const statVals = ref(stats.map(() => 0))

/* ================= 四大功能 ================= */
const features = [
  {
    tag: '文旅大屏', title: '徽州意象馆', path: '/bigscreen', type: 'map',
    desc: '文旅数字大屏，一屏纵览徽派建筑、文房四宝、徽商与戏曲。43 处文化景点地理标注，游客画像、热词、非遗滚动看板实时呈现。',
    points: ['8 市文化圈 · 43 处景点地理标注', '游客画像 / 热词 / 非遗滚动看板', '黄山实景页脚，水墨大屏沉浸观览'],
  },
  {
    tag: 'AI 生图', title: 'AI 徽画工坊', path: '/studio', type: 'paint',
    desc: '自研徽派 LoRA 模型，输入一句话即可生成水墨徽州。徽派建筑、山水、人文多题材，让每一次描述都成为一幅可收藏的画。',
    points: ['一句话描述 · 多风格水墨生图', '徽派建筑 / 山水 / 人文多题材', '生成作品一键下印为文创'],
  },
  {
    tag: 'AI 问答', title: '徽史问答官', path: '/ask', type: 'chat',
    desc: '基于徽文化知识库的 RAG 智能讲解，有问必答、言必有据。从徽商源流到徽剧腔调，从三雕技艺到民俗节令，知无不言。',
    points: ['1,280+ 条徽文化知识库', '检索增强生成，回答附出处', '徽商 / 徽剧 / 三雕 / 民俗全覆盖'],
  },
  {
    tag: '文创制作', title: '文创印务局', path: '/craft', type: 'craft',
    desc: '把 AI 作品一键制成明信片、海报、书签等文创成品。徽州纹样自动排版，所见即所得，导出高清成品。',
    points: ['明信片 / 海报 / 书签多模板', '徽州纹样自动排版', '所见即所得 · 导出高清成品'],
  },
]

/* ================= 三步流程 ================= */
const steps = [
  { n: '一', title: '输入一句话', desc: '描述你想见的徽州，如「细雨中的宏村月沼」' },
  { n: '二', title: 'AI 生成 · 作答', desc: 'LoRA 生图或知识库 RAG，秒出水墨作品与解答' },
  { n: '三', title: '一键文创', desc: '选模板排布，把作品制成明信片、海报' },
]

/* ================= 作品画廊 ================= */
const gallery = [
  { src: g4, title: '黄山 · 云海浮峰', cap: '实景灵感' },
  { src: g1, title: '黄山 · 群峰叠翠', cap: 'AI 水墨' },
  { src: g6, title: '宏村 · 水韵', cap: '实景灵感' },
  { src: g5, title: '黄山 · 雾起群峰', cap: 'AI 水墨' },
  { src: g7, title: '徽州 · 古村', cap: '实景灵感' },
  { src: g2, title: '黄山 · 云海深处', cap: 'AI 水墨' },
  { src: g3, title: '黄山 · 奇松', cap: '实景灵感' },
]

/* ================= Hero 实时演示窗（迷你徽州地图） ================= */
echarts.registerMap('anhuiHome', anhuiGeo)
const heroMapRef = ref(null)
let heroChart = null
const HERO_SITES = CULTURE_SITES.filter((s) => ['黄山风景区', '宏村', '西递', '徽州古城', '屯溪老街', '呈坎', '棠樾牌坊群·鲍家花园', '齐云山', '九华山', '龙川景区'].includes(s.name))
const heroOption = {
  backgroundColor: 'transparent',
  tooltip: { trigger: 'item', backgroundColor: 'rgba(36,27,21,0.9)', borderColor: 'rgba(160,58,46,0.6)', textStyle: { color: '#f3ece3', fontSize: 12 }, formatter: (p) => p.name },
  geo: {
    map: 'anhuiHome',
    zoom: 1.06,
    center: [117.3, 30.5],
    layoutCenter: ['50%', '52%'],
    layoutSize: '98%',
    regions: anhuiGeo.features.map((f) => {
      const inC = HUIZHOU_CIRCLE_CITIES.includes(f.properties.name)
      return {
        name: f.properties.name,
        itemStyle: {
          areaColor: inC ? 'rgba(197,123,58,0.30)' : 'rgba(106,71,53,0.06)',
          borderColor: inC ? 'rgba(160,58,46,0.6)' : 'rgba(106,71,53,0.3)',
          borderWidth: inC ? 1.4 : 0.8,
        },
        label: { show: inC, fontSize: 9, color: '#4a3a2a', fontFamily: '"Kaiti SC","楷体",serif' },
        emphasis: { itemStyle: { areaColor: 'rgba(197,123,58,0.45)' } },
      }
    }),
  },
  series: [
    {
      name: '徽州文化景点',
      type: 'scatter',
      coordinateSystem: 'geo',
      data: HERO_SITES.map((s) => ({ name: s.name, value: [s.lng, s.lat] })),
      symbolSize: 5,
      itemStyle: { color: '#a03a2e', borderColor: '#f3ece3', borderWidth: 1, shadowBlur: 4, shadowColor: 'rgba(160,58,46,0.5)' },
      label: { show: false },
      emphasis: { scale: 1.6 },
    },
    {
      name: '脉冲',
      type: 'effectScatter',
      coordinateSystem: 'geo',
      data: HERO_SITES.filter((_, i) => i % 2 === 0).map((s) => ({ name: s.name, value: [s.lng, s.lat] })),
      symbolSize: 5,
      rippleEffect: { brushType: 'stroke', scale: 2.6, period: 4 },
      itemStyle: { color: '#c57b3a' },
      zlevel: 2,
    },
  ],
}
function initHeroMap() {
  if (!heroMapRef.value) return
  heroChart = echarts.init(heroMapRef.value)
  heroChart.setOption(heroOption)
}

/* ================= 滚动浮现 + 数字滚动 ================= */
const statsEl = ref(null)
let io = null
function observeReveal() {
  io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target) }
    })
  }, { threshold: 0.16 })
  document.querySelectorAll('.home .reveal').forEach((el) => io.observe(el))
}
function startCount() {
  if (!statsEl.value) return
  const io2 = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      io2.disconnect()
      stats.forEach((s, i) => {
        const t0 = performance.now(); const dur = 1300
        const tick = (t) => {
          const p = Math.min(1, (t - t0) / dur)
          statVals.value[i] = Math.round(s.value * (1 - Math.pow(1 - p, 3)))
          if (p < 1) requestAnimationFrame(tick)
        }
        requestAnimationFrame(tick)
      })
    }
  }, { threshold: 0.4 })
  io2.observe(statsEl.value)
}
function onResize() { if (heroChart) heroChart.resize() }

onMounted(() => {
  initHeroMap()
  observeReveal()
  startCount()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => {
  if (heroChart) { heroChart.dispose(); heroChart = null }
  if (io) io.disconnect()
  window.removeEventListener('resize', onResize)
})
</script>

<template>
  <div class="home">
    <!-- ================= ① Hero ================= -->
    <section class="hero">
      <div class="hero-wash" aria-hidden="true">
        <span class="wash-ink wash-1"></span>
        <span class="wash-ink wash-2"></span>
      </div>

      <div class="hero-inner">
        <div class="hero-copy">
          <div class="hero-kicker">徽 文 化 · A I G C · 数 字 文 创</div>
          <h1 class="hero-title">墨蕴徽州</h1>
          <div class="hero-orn">—◆— ◆ —◆—</div>
          <p class="hero-subtitle">一键「画出徽州 · 讲出徽州 · 造出徽州文创」<br />让千年徽州意象，在数字时代重新生长</p>
          <div class="hero-actions">
            <button class="btn-primary" @click="go('/bigscreen')">步入数字徽州 →</button>
            <button class="btn-ghost" @click="go('/studio')">即刻作画</button>
          </div>
          <div class="hero-meta">
            <span v-for="s in stats" :key="s.label"><b>{{ s.value.toLocaleString() }}</b> {{ s.label }}</span>
          </div>
        </div>

        <div class="hero-demo">
          <div class="demo-window">
            <div class="demo-bar">
              <i></i><i></i><i></i>
              <span>徽州文化圈 · 实时地图</span>
            </div>
            <div ref="heroMapRef" class="demo-map"></div>
            <div class="demo-cap">
              <span class="cap-dot"></span> 43 处文化景点实时标记 · 8 市文化圈
            </div>
          </div>
          <div class="demo-badge">LIVE · 数据大屏同源</div>
        </div>
      </div>

      <div class="hero-scroll">向下滚动</div>
    </section>

    <!-- ================= ② 数据信任条 ================= -->
    <section ref="statsEl" class="stats">
      <div v-for="(s, i) in stats" :key="s.label" class="stat">
        <div class="stat-num">
          <b>{{ statVals[i].toLocaleString() }}</b>
          <span class="stat-unit" v-if="s.label === '文化圈城市'">市</span>
        </div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </section>

    <!-- ================= ③ 功能图文交替 ================= -->
    <section class="features">
      <div class="section-head reveal">
        <span class="sec-kicker">四大能力</span>
        <h2>从观览到生成，从问答到文创</h2>
        <p>一条完整链路，把徽州文化变成可看、可玩、可收藏的数字资产</p>
      </div>

      <div v-for="(f, i) in features" :key="f.title" class="feature-row" :class="{ reverse: i % 2 === 1 }">
        <div class="feature-media reveal">
          <!-- 各功能交互预览 -->
          <div v-if="f.type === 'map'" class="mock mock-map">
            <div class="mock-head"><i></i><i></i><i></i><span>徽州意象馆 · 数据大屏</span></div>
            <div class="mock-map-body">
              <div class="mock-stat"><b>1280</b><span>知识库条目</span></div>
              <div class="mock-stat"><b>43</b><span>核心景点</span></div>
              <div class="mock-stat"><b>38</b><span>非遗名录</span></div>
              <div class="mock-bars">
                <i v-for="(h, k) in [46, 68, 52, 84, 60, 74, 42, 58]" :key="k" :style="{ height: h + '%' }"></i>
              </div>
              <div class="mock-map-note">游客画像 · 热词 · 非遗滚动</div>
            </div>
          </div>

          <div v-else-if="f.type === 'paint'" class="mock mock-paint">
            <div class="mock-head"><i></i><i></i><i></i><span>AI 徽画工坊 · 生图</span></div>
            <div class="mock-prompt">
              <span class="mock-cursor"></span>
              细雨中的宏村月沼，白墙黛瓦，水墨晕染
              <button class="mock-gen">生成</button>
            </div>
            <div class="mock-grid">
              <div v-for="(im, k) in [g4, g1, g5, g2]" :key="k" class="mock-cell" :style="{ backgroundImage: `url(${im})` }"></div>
            </div>
          </div>

          <div v-else-if="f.type === 'chat'" class="mock mock-chat">
            <div class="mock-head"><i></i><i></i><i></i><span>徽史问答官 · 对话</span></div>
            <div class="mock-msg u">徽商的「贾而好儒」是什么意思？</div>
            <div class="mock-msg ai">
              徽商以「贾而好儒」著称，即商而兼士、以商弘文：既经营四方，又兴办学堂、藏书刻书，将儒家伦理贯注于经营之中……
              <span class="mock-src">· 来源：徽商史料 · RAG</span>
            </div>
            <div class="mock-input"><span class="mock-cursor"></span>问点什么…</div>
          </div>

          <div v-else class="mock mock-craft">
            <div class="mock-head"><i></i><i></i><i></i><span>文创印务局 · 成品</span></div>
            <div class="mock-craft-grid">
              <div class="mock-card"><img :src="g6" alt="" /><b>宏村 · 月沼</b><span>明信片</span></div>
              <div class="mock-card"><img :src="g4" alt="" /><b>黄山 · 云海</b><span>海报</span></div>
              <div class="mock-card"><img :src="g7" alt="" /><b>徽州 · 古村</b><span>书签</span></div>
            </div>
          </div>
        </div>

        <div class="feature-text reveal">
          <span class="feature-index">{{ String(i + 1).padStart(2, '0') }}</span>
          <div class="feature-tag">{{ f.tag }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
          <ul class="feature-points">
            <li v-for="pt in f.points" :key="pt">{{ pt }}</li>
          </ul>
          <button class="feature-enter" @click="go(f.path)">进入 {{ f.title }} →</button>
        </div>
      </div>
    </section>

    <!-- ================= ④ 三步流程 ================= -->
    <section class="how">
      <div class="section-head reveal">
        <span class="sec-kicker">How it works</span>
        <h2>三步，造出你的徽州意象</h2>
      </div>
      <div class="steps">
        <div v-for="(s, i) in steps" :key="i" class="step reveal">
          <div class="step-no">{{ s.n }}</div>
          <div class="step-arrow" v-if="i < steps.length - 1">→</div>
          <h3>{{ s.title }}</h3>
          <p>{{ s.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ================= ⑤ 作品画廊 ================= -->
    <section class="gallery">
      <div class="section-head reveal">
        <span class="sec-kicker">Gallery</span>
        <h2>徽州意象画廊</h2>
        <p>AI 水墨作品 × 徽州实景灵感</p>
      </div>
      <div class="gallery-track reveal">
        <div v-for="(g, i) in gallery" :key="i" class="gallery-item">
          <div class="gallery-img" :style="{ backgroundImage: `url(${g.src})` }">
            <span class="gallery-cap">{{ g.cap }}</span>
          </div>
          <span class="gallery-title">{{ g.title }}</span>
        </div>
      </div>
    </section>

    <!-- ================= ⑥ 文化叙事 ================= -->
    <section class="culture">
      <div class="culture-frame reveal">
        <span class="culture-mark">徽</span>
        <p class="culture-quote">「一生痴绝处，无梦到徽州。」</p>
        <p class="culture-note">徽州，是山水与笔墨共生的地方。白墙黛瓦、马头墙檐、三雕匠心，连同那句流传四百年的感叹，<br />如今都将在 AI 的笔锋下重新被看见、被讲述、被珍藏。</p>
        <span class="culture-src">—— 明 · 汤显祖</span>
      </div>
    </section>

    <!-- ================= ⑦ CTA ================= -->
    <section class="cta reveal">
      <h2>步入数字徽州，让千年意象在指尖重生</h2>
      <p>现在开始，说出你心中的徽州。</p>
      <div class="cta-btns">
        <button class="btn-primary big" @click="go('/studio')">开始创作</button>
        <button class="btn-ghost big" @click="go('/bigscreen')">观看数据大屏</button>
      </div>
    </section>

    <!-- ================= ⑧ 页脚 ================= -->
    <footer class="foot">
      <div class="foot-grid">
        <div class="foot-brand">
          <span class="foot-seal">墨蕴<br />徽州</span>
          <div>
            <b>墨蕴徽州</b>
            <p>徽文化数字文创智造平台 · iCAN 2026</p>
          </div>
        </div>
        <div class="foot-links">
          <router-link to="/bigscreen">徽州意象馆</router-link>
          <router-link to="/studio">AI 徽画工坊</router-link>
          <router-link to="/ask">徽史问答官</router-link>
          <router-link to="/craft">文创印务局</router-link>
        </div>
        <div class="foot-meta">
          <span>以 AIGC 让每个人一键「画出徽州 · 讲出徽州 · 造出徽州文创」</span>
          <span class="foot-icp">© 2026 墨蕴徽州 · 徽文化数字文创智造平台 · 演示数据</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
.home {
  overflow-x: hidden;
  background:
    radial-gradient(circle at 50% -10%, rgba(255, 255, 255, 0.75), transparent 42%),
    var(--paper);
}
.reveal { opacity: 0; transform: translateY(26px); transition: opacity .7s ease, transform .7s ease; }
.reveal.visible { opacity: 1; transform: translateY(0); }

/* 通用段落标题 */
.section-head { text-align: center; padding: 70px 20px 36px; }
.sec-kicker {
  font-size: 12px; letter-spacing: 5px; color: #a03a2e;
  border: 1px solid rgba(160, 58, 46, 0.35); border-radius: 2px;
  padding: 3px 14px; display: inline-block;
}
.section-head h2 {
  margin: 18px 0 10px; font-size: 34px; font-weight: 900; letter-spacing: 8px; color: var(--ink);
}
.section-head p { margin: 0; color: #6a4735; font-size: 14px; letter-spacing: 2px; }

/* ================= ① Hero ================= */
.hero { position: relative; min-height: 86vh; display: flex; align-items: center; overflow: hidden; }
.hero-wash { position: absolute; inset: 0; pointer-events: none; }
.wash-ink {
  position: absolute; border-radius: 50%; filter: blur(30px); opacity: 0.5;
}
.wash-1 { width: 520px; height: 520px; left: -160px; top: -120px; background: radial-gradient(circle, rgba(106,71,53,0.16), transparent 70%); }
.wash-2 { width: 460px; height: 460px; right: -140px; bottom: -140px; background: radial-gradient(circle, rgba(160,58,46,0.10), transparent 70%); }

.hero-inner {
  position: relative; z-index: 2;
  max-width: 1180px; margin: 0 auto; padding: 40px 40px;
  width: 100%; display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 56px; align-items: center;
}

.hero-kicker { font-size: 13px; letter-spacing: 6px; color: #a03a2e; margin-bottom: 14px; }
.hero-title {
  margin: 0; font-size: 76px; font-weight: 900; letter-spacing: 20px; line-height: 1.05;
  color: var(--ink); font-family: var(--zh-font);
  text-shadow: 0 4px 0 rgba(160, 58, 46, 0.12);
}
.hero-orn { color: #a03a2e; font-size: 12px; letter-spacing: 8px; margin: 18px 0 16px; opacity: 0.7; }
.hero-subtitle { margin: 0; color: #4a3a2a; font-size: 16px; line-height: 2; letter-spacing: 2px; }
.hero-actions { display: flex; gap: 14px; margin-top: 30px; }

.btn-primary {
  border: none; cursor: pointer; color: #f3ece3;
  background: linear-gradient(120deg, #6a4735, #241b15);
  padding: 13px 30px; font-size: 14px; letter-spacing: 3px; border-radius: 4px;
  box-shadow: 0 6px 18px rgba(36, 27, 21, 0.22); transition: all .25s;
}
.btn-primary:hover { background: linear-gradient(120deg, #a03a2e, #6a4735); transform: translateY(-2px); box-shadow: 0 10px 26px rgba(160, 58, 46, 0.3); }
.btn-primary.big { padding: 16px 40px; font-size: 15px; }
.btn-ghost {
  cursor: pointer; color: #6a4735; background: transparent;
  border: 1px solid #6a4735; padding: 13px 30px; font-size: 14px; letter-spacing: 3px; border-radius: 4px;
  transition: all .25s;
}
.btn-ghost:hover { background: rgba(106, 71, 53, 0.08); transform: translateY(-2px); }
.btn-ghost.big { padding: 16px 40px; font-size: 15px; }

.hero-meta { margin-top: 34px; display: flex; gap: 26px; flex-wrap: wrap; }
.hero-meta span { font-size: 13px; color: #8a7462; letter-spacing: 1px; }
.hero-meta b { font-size: 20px; color: #6a4735; font-family: var(--num-font); margin-right: 5px; }

/* Hero 演示窗 */
.hero-demo { position: relative; }
.demo-window {
  border-radius: 10px; overflow: hidden;
  background: #faf5ec;
  border: 1px solid rgba(106, 71, 53, 0.22);
  box-shadow: 0 30px 60px rgba(74, 58, 42, 0.18), 0 4px 14px rgba(74, 58, 42, 0.08);
  transform: rotate(0.6deg);
}
.demo-bar {
  height: 38px; background: rgba(36, 27, 21, 0.9); display: flex; align-items: center; gap: 6px; padding: 0 14px;
}
.demo-bar i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.demo-bar i:nth-child(1) { background: #a03a2e; }
.demo-bar i:nth-child(2) { background: #c57b3a; }
.demo-bar i:nth-child(3) { background: #4f7681; }
.demo-bar span { margin-left: 8px; color: #d8c9ae; font-size: 12px; letter-spacing: 1px; }
.demo-map { height: 320px; width: 100%; }
.demo-cap {
  height: 34px; display: flex; align-items: center; gap: 8px; padding: 0 14px;
  font-size: 12px; color: #6a4735; letter-spacing: 1px; background: #f3ece3;
  border-top: 1px solid rgba(106, 71, 53, 0.15);
}
.cap-dot { width: 8px; height: 8px; border-radius: 50%; background: #a03a2e; animation: pulseDot 2s ease-in-out infinite; }
@keyframes pulseDot { 0%,100% { box-shadow: 0 0 0 0 rgba(160,58,46,0.4);} 50% { box-shadow: 0 0 0 5px rgba(160,58,46,0);} }
.demo-badge {
  position: absolute; top: -12px; right: -10px; z-index: 3;
  background: #a03a2e; color: #f3ece3; font-size: 11px; letter-spacing: 2px;
  padding: 5px 12px; border-radius: 2px; transform: rotate(3deg);
  box-shadow: 0 4px 10px rgba(160, 58, 46, 0.4);
}

.hero-scroll {
  position: absolute; left: 50%; bottom: 22px; transform: translateX(-50%);
  font-size: 12px; color: #9a8470; letter-spacing: 3px; animation: scrollHint 2.4s ease-in-out infinite;
}
@keyframes scrollHint { 0%,100% { opacity: 0.35; } 50% { opacity: 1; } }

/* ================= ② 数据信任条 ================= */
.stats {
  max-width: 1180px; margin: 20px auto 10px; padding: 34px 40px;
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px;
  border-top: 1px solid rgba(106, 71, 53, 0.18); border-bottom: 1px solid rgba(106, 71, 53, 0.18);
}
.stat { text-align: center; padding: 6px 0; }
.stat-num { font-size: 42px; font-weight: 800; color: #241b15; font-family: var(--num-font); line-height: 1; }
.stat-num .stat-unit { font-size: 16px; color: #6a4735; margin-left: 2px; }
.stat-label { margin-top: 10px; font-size: 13px; color: #6a4735; letter-spacing: 3px; }

/* ================= ③ 功能图文交替 ================= */
.features { max-width: 1180px; margin: 0 auto; padding: 10px 40px 0; }
.feature-row { display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 52px; align-items: center; padding: 44px 0; }
.feature-row.reverse { direction: rtl; }
.feature-row > * { direction: ltr; }

.feature-index {
  font-family: var(--num-font); font-size: 44px; font-weight: 800; color: rgba(106, 71, 53, 0.18); line-height: 1; display: block;
}
.feature-tag {
  display: inline-block; margin: 14px 0 8px; font-size: 12px; color: #a03a2e;
  border: 1px solid rgba(160, 58, 46, 0.35); padding: 2px 12px; border-radius: 2px; letter-spacing: 2px;
}
.feature-text h3 { margin: 0 0 12px; font-size: 30px; font-weight: 900; letter-spacing: 5px; color: var(--ink); }
.feature-text p { margin: 0 0 16px; color: #4a3a2a; font-size: 14px; line-height: 1.9; letter-spacing: 1px; }
.feature-points { list-style: none; margin: 0 0 22px; padding: 0; }
.feature-points li {
  position: relative; padding: 5px 0 5px 22px; color: #6a4735; font-size: 13px; letter-spacing: 1px;
}
.feature-points li::before {
  content: '◆'; position: absolute; left: 0; top: 5px; color: #a03a2e; font-size: 10px;
}
.feature-enter {
  border: none; cursor: pointer; color: #f3ece3; background: linear-gradient(120deg, #a03a2e, #6a4735);
  padding: 11px 26px; font-size: 13px; letter-spacing: 2px; border-radius: 4px; transition: all .25s;
  box-shadow: 0 5px 14px rgba(160, 58, 46, 0.24);
}
.feature-enter:hover { transform: translateY(-2px); box-shadow: 0 9px 22px rgba(160, 58, 46, 0.34); }

/* —— 各功能预览 mock —— */
.mock {
  border-radius: 10px; overflow: hidden; background: #faf5ec;
  border: 1px solid rgba(106, 71, 53, 0.2); box-shadow: 0 18px 40px rgba(74, 58, 42, 0.12);
}
.mock-head { height: 34px; background: rgba(36, 27, 21, 0.88); display: flex; align-items: center; gap: 5px; padding: 0 12px; }
.mock-head i { width: 8px; height: 8px; border-radius: 50%; }
.mock-head i:nth-child(1) { background: #a03a2e; }
.mock-head i:nth-child(2) { background: #c57b3a; }
.mock-head i:nth-child(3) { background: #4f7681; }
.mock-head span { margin-left: 8px; color: #c9b696; font-size: 11px; letter-spacing: 1px; }

/* 大屏 mock */
.mock-map-body { padding: 18px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.mock-stat { text-align: center; padding: 12px 6px; background: rgba(106,71,53,0.06); border-left: 3px solid #6a4735; }
.mock-stat b { display: block; font-size: 24px; font-family: var(--num-font); color: #241b15; }
.mock-stat span { font-size: 11px; color: #6a4735; letter-spacing: 1px; }
.mock-bars {
  grid-column: 1 / -1; height: 90px; display: flex; align-items: flex-end; gap: 8px; padding: 10px 6px 0;
  background: rgba(106,71,53,0.04); border-radius: 6px;
}
.mock-bars i {
  flex: 1; background: linear-gradient(180deg, #a03a2e, #c57b3a); border-radius: 3px 3px 0 0; opacity: 0.75;
  animation: growBar 1.4s ease-in-out both;
}
@keyframes growBar { from { height: 4% !important; } }
.mock-map-note { grid-column: 1 / -1; text-align: center; font-size: 11px; color: #8a7462; letter-spacing: 2px; }

/* 生图 mock */
.mock-paint { padding-bottom: 12px; }
.mock-prompt {
  margin: 14px; display: flex; align-items: center; gap: 8px;
  border: 1px solid rgba(106, 71, 53, 0.3); border-radius: 4px; padding: 9px 12px;
  font-size: 12px; color: #4a3a2a; background: #fff;
}
.mock-cursor { width: 2px; height: 14px; background: #a03a2e; animation: blink 1s step-end infinite; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
.mock-gen {
  margin-left: auto; border: none; cursor: default; color: #f3ece3; background: linear-gradient(120deg, #a03a2e, #6a4735);
  font-size: 12px; padding: 6px 14px; border-radius: 3px; letter-spacing: 1px;
}
.mock-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; padding: 0 14px 14px; }
.mock-cell { height: 88px; border-radius: 6px; background-size: cover; background-position: center; border: 1px solid rgba(255,255,255,0.7); }

/* 对话 mock */
.mock-chat { padding-bottom: 14px; }
.mock-msg {
  margin: 14px 14px 0; padding: 10px 12px; font-size: 12px; line-height: 1.8; letter-spacing: 0.5px;
  max-width: 78%;
}
.mock-msg.u { margin-left: auto; color: #f3ece3; background: linear-gradient(120deg, #6a4735, #241b15); border-radius: 8px 8px 2px 8px; }
.mock-msg.ai { color: #241b15; background: #fff; border: 1px solid rgba(106,71,53,0.25); border-radius: 8px 8px 8px 2px; }
.mock-src { display: block; margin-top: 6px; color: #a03a2e; font-size: 10px; letter-spacing: 1px; }
.mock-input {
  margin: 14px 14px 0; border: 1px solid rgba(106, 71, 53, 0.3); border-radius: 4px; padding: 9px 12px;
  display: flex; align-items: center; gap: 8px; font-size: 12px; color: #9a8470; background: #fff;
}

/* 文创 mock */
.mock-craft { padding-bottom: 14px; }
.mock-craft-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 14px; }
.mock-card {
  background: #fff; border: 1px solid rgba(106,71,53,0.2); border-radius: 6px; overflow: hidden;
  text-align: center; padding-bottom: 8px;
}
.mock-card img { width: 100%; height: 76px; object-fit: cover; display: block; }
.mock-card b { display: block; font-size: 12px; color: #241b15; margin-top: 6px; letter-spacing: 1px; }
.mock-card span { font-size: 10px; color: #a03a2e; letter-spacing: 1px; }

/* ================= ④ 三步流程 ================= */
.how { max-width: 1180px; margin: 0 auto; padding: 20px 40px 0; }
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.step {
  position: relative; padding: 30px 24px; text-align: center;
  background: linear-gradient(160deg, rgba(255,255,255,0.6), rgba(255,255,255,0) 45%), var(--paper-light);
  border: 1px solid rgba(106, 71, 53, 0.2); border-radius: 8px;
  box-shadow: 0 8px 24px rgba(74, 58, 42, 0.07);
}
.step-no {
  width: 44px; height: 44px; margin: 0 auto 14px; display: flex; align-items: center; justify-content: center;
  color: #f3ece3; font-family: var(--zh-font); font-size: 20px; font-weight: 700;
  background: linear-gradient(135deg, #a03a2e, #6a4735); border-radius: 50%;
  box-shadow: 0 5px 12px rgba(160, 58, 46, 0.3);
}
.step h3 { margin: 0 0 8px; font-size: 20px; color: var(--ink); letter-spacing: 3px; }
.step p { margin: 0; font-size: 13px; color: #6a4735; line-height: 1.8; letter-spacing: 1px; }
.step-arrow {
  position: absolute; top: 42%; right: -20px; z-index: 3; color: #c57b3a; font-size: 22px; transform: translateX(50%);
}

/* ================= ⑤ 作品画廊 ================= */
.gallery { max-width: 1180px; margin: 0 auto; padding: 30px 40px 0; }
.gallery-track {
  display: flex; gap: 18px; overflow-x: auto; padding: 12px 4px 22px;
  scroll-snap-type: x mandatory; scrollbar-width: thin; scrollbar-color: rgba(160,58,46,0.4) transparent;
}
.gallery-track::-webkit-scrollbar { height: 6px; }
.gallery-track::-webkit-scrollbar-thumb { background: rgba(160, 58, 46, 0.4); border-radius: 3px; }
.gallery-item { flex: 0 0 280px; scroll-snap-align: start; }
.gallery-img {
  height: 190px; border-radius: 8px; background-size: cover; background-position: center;
  position: relative; overflow: hidden; border: 1px solid rgba(106, 71, 53, 0.18);
  box-shadow: 0 10px 26px rgba(74, 58, 42, 0.12);
}
.gallery-cap {
  position: absolute; top: 10px; left: 10px; font-size: 11px; color: #6a4735; letter-spacing: 2px;
  background: rgba(243, 236, 227, 0.9); padding: 2px 10px; border-radius: 2px;
}
.gallery-title { display: block; margin-top: 10px; text-align: center; font-size: 14px; color: #241b15; letter-spacing: 3px; font-family: var(--zh-font); }

/* ================= ⑥ 文化叙事 ================= */
.culture { max-width: 1180px; margin: 30px auto; padding: 40px 40px 0; }
.culture-frame {
  position: relative; text-align: center; padding: 56px 40px 44px;
  background: linear-gradient(160deg, rgba(255,255,255,0.55), rgba(255,255,255,0) 50%), rgba(106, 71, 53, 0.05);
  border: 1px solid rgba(106, 71, 53, 0.18); border-radius: 10px;
}
.culture-mark {
  position: absolute; top: -22px; left: 50%; transform: translateX(-50%);
  width: 46px; height: 46px; color: #f3ece3; background: #a03a2e;
  font-family: var(--zh-font); font-size: 22px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; border-radius: 4px;
  box-shadow: inset 0 0 0 2px rgba(243,236,227,0.4), 0 6px 14px rgba(160,58,46,0.35);
}
.culture-quote { margin: 0; font-family: var(--zh-font); font-size: 30px; font-weight: 700; letter-spacing: 6px; color: var(--ink); }
.culture-note { margin: 18px 0 14px; color: #4a3a2a; font-size: 14px; line-height: 2.1; letter-spacing: 1px; }
.culture-src { font-size: 13px; color: #9a8470; letter-spacing: 2px; }

/* ================= ⑦ CTA ================= */
.cta {
  max-width: 1180px; margin: 30px auto; padding: 56px 40px; text-align: center;
  background:
    radial-gradient(circle at 50% 0%, rgba(255,255,255,0.35), transparent 55%),
    linear-gradient(135deg, #241b15, #4a3a2a);
  border-radius: 12px; box-shadow: 0 20px 46px rgba(36, 27, 21, 0.25);
}
.cta h2 { margin: 0 0 10px; color: #f3ece3; font-size: 32px; letter-spacing: 8px; font-weight: 900; }
.cta p { margin: 0 0 28px; color: #c9b696; font-size: 14px; letter-spacing: 2px; }
.cta-btns { display: flex; gap: 16px; justify-content: center; }
.cta .btn-primary { background: linear-gradient(120deg, #a03a2e, #6a4735); }
.cta .btn-ghost { color: #f3ece3; border-color: rgba(243, 236, 227, 0.6); }
.cta .btn-ghost:hover { background: rgba(243, 236, 227, 0.08); }

/* ================= ⑧ 页脚 ================= */
.foot {
  margin-top: 40px; padding: 34px 40px 40px;
  border-top: 1px solid rgba(106, 71, 53, 0.2);
  background: rgba(106, 71, 53, 0.05);
}
.foot-grid { max-width: 1180px; margin: 0 auto; display: grid; grid-template-columns: 1.2fr 0.8fr 1.4fr; gap: 30px; align-items: start; }
.foot-brand { display: flex; gap: 14px; align-items: center; }
.foot-seal {
  width: 40px; height: 40px; flex-shrink: 0; color: #f3ece3; background: #a03a2e;
  font-family: var(--zh-font); font-size: 11px; font-weight: 700; text-align: center; line-height: 1.2;
  padding-top: 8px; border-radius: 3px; box-shadow: inset 0 0 0 2px rgba(243,236,227,0.4);
}
.foot-brand b { font-size: 17px; color: var(--ink); letter-spacing: 3px; font-family: var(--zh-font); }
.foot-brand p { margin: 4px 0 0; font-size: 12px; color: #8a7462; letter-spacing: 1px; }
.foot-links { display: flex; flex-direction: column; gap: 8px; }
.foot-links a { color: #6a4735; text-decoration: none; font-size: 13px; letter-spacing: 2px; }
.foot-links a:hover { color: #a03a2e; }
.foot-meta { display: flex; flex-direction: column; gap: 10px; text-align: right; }
.foot-meta span { font-size: 12px; color: #8a7462; letter-spacing: 1px; line-height: 1.8; }
.foot-icp { color: #9a8470; font-size: 11px !important; }

/* 响应式 */
@media (max-width: 960px) {
  .hero-inner { grid-template-columns: 1fr; gap: 30px; padding: 40px 20px; }
  .hero-title { font-size: 52px; letter-spacing: 12px; }
  .stats { grid-template-columns: repeat(2, 1fr); }
  .feature-row { grid-template-columns: 1fr; gap: 24px; padding: 28px 0; }
  .steps { grid-template-columns: 1fr; }
  .step-arrow { display: none; }
  .foot-grid { grid-template-columns: 1fr; text-align: center; }
  .foot-meta { text-align: center; }
}
</style>
