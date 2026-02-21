import apiClient from './client'
import type { Server, HeaderData } from '@/types/api'

export async function getServers(): Promise<Server[]> {
  const { data } = await apiClient.get<Server[]>('/servers')
  return data
}

export async function getHeaderData(): Promise<HeaderData> {
  const { data } = await apiClient.get<HeaderData>('/header')
  return data
}
