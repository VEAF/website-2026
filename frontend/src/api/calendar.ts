import apiClient from './client'
import type { EventListItem, EventDetail, EventCreate, EventUpdate, VoteCreate, Vote, ChoiceCreate, Choice, TaskType, AdminEvent, AdminEventListResponse } from '@/types/calendar'

export async function getEvents(fromDate?: string, toDate?: string): Promise<EventListItem[]> {
  const params: Record<string, string> = {}
  if (fromDate) params.from_date = fromDate
  if (toDate) params.to_date = toDate
  const { data } = await apiClient.get<EventListItem[]>('/calendar/events', { params })
  return data
}

export async function getMyEvents(): Promise<EventListItem[]> {
  const { data } = await apiClient.get<EventListItem[]>('/calendar/my-events')
  return data
}

export async function getEvent(id: number): Promise<EventDetail> {
  const { data } = await apiClient.get<EventDetail>(`/calendar/events/${id}`)
  return data
}

export async function createEvent(event: EventCreate): Promise<EventDetail> {
  const { data } = await apiClient.post<EventDetail>('/calendar/events', event)
  return data
}

export async function updateEvent(id: number, event: EventUpdate): Promise<EventDetail> {
  const { data } = await apiClient.put<EventDetail>(`/calendar/events/${id}`, event)
  return data
}

export async function deleteEvent(id: number): Promise<void> {
  await apiClient.delete(`/calendar/events/${id}`)
}

export async function copyEvent(id: number): Promise<EventDetail> {
  const { data } = await apiClient.post<EventDetail>(`/calendar/events/${id}/copy`)
  return data
}

export async function voteEvent(id: number, vote: VoteCreate): Promise<Vote> {
  const { data } = await apiClient.post<Vote>(`/calendar/events/${id}/vote`, vote)
  return data
}

export async function addChoice(eventId: number, choice: ChoiceCreate): Promise<Choice> {
  const { data } = await apiClient.post<Choice>(`/calendar/events/${eventId}/choices`, choice)
  return data
}

export async function updateChoice(choiceId: number, choice: Partial<ChoiceCreate>): Promise<Choice> {
  const { data } = await apiClient.put<Choice>(`/calendar/choices/${choiceId}`, choice)
  return data
}

export async function deleteChoice(choiceId: number): Promise<void> {
  await apiClient.delete(`/calendar/choices/${choiceId}`)
}

export async function markAllViewed(): Promise<void> {
  await apiClient.post('/calendar/mark-all-viewed')
}

export async function getTasks(): Promise<TaskType[]> {
  const { data } = await apiClient.get<TaskType[]>('/calendar/tasks')
  return data
}

// --- Admin Event endpoints ---

export async function getAdminEvents(params?: {
  search?: string
  type?: number
  deleted?: boolean
  sim?: string
  date_from?: string
  date_to?: string
  skip?: number
  limit?: number
}): Promise<AdminEventListResponse> {
  const { data } = await apiClient.get<AdminEventListResponse>('/admin/events', { params })
  return data
}

export async function getAdminEvent(id: number): Promise<EventDetail> {
  const { data } = await apiClient.get<EventDetail>(`/admin/events/${id}`)
  return data
}

export async function restoreAdminEvent(id: number): Promise<AdminEvent> {
  const { data } = await apiClient.patch<AdminEvent>(`/admin/events/${id}/restore`)
  return data
}
