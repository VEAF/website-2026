<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getEvent, createEvent, updateEvent } from '@/api/calendar'
import { getModules } from '@/api/modules'
import { getServers } from '@/api/servers'
import { uploadFile } from '@/api/files'
import { useToast } from '@/composables/useToast'
import MarkdownEditor from '@/components/ui/MarkdownEditor.vue'
import MultiSelect from '@/components/ui/MultiSelect.vue'
import type { MultiSelectOption } from '@/components/ui/MultiSelect.vue'
import type { EventUpdate } from '@/types/calendar'
import type { Module } from '@/types/module'
import type { Server } from '@/types/api'
import { MODULE_TYPE_MAP, MODULE_TYPE_AIRCRAFT, MODULE_TYPE_HELICOPTER, MODULE_TYPE_SPECIAL, FLYABLE_MODULE_TYPES } from '@/constants/modules'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const id = route.params.id ? Number(route.params.id) : null
const isEdit = computed(() => id !== null)
const loading = ref(false)

const form = ref<EventUpdate>({
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
  map_id: undefined,
  server_id: undefined,
  image_id: undefined,
  module_ids: [],
  debrief: '',
})

const eventTypes = [
  { value: 1, label: 'Training' },
  { value: 2, label: 'Mission' },
  { value: 3, label: 'OPEX' },
  { value: 4, label: 'Meeting' },
  { value: 5, label: 'Maintenance' },
  { value: 6, label: 'ATC / GCI' },
]

const repeatOptions = [
  { value: 0, label: 'Pas de répétition' },
  { value: 1, label: '1x par semaine, le même jour' },
  { value: 2, label: '1x par mois, le même jour' },
  { value: 3, label: '1x par mois, même jour de la semaine' },
]

// Dropdown data
const maps = ref<Module[]>([])
const aircraftModules = ref<Module[]>([])
const servers = ref<Server[]>([])

const MODULE_TYPE_COLORS: Record<number, string> = {
  [MODULE_TYPE_AIRCRAFT]: 'module-aircraft',
  [MODULE_TYPE_HELICOPTER]: 'module-helicopter',
  [MODULE_TYPE_SPECIAL]: 'module-special',
}

const moduleOptions = computed((): MultiSelectOption[] =>
  aircraftModules.value.map(m => ({
    id: m.id,
    label: m.name,
    section: m.period_as_string || 'Autre',
    group: m.type_as_string ?? '',
    colorClass: MODULE_TYPE_COLORS[m.type],
  }))
)

// Image state
const imageUploading = ref(false)
const currentImageUuid = ref<string | null>(null)

onMounted(async () => {
  // Load dropdown data in parallel
  const [mapsData, allModules, serversData] = await Promise.all([
    getModules(MODULE_TYPE_MAP),
    getModules(),
    getServers(),
  ])
  maps.value = mapsData
  aircraftModules.value = allModules.filter(m => FLYABLE_MODULE_TYPES.includes(m.type))
  servers.value = serversData

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
      image_id: event.image_id ?? undefined,
      module_ids: event.module_ids,
      debrief: event.debrief || '',
    }
    currentImageUuid.value = event.image_uuid
  } else if (route.query.date) {
    const dateStr = route.query.date as string
    form.value.start_date = `${dateStr}T21:00`
    form.value.end_date = `${dateStr}T23:00`
  }
})

async function handleImageUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!allowedTypes.includes(file.type)) {
    toast.error('Format accepté : JPG ou PNG uniquement')
    input.value = ''
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    toast.error('La taille du fichier ne doit pas dépasser 20 Mo')
    input.value = ''
    return
  }

  imageUploading.value = true
  try {
    const result = await uploadFile(file)
    form.value.image_id = result.id
    currentImageUuid.value = result.uuid
    toast.success('Image uploadée')
  } catch (e) {
    toast.error(e)
  } finally {
    imageUploading.value = false
    input.value = ''
  }
}

function removeImage() {
  form.value.image_id = null
  currentImageUuid.value = null
}

