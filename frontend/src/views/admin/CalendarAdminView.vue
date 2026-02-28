<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getAdminEvents, restoreAdminEvent } from '@/api/calendar'
import AdminBreadcrumb from '@/components/admin/AdminBreadcrumb.vue'
import type { AdminEvent } from '@/types/calendar'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'

const toast = useToast()
const { confirm } = useConfirm()

// localStorage persistence helpers
const STORAGE_PREFIX = 'admin.events.'

function loadStorage<T>(key: string, defaultValue: T): T {
  const raw = localStorage.getItem(STORAGE_PREFIX + key)
  if (raw === null) return defaultValue
  try { return JSON.parse(raw) } catch { return defaultValue }
}

function saveStorage(key: string, value: unknown): void {
  localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value))
}

// Data
const events = ref<AdminEvent[]>([])
const total = ref(0)
const loading = ref(false)

// Search and filters (restored from localStorage)
const searchInput = ref(loadStorage<string>('search', ''))
const search = ref(loadStorage<string>('search', ''))
const typeFilter = ref(loadStorage<number | null>('typeFilter', null))
const deletedFilter = ref(loadStorage<boolean | null>('deletedFilter', null))
const dateFrom = ref(loadStorage<string>('dateFrom', ''))
const dateTo = ref(loadStorage<string>('dateTo', ''))
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
  { value: 1, label: 'Training' },
  { value: 2, label: 'Mission' },
  { value: 3, label: 'OPEX' },
  { value: 4, label: 'Meeting' },
  { value: 5, label: 'Maintenance' },
  { value: 6, label: 'ATC / GCI' },
]

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

async function loadEvents() {
  loading.value = true
  try {
    const params: Record<string, string | number | boolean> = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (search.value) params.search = search.value
    if (typeFilter.value !== null) params.type = typeFilter.value
    if (deletedFilter.value !== null) params.deleted = deletedFilter.value
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value

    const result = await getAdminEvents(params)
    events.value = result.items
    total.value = result.total
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleRestore(event: AdminEvent) {
  const ok = await confirm(`Restaurer l'événement « ${event.title} » ?`)
  if (!ok) return
  try {
    await restoreAdminEvent(event.id)
    toast.success('Événement restauré avec succès')
    await loadEvents()
  } catch (e) {
    toast.error(e)
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

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadEvents()
}

watch([search, typeFilter, deletedFilter, dateFrom, dateTo, pageSize], () => {
  currentPage.value = 1
  loadEvents()
})

// Persist all filter/pagination state to localStorage
watch([search, typeFilter, deletedFilter, dateFrom, dateTo, currentPage, pageSize], () => {
  saveStorage('search', search.value)
  saveStorage('typeFilter', typeFilter.value)
  saveStorage('deletedFilter', deletedFilter.value)
  saveStorage('dateFrom', dateFrom.value)
  saveStorage('dateTo', dateTo.value)
  saveStorage('currentPage', currentPage.value)
  saveStorage('pageSize', pageSize.value)
})

onMounted(loadEvents)
</script>

<template>
  <div>
    <AdminBreadcrumb />

    <!-- Search & Filters -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="relative flex-1">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
        <input
          :value="searchInput"
          type="text"
          class="input pl-9 w-full"
          placeholder="Rechercher par titre..."
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
      <select
        :value="deletedFilter === null ? '' : deletedFilter ? 'true' : 'false'"
        class="input w-full sm:w-48"
        @change="deletedFilter = ($event.target as HTMLSelectElement).value === '' ? null : ($event.target as HTMLSelectElement).value === 'true'"
      >
        <option value="">Tous</option>
        <option value="false">Actifs seulement</option>
        <option value="true">Supprimés seulement</option>
      </select>
    </div>
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 whitespace-nowrap">Du</label>
        <input
          v-model="dateFrom"
          type="date"
          class="input"
        />
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 whitespace-nowrap">Au</label>
        <input
          v-model="dateTo"
          type="date"
          class="input"
        />
      </div>
    </div>

    <!-- Events table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Début</th>
            <th class="p-2">Fin</th>
            <th class="p-2">Titre</th>
            <th class="p-2">Type</th>
            <th class="p-2">DCS</th>
            <th class="p-2">BMS</th>
            <th class="p-2">Carte</th>
            <th class="p-2">Créateur</th>
            <th class="p-2">Supprimé</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && !events.length">
            <td colspan="10" class="p-4 text-center text-gray-500">Chargement...</td>
          </tr>
          <tr v-else-if="!events.length">
            <td colspan="10" class="p-4 text-center text-gray-500">Aucun événement</td>
          </tr>
          <tr
            v-for="ev in events"
            :key="ev.id"
            class="border-b hover:bg-gray-50"
            :class="{ 'opacity-50': ev.deleted }"
          >
            <td class="p-2 whitespace-nowrap">{{ formatDateTime(ev.start_date) }}</td>
            <td class="p-2 whitespace-nowrap">{{ formatDateTime(ev.end_date) }}</td>
            <td class="p-2 font-medium">{{ ev.title }}</td>
            <td class="p-2">
              <span
                class="inline-block px-2 py-0.5 rounded-full text-xs font-medium text-white"
                :style="{ backgroundColor: ev.type_color ?? '#6b7280' }"
              >
                {{ ev.type_as_string }}
              </span>
            </td>
            <td class="p-2">{{ ev.sim_dcs ? 'oui' : 'non' }}</td>
            <td class="p-2">{{ ev.sim_bms ? 'oui' : 'non' }}</td>
            <td class="p-2">{{ ev.map_name ?? '-' }}</td>
            <td class="p-2">{{ ev.owner_nickname ?? '-' }}</td>
            <td class="p-2">
              <span
                class="inline-block px-2 py-0.5 rounded-full text-xs font-medium"
                :class="ev.deleted ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
              >
                {{ ev.deleted ? 'oui' : 'non' }}
              </span>
            </td>
            <td class="p-2 whitespace-nowrap">
              <RouterLink
                :to="`/calendar/${ev.id}`"
                class="text-veaf-600 hover:text-veaf-800 text-sm mr-3"
                title="Voir l'événement"
              >
                <i class="fa-solid fa-eye"></i>
              </RouterLink>
              <button
                v-if="ev.deleted"
                class="text-green-600 hover:text-green-800 text-sm"
                title="Restaurer"
                @click="handleRestore(ev)"
              >
                <i class="fa-solid fa-trash-arrow-up"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between mt-4">
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-600">
          {{ total }} événement{{ total > 1 ? 's' : '' }}
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
</template>
