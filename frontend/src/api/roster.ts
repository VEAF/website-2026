import apiClient from './client'

// --- Types ---

export interface RosterStats {
  all: number
  cadets: number
  members: number
}

export interface RosterUserModule {
  module_id: number
  module_name: string | null
  module_code: string | null
  module_long_name: string | null
  module_type: number | null
  module_type_as_string: string | null
  module_period: number | null
  module_period_as_string: string | null
  active: boolean
  level: number
  level_as_string: string | null
}

export interface RosterUser {
  id: number
  nickname: string
  status: number
  status_as_string: string | null
  sim_dcs: boolean
  sim_bms: boolean
  modules: RosterUserModule[]
}

export interface RosterModule {
  id: number
  name: string
  long_name: string
  code: string
  type: number
  period: number | null
  period_as_string: string | null
  image_header_uuid: string | null
  user_count: number
}

export interface RosterModuleDetailUser {
  id: number
  nickname: string
  status: number
  status_as_string: string | null
  active: boolean
  level: number
  level_as_string: string | null
}

export interface RosterModuleDetail {
  module: RosterModule
  users: RosterModuleDetailUser[]
}

// --- API functions ---

export async function getRosterStats(): Promise<RosterStats> {
  const { data } = await apiClient.get<RosterStats>('/roster/stats')
  return data
}

export async function getRosterPilots(group: string = 'all'): Promise<RosterUser[]> {
  const { data } = await apiClient.get<RosterUser[]>('/roster/pilots', { params: { group } })
  return data
}

export async function getRosterModules(type: number, group: string = 'all'): Promise<RosterModule[]> {
  const { data } = await apiClient.get<RosterModule[]>('/roster/modules', { params: { type, group } })
  return data
}

export async function getRosterModuleDetail(
  moduleId: number,
  group: string = 'all',
): Promise<RosterModuleDetail> {
  const { data } = await apiClient.get<RosterModuleDetail>(`/roster/modules/${moduleId}`, {
    params: { group },
  })
  return data
}
