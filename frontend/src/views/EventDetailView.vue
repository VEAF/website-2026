<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getEvent, voteEvent, deleteEvent } from '@/api/calendar'
import type { EventDetail } from '@/types/calendar'
import { useConfirm } from '@/composables/useConfirm'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const event = ref<EventDetail | null>(null)
const loading = ref(true)

const { confirm } = useConfirm()
const id = Number(route.params.id)

onMounted(async () => {
  try {
    event.value = await getEvent(id)
  } finally {
    loading.value = false
  }
})

async function handleVote(vote: boolean | null) {
  if (!event.value) return
  await voteEvent(event.value.id, { vote })
  event.value = await getEvent(id)
}

async function handleDelete() {
  if (!event.value || !(await confirm('Supprimer cet événement ?'))) return
  await deleteEvent(event.value.id)
  router.push('/calendar')
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>

  <div v-else-if="event" class="max-w-4xl mx-auto">
    <div class="card">
      <!-- Header -->
      <div class="flex items-start justify-between mb-4">
        <div>
          <span class="text-xs font-medium px-2 py-1 rounded-full text-white" :style="{ backgroundColor: event.type_color || '#999' }">
            {{ event.type_as_string }}
          </span>
          <h1 class="text-2xl font-bold mt-2">{{ event.title }}</h1>
        </div>
        <div v-if="auth.user && (auth.user.id === event.owner_id || auth.isAdmin)" class="flex space-x-2">
          <RouterLink :to="`/calendar/${event.id}/edit`" class="btn-secondary text-sm"><i class="fa-solid fa-pen mr-1"></i>Modifier</RouterLink>
          <button @click="handleDelete" class="btn-danger text-sm"><i class="fa-solid fa-trash mr-1"></i>Supprimer</button>
        </div>
      </div>

      <!-- Info -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 text-sm">
        <div><strong>Début :</strong> {{ formatDate(event.start_date) }}</div>
        <div><strong>Fin :</strong> {{ formatDate(event.end_date) }}</div>
        <div><strong>Créé par :</strong> {{ event.owner_nickname }}</div>
        <div v-if="event.map_name"><strong>Carte :</strong> {{ event.map_name }}</div>
      </div>

      <!-- Description -->
      <div v-if="event.description" class="prose max-w-none mb-6">
        <p class="whitespace-pre-wrap">{{ event.description }}</p>
      </div>

      <!-- Voting -->
      <div v-if="event.registration && auth.isAuthenticated" class="mb-6">
        <h2 class="text-lg font-semibold mb-3">Vote</h2>
        <div class="flex space-x-3">
          <button @click="handleVote(true)" class="btn-success"><i class="fa-solid fa-check mr-1"></i>Oui</button>
          <button @click="handleVote(null)" class="btn-secondary"><i class="fa-solid fa-question mr-1"></i>Peut-être</button>
          <button @click="handleVote(false)" class="btn-danger"><i class="fa-solid fa-xmark mr-1"></i>Non</button>
        </div>
      </div>

      <!-- Votes -->
      <div v-if="event.votes.length" class="mb-6">
        <h2 class="text-lg font-semibold mb-3">Votes ({{ event.votes.length }})</h2>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <h3 class="text-green-600 font-medium mb-2">Oui ({{ event.votes.filter(v => v.vote === true).length }})</h3>
            <ul class="text-sm space-y-1">
              <li v-for="v in event.votes.filter(v => v.vote === true)" :key="v.id">{{ v.user_nickname }}</li>
            </ul>
          </div>
          <div>
            <h3 class="text-yellow-600 font-medium mb-2">Peut-être ({{ event.votes.filter(v => v.vote === null).length }})</h3>
            <ul class="text-sm space-y-1">
              <li v-for="v in event.votes.filter(v => v.vote === null)" :key="v.id">{{ v.user_nickname }}</li>
            </ul>
          </div>
          <div>
            <h3 class="text-red-600 font-medium mb-2">Non ({{ event.votes.filter(v => v.vote === false).length }})</h3>
            <ul class="text-sm space-y-1">
              <li v-for="v in event.votes.filter(v => v.vote === false)" :key="v.id">{{ v.user_nickname }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Choices -->
      <div v-if="event.choices.length" class="mb-6">
        <h2 class="text-lg font-semibold mb-3">Choix modules</h2>
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b">
              <th class="text-left py-2">Pilote</th>
              <th class="text-left py-2">Module</th>
              <th class="text-left py-2">Mission</th>
              <th class="text-left py-2">Priorité</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in event.choices" :key="c.id" class="border-b">
              <td class="py-2">{{ c.user_nickname }}</td>
              <td class="py-2">{{ c.module_name }}</td>
              <td class="py-2">{{ c.task_as_string }}</td>
              <td class="py-2">{{ c.priority }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ATO / Flights -->
      <div v-if="event.ato && event.flights.length" class="mb-6">
        <h2 class="text-lg font-semibold mb-3">ATO - Flights</h2>
        <div class="space-y-4">
          <div v-for="f in event.flights" :key="f.id" class="bg-gray-50 rounded-lg p-4">
            <div class="font-medium mb-2">{{ f.name }} - {{ f.aircraft_name }} ({{ f.slots.length }}/{{ f.nb_slots }})</div>
            <div v-if="f.mission" class="text-sm text-gray-600 mb-2">Mission: {{ f.mission }}</div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
              <div v-for="s in f.slots" :key="s.id" class="bg-white rounded px-3 py-1 text-sm border">
                {{ s.user_nickname || s.username || '— vide —' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Debrief -->
      <div v-if="event.debrief" class="mb-6">
        <h2 class="text-lg font-semibold mb-3">Debrief</h2>
        <p class="whitespace-pre-wrap text-sm">{{ event.debrief }}</p>
      </div>
    </div>
  </div>
</template>
