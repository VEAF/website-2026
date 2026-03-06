<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  getAdminRecruitmentEvents,
  updateAdminRecruitmentEvent,
  deleteAdminRecruitmentEvent,
} from '@/api/recruitment'
import type { AdminRecruitmentEvent } from '@/api/recruitment'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'

const toast = useToast()
const { confirm } = useConfirm()

// localStorage persistence helpers
const STORAGE_PREFIX = 'admin.activities.'

function loadStorage<T>(key: string, defaultValue: T): T {
  const raw = localStorage.getItem(STORAGE_PREFIX + key)
  if (raw === null) return defaultValue
  try { return JSON.parse(raw) } catch { return defaultValue }
}

function saveStorage(key: string, value: unknown): void {
  localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value))
}

// Data
const events = ref<AdminRecruitmentEvent[]>([])
const total = ref(0)
const loading = ref(false)

// Search and filters
const searchInput = ref('')
const search = ref('')
const typeFilter = ref<number | null>(null)
const currentPage = ref(loadStorage<number>('currentPage', 1))
const pageSize = ref(loadStorage<number>('pageSize', 50))
const pageSizeOptions = [10, 20, 50, 100]

let searchTimeout: ReturnType<typeof setTimeout> | null = null

function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    search.value = searchInput.value
  }, 300)
}

const typeOptions = [
  { value: 1, label: 'Candidature' },
  { value: 2, label: 'Présentation' },
  { value: 3, label: 'Promotion' },
  { value: 4, label: 'Activité' },
  { value: 5, label: 'Invité' },
]

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// Edit form
const showEditForm = ref(false)
const editingEventId = ref<number | null>(null)
const editForm = ref({
  comment: '' as string | null,
  event_at: '' as string | null,
})

