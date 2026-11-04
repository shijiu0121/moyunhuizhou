<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { getKnowledgeGraph } from '../api'
import { INK } from '../bigscreen/modules/inkTheme'

const graph = ref(null)
const loading = ref(true)
const error = ref(false)
const keyword = ref('')
const activeTopic = ref('')
const selectedId = ref('huizhou')
const reading = ref(false)
const touring = ref(false)
const chartEl = ref(null)
const readingEl = ref(null)
const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
const reducedMotion = ref(motion.matches)
const controller = new AbortController()
const colors = [INK.brown, INK.red, INK.blue, INK.orange, '#788267', INK.gold, '#76758a', '#62877c', '#957968']
let chart
let resizeObserver
let tourTimer

const articles = computed(() => graph.value?.nodes.filter(n => n.kind === 'article') || [])
const filteredArticles = computed(() => {
  const query = keyword.value.trim().toLocaleLowerCase()
  return articles.value.filter(n => (!activeTopic.value || n.topic === activeTopic.value)
    && (!query || `${n.name}\n${n.text}`.toLocaleLowerCase().includes(query)))
})
const selected = computed(() => graph.value?.nodes.find(n => n.id === selectedId.value))
const topicById = computed(() => new Map(graph.value?.topics.map((t, i) => [t.id, { ...t, color: colors[i % colors.length] }]) || []))
const related = computed(() => {
  if (selected.value?.kind !== 'article') return []
  return graph.value.links.filter(l => l.kind === 'related' && (l.source === selectedId.value || l.target === selectedId.value))
    .map(l => ({ ...l, article: articles.value.find(a => a.id === (l.source === selectedId.value ? l.target : l.source)) }))
})
const selectedArticles = computed(() => selected.value?.kind === 'topic'
  ? articles.value.filter(a => a.topic === selected.value.topic) : articles.value)
const questionLink = computed(() => ({
  name: 'ask',
  query: { question: `请介绍${selected.value?.name || '徽州文化'}的历史与文化特色。` },
}))

function stopTour() {
  clearInterval(tourTimer)
  touring.value = false
}

function chooseTopic(id) {
  stopTour()
  activeTopic.value = id
  selectedId.value = id ? `topic-${id}` : 'huizhou'
}

function chooseNode(node) {
  stopTour()
  selectedId.value = node.id
}

function readFromIndex(node) {
  chooseNode(node)
  readingEl.value.scrollIntoView({ behavior: reducedMotion.value ? 'instant' : 'smooth', block: 'nearest' })
}

function openRelated(article) {
  // 关联资料可能位于另一主题；清除筛选，使被选节点始终在画布中可见。
  activeTopic.value = ''
  keyword.value = ''
  chooseNode(article)
}

function resetView() {
  stopTour()
  activeTopic.value = ''
  keyword.value = ''
  selectedId.value = 'huizhou'
  renderGraph(true)
}

function toggleTour() {
  if (touring.value) { stopTour(); return }
  keyword.value = ''
  touring.value = true
  let index = 0
  const step = () => {
    const topic = graph.value.topics[index % graph.value.topics.length]
    activeTopic.value = topic.id
    selectedId.value = `topic-${topic.id}`
    index += 1
  }
  step()
  tourTimer = setInterval(step, 5500)
}

function onSearch() {
  stopTour()
  selectedId.value = activeTopic.value ? `topic-${activeTopic.value}` : 'huizhou'
}

function excerpt(text) {
  const query = keyword.value.trim()
  const match = query ? text.toLocaleLowerCase().indexOf(query.toLocaleLowerCase()) : 0
  const start = Math.max(0, match - 36)
  return `${start ? '…' : ''}${text.slice(start, start + 200).trim()}${text.length > start + 200 ? '…' : ''}`
}

