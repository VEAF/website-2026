export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface MenuItem {
  id: number
  label: string | null
  type: number
  type_as_string: string | null
  icon: string | null
  theme_classes: string | null
  enabled: boolean
  position: number | null
  link: string | null
  restriction: number
  url_slug: string | null
  page_path: string | null
  items: MenuItem[]
}

export interface Page {
  id: number
  route: string
  path: string
  title: string
  enabled: boolean
  restriction: number
  created_at: string | null
  updated_at: string | null
  blocks: PageBlock[]
}

export interface PageBlock {
  id: number
  type: number
  content: string
  number: number
  enabled: boolean
}

export interface Server {
  id: number
  name: string
  code: string
  atc: boolean
  gci: boolean
}

export interface HeaderData {
  ts_client_count: number
  next_events: {
    id: number
    title: string
    start_date: string
    type: number
    type_color: string
  }[]
}
