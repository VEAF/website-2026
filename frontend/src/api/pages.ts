import apiClient from './client'
import type { Page, MenuItem } from '@/types/api'

export async function getPage(slug: string): Promise<Page> {
  const { data } = await apiClient.get<Page>(`/pages/${slug}`)
  return data
}

export async function getMenu(): Promise<MenuItem[]> {
  const { data } = await apiClient.get<MenuItem[]>('/menu')
  return data
}
