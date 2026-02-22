import apiClient from './client'
import type {
  Module,
  ModuleCreate,
  ModuleRole,
  ModuleRoleCreate,
  ModuleRoleUpdate,
  ModuleSystem,
  ModuleSystemCreate,
  ModuleSystemUpdate,
  ModuleUpdate,
} from '@/types/module'

export async function getModules(type?: number): Promise<Module[]> {
  const params = type !== undefined ? { type } : {}
  const { data } = await apiClient.get<Module[]>('/modules', { params })
  return data
}

export async function getModule(id: number): Promise<Module> {
  const { data } = await apiClient.get<Module>(`/modules/${id}`)
  return data
}

export async function getRoles(): Promise<ModuleRole[]> {
  const { data } = await apiClient.get<ModuleRole[]>('/modules/roles')
  return data
}

export async function getSystems(): Promise<ModuleSystem[]> {
  const { data } = await apiClient.get<ModuleSystem[]>('/modules/systems')
  return data
}

// --- Admin Module endpoints ---

export async function createModule(payload: ModuleCreate): Promise<Module> {
  const { data } = await apiClient.post<Module>('/admin/modules', payload)
  return data
}

export async function updateModule(id: number, payload: ModuleUpdate): Promise<Module> {
  const { data } = await apiClient.put<Module>(`/admin/modules/${id}`, payload)
  return data
}

export async function uploadModuleImage(moduleId: number, file: File): Promise<Module> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.put<Module>(`/admin/modules/${moduleId}/image`, formData)
  return data
}

export async function deleteModuleImage(moduleId: number): Promise<Module> {
  const { data } = await apiClient.delete<Module>(`/admin/modules/${moduleId}/image`)
  return data
}

export async function uploadModuleImageHeader(moduleId: number, file: File): Promise<Module> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.put<Module>(`/admin/modules/${moduleId}/image-header`, formData)
  return data
}

export async function deleteModuleImageHeader(moduleId: number): Promise<Module> {
  const { data } = await apiClient.delete<Module>(`/admin/modules/${moduleId}/image-header`)
  return data
}

// --- Admin ModuleRole endpoints ---

export async function createRole(payload: ModuleRoleCreate): Promise<ModuleRole> {
  const { data } = await apiClient.post<ModuleRole>('/admin/modules/roles', payload)
  return data
}

export async function updateRole(id: number, payload: ModuleRoleUpdate): Promise<ModuleRole> {
  const { data } = await apiClient.put<ModuleRole>(`/admin/modules/roles/${id}`, payload)
  return data
}

export async function deleteRole(id: number): Promise<void> {
  await apiClient.delete(`/admin/modules/roles/${id}`)
}

// --- Admin ModuleSystem endpoints ---

export async function createSystem(payload: ModuleSystemCreate): Promise<ModuleSystem> {
  const { data } = await apiClient.post<ModuleSystem>('/admin/modules/systems', payload)
  return data
}

export async function updateSystem(id: number, payload: ModuleSystemUpdate): Promise<ModuleSystem> {
  const { data } = await apiClient.put<ModuleSystem>(`/admin/modules/systems/${id}`, payload)
  return data
}

export async function deleteSystem(id: number): Promise<void> {
  await apiClient.delete(`/admin/modules/systems/${id}`)
}
