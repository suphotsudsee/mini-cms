<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const navigation = [
  { name: 'Home', to: { name: 'Home' } },
  { name: 'แดชบอร์ด', to: { name: 'Dashboard' }, requiresAuth: true },
]

const isActive = (target) => route.name === target

const filteredNavigation = computed(() =>
  navigation.filter((item) => !item.requiresAuth || authStore.isAuthenticated)
)

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'Home' })
}

const currentYear = new Date().getFullYear()
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
    <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <RouterLink
          :to="{ name: 'Home' }"
          class="flex items-center gap-3 text-lg font-semibold tracking-tight text-sky-300"
        >
          <span
            class="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br from-sky-400 via-blue-500 to-indigo-600 font-bold text-slate-900 shadow-lg shadow-sky-500/40"
          >
            CMS
          </span>
          <span>
            Mini CMS
            <span class="block text-xs font-normal text-slate-400">ข่าวสาร & ไฟล์แนบ</span>
          </span>
        </RouterLink>

        <nav class="hidden items-center gap-1 rounded-full border border-slate-800 bg-slate-900/70 p-1 text-sm font-medium sm:flex">
          <RouterLink
            v-for="item in filteredNavigation"
            :key="item.name"
            :to="item.to"
            class="rounded-full px-4 py-2 transition hover:bg-slate-800 hover:text-white"
            :class="isActive(item.to.name) ? 'bg-slate-100 text-slate-900' : 'text-slate-300'"
          >
            {{ item.name }}
          </RouterLink>
        </nav>

        <div class="flex items-center gap-3 text-sm">
          <template v-if="authStore.isAuthenticated">
            <span class="hidden text-slate-300 sm:block">
              ลงชื่อเข้าใช้ในชื่อ <span class="font-semibold text-sky-300">{{ authStore.username }}</span>
            </span>
            <button
              class="rounded-full bg-sky-500 px-4 py-2 font-semibold text-slate-900 shadow-lg shadow-sky-500/30 transition hover:bg-sky-400"
              type="button"
              @click="handleLogout"
            >
              ออกจากระบบ
            </button>
          </template>
          <template v-else>
            <RouterLink
              :to="{ name: 'Login' }"
              class="rounded-full bg-sky-500 px-4 py-2 font-semibold text-slate-900 shadow-lg shadow-sky-500/30 transition hover:bg-sky-400"
            >
              เข้าสู่ระบบ
            </RouterLink>
          </template>
        </div>
      </div>
    </header>

    <main class="flex-1">
      <RouterView />
    </main>

    <footer class="border-t border-slate-800 bg-slate-950/80">
      <div class="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-6 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:text-sm">
        <p>© {{ currentYear }} Mini CMS. All rights reserved.</p>
        <p class="text-slate-400">ออกแบบเพื่อแสดงข่าวและจัดการไฟล์แนบของระบบภายในองค์กร</p>
      </div>
    </footer>
  </div>
</template>
