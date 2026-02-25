export interface Vote {
  id: number
  user_id: number
  user_nickname: string | null
  vote: boolean | null
  comment: string | null
  created_at: string | null
}

export interface Choice {
  id: number
  user_id: number
  user_nickname: string | null
  module_id: number
  module_name: string | null
  task: number | null
  task_as_string: string | null
  priority: number
  comment: string | null
}

export interface Slot {
  id: number
  user_id: number | null
  user_nickname: string | null
  username: string | null
}

export interface Flight {
  id: number
  name: string
  mission: string | null
  aircraft_id: number
  aircraft_name: string | null
  nb_slots: number
  slots: Slot[]
}

export interface EventListItem {
  id: number
  title: string
  start_date: string
  end_date: string
  type: number
  type_as_string: string | null
  type_color: string | null
  sim_dcs: boolean
  sim_bms: boolean
  registration: boolean
  owner_nickname: string | null
}

export interface EventDetail extends EventListItem {
  description: string | null
  restrictions: number[]
  ato: boolean
  debrief: string | null
  repeat_event: number
  deleted: boolean
  map_id: number | null
  map_name: string | null
  server_id: number | null
  server_name: string | null
  image_id: number | null
  image_uuid: string | null
  owner_id: number
  module_ids: number[]
  module_names: string[]
  restriction_labels: string[]
  votes: Vote[]
  choices: Choice[]
  flights: Flight[]
}

export interface EventCreate {
  title: string
  start_date: string
  end_date: string
  type: number
  sim_dcs?: boolean
  sim_bms?: boolean
  description?: string
  restrictions?: number[]
  registration?: boolean
  ato?: boolean
  repeat_event?: number
  map_id?: number
  server_id?: number
  image_id?: number | null
  module_ids?: number[]
}

export interface EventUpdate extends EventCreate {
  debrief?: string
}

export interface VoteCreate {
  vote: boolean | null
  comment?: string
}

export interface ChoiceCreate {
  module_id: number
  task?: number
  priority?: number
  comment?: string
}
