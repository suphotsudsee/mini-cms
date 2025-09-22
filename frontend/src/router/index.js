import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: Home, meta: { title: 'หน้าแรก' } },
    { path: '/login', name: 'Login', component: Login, meta: { title: 'เข้าสู่ระบบ' } },
    {
      path: '/admin',
      name: 'Dashboard',
      component: Dashboard,
      meta: { requiresAuth: true, title: 'แดชบอร์ดผู้ดูแล' },
    },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta?.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'Login',
      query: { redirect: to.fullPath },
    }
  }
  if (to.name === 'Login' && authStore.isAuthenticated) {
    return { name: 'Dashboard' }
  }
  return true
})

router.afterEach((to) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} | Mini CMS`
  } else {
    document.title = 'Mini CMS'
  }
})

export default router
