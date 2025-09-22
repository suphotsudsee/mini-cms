import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../services/api'

const TOKEN_KEY = 'mini-cms-token'
const USERNAME_KEY = 'mini-cms-username'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const username = ref(localStorage.getItem(USERNAME_KEY) || '')
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => Boolean(token.value))

  const setSession = (accessToken, name) => {
    token.value = accessToken
    username.value = name
    if (accessToken) {
      localStorage.setItem(TOKEN_KEY, accessToken)
      api.defaults.headers.common.Authorization = `Bearer ${accessToken}`
    } else {
      localStorage.removeItem(TOKEN_KEY)
      delete api.defaults.headers.common.Authorization
    }

    if (name) {
      localStorage.setItem(USERNAME_KEY, name)
    } else {
      localStorage.removeItem(USERNAME_KEY)
    }
  }

  if (token.value) {
    api.defaults.headers.common.Authorization = `Bearer ${token.value}`
  }

  const login = async ({ username: user, password }) => {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.post('/auth/login', { username: user, password })
      if (!data?.access_token) {
        throw new Error('ไม่สามารถรับโทเค็นจากเซิร์ฟเวอร์ได้')
      }
      setSession(data.access_token, user)
      return data
    } catch (err) {
      const message =
        err.response?.data?.detail || err.message || 'เกิดข้อผิดพลาดในการเข้าสู่ระบบ'
      error.value = message
      throw new Error(message)
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    setSession('', '')
  }

  return {
    token,
    username,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
  }
})
