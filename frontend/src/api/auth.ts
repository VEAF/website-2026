import apiClient from './client'
import type { TokenResponse } from '@/types/api'

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', { email, password })
  return data
}

export async function register(email: string, password: string, nickname: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/register', { email, password, nickname })
  return data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}

export async function resetPassword(email: string): Promise<void> {
  await apiClient.post('/auth/reset-password', { email })
}

export async function confirmResetPassword(token: string, password: string): Promise<void> {
  await apiClient.post('/auth/reset-password/confirm', { token, password })
}
