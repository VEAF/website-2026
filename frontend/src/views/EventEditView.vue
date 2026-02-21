<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getEvent, createEvent, updateEvent } from '@/api/calendar'
import type { EventCreate } from '@/types/calendar'

const route = useRoute()
const router = useRouter()

const id = route.params.id ? Number(route.params.id) : null
const isEdit = computed(() => id !== null)
const loading = ref(false)

const form = ref<EventCreate>({
  title: '',
  start_date: '',
  end_date: '',
  type: 1,
  sim_dcs: true,
  sim_bms: false,
  description: '',
  restrictions: [],
  registration: true,
  ato: false,
  repeat_event: 0,
  module_ids: [],
})

const eventTypes = [
  { value: 1, label: 'Training' },
  { value: 2, label: 'Mission' },
  { value: 3, label: 'OPEX' },
  { value: 4, label: 'Meeting' },
  { value: 5, label: 'Maintenance' },
  { value: 6, label: 'ATC / GCI' },
]

onMounted(async () => {
  if (id) {
    const event = await getEvent(id)
    form.value = {
      title: event.title,
      start_date: event.start_date.slice(0, 16),
      end_date: event.end_date.slice(0, 16),
      type: event.type,
      sim_dcs: event.sim_dcs,
      sim_bms: event.sim_bms,
      description: event.description || '',
      restrictions: event.restrictions,
      registration: event.registration,
      ato: event.ato,
      repeat_event: event.repeat_event,
      map_id: event.map_id ?? undefined,
      server_id: event.server_id ?? undefined,
      module_ids: event.module_ids,
    }
  }
})

async function handleSubmit() {
  loading.value = true
  try {
    if (isEdit.value && id) {
      await updateEvent(id, form.value)
      router.push(`/calendar/${id}`)
    } else {
      const event = await createEvent(form.value)
      router.push(`/calendar/${event.id}`)
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">{{ isEdit ? "Modifier l'événement" : 'Créer un événement' }}</h1>

    <form @submit.prevent="handleSubmit" class="card space-y-4">
      <div>
        <label class="label">Titre</label>
        <input v-model="form.title" type="text" class="input" required />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">Date de début</label>
          <input v-model="form.start_date" type="datetime-local" class="input" required />
        </div>
        <div>
          <label class="label">Date de fin</label>
          <input v-model="form.end_date" type="datetime-local" class="input" required />
        </div>
      </div>

      <div>
        <label class="label">Type</label>
        <select v-model.number="form.type" class="input">
          <option v-for="t in eventTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
      </div>

      <div>
        <label class="label">Description</label>
        <textarea v-model="form.description" class="input" rows="4" />
      </div>

      <div class="flex space-x-6">
        <label class="flex items-center space-x-2">
          <input v-model="form.sim_dcs" type="checkbox" class="rounded" />
          <span class="text-sm">DCS</span>
        </label>
        <label class="flex items-center space-x-2">
          <input v-model="form.sim_bms" type="checkbox" class="rounded" />
          <span class="text-sm">BMS</span>
        </label>
        <label class="flex items-center space-x-2">
          <input v-model="form.registration" type="checkbox" class="rounded" />
          <span class="text-sm">Inscription</span>
        </label>
        <label class="flex items-center space-x-2">
          <input v-model="form.ato" type="checkbox" class="rounded" />
          <span class="text-sm">ATO</span>
        </label>
      </div>

      <div class="flex justify-end space-x-3">
        <button type="button" @click="router.back()" class="btn-secondary">Annuler</button>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Sauvegarde...' : isEdit ? 'Modifier' : 'Créer' }}
        </button>
      </div>
    </form>
  </div>
</template>
