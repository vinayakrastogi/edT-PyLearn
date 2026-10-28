import axios from 'axios'
import { API_BASE_URL } from './url'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Send httpOnly cookie with every request
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Protection': '1',
  },
})

// Streaks and the daily goal follow the learner's local date: tell the backend our UTC offset
// (minutes, as JavaScript reports it: UTC minus local, so IST is -330).
apiClient.interceptors.request.use((config) => {
  config.headers.set('X-TZ-Offset', String(new Date().getTimezoneOffset()))
  return config
})

// Redirect to login on 401 (expired/invalid session)
apiClient.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/signup' && currentPath !== '/') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
