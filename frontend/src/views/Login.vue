<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const form = reactive({ username: '', password: '' })
const showPassword = ref(false)
const submitError = ref('')

const handleSubmit = async () => {
  submitError.value = ''
  try {
    await authStore.login(form)
    router.push(route.query.redirect || { name: 'Dashboard' })
  } catch (err) {
    submitError.value = err.message
  }
}
</script>

<template>
  <div class="mx-auto grid max-w-5xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:items-center lg:gap-16">
    <section class="space-y-6">
      <span class="inline-flex items-center gap-2 rounded-full border border-purple-500/40 bg-purple-500/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-purple-200">
        Secure Access
      </span>
      <h1 class="text-3xl font-semibold text-white sm:text-4xl">เข้าสู่ระบบผู้ดูแล Mini CMS</h1>
      <p class="text-sm leading-relaxed text-slate-300 sm:text-base">
        จัดการข่าวสาร สร้างประกาศใหม่ และแนบไฟล์ให้บุคลากรดาวน์โหลดได้จากศูนย์กลางเดียว ตรวจสอบความถูกต้องก่อนเผยแพร่เพื่อให้ข้อมูลที่ส่งถึงผู้รับมีความน่าเชื่อถือที่สุด
      </p>
      <div class="rounded-2xl border border-purple-500/30 bg-purple-500/10 p-5 text-sm text-purple-100">
        <p class="font-medium">บัญชีเริ่มต้นสำหรับทดสอบ</p>
        <p class="mt-1 text-xs text-purple-200/80">username: <span class="font-semibold">admin</span> · password: <span class="font-semibold">admin123</span></p>
        <p class="mt-3 text-xs text-purple-200/70">สามารถเปลี่ยนรหัสผ่านได้จากฝั่ง Backend (ไฟล์ .env)</p>
      </div>
    </section>

    <section class="rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-purple-500/10 backdrop-blur">
      <form class="space-y-6" @submit.prevent="handleSubmit">
        <div class="space-y-2">
          <label class="block text-sm font-medium text-slate-200" for="username">ชื่อผู้ใช้</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            class="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 focus:border-purple-400 focus:ring-2 focus:ring-purple-400/40"
            placeholder="เช่น admin"
          />
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-medium text-slate-200" for="password">รหัสผ่าน</label>
          <div class="relative">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              class="w-full rounded-2xl border border-slate-800 bg-slate-950/60 px-4 py-3 pr-12 text-sm text-slate-100 focus:border-purple-400 focus:ring-2 focus:ring-purple-400/40"
              placeholder="รหัสผ่านของผู้ดูแล"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-3 flex items-center text-xs font-semibold uppercase tracking-wide text-purple-200"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'ซ่อน' : 'แสดง' }}
            </button>
          </div>
        </div>

        <div v-if="submitError" class="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {{ submitError }}
        </div>

        <button
          type="submit"
          class="w-full rounded-2xl bg-gradient-to-r from-purple-500 via-sky-500 to-blue-500 px-4 py-3 text-sm font-semibold text-slate-900 shadow-lg shadow-purple-500/20 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="authStore.loading"
        >
          <span v-if="authStore.loading" class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-900 border-t-transparent"></span>
          เข้าสู่ระบบ
        </button>

        <p class="text-center text-xs text-slate-500">
          ระบบนี้สำหรับผู้ดูแลระบบเท่านั้น หากไม่มีบัญชี โปรดติดต่อแอดมินของระบบเพื่อขอสิทธิ์การใช้งาน
        </p>
      </form>
    </section>
  </div>
</template>
