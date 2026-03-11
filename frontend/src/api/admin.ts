import apiClient from './client'

export interface AdminStats {
  modules: number
  users: number
  events: number
  files: number
  files_total_size: number
  pages: number
  urls: number
  menu_items: number
  servers: number
  cadets_ready_to_promote: number
  recruitment_events: number
}

export async function getAdminStats(): Promise<AdminStats> {
  const { data } = await apiClient.get<AdminStats>('/admin/stats')
  return data
}