function typeClass(type: number): string {
  switch (type) {
    case 1: return 'bg-blue-100 text-blue-800'
    case 2: return 'bg-purple-100 text-purple-800'
    case 3: return 'bg-green-100 text-green-800'
    case 4: return 'bg-yellow-100 text-yellow-800'
    case 5: return 'bg-gray-100 text-gray-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function toDatetimeLocal(dateStr: string | null): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadEvents() {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (search.value) params.search = search.value
    if (typeFilter.value !== null) params.type = typeFilter.value

    const result = await getAdminRecruitmentEvents(params)
    events.value = result.items
    total.value = result.total
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

function openEdit(event: AdminRecruitmentEvent) {
  editingEventId.value = event.id
  editForm.value = {
    comment: event.comment ?? '',
    event_at: toDatetimeLocal(event.event_at),
  }
  showEditForm.value = true
}

async function handleEditSubmit() {
  if (!editingEventId.value) return
  loading.value = true
  try {
    const payload = {
      comment: editForm.value.comment || null,
      event_at: editForm.value.event_at ? new Date(editForm.value.event_at).toISOString() : null,
    }
    await updateAdminRecruitmentEvent(editingEventId.value, payload)
    toast.success('Activité modifiée avec succès')
    showEditForm.value = false
    await loadEvents()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(event: AdminRecruitmentEvent) {
  const label = `l'activité « ${event.type_as_string} » de ${event.user_nickname ?? 'inconnu'}`
  const ok = await confirm(`Supprimer ${label} ? Cette action est irréversible.`)
  if (!ok) return
  try {
    await deleteAdminRecruitmentEvent(event.id)
    toast.success('Activité supprimée avec succès')
    await loadEvents()
  } catch (e) {
    toast.error(e)
  }
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadEvents()
}

watch([search, typeFilter, pageSize], () => {
  currentPage.value = 1
  loadEvents()
})

// Persist filter/pagination state to localStorage
watch([search, typeFilter, currentPage, pageSize], () => {
  saveStorage('search', search.value)
  saveStorage('typeFilter', typeFilter.value)
  saveStorage('currentPage', currentPage.value)
  saveStorage('pageSize', pageSize.value)
})

onMounted(loadEvents)
</script>

<template>
  <div>
    <AppBreadcrumb :show-title="false" />

    <!-- Search & Filters -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="relative flex-1">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
        <input
          :value="searchInput"
          type="text"
          class="input pl-9 w-full"
          placeholder="Rechercher par pseudo du cadet..."
          @input="searchInput = ($event.target as HTMLInputElement).value; onSearchInput()"
        />
      </div>
      <select
        :value="typeFilter ?? ''"
        class="input w-full sm:w-48"
        @change="typeFilter = ($event.target as HTMLSelectElement).value === '' ? null : Number(($event.target as HTMLSelectElement).value)"
      >
        <option value="">Tous les types</option>
        <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </div>

    <!-- Edit form -->
    <div v-if="showEditForm" class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">Modifier l'activité</h3>
      <form class="space-y-4" @submit.prevent="handleEditSubmit">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Date</label>
            <input v-model="editForm.event_at" type="datetime-local" class="input" />
          </div>
          <div>
            <label class="label">Commentaire</label>
            <input v-model="editForm.comment" type="text" class="input" maxlength="255" />
          </div>
        </div>
        <div class="flex justify-end space-x-3">
          <button type="button" class="btn-secondary" @click="showEditForm = false">
            <i class="fa-solid fa-xmark mr-1"></i>Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : 'Modifier' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Activities table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Cadet</th>
            <th class="p-2">Type</th>
            <th class="p-2">Date</th>
            <th class="p-2">Commentaire</th>
            <th class="p-2">Validateur</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && !events.length">
            <td colspan="6" class="p-4 text-center text-gray-500">Chargement...</td>
          </tr>
          <tr v-else-if="!events.length">
            <td colspan="6" class="p-4 text-center text-gray-500">Aucune activité</td>
          </tr>
          <tr
            v-for="event in events"
            :key="event.id"
            class="border-b hover:bg-gray-50"
          >
            <td class="p-2 font-medium">{{ event.user_nickname ?? '-' }}</td>
            <td class="p-2">
              <span
                class="inline-block px-2 py-0.5 rounded-full text-xs font-medium"
                :class="typeClass(event.type)"
              >
                {{ event.type_as_string }}
              </span>
            </td>
            <td class="p-2 whitespace-nowrap">{{ formatDateTime(event.event_at) }}</td>
            <td class="p-2 max-w-xs truncate" :title="event.comment ?? ''">
              {{ event.comment ?? '-' }}
            </td>
            <td class="p-2">{{ event.validator_nickname ?? '-' }}</td>
            <td class="p-2 whitespace-nowrap">
              <button
                class="text-veaf-600 hover:text-veaf-800 text-sm mr-3"
                title="Modifier"
                @click="openEdit(event)"
              >
                <i class="fa-solid fa-edit"></i>
              </button>
              <button
                class="text-red-600 hover:text-red-800 text-sm"
                title="Supprimer"
                @click="handleDelete(event)"
              >
                <i class="fa-solid fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="flex items-center justify-between p-3 border-t">
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-600">
            {{ total }} activité{{ total > 1 ? 's' : '' }}
          </span>
          <select
            :value="pageSize"
            class="input text-sm py-1 w-auto"
            @change="pageSize = Number(($event.target as HTMLSelectElement).value)"
          >
            <option v-for="size in pageSizeOptions" :key="size" :value="size">
              {{ size }} / page
            </option>
          </select>
        </div>
        <div v-if="totalPages > 1" class="flex items-center space-x-2">
          <button
            class="btn-secondary text-sm"
            :disabled="currentPage <= 1"
            @click="goToPage(currentPage - 1)"
          >
            <i class="fa-solid fa-chevron-left mr-1"></i>Précédent
          </button>
          <span class="text-sm text-gray-600">
            Page {{ currentPage }} sur {{ totalPages }}
          </span>
          <button
            class="btn-secondary text-sm"
            :disabled="currentPage >= totalPages"
            @click="goToPage(currentPage + 1)"
          >
            Suivant<i class="fa-solid fa-chevron-right ml-1"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
