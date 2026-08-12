import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/Home.vue'), meta: { title: '首页' } },
  { path: '/bigscreen', name: 'bigscreen', component: () => import('../bigscreen/index.vue'), meta: { title: '徽州意象馆 · 文旅数字大屏', fullscreen: true } },
  { path: '/studio', name: 'studio', component: () => import('../views/Studio.vue'), meta: { title: 'AI徽画工坊' } },
  { path: '/ask', name: 'ask', component: () => import('../views/Ask.vue'), meta: { title: '徽史问答官' } },
  { path: '/craft', name: 'craft', component: () => import('../views/Craft.vue'), meta: { title: '文创印务局' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · 墨蕴徽州` : '墨蕴徽州'
})

export default router
