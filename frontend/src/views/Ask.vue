<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { askQuestion } from '../api'
import { ElMessage } from 'element-plus'

/* ---------------- 知识库覆盖范围 ---------------- */
const SCOPES = ['徽派建筑', '徽州三雕', '文房四宝', '徽商文化', '徽剧·黄梅戏', '民俗·饮食', '非遗·工艺']

/* ---------------- 关键词 → 延伸追问 ---------------- */
const FOLLOWUP_MAP = [
  {
    keys: ['四水归堂', '天井', '马头墙', '徽派建筑', '祠堂', '承志堂'],
    qs: ['马头墙除了好看，还有什么实际功能？', '徽派建筑的天井为什么叫"四水归堂"？', '徽州宗祠的建筑有什么讲究？'],
  },
  {
    keys: ['三雕', '砖雕', '木雕', '石雕', '门罩'],
    qs: ['徽州三雕各自用在哪里？', '徽州木雕的常用题材有哪些？'],
  },
  {
    keys: ['徽商', '儒商', '商帮', '胡雪岩', '徽州商人'],
    qs: ['徽商为什么被称为"儒商"？', '徽商主要经营哪些生意？', '徽商是怎么衰落的？'],
  },
  {
    keys: ['宏村', '西递', '古村落', '画里乡村', '水圳', '皖南'],
    qs: ['宏村的水系是怎么设计的？', '西递和宏村有哪些区别？', '皖南古村落为什么能入选世界遗产？'],
  },
  {
    keys: ['徽墨', '歙砚', '文房四宝', '宣纸', '湖笔'],
    qs: ['歙砚有什么独特之处？', '徽墨的制作工艺是怎样的？', '宣纸为什么"纸寿千年"？'],
  },
  {
    keys: ['黄梅戏', '徽剧', '徽戏', '戏曲', '京剧'],
    qs: ['徽剧与京剧有什么关系？', '黄梅戏的经典曲目有哪些？'],
  },
  {
    keys: ['毛豆腐', '臭鳜鱼', '徽菜', '饮食', '美食', '一品锅'],
    qs: ['臭鳜鱼为什么"闻着臭、吃着香"？', '徽菜的口味特点是什么？'],
  },
]
const DEFAULT_FOLLOWUPS = ['徽州三雕是哪三种雕刻？', '皖南古村落为什么能入选世界遗产？', '徽州四大名茶分别是什么？']

const WELCOME_QUESTIONS = [
  '徽派建筑的"四水归堂"是什么意思？',
  '徽商为什么被称为"儒商"？',
  '宏村的水系是如何设计的？',
  '徽州三雕指哪三种雕刻？',
  '徽墨和歙砚为何名扬天下？',
  '徽剧与京剧有什么关系？',
]

/* ---------------- 会话存储（localStorage 多会话） ---------------- */
const SESSIONS_KEY = 'moyun_ask_sessions_v1'
const MAX_SESSIONS = 20

function loadSessions() {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY)
    const arr = raw ? JSON.parse(raw) : []
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

const sessions = ref(loadSessions())
const currentId = ref(sessions.value.length ? sessions.value[0].id : null)
const messages = ref([])
const sending = ref(false)
const questionText = ref('')
const threadRef = ref(null)

let typeTimer = null

/* ---------------- 消息运行时字段补齐 ---------------- */
function ensureRuntime(m) {
  if (m.display === undefined) m.display = m.text
  if (m.done === undefined) m.done = true
  if (!m.srcOpen) m.srcOpen = {}
  if (m.srcPanelOpen === undefined) m.srcPanelOpen = false
  return m
}

function runtimeizeSession(s) {
  s.messages.forEach(ensureRuntime)
  return s
}

/* ---------------- 会话管理 ---------------- */
function persistSessions() {
  const clean = sessions.value.slice(0, MAX_SESSIONS).map(s => ({
    id: s.id,
    title: s.title,
    updatedAt: s.updatedAt,
    messages: s.messages.map(m => ({
      role: m.role,
      text: m.text,
      sources: m.sources || [],
      createdAt: m.createdAt,
    })),
  }))
  localStorage.setItem(SESSIONS_KEY, JSON.stringify(clean))
}