function renderGraph(reset = false) {
  if (!chart || !graph.value) return
  const visibleIds = new Set(filteredArticles.value.map(n => n.id))
  const visibleTopics = new Set(filteredArticles.value.map(n => n.topic))
  const nodes = graph.value.nodes.filter(n => n.kind === 'root'
    || (n.kind === 'topic' ? visibleTopics.has(n.topic) : visibleIds.has(n.id)))
  const ids = new Set(nodes.map(n => n.id))
  const links = graph.value.links.filter(l => ids.has(l.source) && ids.has(l.target))
  const focus = new Set([selectedId.value])
  links.forEach(l => {
    if (l.source === selectedId.value) focus.add(l.target)
    if (l.target === selectedId.value) focus.add(l.source)
  })
  const hasFocus = selectedId.value !== 'huizhou'
  const singleTopic = visibleTopics.size === 1
  const compact = chart.getWidth() < 480
  const data = nodes.map(n => {
    const topic = topicById.value.get(n.topic)
    let x = 0, y = 0
    if (singleTopic) {
      if (n.kind === 'root') x = -210
      if (n.kind === 'topic') x = -65
      if (n.kind === 'article') {
        const index = filteredArticles.value.findIndex(a => a.id === n.id)
        const angle = ((index + 0.5) / filteredArticles.value.length - 0.5) * Math.PI * 1.55
        x = -30 + Math.cos(angle) * 230
        y = Math.sin(angle) * 230
      }
    } else if (topic) {
      const index = graph.value.topics.findIndex(t => t.id === n.topic)
      const angle = index * Math.PI * 2 / graph.value.topics.length - Math.PI / 2
      x = Math.cos(angle) * 245
      y = Math.sin(angle) * 245
      if (n.kind === 'article') {
        const siblings = articles.value.filter(a => a.topic === n.topic)
        const position = siblings.findIndex(a => a.id === n.id)
        const spread = angle + position * Math.PI * 2 / siblings.length
        const radius = 62 + (position % 2) * 22
        x += Math.cos(spread) * radius
        y += Math.sin(spread) * radius
      }
    }
    const isSelected = n.id === selectedId.value
    const isArticle = n.kind === 'article'
    const isRoot = n.kind === 'root'
    const color = isRoot ? INK.red : topic.color
    const highlighted = !hasFocus || focus.has(n.id)
    return {
      id: n.id, name: n.name, kind: n.kind, x, y,
      symbolSize: isRoot ? (compact ? 46 : 66) : isArticle ? (isSelected ? 17 : compact ? 7 : 11) : compact ? 34 : 45,
      draggable: true,
      itemStyle: {
        color: isRoot || isSelected ? color : isArticle ? color : INK.paperLight,
        borderColor: color, borderWidth: isArticle ? 1 : 1.6,
        opacity: highlighted ? 1 : 0.22,
        shadowBlur: isSelected ? 14 : 0, shadowColor: `${color}40`,
      },
      label: {
        show: !compact || !isArticle || singleTopic || isSelected,
        formatter: isRoot ? '徽州\n文脉' : isArticle ? n.name : `${n.name.slice(0, 2)}\n${n.name.slice(2)}`,
        position: isArticle ? 'right' : 'inside', distance: 6,
        color: isRoot || (!isArticle && isSelected) ? INK.paperLight : INK.inkSoft,
        fontFamily: '"STKaiti", "KaiTi", "Microsoft YaHei", sans-serif',
        fontSize: isRoot ? (compact ? 15 : 19) : isArticle ? 11 : compact ? 12 : 14,
        lineHeight: isRoot && !compact ? 24 : 16,
        width: isArticle ? (singleTopic ? 138 : 78) : 52,
        overflow: 'truncate', opacity: highlighted ? 1 : 0.3,
      },
      emphasis: { itemStyle: { borderWidth: 3, opacity: 1 }, label: { opacity: 1 } },
    }
  })
  // 等比例铺开坐标，防止宽屏或单篇搜索时节点被拉成椭圆。
  const xs = data.map(n => n.x), ys = data.map(n => n.y)
  const spanX = Math.max(...xs) - Math.min(...xs) || 2
  const spanY = Math.max(...ys) - Math.min(...ys) || 2
  const labelSpace = singleTopic ? 90 : compact ? 0 : 45
  const scale = Math.min((chart.getWidth() - (compact ? 50 : 100) - labelSpace) / spanX, (chart.getHeight() - 110) / spanY)
  const width = spanX * scale, height = spanY * scale
  chart.setOption({
    animation: !reducedMotion.value,
    animationDuration: 700,
    animationDurationUpdate: 650,
    animationEasingUpdate: 'cubicInOut',
    tooltip: {
      trigger: 'item', renderMode: 'richText', confine: true,
      backgroundColor: INK.paperLight, borderColor: INK.paperEdge,
      textStyle: { color: INK.inkSoft, fontSize: 12 },
      formatter: p => p.dataType === 'edge'
        ? (p.data.kind === 'related' ? `共同提及：${p.data.keywords.join('、')}` : '主题收录')
        : p.name,
    },
    series: [{
      id: 'knowledge', type: 'graph', layout: 'none',
      roam: true, scaleLimit: { min: 0.55, max: 3 },
      left: (chart.getWidth() - width - labelSpace) / 2, top: (chart.getHeight() - height) / 2,
      width, height,
      ...(reset ? { center: null, zoom: 1 } : {}),
      data,
      links: links.map(l => ({
        ...l,
        lineStyle: {
          color: l.kind === 'related' ? INK.blue : INK.inkLine,
          type: l.kind === 'related' ? 'dashed' : 'solid',
          curveness: l.kind === 'related' ? 0.12 : 0.04,
          width: l.source === selectedId.value || l.target === selectedId.value ? 1.8 : 0.8,
          opacity: hasFocus ? (l.source === selectedId.value || l.target === selectedId.value ? 0.85 : 0.12)
            : l.kind === 'related' ? 0.35 : 0.5,
        },
      })),
      labelLayout: { hideOverlap: true },
      emphasis: { focus: 'adjacency' },
    }],
  }, { notMerge: reset })
}

