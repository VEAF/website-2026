<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCalendarStore } from '@/stores/calendar'
import { useAuthStore } from '@/stores/auth'

const calendar = useCalendarStore()
const auth = useAuthStore()

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth() + 1)

const monthStr = computed(() => `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}`)
const monthLabel = computed(() => {
  const date = new Date(currentYear.value, currentMonth.value - 1)
  return date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
})

function prevMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
  calendar.fetchEvents(monthStr.value)
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
  calendar.fetchEvents(monthStr.value)
}

onMounted(() => {
  calendar.fetchEvents(monthStr.value)
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Calendrier</h1>
      <RouterLink v-if="auth.isMember" to="/calendar/new" class="btn-primary"><i class="fa-solid fa-plus mr-1"></i>Créer un événement</RouterLink>
    </div>

    <!-- Month navigation -->
    <div class="flex items-center justify-center space-x-4 mb-6">
      <button @click="prevMonth" class="btn-secondary"><i class="fa-solid fa-chevron-left mr-1"></i>Précédent</button>
      <span class="text-lg font-semibold capitalize">{{ monthLabel }}</span>
      <button @click="nextMonth" class="btn-secondary">Suivant<i class="fa-solid fa-chevron-right ml-1"></i></button>
    </div>

    <!-- Events list -->
    <div v-if="calendar.events.length === 0" class="text-center text-gray-500 py-8">
      Aucun événement ce mois-ci
    </div>

    <div class="space-y-3">
      <RouterLink
        v-for="event in calendar.events"
        :key="event.id"
        :to="`/calendar/${event.id}`"
        class="card block hover:shadow-md transition-shadow !p-4"
      >
        <div class="flex items-center space-x-4">
          <div
            class="w-1 h-12 rounded-full"
            :style="{ backgroundColor: event.type_color || '#999' }"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2">
              <span class="text-xs font-medium px-2 py-0.5 rounded-full text-white" :style="{ backgroundColor: event.type_color || '#999' }">
                {{ event.type_as_string }}
              </span>
              <span class="font-semibold truncate">{{ event.title }}</span>
            </div>
            <div class="text-sm text-gray-500 mt-1">
              {{ formatDate(event.start_date) }} - {{ formatDate(event.end_date) }}
            </div>
          </div>
          <div class="text-sm text-gray-400">
            {{ event.owner_nickname }}
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
