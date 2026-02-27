import apiClient from './client'
import type { Url, UrlCreate, UrlUpdate, AdminUrlListResponse } from '@/types/api'

// --- Public ---

export async function getUrlBySlug(slug: string): Promise<Url> {
  const { data } = await apiClient.get<Url>(`/urls/${slug}`)
  return data
}

// --- Admin ---

export async function getAdminUrls(params?: {
  search?: string
  status?: boolean
  skip?: number
  limit?: number
}): Promise<AdminUrlListResponse> {
  const { data } = await apiClient.get<AdminUrlListResponse>('/admin/urls', { params })
  return data
}

export async function createAdminUrl(payload: UrlCreate): Promise<Url> {
  const { data } = await apiClient.post<Url>('/admin/urls', payload)
  return data
}

export async function updateAdminUrl(urlId: number, payload: UrlUpdate): Promise<Url> {
  const { data } = await apiClient.put<Url>(`/admin/urls/${urlId}`, payload)
  return data
}

export async function deleteAdminUrl(urlId: number): Promise<void> {
  await apiClient.delete(`/admin/urls/${urlId}`)
}