async function loadGraph() {
  loading.value = true
  error.value = false
  try {
    graph.value = await getKnowledgeGraph(controller.signal)
    loading.value = false
    await nextTick()
    if (controller.signal.aborted || !graph.value.stats.articles) return
    chart = echarts.init(chartEl.value)
    chart.on('click', p => {
      if (p.dataType === 'node') {
        const node = graph.value.nodes.find(n => n.id === p.data.id)
        if (chart.getWidth() < 480) readFromIndex(node)
        else chooseNode(node)
      }
    })
    renderGraph(true)
    resizeObserver = new ResizeObserver(() => { chart.resize(); renderGraph() })
    resizeObserver.observe(chartEl.value)
  } catch {
    if (!controller.signal.aborted) error.value = true
  } finally {
    loading.value = false
  }
}

watch([activeTopic, keyword], () => renderGraph(true))
watch(selectedId, () => renderGraph())
function onMotionChange(event) {
  reducedMotion.value = event.matches
  if (event.matches) stopTour()
  renderGraph()
}
function onVisibilityChange() { if (document.hidden) stopTour() }
onMounted(() => {
  loadGraph()
  motion.addEventListener('change', onMotionChange)
  document.addEventListener('visibilitychange', onVisibilityChange)
})
onBeforeUnmount(() => {
  controller.abort()
  stopTour()
  resizeObserver?.disconnect()
  chart?.dispose()
  motion.removeEventListener('change', onMotionChange)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>

<template>
  <div class="page knowledge-page">
    <nav class="breadcrumb" aria-label="当前位置">
      <router-link to="/ask">徽史问答官</router-link><span aria-hidden="true">/</span><span>知识图谱</span>
      <router-link class="back-link" to="/ask">← 返回问答</router-link>
    </nav>
    <header class="atlas-head">
      <div class="page-head">
        <span class="atlas-kicker">循 文 脉 · 识 徽 州</span>
        <h2>徽州知识图谱</h2>
        <p>从一篇典藏出发，看见建筑、风物与人文之间的联系。</p>
      </div>
      <div v-if="graph && !error" class="atlas-stats" aria-label="知识库概览">
        <div><b>{{ graph.stats.articles }}</b><span>篇原文资料</span></div>
        <div><b>{{ graph.stats.topics }}</b><span>个文化主题</span></div>
        <div><b>{{ graph.stats.relations }}</b><span>组词语关联</span></div>
      </div>
    </header>

    <div v-if="loading" class="ink-card state-panel" role="status"><span class="state-seal">知</span><h3>正在展开徽州文脉…</h3><p>读取知识库，连接篇章。</p></div>
    <div v-else-if="error" class="ink-card state-panel" role="alert"><span class="state-seal">知</span><h3>暂时未能展开图谱</h3><p>资料加载失败，请稍后重试。</p><button class="ink-button" @click="loadGraph">重新加载</button></div>
    <div v-else-if="!graph.stats.articles" class="ink-card state-panel"><span class="state-seal">知</span><h3>知识库尚无可展示的资料</h3><p>添加徽文化资料后，即可在此展开文脉。</p></div>

    <template v-else>
      <section class="atlas-filters ink-card" aria-label="筛选知识图谱">
        <div class="filter-top">
          <span class="filter-label">寻脉</span>
          <label class="search-box"><span aria-hidden="true">⌕</span><input v-model="keyword" type="search" placeholder="搜索篇名或原文，如：朱熹、马头墙" aria-label="搜索知识库" @input="onSearch" /></label>
          <span class="result-count" aria-live="polite">当前 {{ filteredArticles.length }} / {{ articles.length }} 篇</span>
        </div>
        <div class="topic-filters">
          <button :class="{ active: !activeTopic }" :aria-pressed="!activeTopic" @click="chooseTopic('')">全部文脉</button>
          <button v-for="topic in graph.topics" :key="topic.id" :style="{ '--topic-color': topicById.get(topic.id).color }"
                  :class="{ active: activeTopic === topic.id }" :aria-pressed="activeTopic === topic.id" @click="chooseTopic(topic.id)">
            <i aria-hidden="true"></i>{{ topic.name }}<small>{{ topic.count }}</small>
          </button>
        </div>
      </section>

      <div class="atlas-layout">
        <section class="network-panel ink-card" aria-label="知识关系网络">
          <div class="network-heading">
            <div><h3>{{ activeTopic ? topicById.get(activeTopic).name : '文脉全景' }}</h3><span>{{ touring ? '主题漫游中 · 循序翻阅文化主题' : '点选一篇资料，循线发现关联' }}</span></div>
            <div class="network-actions">
              <button :aria-pressed="touring" :disabled="reducedMotion" @click="toggleTour">{{ touring ? 'Ⅱ 暂停漫游' : '▷ 主题漫游' }}</button>
              <button @click="resetView">复位</button>
            </div>
          </div>
          <div class="network-stage">
            <div class="paper-rings" aria-hidden="true"></div>
            <span class="margin-note" aria-hidden="true">一府六县 · 千年文脉</span>
            <div ref="chartEl" class="network-canvas" role="img" aria-label="徽州知识网络，可点击节点浏览；完整资料亦可通过下方资料索引选择。"></div>
            <div v-if="!filteredArticles.length" class="no-results" role="status"><h3>未寻得这一篇</h3><p>试试其他词语，或清除主题与搜索条件。</p><button class="ink-button" @click="resetView">查看全部资料</button></div>
            <span class="atlas-stamp" aria-hidden="true">徽<br />州</span>
          </div>
          <footer class="network-legend"><span><i class="solid-line"></i>主题收录</span><span><i class="dashed-line"></i>共同提及</span><em>滚轮缩放 · 拖动画布 / 节点</em></footer>
        </section>

        <aside ref="readingEl" class="reading-panel ink-card" aria-label="节点详情" aria-live="polite">
          <div class="reading-kicker"><span>阅 览 笺</span><span>{{ selected?.kind === 'article' ? '原文资料' : selected?.kind === 'topic' ? '文化主题' : '文脉总览' }}</span></div>
          <template v-if="selected?.kind === 'article'">
            <span class="topic-tag" :style="{ color: topicById.get(selected.topic).color }">{{ topicById.get(selected.topic).name }}</span>
            <h3>{{ selected.name }}</h3>
            <p class="source-name">知识库来源 · {{ selected.source }}</p>
            <p class="article-excerpt">{{ excerpt(selected.text) }}</p>
            <button class="text-button" @click="reading = true">展开原文 <span aria-hidden="true">↗</span></button>
            <div class="keyword-tags"><span v-for="word in selected.keywords" :key="word">{{ word }}</span></div>
            <div class="related-section">
              <h4>循线延伸 <small>{{ related.length }} 篇</small></h4>
              <button v-for="item in related" :key="item.article.id" class="related-item" @click="openRelated(item.article)">
                <b>{{ item.article.name }} <span aria-hidden="true">↗</span></b><small>共同提及 · {{ item.keywords.join('、') }}</small>
              </button>
              <p v-if="!related.length" class="quiet-note">暂未形成关键词连线，可从同主题资料继续阅读。</p>
            </div>
            <router-link class="ink-button ask-link" :to="questionLink">带着这篇资料去提问 <span aria-hidden="true">→</span></router-link>
            <p class="draft-note">问题将填入问答输入框，可编辑后发送。</p>
          </template>
          <template v-else>
            <span class="reading-seal" aria-hidden="true">{{ selected?.kind === 'topic' ? '篇' : '知' }}</span>
            <h3>{{ selected?.name || '徽州文脉' }}</h3>
            <p class="intro-copy">{{ selected?.kind === 'topic' ? `这一主题收录 ${selectedArticles.length} 篇资料。点选篇章，阅读原文，也看看它与其他主题如何相连。` : '一座村落、一方歙砚、一曲徽调。散落在典籍中的徽州，在这里连成一张可探索的文化地图。' }}</p>
            <div class="reading-guide"><p><b>观全景</b><span>沿主题，读懂知识库的脉络</span></p><p><b>读一篇</b><span>点节点，回到真实的资料原文</span></p><p><b>再追问</b><span>带着好奇，向徽史问答官提问</span></p></div>
            <div class="starter-list"><h4>不妨从这里读起</h4><button v-for="article in selectedArticles.slice(0, 3)" :key="article.id" @click="openRelated(article)">{{ article.name }} <span aria-hidden="true">↗</span></button></div>
            <router-link class="text-button return-ask" to="/ask">向徽史问答官提问 →</router-link>
          </template>
        </aside>
      </div>

      <section class="source-index ink-card" aria-label="资料索引">
        <div class="index-heading"><h3>篇章索引 <small>{{ filteredArticles.length }} 篇</small></h3><span>与上方图谱同步 · 选择篇名即可阅读</span></div>
        <div v-if="filteredArticles.length" class="index-grid">
          <button v-for="(article, index) in filteredArticles" :key="article.id" :class="{ selected: selectedId === article.id }" :aria-pressed="selectedId === article.id" @click="readFromIndex(article)">
            <span class="index-number">{{ String(index + 1).padStart(2, '0') }}</span><span>{{ article.name }}</span><i :style="{ background: topicById.get(article.topic).color }" aria-hidden="true"></i>
          </button>
        </div>
        <p v-else class="quiet-note">没有匹配的资料。</p>
      </section>
      <p class="atlas-note">图谱取自徽史问答官现有知识库。实线表示主题收录，虚线表示两篇原文共同提及至少两个文化关键词，仅供探索关联；原文按知识库内容呈现。</p>

      <el-dialog v-model="reading" :title="selected?.name" width="min(760px, calc(100vw - 32px))" class="knowledge-dialog">
        <template v-if="selected?.kind === 'article'"><p class="dialog-source">知识库原文 · {{ selected.source }}</p><article class="full-article">{{ selected.text }}</article></template>
        <template #footer><el-button @click="reading = false">合卷</el-button><router-link class="ink-button" :to="questionLink">就此提问 →</router-link></template>
      </el-dialog>
    </template>
  </div>
</template>

<style scoped>
.knowledge-page { max-width: 1180px; padding-top: 23px; }
.knowledge-page button, .knowledge-page input { font: inherit; }
.knowledge-page button { cursor: pointer; }
.knowledge-page button:focus-visible, .knowledge-page a:focus-visible, .knowledge-page input:focus-visible { outline: 2px solid var(--red); outline-offset: 4px; }
.breadcrumb { display: flex; gap: 12px; align-items: center; font-size: 12px; color: var(--ink-line); margin-bottom: 27px; }
.breadcrumb a { color: var(--brown); text-decoration: none; }
.breadcrumb a:hover { color: var(--red); }
.breadcrumb .back-link { margin-left: auto; }
.atlas-head { display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.atlas-head .page-head { margin-bottom: 24px; }
.atlas-kicker { display: block; color: var(--red); font-size: 11px; letter-spacing: 3px; margin-bottom: 11px; }
.atlas-head h2 { font-size: 32px; letter-spacing: 5px; }
.atlas-head .page-head p { margin-top: 12px; font-size: 13px; }
.atlas-stats { display: flex; flex-shrink: 0; gap: 26px; padding-bottom: 8px; }
.atlas-stats div { display: flex; flex-direction: column; gap: 6px; padding-left: 21px; border-left: 1px solid var(--ink-faint); }
.atlas-stats b { font: 32px var(--num-font); color: var(--brown); }
.atlas-stats span { font-size: 11px; color: var(--ink-line); }
.atlas-filters { padding: 16px 20px; margin-bottom: 16px; }
.filter-top { display: flex; align-items: center; gap: 18px; }
.filter-label { font: 18px var(--zh-font); letter-spacing: 3px; color: var(--brown); }
.search-box { display: flex; align-items: center; width: 400px; max-width: 100%; gap: 8px; border-bottom: 1px solid var(--ink-faint); }
.search-box > span { font-size: 25px; color: var(--brown); }
.search-box input { width: 100%; border: none; background: transparent; padding: 9px 0; font-size: 12px; color: var(--ink); }
.search-box input::placeholder { color: var(--ink-line); }
.result-count { margin-left: auto; font-size: 11px; white-space: nowrap; color: var(--ink-line); }
.topic-filters { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 14px; }
.topic-filters button { display: inline-flex; align-items: center; gap: 5px; border: 1px solid transparent; padding: 6px 8px; color: var(--ink-soft); background: transparent; border-radius: 3px; font-size: 12px; transition: background .2s; }
.topic-filters button:hover { background: var(--paper); }
.topic-filters button.active { border-color: var(--ink-faint); background: var(--paper-dark); color: var(--ink); }
.topic-filters i, .index-grid i { width: 5px; height: 5px; border-radius: 50%; background: var(--topic-color); flex-shrink: 0; }
.topic-filters small { font: 11px var(--num-font); opacity: .65; }
.atlas-layout { display: grid; grid-template-columns: minmax(0, 1fr) 290px; gap: 16px; align-items: start; }
.network-panel { padding: 0; overflow: hidden; }
.network-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 19px 21px 0; }
.network-heading h3 { margin: 0 0 6px; font-size: 19px; font-weight: 700; }
.network-heading > div > span { font-size: 11px; color: var(--ink-line); }
.network-actions { display: flex; gap: 6px; }
.network-actions button { border: 1px solid var(--ink-faint); border-radius: 3px; background: transparent; padding: 6px 9px; font-size: 11px; white-space: nowrap; color: var(--brown); }
.network-actions button:hover, .network-actions button[aria-pressed="true"] { background: var(--paper-dark); }
.network-actions button:disabled { opacity: .4; cursor: default; }
.network-stage { position: relative; height: 550px; background: radial-gradient(ellipse at center, rgba(216, 201, 174, .2), transparent 65%); }
.network-canvas { width: 100%; height: 100%; position: relative; z-index: 1; }
.paper-rings { position: absolute; width: 310px; height: 310px; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 1px solid rgba(154, 132, 112, .1); border-radius: 50%; box-shadow: 0 0 0 64px rgba(216, 201, 174, .045), 0 0 0 126px rgba(216, 201, 174, .035); animation: ink-breath 7s ease-in-out infinite; pointer-events: none; }
.margin-note { position: absolute; left: 16px; top: 40px; writing-mode: vertical-rl; letter-spacing: 4px; color: var(--ink-line); opacity: .5; font: 12px var(--zh-font); }
.atlas-stamp { position: absolute; right: 21px; bottom: 25px; color: var(--red); opacity: .65; font: 19px/1.15 var(--zh-font); border: 1px solid currentColor; padding: 5px 4px; transform: rotate(-5deg); }
.network-legend { display: flex; flex-wrap: wrap; gap: 17px; border-top: 1px solid rgba(154, 132, 112, .18); padding: 13px 20px; font-size: 10px; color: var(--ink-line); }
.network-legend span { display: flex; align-items: center; gap: 7px; }
.network-legend i { width: 20px; border-top: 1px solid var(--ink-line); }
.network-legend .dashed-line { border-top-style: dashed; border-color: var(--blue); }
.network-legend em { font-style: normal; margin-left: auto; }
.reading-panel { padding: 21px; min-height: 655px; position: relative; scroll-margin-top: 130px; }
.reading-kicker { display: flex; justify-content: space-between; gap: 8px; border-bottom: 1px solid var(--ink-faint); padding-bottom: 14px; margin-bottom: 20px; font-size: 11px; color: var(--ink-line); }
.reading-kicker > span:first-child { color: var(--red); }
.reading-panel h3 { font-size: 23px; line-height: 1.5; letter-spacing: 2px; margin: 10px 0; overflow-wrap: anywhere; }
.reading-seal { display: block; font: 32px var(--zh-font); color: var(--red); border: 1px solid currentColor; width: 50px; height: 50px; padding: 6px; text-align: center; margin: 26px 0 17px; border-radius: 2px; }
.intro-copy, .article-excerpt { font-size: 12px; line-height: 2; color: var(--ink-soft); margin: 0 0 14px; overflow-wrap: anywhere; }
.reading-guide { border-block: 1px dashed var(--ink-faint); padding: 10px 0; margin: 23px 0; }
.reading-guide p { display: flex; gap: 12px; align-items: center; margin: 13px 0; }
.reading-guide b { color: var(--brown); font: 15px var(--zh-font); white-space: nowrap; }
.reading-guide span { font-size: 11px; color: var(--ink-line); line-height: 1.7; }
.reading-panel h4 { font: 15px var(--zh-font); color: var(--brown); margin: 0 0 12px; }
.starter-list button { display: flex; width: 100%; justify-content: space-between; text-align: left; border: none; border-bottom: 1px solid rgba(154, 132, 112, .15); padding: 10px 0; background: transparent; color: var(--ink-soft); font-size: 12px; gap: 8px; }
.starter-list button:hover { color: var(--red); }
.return-ask { display: block; margin-top: 22px; }
.topic-tag { display: inline-block; border: 1px solid currentColor; border-radius: 2px; font-size: 10px; padding: 3px 8px; }
.source-name { margin: 0 0 18px; font-size: 10px; line-height: 1.7; color: var(--ink-line); overflow-wrap: anywhere; }
.text-button { color: var(--red); border: none; background: transparent; font-size: 12px; text-decoration: none; padding: 0; }
.keyword-tags { display: flex; flex-wrap: wrap; gap: 5px; margin: 17px 0 22px; }
.keyword-tags span { font-size: 10px; padding: 3px 6px; color: var(--brown); background: var(--paper); border-radius: 2px; }
.related-section { border-top: 1px dashed var(--ink-faint); padding-top: 18px; }
.related-section h4 small { margin-left: 6px; font: 10px 'Microsoft YaHei', sans-serif; color: var(--ink-line); }
.related-item { display: block; width: 100%; background: transparent; border: none; text-align: left; padding: 0 0 13px; color: var(--ink-soft); }
.related-item b { display: flex; justify-content: space-between; gap: 8px; font-size: 12px; font-weight: 400; line-height: 1.6; }
.related-item:hover b { color: var(--red); }
.related-item small { display: block; font-size: 10px; line-height: 1.7; color: var(--ink-line); padding-top: 4px; }
.ink-button { display: inline-flex; align-items: center; justify-content: center; gap: 10px; background: linear-gradient(120deg, var(--brown), var(--ink)); color: var(--paper-light); border: none; padding: 11px 14px; font-size: 12px; border-radius: 3px; text-decoration: none; }
.ink-button:hover { background: linear-gradient(120deg, var(--red), var(--brown)); }
.ask-link { width: 100%; margin-top: 11px; }
.draft-note { font-size: 10px; color: var(--ink-line); text-align: center; margin: 10px 0 0; line-height: 1.7; }
.source-index { margin-top: 16px; }
.index-heading { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 14px; }
.index-heading h3 { font-size: 18px; margin: 0; }
.index-heading h3 small { font: 11px 'Microsoft YaHei', sans-serif; color: var(--ink-line); letter-spacing: 0; }
.index-heading > span { font-size: 11px; color: var(--ink-line); }
.index-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2px 20px; max-height: 205px; overflow-y: auto; scrollbar-width: thin; scrollbar-color: var(--ink-faint) transparent; }
.index-grid button { display: flex; align-items: center; gap: 10px; color: var(--ink-soft); text-align: left; background: transparent; border: 1px solid transparent; border-bottom-color: rgba(154, 132, 112, .15); padding: 10px 6px; font-size: 12px; line-height: 1.5; }
.index-grid button:hover, .index-grid button.selected { background: var(--paper); color: var(--red); }
.index-grid button.selected { border-color: var(--ink-faint); }
.index-grid .index-number { color: var(--ink-line); font: 12px var(--num-font); }
.index-grid i { margin-left: auto; }
.atlas-note { margin: 14px 6px 0; font-size: 11px; color: var(--ink-line); line-height: 1.9; }
.quiet-note { color: var(--ink-line); font-size: 12px; line-height: 1.9; }
.state-panel { text-align: center; padding: 75px 24px; }
.state-seal { display: inline-block; padding: 9px; font: 34px var(--zh-font); color: var(--red); border: 1px solid currentColor; }
.state-panel h3 { font-size: 24px; }
.state-panel p, .no-results p { font-size: 13px; color: var(--ink-line); line-height: 1.8; }
.no-results { position: absolute; inset: 0; z-index: 2; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--paper-light); padding: 30px; text-align: center; }
.no-results h3 { font-size: 26px; margin: 0; }
.dialog-source { font-size: 12px; color: var(--ink-line); padding-bottom: 14px; border-bottom: 1px solid var(--ink-faint); }
.full-article { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 14px; line-height: 2.1; max-height: 60vh; overflow-y: auto; padding-right: 12px; color: var(--ink-soft); }
:global(.knowledge-dialog) { background: var(--paper-light); }
:global(.knowledge-dialog .el-dialog__title) { font-family: var(--zh-font); }
.knowledge-dialog .ink-button { margin-left: 12px; }
@keyframes ink-breath { 0%, 100% { opacity: .35; } 50% { opacity: 1; } }
@media (max-width: 1000px) {
  .atlas-stats { gap: 14px; }
  .atlas-stats div { padding-left: 14px; }
  .atlas-layout { grid-template-columns: minmax(0, 1fr) 260px; gap: 12px; }
  .network-heading { flex-wrap: wrap; }
  .network-stage { height: 540px; }
  .network-legend em { margin-left: 0; }
}
@media (max-width: 760px) {
  .knowledge-page { padding: 20px 16px 40px; }
  .atlas-head { flex-wrap: wrap; gap: 0; }
  .atlas-head .page-head { margin-bottom: 20px; }
  .atlas-head h2 { font-size: 29px; }
  .atlas-stats { width: 100%; justify-content: space-between; margin-bottom: 17px; padding: 0; }
  .atlas-stats div { flex: 1; }
  .atlas-stats b { font-size: 27px; }
  .atlas-filters { padding: 13px; }
  .filter-top { flex-wrap: wrap; gap: 5px 10px; }
  .filter-label { font-size: 16px; }
  .search-box { flex: 1; min-width: 0; }
  .result-count { width: 100%; text-align: right; }
  .topic-filters { gap: 5px; }
  .topic-filters button { padding: 6px; }
  .atlas-layout { grid-template-columns: 1fr; }
  .network-heading { padding-inline: 15px; }
  .network-stage { height: 450px; }
  .network-legend { padding-inline: 14px; gap: 12px; }
  .reading-panel { min-height: auto; }
  .reading-seal { margin-top: 10px; }
  .index-grid { grid-template-columns: 1fr; max-height: 260px; }
  .index-heading { flex-wrap: wrap; }
  .index-heading > span { font-size: 10px; }
}
@media (prefers-reduced-motion: reduce) {
  .paper-rings { animation: none; }
  .topic-filters button { transition: none; }
}
</style>
