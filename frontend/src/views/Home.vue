<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api, { resolveFileUrl } from '../services/api'

const news = ref([])
const loading = ref(true)
const refreshing = ref(false)
const error = ref('')

const newsCount = computed(() => news.value.length)

const imageFiles = (files) => (files || []).filter((file) => file?.is_image)
const otherFiles = (files) => (files || []).filter((file) => !file?.is_image)

const formatDate = (value) =>
  new Intl.DateTimeFormat('th-TH', {
    dateStyle: 'long',
    timeStyle: 'short',
  }).format(new Date(value))

const fetchNews = async () => {
  if (loading.value) {
    error.value = ''
  }
  try {
    const { data } = await api.get('/news/')
    news.value = data
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'โหลดข้อมูลไม่สำเร็จ'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const refresh = async () => {
  refreshing.value = true
  await fetchNews()
}

onMounted(fetchNews)
</script>

<template>
  <div class="mx-auto flex max-w-6xl flex-col gap-12 px-4 py-10 sm:px-6 lg:px-8">
    <section class="grid gap-8 rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-950 to-black p-10 text-slate-100 shadow-2xl shadow-sky-500/5">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div class="space-y-4 lg:max-w-2xl">
          <span class="inline-flex items-center gap-2 rounded-full border border-sky-500/40 bg-sky-500/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-sky-300">
            MINI CMS HUB
          </span>
          <h1 class="text-3xl font-semibold leading-tight text-white sm:text-4xl lg:text-5xl">
            ศูนย์กลางเผยแพร่ข่าวสารและเอกสารสำคัญของหน่วยงาน
          </h1>
          <p class="text-base text-slate-300 sm:text-lg">
            รวบรวมประกาศ แจ้งเตือน และไฟล์แนบล่าสุดไว้ในที่เดียว เพื่อให้ทีมงานทุกคนเข้าถึงข้อมูลสำคัญได้อย่างรวดเร็วและปลอดภัย
          </p>
        </div>
        <div class="grid gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
          <div>
            <p class="text-xs uppercase tracking-[0.2em] text-slate-500">จำนวนข่าวทั้งหมด</p>
            <p class="text-4xl font-semibold text-sky-300">{{ newsCount }}</p>
          </div>
          <button
            type="button"
            class="flex items-center justify-center gap-2 rounded-full bg-sky-500 px-4 py-2 font-medium text-slate-900 transition hover:bg-sky-400"
            @click="refresh"
            :disabled="loading || refreshing"
          >
            <span v-if="refreshing" class="h-4 w-4 animate-spin rounded-full border-2 border-slate-900 border-t-transparent"></span>
            <span>{{ refreshing ? 'กำลังอัปเดต' : 'รีเฟรชข้อมูลล่าสุด' }}</span>
          </button>
          <p class="text-xs text-slate-500">
            ข้อมูลถูกอัปเดตโดยอัตโนมัติจากระบบจัดการข่าวของผู้ดูแล หากต้องการเพิ่มข่าวใหม่ต้องเข้าสู่ระบบในโหมดผู้ดูแล
          </p>
        </div>
      </div>
      <div class="grid gap-3 text-xs text-slate-500 sm:grid-cols-3">
        <div class="rounded-2xl border border-slate-800/70 bg-slate-900/30 p-4">
          <p class="text-slate-400">พร้อมสำหรับ Mobile</p>
          <p class="mt-1 text-base font-medium text-slate-200">ออกแบบแบบ Responsive รองรับทุกหน้าจอ</p>
        </div>
        <div class="rounded-2xl border border-slate-800/70 bg-slate-900/30 p-4">
          <p class="text-slate-400">ไฟล์แนบปลอดภัย</p>
          <p class="mt-1 text-base font-medium text-slate-200">รองรับเอกสารแนบและลิงก์ดาวน์โหลด</p>
        </div>
        <div class="rounded-2xl border border-slate-800/70 bg-slate-900/30 p-4">
          <p class="text-slate-400">เชื่อมต่อ API</p>
          <p class="mt-1 text-base font-medium text-slate-200">ดึงข้อมูลข่าวจาก Mini CMS Backend</p>
        </div>
      </div>
    </section>

    <section class="space-y-6">
      <header class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 class="text-2xl font-semibold text-white">ข่าวสารล่าสุด</h2>
          <p class="text-sm text-slate-400">อัปเดตเรียลไทม์จากระบบ Mini CMS Backend</p>
        </div>
        <RouterLink
          :to="{ name: 'Dashboard' }"
          class="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-sm font-medium text-sky-200 transition hover:border-sky-500/40 hover:bg-sky-500/10"
        >
          สำหรับผู้ดูแลระบบ
        </RouterLink>
      </header>

      <div v-if="loading" class="grid gap-4">
        <div
          v-for="index in 3"
          :key="index"
          class="animate-pulse rounded-2xl border border-slate-800 bg-slate-900/50 p-6"
        >
          <div class="h-4 w-1/3 rounded bg-slate-700/60"></div>
          <div class="mt-4 h-6 w-2/3 rounded bg-slate-700/60"></div>
          <div class="mt-4 h-24 rounded bg-slate-800/60"></div>
        </div>
      </div>

      <div v-else-if="error" class="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-red-200">
        {{ error }}
      </div>

      <div v-else-if="!news.length" class="grid place-items-center rounded-2xl border border-slate-800 bg-slate-900/60 p-16 text-center text-slate-400">
        <div class="space-y-2">
          <p class="text-lg font-semibold text-slate-200">ยังไม่มีข่าวในระบบ</p>
          <p>เข้าสู่ระบบผู้ดูแลเพื่อเพิ่มข่าวสารฉบับแรก</p>
        </div>
      </div>

      <div v-else class="grid gap-6">
        <article
          v-for="item in news"
          :key="item.id"
          class="group rounded-3xl border border-slate-800 bg-slate-900/50 p-8 transition hover:border-sky-500/40 hover:bg-slate-900/80"
        >
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div class="space-y-3">
              <p class="text-xs uppercase tracking-[0.25em] text-slate-500">#{{ item.id }}</p>
              <h3 class="text-2xl font-semibold text-white transition group-hover:text-sky-300">
                {{ item.title }}
              </h3>
              <p class="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
                {{ item.content }}
              </p>
            </div>
            <div class="flex flex-col items-end gap-2 text-right text-sm text-slate-400">
              <span class="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1">
                <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
                เผยแพร่เมื่อ {{ formatDate(item.created_at) }}
              </span>
              <span v-if="item.updated_at" class="text-xs text-slate-500">
                แก้ไขล่าสุด {{ formatDate(item.updated_at) }}
              </span>
            </div>
          </div>

          <div v-if="imageFiles(item.files).length" class="mt-6 space-y-3">
            <p class="text-sm font-medium text-slate-200">รูปภาพประกอบ</p>
            <div class="grid gap-4 sm:grid-cols-2">
              <figure
                v-for="file in imageFiles(item.files)"
                :key="`image-${file.id}`"
                class="overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/60"
              >
                <img :src="resolveFileUrl(file.filepath)" :alt="file.filename" class="h-56 w-full object-cover" />
                <figcaption class="border-t border-slate-800/60 px-4 py-2 text-xs text-slate-400">
                  {{ file.filename }}
                </figcaption>
              </figure>
            </div>
          </div>

          <div v-if="otherFiles(item.files).length" class="mt-6 space-y-3">
            <p class="text-sm font-medium text-slate-200">ไฟล์แนบอื่น ๆ</p>
            <ul class="grid gap-3 sm:grid-cols-2">
              <li
                v-for="file in otherFiles(item.files)"
                :key="file.id"
                class="group/file flex items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-300 transition hover:border-sky-500/30 hover:bg-sky-500/10"
              >
                <div class="flex items-center gap-3">
                  <span class="grid h-10 w-10 place-items-center rounded-full bg-slate-800/80 text-sky-300 group-hover/file:bg-sky-500/20">
                    📎
                  </span>
                  <div>
                    <p class="font-medium text-slate-100 group-hover/file:text-sky-200">{{ file.filename }}</p>
                    <p class="text-xs text-slate-500">อัปโหลดเมื่อ {{ formatDate(file.uploaded_at) }}</p>
                  </div>
                </div>
                <a
                  :href="resolveFileUrl(file.filepath)"
                  class="text-xs font-semibold uppercase tracking-wider text-sky-300 hover:text-sky-200"
                  target="_blank"
                  rel="noopener"
                >
                  ดาวน์โหลด
                </a>
              </li>
            </ul>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
