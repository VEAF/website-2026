import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as calendarApi from '@/api/calendar'
import type { EventListItem, TaskType } from '@/types/calendar'

interface DateRange {
  from: string
  to: string
}

export const useCalendarStore = defineStore('calendar', () => {
  const events = ref<EventListItem[]>([])
  const currentRange = ref<DateRange>({ from: '', to: '' })
  const myEvents = ref<EventListItem[]>([])
  const tasks = ref<TaskType[]>([])

  async function fetchTasks() {
    if (tasks.value.length > 0) return
    tasks.value = await calendarApi.getTasks()
  }

  async function fetchEvents(fromDate: string, toDate: string) {
    currentRange.value = { from: fromDate, to: toDate }
    events.value = await calendarApi.getEvents(fromDate, toDate)
  }

  async function fetchMyEvents() {
    try {
      myEvents.value = await calendarApi.getMyEvents()
    } catch {
      myEvents.value = []
    }
  }

  return { events, currentRange, myEvents, tasks, fetchEvents, fetchMyEvents, fetchTasks }
})
