import apiClient from './client'
import type { Player, PlayerCreate, PlayerUpdate, AdminPlayerListResponse } from '@/types/api'

// --- Admin ---

export async function getAdminPlayers(params?: {
  search?: string
  skip?: number
  limit?: number
}): Promise<AdminPlayerListResponse> {
  const { data } = await apiClient.get<AdminPlayerListResponse>('/admin/players', { params })
  return data
}

export async function createAdminPlayer(payload: PlayerCreate): Promise<Player> {
  const { data } = await apiClient.post<Player>('/admin/players', payload)
  return data
}

export async function updateAdminPlayer(playerId: number, payload: PlayerUpdate): Promise<Player> {
  const { data } = await apiClient.put<Player>(`/admin/players/${playerId}`, payload)
  return data
}

export async function deleteAdminPlayer(playerId: number): Promise<void> {
  await apiClient.delete(`/admin/players/${playerId}`)
}
