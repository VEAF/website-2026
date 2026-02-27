import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as calendarApi from '@/api/calendar'
import type { EventListItem, TaskType } from '@/types/calendar'

export const useCalendarStore = defineStore('calendar', () => {
  const events = ref<EventListItem[]>([])
  const currentMonth = ref('')
  const myEvents = ref<EventListItem[]>([])
  const tasks = ref<TaskType[]>([])

  async function fetchTasks() {
    if (tasks.value.length > 0) return
    tasks.value = await calendarApi.getTasks()
  }

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

  return { events, currentMonth, myEvents, tasks, fetchEvents, fetchMyEvents, fetchTasks }
})
