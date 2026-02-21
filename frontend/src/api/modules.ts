import apiClient from './client'
import type { Module, ModuleRole, ModuleSystem } from '@/types/module'

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
