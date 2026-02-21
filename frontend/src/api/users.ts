import apiClient from './client'
import type { UserMe, UserPublic, UserUpdate } from '@/types/user'

export async function getMe(): Promise<UserMe> {
  const { data } = await apiClient.get<UserMe>('/users/me')
  return data
}

export async function updateMe(updates: UserUpdate): Promise<UserPublic> {
  const { data } = await apiClient.put<UserPublic>('/users/me', updates)
  return data
}

export async function getUser(userId: number): Promise<UserPublic> {
  const { data } = await apiClient.get<UserPublic>(`/users/${userId}`)
  return data
}
