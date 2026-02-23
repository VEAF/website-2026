export interface UserModule {
  id: number
  module_id: number
  module_name: string | null
  module_code: string | null
  module_long_name: string | null
  module_type: number | null
  active: boolean
  level: number
  level_as_string: string | null
}

export interface UserPublic {
  id: number
  nickname: string
  status: number
  status_as_string: string | null
  sim_dcs: boolean
  sim_bms: boolean
  discord: string | null
  forum: string | null
  created_at: string | null
}

export interface UserMe extends UserPublic {
  email: string
  roles: string[]
  need_presentation: boolean
  cadet_flights: number
  modules: UserModule[]
}

export interface UserModuleUpdateResponse {
  module_id: number
  active: boolean
  level: number
  level_as_string: string | null
  deleted: boolean
}

export interface UserUpdate {
  nickname?: string
  discord?: string
  forum?: string
  sim_dcs?: boolean
  sim_bms?: boolean
}

// --- Admin types ---

export interface AdminUser {
  id: number
  email: string
  nickname: string
  roles: string[]
  status: number
  status_as_string: string | null
  sim_dcs: boolean
  sim_bms: boolean
  discord: string | null
  forum: string | null
  need_presentation: boolean
  cadet_flights: number
  created_at: string | null
  updated_at: string | null
}

export interface AdminUserUpdate {
  email: string
  nickname: string
  roles: string[]
  status: number
  discord: string | null
  forum: string | null
  sim_dcs: boolean
  sim_bms: boolean
  need_presentation: boolean
}

export interface AdminUserListResponse {
  items: AdminUser[]
  total: number
}