async function handleSubmit() {
  loading.value = true
  try {
    if (isEdit.value && id) {
      await updateEvent(id, form.value)
      toast.success('Événement modifié')
      router.push(`/calendar/${id}`)
    } else {
      const event = await createEvent(form.value)
      toast.success('Événement créé')
      router.push(`/calendar/${event.id}`)
    }
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-container py-6">
    <h1 class="text-2xl font-bold mb-6">{{ isEdit ? "Modifier l'événement" : 'Créer un événement' }}</h1>

    <form @submit.prevent="handleSubmit" class="card space-y-4">
      <!-- Dates -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="label">Début</label>
          <input v-model="form.start_date" type="datetime-local" class="input" required />
        </div>
        <div>
          <label class="label">Fin</label>
          <input v-model="form.end_date" type="datetime-local" class="input" required />
        </div>
      </div>

      <!-- Registration -->
      <div>
        <label class="flex items-center space-x-2">
          <input v-model="form.registration" type="checkbox" class="rounded" />
          <span class="text-sm">Inscriptions ouvertes</span>
        </label>
      </div>

      <!-- Type -->
      <div>
        <label class="label">Type</label>
        <select v-model.number="form.type" class="input">
          <option v-for="t in eventTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
      </div>

      <!-- Sim / ATO checkboxes -->
      <div class="flex space-x-6">
        <label class="flex items-center space-x-2">
          <input v-model="form.sim_dcs" type="checkbox" class="rounded" />
          <span class="text-sm">Simulateur DCS</span>
        </label>
        <label class="flex items-center space-x-2">
          <input v-model="form.sim_bms" type="checkbox" class="rounded" />
          <span class="text-sm">Simulateur BMS</span>
        </label>
        <label class="flex items-center space-x-2">
          <input v-model="form.ato" type="checkbox" class="rounded" />
          <span class="text-sm">ATO</span>
        </label>
      </div>

      <!-- Title -->
      <div>
        <label class="label">Titre</label>
        <input v-model="form.title" type="text" class="input" required />
      </div>

      <!-- Description -->
      <div>
        <label class="label">Description</label>
        <MarkdownEditor :model-value="form.description ?? ''" @update:model-value="form.description = $event" />
      </div>

      <!-- Restrictions -->
      <div>
        <label class="label">Réservé aux</label>
        <p class="text-xs text-gray-500 mb-1">Ne rien cocher si ouvert à tout le monde</p>
        <div class="flex space-x-6">
          <label class="flex items-center space-x-2">
            <input type="checkbox" :value="1" v-model="form.restrictions" class="rounded" />
            <span class="text-sm">Cadets</span>
          </label>
          <label class="flex items-center space-x-2">
            <input type="checkbox" :value="2" v-model="form.restrictions" class="rounded" />
            <span class="text-sm">Membres</span>
          </label>
        </div>
      </div>

      <!-- Map -->
      <div>
        <label class="label">Carte</label>
        <select v-model="form.map_id" class="input">
          <option :value="undefined">-</option>
          <option v-for="m in maps" :key="m.id" :value="m.id">{{ m.long_name || m.name }}</option>
        </select>
      </div>

      <!-- Modules -->
      <div v-if="aircraftModules.length">
        <label class="label">Modules</label>
        <MultiSelect
          :model-value="form.module_ids ?? []"
          @update:model-value="form.module_ids = $event"
          :options="moduleOptions"
          placeholder="Rechercher un module..."
          no-results-text="Aucun module trouvé"
        />
      </div>

      <!-- Image -->
      <div>
        <label class="label">Image</label>
        <div v-if="currentImageUuid" class="mb-2">
          <img :src="`/api/files/${currentImageUuid}`" alt="Image de l'événement"
               class="max-w-full max-h-40 rounded border border-gray-300" />
          <button type="button" class="mt-1 text-red-600 hover:text-red-800 text-sm" @click="removeImage">
            <i class="fa-solid fa-trash mr-1"></i>Supprimer l'image
          </button>
        </div>
        <input type="file" accept="image/jpeg,image/png" class="input"
               :disabled="imageUploading" @change="handleImageUpload" />
        <p class="text-xs text-gray-500 mt-1">JPG ou PNG, max 20 Mo</p>
      </div>

      <!-- Server -->
      <div>
        <label class="label">Serveur</label>
        <select v-model="form.server_id" class="input">
          <option :value="undefined">-</option>
          <option v-for="s in servers" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>

      <!-- Debrief (edit only) -->
      <div v-if="isEdit">
        <label class="label">Debrief</label>
        <MarkdownEditor :model-value="form.debrief ?? ''" @update:model-value="form.debrief = $event" />
      </div>

      <!-- Repeat -->
      <div>
        <label class="label">Répétition</label>
        <div class="space-y-2 mt-1">
          <label v-for="opt in repeatOptions" :key="opt.value" class="flex items-center space-x-2">
            <input type="radio" :value="opt.value" v-model.number="form.repeat_event" />
            <span class="text-sm">{{ opt.label }}</span>
          </label>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3">
        <button type="button" @click="router.back()" class="btn-secondary">
          <i class="fa-solid fa-xmark mr-1"></i>Annuler
        </button>
        <button type="submit" class="btn-primary" :disabled="loading || imageUploading">
          <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Sauvegarde...' : isEdit ? 'Modifier' : 'Créer' }}
        </button>
      </div>
    </form>
  </div>
</template>
