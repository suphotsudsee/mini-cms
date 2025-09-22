import axios from 'axios'

const baseURL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('mini-cms-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const resolveFileUrl = (filepath) => {
  if (!filepath) return '#'
  if (/^https?:/i.test(filepath)) {
    return filepath
  }
  const sanitized = filepath.startsWith('/') ? filepath : `/${filepath}`
  return `${baseURL}${sanitized}`
}

export default api
