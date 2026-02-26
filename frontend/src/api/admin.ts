import apiClient from './client'

export interface AdminStats {
  modules: number
  users: number
  pages: number
}

export async function getAdminStats(): Promise<AdminStats> {
  const { data } = await apiClient.get<AdminStats>('/admin/stats')
  return data
}
