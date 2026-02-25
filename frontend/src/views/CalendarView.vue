<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import frLocale from '@fullcalendar/core/locales/fr'
import type { EventClickArg, DatesSetArg } from '@fullcalendar/core'
import type { DateClickArg } from '@fullcalendar/interaction'
import { useCalendarStore } from '@/stores/calendar'
import { useAuthStore } from '@/stores/auth'
import type { EventListItem } from '@/types/calendar'

const router = useRouter()
const calendar = useCalendarStore()
const auth = useAuthStore()

const eventTypes = [
  { label: 'Training', color: '#27AE60' },
  { label: 'Mission', color: '#F1C40F' },
  { label: 'OPEX', color: '#7D3C98' },
  { label: 'Meeting', color: '#2980B9' },
  { label: 'Maintenance', color: '#E74C3C' },
  { label: 'ATC / GCI', color: '#EA9417' },
]

const calendarEvents = computed(() =>
  calendar.events.map((e: EventListItem) => ({
    id: String(e.id),
    title: e.title,
    start: e.start_date,
    end: e.end_date,
    backgroundColor: e.type_color || '#999',
    borderColor: e.type_color || '#999',
    extendedProps: { eventId: e.id },
  }))
)

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth' as const,
  locale: frLocale,
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  eventTimeFormat: {
    hour: '2-digit' as const,
    minute: '2-digit' as const,
    meridiem: false as const,
  },
  nowIndicator: true,
  events: calendarEvents.value,
  eventClick: handleEventClick,
  dateClick: handleDateClick,
  datesSet: handleDatesSet,
  height: 'auto' as const,
}))

function handleEventClick(info: EventClickArg) {
  info.jsEvent.preventDefault()
  const eventId = info.event.extendedProps.eventId
  router.push(`/calendar/${eventId}`)
}

function handleDateClick(info: DateClickArg) {
  if (!auth.isMember) return
  router.push({
    path: '/calendar/new',
    query: { date: info.dateStr },
  })
}

function handleDatesSet(info: DatesSetArg) {
  const mid = new Date((info.start.getTime() + info.end.getTime()) / 2)
  const month = `${mid.getFullYear()}-${String(mid.getMonth() + 1).padStart(2, '0')}`
  if (month !== calendar.currentMonth) {
    calendar.fetchEvents(month)
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('fr-FR', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function eventTimeBadge(event: EventListItem): { text: string; cssClass: string } {
  const now = Date.now()
  const start = new Date(event.start_date).getTime()
  const end = new Date(event.end_date).getTime()

  if (now < start) {
    const days = Math.ceil((start - now) / (1000 * 60 * 60 * 24))
    return { text: `dans ${days}j`, cssClass: 'bg-green-100 text-green-800' }
  } else if (now < end) {
    return { text: 'en cours !', cssClass: 'bg-yellow-100 text-yellow-800' }
  } else {
    return { text: 'terminé', cssClass: 'bg-red-100 text-red-800' }
  }
}

onMounted(() => {
  const now = new Date()
  const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  calendar.fetchEvents(month)

  if (auth.isAuthenticated) {
    calendar.fetchMyEvents()
  }
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Calendrier</h1>
      <RouterLink v-if="auth.isMember" to="/calendar/new" class="btn-primary">
        <i class="fa-solid fa-plus mr-1"></i>Créer un événement
      </RouterLink>
    </div>

    <div class="card mb-6">
      <FullCalendar :options="calendarOptions" />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="md:col-span-1">
        <div class="card">
          <h2 class="font-semibold mb-3">Légende</h2>
          <div v-for="et in eventTypes" :key="et.label" class="flex items-center space-x-2 mb-1">
            <i class="fa-solid fa-circle text-xs" :style="{ color: et.color }"></i>
            <span class="text-sm" :style="{ color: et.color }">{{ et.label }}</span>
          </div>
        </div>
      </div>

      <div v-if="auth.isAuthenticated" class="md:col-span-3">
        <div class="card">
          <h2 class="font-semibold mb-3">Mes prochains événements</h2>

          <div v-if="calendar.myEvents.length === 0" class="text-sm text-gray-500 italic">
            Je n'ai prévu de participer à aucun événement pour l'instant.
          </div>

          <div v-for="event in calendar.myEvents" :key="event.id" class="flex items-center flex-wrap gap-2 mb-2 text-sm">
            <i class="fa-solid fa-circle text-xs" :style="{ color: event.type_color || '#999' }"></i>
            <span :style="{ color: event.type_color || '#999' }">{{ event.type_as_string }}</span>
            <span class="text-gray-600">{{ formatDate(event.start_date) }}</span>
            <span
              class="text-xs font-medium px-2 py-0.5 rounded-full"
              :class="eventTimeBadge(event).cssClass"
            >
              {{ eventTimeBadge(event).text }}
            </span>
            <RouterLink
              :to="`/calendar/${event.id}`"
              class="text-veaf-600 hover:text-veaf-800 hover:underline"
            >
              {{ event.title }}
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
