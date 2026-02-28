import apiClient from './client'

export interface AdminStats {
  modules: number
  users: number
  events: number
  pages: number
  urls: number
  menu_items: number
  servers: number
}

export async function getAdminStats(): Promise<AdminStats> {
  const { data } = await apiClient.get<AdminStats>('/admin/stats')
  return data
}
