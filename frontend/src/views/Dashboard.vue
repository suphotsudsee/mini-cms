<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { resolveFileUrl } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const news = ref([])
const loading = ref(true)
const error = ref('')
const refreshing = ref(false)
const createState = reactive({ title: '', content: '' })
const createLoading = ref(false)
const createMessage = ref('')
const uploadState = reactive({})
const editingId = ref(null)
const editState = reactive({ title: '', content: '' })
const editLoading = ref(false)
const editFeedback = reactive({ message: '', status: 'info' })
const deletingId = ref(null)
const deleteErrors = reactive({})

let editResetTimer = null

const hasNews = computed(() => news.value.length > 0)

const imageFiles = (files) => (files || []).filter((file) => file?.is_image)
const otherFiles = (files) => (files || []).filter((file) => !file?.is_image)

const formatDate = (value) =>
  new Intl.DateTimeFormat('th-TH', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))

const handleUnauthorized = () => {
  authStore.logout()
  router.push({ name: 'Login', query: { redirect: '/admin' } })
}

const fetchNews = async () => {
  if (!refreshing.value) {
    loading.value = true
  }
  error.value = ''
  try {
    const { data } = await api.get('/news/')
    news.value = data
  } catch (err) {
    if (err.response?.status === 401) {
      handleUnauthorized()
    } else {
      error.value = err.response?.data?.detail || err.message || 'ไม่สามารถโหลดข่าวได้'
    }
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const refresh = async () => {
  refreshing.value = true
  await fetchNews()
}

const resetCreateForm = () => {
  createState.title = ''
  createState.content = ''
}

const resetEditState = () => {
  editState.title = ''
  editState.content = ''
  editFeedback.message = ''
  editFeedback.status = 'info'
  if (editResetTimer) {
    clearTimeout(editResetTimer)
    editResetTimer = null
  }
}

const startEdit = (item) => {
  if (editResetTimer) {
    clearTimeout(editResetTimer)
    editResetTimer = null
  }
  editingId.value = item.id
  editState.title = item.title
  editState.content = item.content
  editFeedback.message = ''
  editFeedback.status = 'info'
  deleteErrors[item.id] = ''
}

const cancelEdit = () => {
  editingId.value = null
  resetEditState()
}

const handleEditSubmit = async (newsId) => {
  if (!editState.title.trim() || !editState.content.trim()) {
    editFeedback.message = 'กรุณากรอกหัวข้อและเนื้อหาให้ครบถ้วน'
    editFeedback.status = 'error'
    return
  }

  editLoading.value = true
  editFeedback.message = ''

  try {
    const { data } = await api.put(`/news/${newsId}`, {
      title: editState.title.trim(),
      content: editState.content.trim(),
    })
    const index = news.value.findIndex((item) => item.id === newsId)
    if (index !== -1) {
      news.value.splice(index, 1, data)
    }
    editFeedback.message = 'แก้ไขข่าวสำเร็จ'
    editFeedback.status = 'success'
    editResetTimer = window.setTimeout(() => {
      cancelEdit()
    }, 1200)
  } catch (err) {
    if (err.response?.status === 401) {
      handleUnauthorized()
      return
    }
    editFeedback.message = err.response?.data?.detail || err.message || 'ไม่สามารถแก้ไขข่าวได้'
    editFeedback.status = 'error'
  } finally {
    editLoading.value = false
  }
}

const handleCreate = async () => {
  if (!createState.title.trim() || !createState.content.trim()) {
    createMessage.value = 'กรุณากรอกหัวข้อและเนื้อหาให้ครบถ้วน'
    return
  }
  createLoading.value = true
  createMessage.value = ''
  try {
    const { data } = await api.post('/news/', {
      title: createState.title.trim(),
      content: createState.content.trim(),
    })
    news.value = [data, ...news.value]
    createMessage.value = 'บันทึกข่าวสำเร็จ'
    resetCreateForm()
  } catch (err) {
    if (err.response?.status === 401) {
      handleUnauthorized()
      return
    }
    createMessage.value = err.response?.data?.detail || err.message || 'ไม่สามารถบันทึกข่าวได้'
  } finally {
    createLoading.value = false
  }
}

const handleUpload = async (newsId, file) => {
  if (!file) {
    uploadState[newsId] = { message: 'กรุณาเลือกไฟล์ก่อน', status: 'error', loading: false }
    return
  }
  uploadState[newsId] = { loading: true, message: '', status: 'info' }
  try {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post(`/news/${newsId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const target = news.value.find((item) => item.id === newsId)
    if (target) {
      target.files = target.files ? [data, ...target.files] : [data]
    }
    uploadState[newsId] = { loading: false, message: 'อัปโหลดไฟล์สำเร็จ', status: 'success' }
  } catch (err) {
    if (err.response?.status === 401) {
      handleUnauthorized()
      return
    }
    uploadState[newsId] = {
      loading: false,
      message: err.response?.data?.detail || err.message || 'อัปโหลดไฟล์ไม่สำเร็จ',
      status: 'error',
    }
  }
}

const onFileChange = (event, newsId) => {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }
  handleUpload(newsId, file)
  event.target.value = ''
}

const handleDelete = async (newsId) => {
  if (typeof window !== 'undefined' && !window.confirm('ต้องการลบข่าวนี้หรือไม่?')) {
    return
  }
  deleteErrors[newsId] = ''
  deletingId.value = newsId
  try {
    await api.delete(`/news/${newsId}`)
    news.value = news.value.filter((item) => item.id !== newsId)
    delete uploadState[newsId]
    delete deleteErrors[newsId]
    if (editingId.value === newsId) {
      cancelEdit()
    }
  } catch (err) {
    if (err.response?.status === 401) {
      handleUnauthorized()
      return
    }
    deleteErrors[newsId] = err.response?.data?.detail || err.message || 'ไม่สามารถลบข่าวได้'
  } finally {
    deletingId.value = null
  }
}

onMounted(fetchNews)

onBeforeUnmount(() => {
  if (editResetTimer) {
    clearTimeout(editResetTimer)
  }
})
</script>

<template>
  <div class="mx-auto flex max-w-6xl flex-col gap-10 px-4 py-12 sm:px-6 lg:px-8">
    <section class="rounded-3xl border border-emerald-500/30 bg-gradient-to-br from-slate-900 via-slate-950 to-black p-10 shadow-2xl shadow-emerald-500/10">
      <div class="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
        <div class="space-y-4 md:max-w-2xl">
          <span class="inline-flex items-center gap-2 rounded-full border border-emerald-400/40 bg-emerald-500/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-200">
            Admin Workspace
          </span>
          <h1 class="text-3xl font-semibold text-white sm:text-4xl">แดชบอร์ดจัดการข่าวสาร</h1>
          <p class="text-sm leading-relaxed text-slate-300 sm:text-base">
            สร้างและเผยแพร่ข่าวสารสำคัญ พร้อมแนบเอกสารที่เกี่ยวข้อง อัปเดตข้อมูลให้ทันสมัย เพื่อให้บุคลากรเข้าถึงข่าวสารล่าสุดได้เสมอ
          </p>
        </div>
        <div class="grid gap-4 rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-6 text-sm text-emerald-100">
          <div>
            <p class="text-xs uppercase tracking-[0.2em] text-emerald-300/70">ผู้ใช้งานปัจจุบัน</p>
            <p class="text-2xl font-semibold text-white">{{ authStore.username }}</p>
          </div>
          <button
            type="button"
            class="flex items-center justify-center gap-2 rounded-full border border-emerald-400/60 bg-emerald-500/20 px-4 py-2 text-sm font-medium text-emerald-100 transition hover:bg-emerald-400/30"
            @click="refresh"
            :disabled="loading || refreshing"
          >
            <span v-if="refreshing" class="h-4 w-4 animate-spin rounded-full border-2 border-emerald-200 border-t-transparent"></span>
            <span>{{ refreshing ? 'กำลังรีเฟรช' : 'รีเฟรชรายการข่าว' }}</span>
          </button>
          <p class="text-xs text-emerald-200/70">ระบบจะรีเฟรชอัตโนมัติหลังจากเพิ่มข่าวหรือไฟล์ใหม่</p>
        </div>
      </div>
    </section>

    <section class="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-start">
      <div class="space-y-6">
        <header class="flex flex-col gap-2">
          <h2 class="text-xl font-semibold text-white">รายการข่าวที่เผยแพร่</h2>
          <p class="text-sm text-slate-400">จัดการไฟล์แนบของข่าวแต่ละรายการได้จากที่นี่</p>
        </header>

        <div v-if="loading" class="grid gap-4">
          <div v-for="index in 3" :key="index" class="animate-pulse rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div class="h-5 w-2/3 rounded bg-slate-700/60"></div>
            <div class="mt-3 h-20 rounded bg-slate-800/60"></div>
          </div>
        </div>

        <div v-else-if="error" class="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-red-200">
          {{ error }}
        </div>

        <div v-else-if="!hasNews" class="grid place-items-center rounded-2xl border border-slate-800 bg-slate-900/60 p-16 text-center text-slate-400">
          <div class="space-y-3">
            <p class="text-lg font-semibold text-slate-200">ยังไม่มีข่าวในระบบ</p>
            <p>สร้างข่าวฉบับแรกจากแบบฟอร์มด้านขวา</p>
          </div>
        </div>

        <div v-else class="space-y-5">
          <article
            v-for="item in news"
            :key="item.id"
            class="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-lg shadow-emerald-500/5"
          >
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div class="space-y-4 md:flex-1">
                <p class="text-xs uppercase tracking-[0.25em] text-slate-500">รหัสข่าว #{{ item.id }}</p>
                <template v-if="editingId === item.id">
                  <form class="space-y-4" @submit.prevent="handleEditSubmit(item.id)">
                    <div class="space-y-2">
                      <label class="block text-sm font-medium text-slate-200" :for="`edit-title-${item.id}`">หัวข้อข่าว</label>
                      <input
                        :id="`edit-title-${item.id}`"
                        v-model="editState.title"
                        type="text"
                        class="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/40"
                        placeholder="แก้ไขหัวข้อข่าว"
                      />
                    </div>
                    <div class="space-y-2">
                      <label class="block text-sm font-medium text-slate-200" :for="`edit-content-${item.id}`">รายละเอียดข่าว</label>
                      <textarea
                        :id="`edit-content-${item.id}`"
                        v-model="editState.content"
                        rows="6"
                        class="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/40"
                        placeholder="แก้ไขรายละเอียดข่าว"
                      ></textarea>
                    </div>
                    <div
                      v-if="editFeedback.message"
                      class="rounded-2xl border px-4 py-3 text-sm"
                      :class="editFeedback.status === 'success'
                        ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100'
                        : 'border-red-500/40 bg-red-500/10 text-red-100'"
                    >
                      {{ editFeedback.message }}
                    </div>
                    <div class="flex flex-wrap gap-3">
                      <button
                        type="submit"
                        class="inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-900 shadow-lg shadow-emerald-500/20 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
                        :disabled="editLoading"
                      >
                        <span v-if="editLoading" class="h-4 w-4 animate-spin rounded-full border-2 border-slate-900 border-t-transparent"></span>
                        <span>บันทึกการแก้ไข</span>
                      </button>
                      <button
                        type="button"
                        class="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-800/60"
                        @click="cancelEdit"
                        :disabled="editLoading"
                      >
                        ยกเลิก
                      </button>
                    </div>
                  </form>
                </template>
                <template v-else>
                  <h3 class="text-2xl font-semibold text-white">{{ item.title }}</h3>
                  <p class="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">{{ item.content }}</p>
                </template>
              </div>
              <div class="flex flex-col items-end gap-3 text-right text-xs text-slate-500">
                <div class="flex flex-wrap justify-end gap-2 text-sm">
                  <button
                    v-if="editingId !== item.id"
                    type="button"
                    class="inline-flex items-center gap-2 rounded-full border border-emerald-400/60 bg-emerald-500/10 px-3 py-1 text-emerald-100 transition hover:bg-emerald-400/30"
                    @click="startEdit(item)"
                  >
                    แก้ไข
                  </button>
                  <button
                    v-else
                    type="button"
                    class="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1 text-slate-200 transition hover:bg-slate-700/60 disabled:cursor-not-allowed disabled:opacity-60"
                    @click="cancelEdit"
                    :disabled="editLoading"
                  >
                    ยกเลิกการแก้ไข
                  </button>
                  <button
                    type="button"
                    class="inline-flex items-center gap-2 rounded-full border border-red-500/40 bg-red-500/10 px-3 py-1 text-red-100 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-60"
                    @click="handleDelete(item.id)"
                    :disabled="deletingId === item.id"
                  >
                    <span v-if="deletingId === item.id" class="h-3 w-3 animate-spin rounded-full border border-red-200 border-t-transparent"></span>
                    <span>{{ deletingId === item.id ? 'กำลังลบ' : 'ลบ' }}</span>
                  </button>
                </div>
                <span class="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/70 px-3 py-1 text-slate-300">
                  เผยแพร่ {{ formatDate(item.created_at) }}
                </span>
                <span v-if="item.updated_at">แก้ไขล่าสุด {{ formatDate(item.updated_at) }}</span>
              </div>
            </div>

            <div class="mt-6 space-y-4">
              <div
                v-if="deleteErrors[item.id]"
                class="rounded-2xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100"
              >
                {{ deleteErrors[item.id] }}
              </div>
              <div class="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-950/60 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div class="space-y-1">
                  <p class="text-sm font-medium text-slate-100">อัปโหลดไฟล์แนบ</p>
                  <p class="text-xs text-slate-400">รองรับไฟล์ทุกประเภท ขนาดตามที่เซิร์ฟเวอร์กำหนด</p>
                </div>
                <label class="inline-flex cursor-pointer items-center gap-3 rounded-full bg-emerald-500/20 px-4 py-2 text-sm font-medium text-emerald-100 shadow-inner shadow-emerald-500/20 transition hover:bg-emerald-400/30">
                  <input type="file" class="hidden" @change="(event) => onFileChange(event, item.id)" />
                  <span>เลือกไฟล์</span>
                </label>
              </div>

              <div v-if="uploadState[item.id]?.message" :class="[
                'rounded-2xl px-4 py-3 text-sm',
                uploadState[item.id]?.status === 'success'
                  ? 'border border-emerald-500/40 bg-emerald-500/10 text-emerald-100'
                  : 'border border-red-500/40 bg-red-500/10 text-red-100',
              ]">
                {{ uploadState[item.id]?.message }}
              </div>

              <div v-if="imageFiles(item.files).length" class="space-y-3">
                <p class="text-sm font-medium text-slate-200">รูปภาพประกอบ</p>
                <div class="grid gap-3 sm:grid-cols-2">
                  <figure
                    v-for="file in imageFiles(item.files)"
                    :key="`image-${file.id}`"
                    class="overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/60"
                  >
                    <img :src="resolveFileUrl(file.filepath)" :alt="file.filename" class="h-48 w-full object-cover" />
                    <figcaption class="border-t border-slate-800/60 px-4 py-2 text-xs text-slate-400">
                      {{ file.filename }}
                    </figcaption>
                  </figure>
                </div>
              </div>

              <div v-if="otherFiles(item.files).length" class="space-y-3">
                <p class="text-sm font-medium text-slate-200">ไฟล์แนบอื่น ๆ {{ otherFiles(item.files).length }} รายการ</p>
                <ul class="grid gap-3 sm:grid-cols-2">
                  <li
                    v-for="file in otherFiles(item.files)"
                    :key="file.id"
                    class="flex items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-300"
                  >
                    <div>
                      <p class="font-medium text-slate-100">{{ file.filename }}</p>
                      <p class="text-xs text-slate-500">อัปโหลด {{ formatDate(file.uploaded_at) }}</p>
                    </div>
                    <a
                      :href="resolveFileUrl(file.filepath)"
                      class="text-xs font-semibold uppercase tracking-wider text-emerald-300 hover:text-emerald-200"
                      target="_blank"
                      rel="noopener"
                    >
                      เปิดดู
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </article>
        </div>
      </div>

      <aside class="space-y-6">
        <div class="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-xl shadow-emerald-500/10">
          <h2 class="text-xl font-semibold text-white">สร้างข่าวใหม่</h2>
          <p class="mt-1 text-sm text-slate-400">ระบุหัวข้อและรายละเอียดข่าว พร้อมตรวจสอบความถูกต้องก่อนกดเผยแพร่</p>

          <form class="mt-6 space-y-5" @submit.prevent="handleCreate">
            <div class="space-y-2">
              <label class="block text-sm font-medium text-slate-200" for="title">หัวข้อข่าว</label>
              <input
                id="title"
                v-model="createState.title"
                type="text"
                required
                class="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/40"
                placeholder="เช่น แจ้งปิดระบบประจำเดือน"
              />
            </div>

            <div class="space-y-2">
              <label class="block text-sm font-medium text-slate-200" for="content">รายละเอียดข่าว</label>
              <textarea
                id="content"
                v-model="createState.content"
                rows="6"
                required
                class="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/40"
                placeholder="อธิบายข้อมูลเพิ่มเติม เช่น วันเวลา เนื้อหา และลิงก์ที่เกี่ยวข้อง"
              ></textarea>
            </div>

            <div
              v-if="createMessage"
              class="rounded-2xl border px-4 py-3 text-sm"
              :class="createMessage === 'บันทึกข่าวสำเร็จ'
                ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100'
                : 'border-red-500/40 bg-red-500/10 text-red-100'"
            >
              {{ createMessage }}
            </div>

            <button
              type="submit"
              class="w-full rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-slate-900 shadow-lg shadow-emerald-500/20 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="createLoading"
            >
              <span v-if="createLoading" class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-900 border-t-transparent"></span>
              บันทึกข่าวและเผยแพร่
            </button>
          </form>
        </div>

        <div class="rounded-3xl border border-slate-800 bg-slate-950/70 p-6 text-xs text-slate-400">
          <h3 class="text-sm font-semibold text-slate-200">คำแนะนำในการเขียนข่าว</h3>
          <ul class="mt-3 space-y-2">
            <li>• ใช้ภาษากระชับ เข้าใจง่าย และระบุวันเวลาให้ชัดเจน</li>
            <li>• หากมีไฟล์แนบ ให้ตั้งชื่อไฟล์สื่อถึงเนื้อหาและเวอร์ชัน</li>
            <li>• สามารถอัปเดตแก้ไขข้อมูลได้จากฝั่ง Backend หากมีการเปลี่ยนแปลง</li>
          </ul>
        </div>
      </aside>
    </section>
  </div>
</template>
