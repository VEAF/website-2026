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

export interface UserUpdate {
  nickname?: string
  discord?: string
  forum?: string
  sim_dcs?: boolean
  sim_bms?: boolean
}
