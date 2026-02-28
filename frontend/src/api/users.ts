import apiClient from './client'
import type {
  AdminUser,
  AdminUserListResponse,
  AdminUserUpdate,
  UserMe,
  UserModuleUpdateResponse,
  UserProfile,
  UserPublic,
  UserUpdate,
} from '@/types/user'

export async function getMe(): Promise<UserMe> {
  const { data } = await apiClient.get<UserMe>('/users/me')
  return data
}

export async function updateMe(updates: UserUpdate): Promise<UserPublic> {
  const { data } = await apiClient.put<UserPublic>('/users/me', updates)
  return data
}

export async function updateMyModuleLevel(
  moduleId: number,
  level: number,
): Promise<UserModuleUpdateResponse> {
  const { data } = await apiClient.put<UserModuleUpdateResponse>(
    `/users/me/modules/${moduleId}/level`,
    { level },
  )
  return data
}

export async function updateMyModuleActive(
  moduleId: number,
  active: boolean,
): Promise<UserModuleUpdateResponse> {
  const { data } = await apiClient.put<UserModuleUpdateResponse>(
    `/users/me/modules/${moduleId}/active`,
    { active },
  )
  return data
}

export async function getUser(userId: number): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>(`/users/${userId}`)
  return data
}

// --- Admin User endpoints ---

export async function getAdminUsers(params?: {
  search?: string
  status?: number
  skip?: number
  limit?: number
}): Promise<AdminUserListResponse> {
  const { data } = await apiClient.get<AdminUserListResponse>('/admin/users', { params })
  return data
}

export async function getAdminUser(userId: number): Promise<AdminUser> {
  const { data } = await apiClient.get<AdminUser>(`/admin/users/${userId}`)
  return data
}

export async function updateAdminUser(userId: number, payload: AdminUserUpdate): Promise<AdminUser> {
  const { data } = await apiClient.put<AdminUser>(`/admin/users/${userId}`, payload)
  return data
}