function newSession() {
  clearType()
  const s = {
    id: 's_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7),
    title: '新会话',
    updatedAt: Date.now(),
    messages: [],
  }
  sessions.value.unshift(s)
  currentId.value = s.id
  messages.value = s.messages
  persistSessions()
}

function loadSession(id) {
  const s = sessions.value.find(x => x.id === id)
  if (!s) return
  clearType()
  currentId.value = id
  runtimeizeSession(s)
  messages.value = s.messages
  nextTick(scrollToBottom)
}

function deleteSession(id) {
  clearType()
  const removing = id === currentId.value
  sessions.value = sessions.value.filter(x => x.id !== id)
  if (removing) {
    currentId.value = null
    messages.value = []
  }
  persistSessions()
  ElMessage.success('会话已删除')
}

function updateTitle(s, q) {
  if (s.title === '新会话') {
    s.title = q.length > 12 ? q.slice(0, 12) + '…' : q
  }
  s.updatedAt = Date.now()
}

/* ---------------- 打字机 ---------------- */
function clearType() {
  if (typeTimer) { clearInterval(typeTimer); typeTimer = null }
}

function typeWrite(m) {
  clearType()
  m.display = ''
  m.done = false
  const full = m.text
  const step = Math.max(2, Math.ceil(full.length / 220))
  let i = 0
  typeTimer = setInterval(() => {
    i += step
    m.display = full.slice(0, i)
    scrollToBottom()
    if (i >= full.length) {
      clearInterval(typeTimer)
      typeTimer = null
      m.display = full
      m.done = true
      scrollToBottom()
    }
  }, 16)
}

function skipType(m) {
  if (m.done) return
  clearType()
  m.display = m.text
  m.done = true
  scrollToBottom()
}

/* ---------------- 提问 / 回答 ---------------- */
function computeFollowups(q) {
  for (const grp of FOLLOWUP_MAP) {
    if (grp.keys.some(k => q.includes(k))) return grp.qs
  }
  return DEFAULT_FOLLOWUPS
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    const el = threadRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function onSend() {
  const q = questionText.value.trim()
  if (!q) return
  if (sending.value) return
  if (!currentId.value) newSession()

  const cur = sessions.value.find(s => s.id === currentId.value)
  if (!cur) { newSession(); return }

  messages.value.push({ role: 'user', text: q, createdAt: Date.now() })
  questionText.value = ''
  updateTitle(cur, q)
  persistSessions()
  scrollToBottom()

  sending.value = true
  try {
    const res = await askQuestion(q)
    const aiMsg = {
      role: 'ai',
      text: res.answer || '',
      sources: res.sources || [],
      createdAt: Date.now(),
      display: '',
      done: false,
      srcOpen: {},
      srcPanelOpen: false,
      followups: computeFollowups(q),
    }
    messages.value.push(aiMsg)
    persistSessions()
    scrollToBottom()
    typeWrite(aiMsg)
  } catch (e) {
    ElMessage.error('问答失败：请确认后端已启动且 DeepSeek 已配置')
    messages.value.push({
      role: 'ai',
      text: '很抱歉，这次问答没有成功。请确认后端服务已启动、DeepSeek 已配置后再试一次。',
      sources: [],
      createdAt: Date.now(),
      display: '很抱歉，这次问答没有成功。请确认后端服务已启动、DeepSeek 已配置后再试一次。',
      done: true,
      srcOpen: {},
      srcPanelOpen: false,
      followups: [],
    })
    scrollToBottom()
  } finally {
    sending.value = false
  }
}

function quickAsk(q) {
  questionText.value = q
  onSend()
}

/* ---------------- 消息操作 ---------------- */
async function copyMsg(m) {
  try {
    await navigator.clipboard.writeText(m.text)
    ElMessage.success('已复制回答')
  } catch {
    ElMessage.warning('复制失败，请手动选择文本复制')
  }
}

function redoMsg(m) {
  const idx = messages.value.indexOf(m)
  const q = idx > 0 && messages.value[idx - 1].role === 'user' ? messages.value[idx - 1].text : ''
  if (q) quickAsk(q)
}

/* ---------------- 来源引用 ---------------- */
function parseSegments(text) {
  if (!text) return []
  const segs = []
  const re = /\[来源(\d*)\]/g
  let last = 0
  let m
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) segs.push({ type: 'text', text: text.slice(last, m.index) })
    segs.push({ type: 'cite', n: m[1] ? parseInt(m[1], 10) : 1 })
    last = m.index + m[0].length
  }
  if (last < text.length) segs.push({ type: 'text', text: text.slice(last) })
  return segs
}

