import axios from 'axios'

// 统一封装后端接口调用（开发环境经 vite 代理到 http://localhost:8000）
const http = axios.create({
  baseURL: '/api',
  timeout: 120000, // 生图可能较慢
})

// 生图：返回图片 Blob（style 控制 LoRA 叠加配比：ink | photo | balanced）
export async function generateImage(prompt, opts = {}) {
  const resp = await http.post('/generate', {
    prompt,
    negative_prompt: opts.negative_prompt || null,
    width: opts.width || 1024,
    height: opts.height || 1024,
    seed: opts.seed ?? 42,
    style: opts.style || 'balanced',
  }, { responseType: 'blob' })
  return URL.createObjectURL(resp.data)
}

// 问答：返回 { answer, sources }
export async function askQuestion(question) {
  const resp = await http.post('/ask', { question })
  return resp.data
}

// 知识图谱：与问答共用原文资料，不触发模型推理。
export async function getKnowledgeGraph(signal) {
  const resp = await http.get('/ask/knowledge-graph', { signal, timeout: 15000 })
  return resp.data
}

// 文创导出：返回图片 Blob（相同 seed + 描述 → 同一幅画，可跨模板复用）
export async function exportProduct(prompt, { title = '墨蕴徽州', subtitle = '', template = 'postcard', seed = null } = {}) {
  const resp = await http.post('/export', {
    prompt, title, subtitle, template, seed,
  }, { responseType: 'blob' })
  return URL.createObjectURL(resp.data)
}

// 大屏数据
export async function getTourOverview() {
  const resp = await http.get('/tour/overview')
  return resp.data
}

// 图像生成模式：查当前 / 切换
export async function getGenMode() {
  const resp = await http.get('/gen-mode')
  return resp.data
}
export async function switchGenMode(mode) {
  const resp = await http.post('/gen-mode', { mode })
  return resp.data
}
