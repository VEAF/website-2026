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

// --- Admin page types ---

export interface PageCreate {
  title: string
  route: string
  path: string
  enabled: boolean
  restriction: number
}

export interface PageUpdate {
  title: string
  route: string
  path: string
  enabled: boolean
  restriction: number
}

export interface AdminPageListResponse {
  items: Page[]
  total: number
}

export interface PageBlockCreate {
  content: string
  number: number
  enabled: boolean
}

export interface PageBlockUpdate {
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

export interface SunState {
  state: string
  icon: string
  color: string
  tooltip: string
}

export interface MissionInfo {
  name: string
  uptime: number
  date_time: string | null
  theatre: string
  blue_slots: number | null
  blue_slots_used: number | null
  red_slots: number | null
  red_slots_used: number | null
  sun_state: SunState | null
  mission_time: string | null
  mission_date_time: string | null
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

// DCSServerBot server detail types

export interface WeatherInfo {
  temperature: number | null
  wind_speed: number | null
  wind_direction: number | null
  pressure: number | null
  visibility: number | null
  clouds_base: number | null
  clouds_density: number | null
  precipitation: number | null
  fog_enabled: boolean | null
  fog_visibility: number | null
  dust_enabled: boolean | null
  dust_visibility: number | null
}

export interface DcsBotServerDetail {
  name: string
  status: string
  num_players: number
  address: string | null
  password: string | null
  restart_time: string | null
  mission: MissionInfo | null
  players: PlayerEntry[]
  weather: WeatherInfo | null
}

export interface TopTheatre {
  theatre: string
  playtime_hours: number
}

export interface TopMission {
  mission_name: string
  playtime_hours: number
}

export interface TopModule {
  module: string
  playtime_hours: number
}

export interface DcsBotAttendance {
  current_players: number
  unique_players_24h: number
  total_playtime_hours_24h: number
  discord_members_24h: number
  unique_players_7d: number
  total_playtime_hours_7d: number
  discord_members_7d: number
  unique_players_30d: number
  total_playtime_hours_30d: number
  discord_members_30d: number
  total_sorties: number | null
  total_kills: number | null
  total_deaths: number | null
  total_pvp_kills: number | null
  total_pvp_deaths: number | null
  top_theatres: TopTheatre[]
  top_missions: TopMission[]
  top_modules: TopModule[]
}

export interface DcsBotServerDetailPage {
  server: DcsBotServerDetail
  stats: DcsBotStats | null
  attendance: DcsBotAttendance | null
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