function togglePanel(m) {
  m.srcPanelOpen = !m.srcPanelOpen
}

function toggleSource(m, n) {
  m.srcPanelOpen = true
  m.srcOpen[n - 1] = !m.srcOpen[n - 1]
  nextTick(() => {
    const panel = threadRef.value
    if (panel) panel.scrollTop = panel.scrollHeight
  })
}

function truncate(s, n) {
  if (!s) return ''
  return s.length > n ? s.slice(0, n) + '…' : s
}

function fmtTime(t) {
  const d = new Date(t)
  const pad = x => String(x).padStart(2, '0')
  return `${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/* ---------------- 生命周期 ---------------- */
onMounted(() => {
  if (sessions.value.length) {
    loadSession(sessions.value[0].id)
  } else {
    newSession()
  }
})

onBeforeUnmount(() => {
  clearType()
})
</script>

<template>
  <div class="page ask-page">
    <div class="page-head">
      <h2>徽史问答官</h2>
      <p>基于徽文化知识库的智能问答 —— 先检索，再回答，言必有据</p>
    </div>

    <div class="ask-wrap">
      <!-- 左侧：会话历史 + 知识范围 -->
      <aside class="ask-side">
        <button class="new-btn" @click="newSession">
          <span class="new-plus">＋</span> 新 会 话
        </button>

        <div class="side-block">
          <div class="side-title">会话历史</div>
          <div class="session-list">
            <div
              v-for="s in sessions"
              :key="s.id"
              class="session-item"
              :class="{ active: s.id === currentId }"
              @click="loadSession(s.id)"
            >
              <span class="s-title">{{ s.title }}</span>
              <span class="s-time">{{ fmtTime(s.updatedAt) }}</span>
              <span class="s-del" title="删除会话" @click.stop="deleteSession(s.id)">✕</span>
            </div>
            <div v-if="!sessions.length" class="side-empty">暂无历史会话</div>
          </div>
        </div>

        <div class="side-block">
          <div class="side-title">知识库覆盖</div>
          <div class="scope-tags">
            <span v-for="t in SCOPES" :key="t" class="scope-tag">{{ t }}</span>
          </div>
        </div>

        <div class="side-note">
          引擎：bge-m3 本地向量检索 + DeepSeek 大模型
          <br />
          回答末尾标注 [来源N]，点击可查看对应资料
        </div>
      </aside>

      <!-- 右侧：对话区 -->
      <section class="ask-chat">
        <div class="chat-thread" ref="threadRef">
          <!-- 欢迎空态 -->
          <div v-if="!messages.length" class="chat-welcome">
            <div class="w-seal">问</div>
            <h3>徽州千年，一问便知</h3>
            <p>从建筑、商帮到三雕、戏曲 —— 输入问题，我先检索徽文化知识库，再给出有出处的回答。</p>
            <div class="w-samples">
              <button v-for="q in WELCOME_QUESTIONS" :key="q" @click="quickAsk(q)">{{ q }}</button>
            </div>
          </div>

          <!-- 消息流 -->
          <template v-for="(m, i) in messages" :key="i">
            <!-- 用户消息 -->
            <div v-if="m.role === 'user'" class="msg msg-user">
              <div class="bubble user-bubble">{{ m.text }}</div>
              <div class="avatar user-avatar">我</div>
            </div>

            <!-- AI 消息 -->
            <div v-else class="msg msg-ai">
              <div class="avatar ai-avatar">徽</div>
              <div class="ai-body">
                <div class="ai-name">徽史问答官</div>

                <div class="ai-text" :class="{ typing: !m.done }" @click="skipType(m)">
                  <template v-for="(seg, k) in parseSegments(m.display)" :key="k">
                    <template v-if="seg.type === 'text'">{{ seg.text }}</template>
                    <sup v-else class="cite-sup" @click.stop="toggleSource(m, seg.n)">{{ seg.n }}</sup>
                  </template>
                  <span v-if="!m.done" class="cursor">▌</span>
                </div>

                <!-- 引用来源 -->
                <transition name="fade">
                  <div v-if="m.done && m.sources.length" class="ai-sources">
                    <div class="src-head" @click="togglePanel(m)">
                      <span class="src-dot"></span>
                      引用来源 · {{ m.sources.length }} 条
                      <span class="src-arrow">{{ m.srcPanelOpen ? '收起' : '展开' }}</span>
                    </div>
                    <transition name="fade">
                      <div v-if="m.srcPanelOpen" class="src-list">
                        <div v-for="(s, j) in m.sources" :key="j" class="src-item">
                          <span class="src-idx">{{ j + 1 }}</span>
                          <span v-if="!m.srcOpen[j]" class="src-text" @click="m.srcOpen[j] = true">
                            {{ truncate(s, 120) }}
                            <em v-if="s.length > 120">展开</em>
                          </span>
                          <span v-else class="src-text open" @click="m.srcOpen[j] = false">{{ s }}</span>
                        </div>
                      </div>
                    </transition>
                  </div>
                </transition>

                <!-- 延伸追问 -->
                <transition name="fade">
                  <div v-if="m.done && m.followups.length" class="ai-followups">
                    <div class="fu-title">延伸追问</div>
                    <div class="fu-chips">
                      <button v-for="fq in m.followups" :key="fq" @click="quickAsk(fq)">{{ fq }}</button>
                    </div>
                  </div>
                </transition>

                <!-- 操作 -->
                <div v-if="m.done" class="ai-actions">
                  <button @click="copyMsg(m)">复制</button>
                  <button @click="redoMsg(m)">重问</button>
                </div>
              </div>
            </div>
          </template>

          <!-- 检索中 -->
          <div v-if="sending" class="msg msg-ai">
            <div class="avatar ai-avatar">徽</div>
            <div class="ai-body">
              <div class="ai-name">徽史问答官</div>
              <div class="think-dots"><span></span><span></span><span></span></div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="composer">
          <el-input
            v-model="questionText"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 5 }"
            resize="none"
            placeholder="关于徽文化的任何问题…（Enter 发送，Shift+Enter 换行）"
            @keydown.enter.exact.prevent="onSend"
          />
          <div class="composer-bar">
            <span class="engine-tip">检索徽文化知识库后作答 · 言必有据</span>
            <button class="send-btn" :disabled="sending || !questionText.trim()" @click="onSend">
              {{ sending ? '检索中…' : '发 送' }}
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.ask-page { max-width: 1180px; }

/* ============ 双栏布局（等高） ============ */
.ask-wrap {
  display: grid;
  grid-template-columns: 288px 1fr;
  gap: 16px;
  align-items: stretch;
  height: calc(100vh - 200px);
  min-height: 540px;
}

/* ============ 左侧栏 ============ */
.ask-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px;
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0) 45%),
    var(--paper-light);
  border: 1px solid rgba(106, 71, 53, 0.28);
  border-radius: 6px;
  box-shadow: 0 3px 16px rgba(74, 58, 42, 0.08);
  min-height: 0;
}
.new-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px 0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--paper-light);
  font-family: var(--zh-font);
  font-size: 15px;
  letter-spacing: 4px;
  background: linear-gradient(120deg, #6a4735, #241b15);
  box-shadow: 0 2px 8px rgba(74, 58, 42, 0.25);
  transition: all .2s;
}
.new-btn:hover { background: linear-gradient(120deg, var(--red), #6a4735); }
.new-plus { font-size: 17px; }

.side-block { display: flex; flex-direction: column; min-height: 0; }
.side-title {
  font-family: var(--zh-font);
  font-size: 13px;
  letter-spacing: 3px;
  color: var(--brown);
  padding-bottom: 7px;
  border-bottom: 1px dashed rgba(106, 71, 53, 0.3);
  margin-bottom: 9px;
}

/* 会话列表 */
.session-list {
  overflow-y: auto;
  flex: 1;
  min-height: 120px;
  max-height: 320px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.session-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 26px 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all .18s;
}
.session-item:hover { background: rgba(106, 71, 53, 0.07); }
.session-item.active {
  background: rgba(160, 58, 46, 0.10);
  border-color: rgba(160, 58, 46, 0.35);
}
.s-title {
  flex: 1;
  font-size: 13px;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.s-time { font-size: 10px; color: var(--ink-line); flex-shrink: 0; }
.s-del {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--ink-line);
  font-size: 11px;
  opacity: 0;
  transition: opacity .18s;
}
.session-item:hover .s-del { opacity: 1; }
.s-del:hover { color: var(--red); }
.side-empty { font-size: 12px; color: var(--ink-line); padding: 10px 4px; }

/* 知识范围标签 */
.scope-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.scope-tag {
  padding: 3px 9px;
  font-size: 11px;
  color: var(--brown);
  border: 1px solid rgba(106, 71, 53, 0.35);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.5);
  letter-spacing: 1px;
}

.side-note {
  margin-top: auto;
  padding: 10px;
  font-size: 11px;
  line-height: 1.8;
  color: var(--ink-line);
  background: rgba(106, 71, 53, 0.06);
  border-left: 3px solid var(--orange);
  border-radius: 2px;
}

/* ============ 右侧对话区 ============ */
.ask-chat {
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: rgba(250, 245, 236, 0.55);
  border: 1px solid rgba(106, 71, 53, 0.28);
  border-radius: 6px;
  box-shadow: 0 3px 16px rgba(74, 58, 42, 0.08);
  overflow: hidden;
}

.chat-thread {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 22px 20px 10px;
  scroll-behavior: smooth;
}
.chat-thread::-webkit-scrollbar { width: 6px; }
.chat-thread::-webkit-scrollbar-thumb { background: rgba(106, 71, 53, 0.25); border-radius: 3px; }

/* ---- 欢迎空态 ---- */
.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
  min-height: 100%;
}
.w-seal {
  width: 56px;
  height: 56px;
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
  margin-bottom: 18px;
}
.chat-welcome h3 {
  margin: 0 0 10px;
  font-size: 24px;
  letter-spacing: 6px;
  color: var(--ink);
}
.chat-welcome p { margin: 0 0 22px; color: var(--ink-soft); font-size: 14px; letter-spacing: 1px; }
.w-samples { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; max-width: 560px; }
.w-samples button {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid rgba(106, 71, 53, 0.35);
  background: rgba(255, 255, 255, 0.6);
  color: var(--brown);
  font-size: 13px;
  cursor: pointer;
  transition: all .2s;
}
.w-samples button:hover {
  color: var(--red);
  border-color: var(--red);
  background: rgba(160, 58, 46, 0.06);
}

/* ---- 消息 ---- */
.msg { display: flex; gap: 10px; margin-bottom: 18px; }
.msg-user { flex-direction: row-reverse; }
.avatar {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--zh-font);
  font-size: 14px;
  font-weight: 700;
}
.user-avatar {
  background: var(--ink-soft);
  color: var(--paper-light);
}
.ai-avatar {
  background: linear-gradient(135deg, var(--red), #6a4735);
  color: var(--paper-light);
  box-shadow: inset 0 0 0 1.5px rgba(243, 236, 227, 0.35);
}

.bubble.user-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 10px 10px 3px 10px;
  background: linear-gradient(150deg, #e6dac7, #dccdb6);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.7;
  box-shadow: 0 2px 8px rgba(74, 58, 42, 0.12);
  word-break: break-word;
  white-space: pre-wrap;
}

.ai-body { max-width: 82%; min-width: 0; }
.ai-name { font-size: 12px; color: var(--brown); letter-spacing: 2px; margin-bottom: 6px; font-family: var(--zh-font); }
.ai-text {
  position: relative;
  padding: 13px 16px;
  border-radius: 3px 10px 10px 10px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(106, 71, 53, 0.22);
  font-size: 14px;
  line-height: 2;
  color: var(--ink);
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 2px 10px rgba(74, 58, 42, 0.08);
}
.ai-text.typing { cursor: pointer; border-style: dashed; }

.cite-sup {
  color: var(--red);
  font-weight: 700;
  font-size: 11px;
  cursor: pointer;
  margin: 0 2px;
  padding: 0 3px;
  background: rgba(160, 58, 46, 0.10);
  border-radius: 3px;
  user-select: none;
}
.cite-sup:hover { background: rgba(160, 58, 46, 0.20); }

.cursor { display: inline-block; margin-left: 2px; color: var(--red); animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* ---- 引用来源 ---- */
.ai-sources {
  margin-top: 10px;
  border: 1px solid rgba(197, 123, 58, 0.35);
  border-radius: 5px;
  background: rgba(197, 123, 58, 0.06);
  overflow: hidden;
}
.src-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 12px;
  color: var(--brown);
  letter-spacing: 1px;
  cursor: pointer;
  user-select: none;
}
.src-head:hover { color: var(--red); }
.src-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--orange);
  box-shadow: 0 0 0 3px rgba(197, 123, 58, 0.2);
}
.src-arrow { margin-left: auto; font-size: 11px; color: var(--ink-line); }

.src-list { padding: 0 12px 12px; display: flex; flex-direction: column; gap: 8px; }
.src-item {
  display: flex;
  gap: 9px;
  font-size: 12px;
  line-height: 1.8;
  color: var(--ink-soft);
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.55);
  border-left: 3px solid var(--orange);
  border-radius: 2px;
}
.src-idx {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(160, 58, 46, 0.14);
  color: var(--red);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 3px;
}
.src-text { cursor: pointer; word-break: break-all; }
.src-text em { font-style: normal; color: var(--orange); font-size: 11px; margin-left: 4px; }
.src-text.open { cursor: default; }

/* ---- 延伸追问 ---- */
.ai-followups { margin-top: 12px; }
.fu-title { font-size: 11px; color: var(--ink-line); letter-spacing: 2px; margin-bottom: 7px; }
.fu-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.fu-chips button {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px dashed rgba(160, 58, 46, 0.45);
  background: rgba(160, 58, 46, 0.05);
  color: var(--brown);
  font-size: 12px;
  cursor: pointer;
  transition: all .2s;
}
.fu-chips button:hover {
  color: var(--red);
  border-color: var(--red);
  background: rgba(160, 58, 46, 0.10);
}

/* ---- 操作 ---- */
.ai-actions { display: flex; gap: 10px; margin-top: 8px; padding-left: 4px; }
.ai-actions button {
  border: none;
  background: none;
  color: var(--ink-line);
  font-size: 12px;
  cursor: pointer;
  padding: 2px 4px;
  transition: color .18s;
}
.ai-actions button:hover { color: var(--red); }

/* ---- 检索中动画 ---- */
.think-dots { display: flex; gap: 5px; padding: 12px 16px; }
.think-dots span {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--orange);
  animation: bounce 1.2s infinite ease-in-out;
}
.think-dots span:nth-child(2) { animation-delay: .15s; }
.think-dots span:nth-child(3) { animation-delay: .3s; }
@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); opacity: .5; } 40% { transform: translateY(-6px); opacity: 1; } }

/* ---- 输入区 ---- */
.composer {
  padding: 12px 16px 14px;
  border-top: 1px solid rgba(106, 71, 53, 0.22);
  background: rgba(250, 245, 236, 0.9);
}
.composer-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 9px;
}
.engine-tip { font-size: 11px; color: var(--ink-line); letter-spacing: 1px; }
.send-btn {
  padding: 8px 26px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--paper-light);
  font-family: var(--zh-font);
  font-size: 14px;
  letter-spacing: 4px;
  background: linear-gradient(120deg, var(--red), #6a4735);
  box-shadow: 0 2px 8px rgba(160, 58, 46, 0.3);
  transition: all .2s;
}
.send-btn:hover:not(:disabled) { filter: brightness(1.1); }
.send-btn:disabled { opacity: .5; cursor: not-allowed; }

/* ---- 过渡 ---- */
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease, transform .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-6px); }

/* ---- 窄屏 ---- */
@media (max-width: 900px) {
  .ask-wrap { grid-template-columns: 1fr; height: auto; }
  .ask-side { order: 2; }
  .session-list { max-height: 160px; }
}
</style>
