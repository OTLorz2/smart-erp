import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = '/api/v1'

export interface User {
  id: number
  username: string
  email?: string
  full_name?: string
  role: string
  is_active: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  // Set axios default headers
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  async function login(username: string, password: string) {
    const response = await axios.post(`${API_URL}/auth/login`, {
      username,
      password
    })

    token.value = response.data.access_token
    localStorage.setItem('token', token.value!)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`

    await fetchUser()
  }

  async function fetchUser() {
    try {
      const response = await axios.get(`${API_URL}/auth/me`)
      user.value = response.data
    } catch (error) {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  // Initialize user on store creation
  if (token.value) {
    fetchUser()
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    fetchUser
  }
})