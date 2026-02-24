import apiClient from './client'
import type { Server, HeaderData, DcsBotPage, DcsBotServerDetailPage } from '@/types/api'

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
