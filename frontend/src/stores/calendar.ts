import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as calendarApi from '@/api/calendar'
import type { EventListItem } from '@/types/calendar'

export const useCalendarStore = defineStore('calendar', () => {
  const events = ref<EventListItem[]>([])
  const currentMonth = ref('')
  const myEvents = ref<EventListItem[]>([])

  async function fetchEvents(month: string) {
    currentMonth.value = month
    events.value = await calendarApi.getEvents(month)
  }

  async function fetchMyEvents() {
    try {
      myEvents.value = await calendarApi.getMyEvents()
    } catch {
      myEvents.value = []
    }
  }

  return { events, currentMonth, myEvents, fetchEvents, fetchMyEvents }
})
