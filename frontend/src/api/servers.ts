import apiClient from './client'
import type { Server, ServerCreate, ServerUpdate, AdminServerListResponse, HeaderData, DcsBotPage, DcsBotServerDetailPage } from '@/types/api'

export async function getServers(): Promise<Server[]> {
  const { data } = await apiClient.get<Server[]>('/servers')
  return data
}

export async function getHeaderData(): Promise<HeaderData> {
  const { data } = await apiClient.get<HeaderData>('/header')
  return data
}

export async function getDcsBotServers(): Promise<DcsBotPage> {
  const { data } = await apiClient.get<DcsBotPage>('/dcsbot/servers')
  return data
}

export async function getDcsBotServer(serverName: string): Promise<DcsBotServerDetailPage> {
  const { data } = await apiClient.get<DcsBotServerDetailPage>(`/dcsbot/servers/${encodeURIComponent(serverName)}`)
  return data
}

// --- Admin ---

export async function getAdminServers(params?: {
  search?: string
  skip?: number
  limit?: number
}): Promise<AdminServerListResponse> {
  const { data } = await apiClient.get<AdminServerListResponse>('/admin/servers', { params })
  return data
}

export async function createAdminServer(payload: ServerCreate): Promise<Server> {
  const { data } = await apiClient.post<Server>('/admin/servers', payload)
  return data
}

export async function updateAdminServer(serverId: number, payload: ServerUpdate): Promise<Server> {
  const { data } = await apiClient.put<Server>(`/admin/servers/${serverId}`, payload)
  return data
}

export async function deleteAdminServer(serverId: number): Promise<void> {
  await apiClient.delete(`/admin/servers/${serverId}`)
}
