export interface ModuleRole {
  id: number
  name: string
  code: string
  position: number
}

export interface ModuleSystem {
  id: number
  code: string
  name: string
  position: number
}

export interface Module {
  id: number
  type: number
  type_as_string: string | null
  name: string
  long_name: string
  code: string
  landing_page: boolean
  landing_page_number: number | null
  period: number | null
  period_as_string: string | null
  image_uuid: string | null
  image_header_uuid: string | null
  roles: ModuleRole[]
  systems: ModuleSystem[]
}
