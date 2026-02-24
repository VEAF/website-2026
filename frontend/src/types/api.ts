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

// DCSServerBot types

export interface MissionInfo {
  name: string
  uptime: number
  date_time: string | null
  theatre: string
}

export interface PlayerEntry {
  nick: string
  side: string | null
  unit_type: string | null
  callsign: string | null
}

export interface DcsBotServer {
  name: string
  status: string
  num_players: number
  mission: MissionInfo | null
  players: PlayerEntry[]
}

export interface DcsBotStats {
  total_players: number
  active_players: number
  total_sorties: number
  avg_playtime: number
  total_kills: number
  total_deaths: number
  total_pvp_kills: number
  total_pvp_deaths: number
}

export interface DcsBotPage {
  servers: DcsBotServer[]
  stats: DcsBotStats | null
}

export interface HeaderData {
  connected_players: number
  next_events_count: number
  ts_client_count: number
  next_events: {
    id: number
    title: string
    start_date: string
    type: number
    type_color: string
  }[]
}
