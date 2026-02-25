import apiClient from './client'
import type { EventListItem, EventDetail, EventCreate, EventUpdate, VoteCreate, Vote, ChoiceCreate, Choice } from '@/types/calendar'

export async function getEvents(month?: string): Promise<EventListItem[]> {
  const params = month ? { month } : {}
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

export async function markAllViewed(): Promise<void> {
  await apiClient.post('/calendar/mark-all-viewed')
}
