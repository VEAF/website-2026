import apiClient from './client'

export const TYPE_PRESENTATION = 2
export const TYPE_ACTIVITY = 4

export interface RecruitmentEvent {
  id: number
  type: number
  type_as_string: string
  event_at: string | null
  comment: string | null
  validator_nickname: string | null
  ack_at: string | null
}

export async function getRecruitmentHistory(userId: number): Promise<RecruitmentEvent[]> {
  const { data } = await apiClient.get<RecruitmentEvent[]>(`/recruitment/${userId}`)
  return data
}

export async function addRecruitmentEvent(
  userId: number,
  type: number,
  comment?: string,
): Promise<void> {
  await apiClient.post(`/recruitment/${userId}/events`, null, {
    params: { type, ...(comment ? { comment } : {}) },
  })
}

// --- Admin Recruitment ---

export interface AdminRecruitmentEvent {
  id: number
  type: number
  type_as_string: string
  event_at: string | null
  comment: string | null
  ack_at: string | null
  user_id: number
  user_nickname: string | null
  validator_id: number | null
  validator_nickname: string | null
  created_at: string | null
  updated_at: string | null
}

export interface AdminRecruitmentEventListResponse {
  items: AdminRecruitmentEvent[]
  total: number
}

export interface AdminRecruitmentEventUpdate {
  comment: string | null
  event_at: string | null
}

export async function getAdminRecruitmentEvents(params?: {
  search?: string
  type?: number
  skip?: number
  limit?: number
}): Promise<AdminRecruitmentEventListResponse> {
  const { data } = await apiClient.get<AdminRecruitmentEventListResponse>('/admin/recruitment', {
    params,
  })
  return data
}

export async function updateAdminRecruitmentEvent(
  eventId: number,
  payload: AdminRecruitmentEventUpdate,
): Promise<AdminRecruitmentEvent> {
  const { data } = await apiClient.put<AdminRecruitmentEvent>(
    `/admin/recruitment/${eventId}`,
    payload,
  )
  return data
}

export async function deleteAdminRecruitmentEvent(eventId: number): Promise<void> {
  await apiClient.delete(`/admin/recruitment/${eventId}`)
}
