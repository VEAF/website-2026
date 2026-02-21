import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import * as usersApi from '@/api/users'
import type { UserMe } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<UserMe | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.roles.includes('ROLE_ADMIN') ?? false)
  const isMember = computed(() => {
    if (!user.value) return false
    const memberStatuses = [2, 3, 4, 5, 6, 7, 8]
    return memberStatuses.includes(user.value.status)
  })

  async function login(email: string, password: string) {
    const data = await authApi.login(email, password)
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    await fetchUser()
  }

  async function register(email: string, password: string, nickname: string) {
    const data = await authApi.register(email, password, nickname)
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    await fetchUser()
  }

  async function logout() {
    await authApi.logout()
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await usersApi.getMe()
    } catch {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
    }
  }

  return { token, user, isAuthenticated, isAdmin, isMember, login, register, logout, fetchUser }
})
