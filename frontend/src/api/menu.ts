import apiClient from './client'
import type {
  AdminMenuItem,
  AdminMenuItemListResponse,
  AdminMenuItemTree,
  MenuItemCreate,
  MenuItemUpdate,
  MenuItemReorderEntry,
} from '@/types/api'

// --- Admin menu endpoints ---

export async function getAdminMenuItems(params?: {
  search?: string
  type?: number
  enabled?: boolean
  skip?: number
  limit?: number
}): Promise<AdminMenuItemListResponse> {
  const { data } = await apiClient.get<AdminMenuItemListResponse>('/admin/menu', { params })
  return data
}

export async function getAdminMenuTree(): Promise<AdminMenuItemTree[]> {
  const { data } = await apiClient.get<AdminMenuItemTree[]>('/admin/menu/tree')
  return data
}

export async function getAdminMenuItem(itemId: number): Promise<AdminMenuItem> {
  const { data } = await apiClient.get<AdminMenuItem>(`/admin/menu/${itemId}`)
  return data
}

export async function createAdminMenuItem(payload: MenuItemCreate): Promise<AdminMenuItem> {
  const { data } = await apiClient.post<AdminMenuItem>('/admin/menu', payload)
  return data
}

export async function updateAdminMenuItem(
  itemId: number,
  payload: MenuItemUpdate,
): Promise<AdminMenuItem> {
  const { data } = await apiClient.put<AdminMenuItem>(`/admin/menu/${itemId}`, payload)
  return data
}

export async function deleteAdminMenuItem(itemId: number): Promise<void> {
  await apiClient.delete(`/admin/menu/${itemId}`)
}

export async function reorderAdminMenuItems(
  items: MenuItemReorderEntry[],
): Promise<AdminMenuItemTree[]> {
  const { data } = await apiClient.put<AdminMenuItemTree[]>('/admin/menu/reorder', { items })
  return data
}
