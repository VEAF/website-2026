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
