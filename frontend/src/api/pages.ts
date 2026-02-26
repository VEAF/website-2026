import apiClient from './client'
import type {
  Page,
  MenuItem,
  AdminPageListResponse,
  PageCreate,
  PageUpdate,
  PageBlockCreate,
  PageBlockUpdate,
} from '@/types/api'

export async function getPage(slug: string): Promise<Page> {
  const { data } = await apiClient.get<Page>(`/pages/${slug}`)
  return data
}

export async function getMenu(): Promise<MenuItem[]> {
  const { data } = await apiClient.get<MenuItem[]>('/menu')
  return data
}

// --- Admin pages ---

export async function getAdminPages(params?: {
  search?: string
  enabled?: boolean
  restriction?: number
  skip?: number
  limit?: number
}): Promise<AdminPageListResponse> {
  const { data } = await apiClient.get<AdminPageListResponse>('/admin/pages', { params })
  return data
}

export async function getAdminPage(pageId: number): Promise<Page> {
  const { data } = await apiClient.get<Page>(`/admin/pages/${pageId}`)
  return data
}

export async function createAdminPage(payload: PageCreate): Promise<Page> {
  const { data } = await apiClient.post<Page>('/admin/pages', payload)
  return data
}

export async function updateAdminPage(pageId: number, payload: PageUpdate): Promise<Page> {
  const { data } = await apiClient.put<Page>(`/admin/pages/${pageId}`, payload)
  return data
}

export async function deleteAdminPage(pageId: number): Promise<void> {
  await apiClient.delete(`/admin/pages/${pageId}`)
}

// --- Admin blocks ---

export async function createAdminBlock(pageId: number, payload: PageBlockCreate): Promise<Page> {
  const { data } = await apiClient.post<Page>(`/admin/pages/${pageId}/blocks`, payload)
  return data
}

export async function updateAdminBlock(
  pageId: number,
  blockId: number,
  payload: PageBlockUpdate,
): Promise<Page> {
  const { data } = await apiClient.put<Page>(`/admin/pages/${pageId}/blocks/${blockId}`, payload)
  return data
}

export async function deleteAdminBlock(pageId: number, blockId: number): Promise<Page> {
  const { data } = await apiClient.delete<Page>(`/admin/pages/${pageId}/blocks/${blockId}`)
  return data
}
