<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getAdminFiles, deleteAdminFile } from '@/api/files'
import type { AdminFile } from '@/api/files'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'

const toast = useToast()
const { confirm } = useConfirm()

// localStorage persistence helpers
const STORAGE_PREFIX = 'admin.files.'

function loadStorage<T>(key: string, defaultValue: T): T {
  const raw = localStorage.getItem(STORAGE_PREFIX + key)
  if (raw === null) return defaultValue
  try { return JSON.parse(raw) } catch { return defaultValue }
}

function saveStorage(key: string, value: unknown): void {
  localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value))
}

// Data
const files = ref<AdminFile[]>([])
const total = ref(0)
const loading = ref(false)

// Search and filters (restored from localStorage)
const searchInput = ref(loadStorage<string>('search', ''))
const search = ref(loadStorage<string>('search', ''))
const typeFilter = ref(loadStorage<number | null>('typeFilter', null))
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
  { value: 1, label: 'Image' },
  { value: 2, label: 'PDF' },
  { value: 0, label: 'Inconnu' },
]

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 o'
  const units = ['o', 'Ko', 'Mo', 'Go']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
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

function fileUrl(uuid: string): string {
  return `/api/files/${uuid}`
}

async function loadFiles() {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (search.value) params.search = search.value
    if (typeFilter.value !== null) params.type = typeFilter.value

    const result = await getAdminFiles(params)
    files.value = result.items
    total.value = result.total
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(file: AdminFile) {
  const name = file.original_name || file.uuid
  const ok = await confirm(`Supprimer le fichier « ${name} » ? Cette action est irréversible.`)
  if (!ok) return
  try {
    await deleteAdminFile(file.id)
    toast.success('Fichier supprimé avec succès')
    await loadFiles()
  } catch (e) {
    toast.error(e)
  }
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadFiles()
}

watch([search, typeFilter, pageSize], () => {
  currentPage.value = 1
  loadFiles()
})

// Persist all filter/pagination state to localStorage
watch([search, typeFilter, currentPage, pageSize], () => {
  saveStorage('search', search.value)
  saveStorage('typeFilter', typeFilter.value)
  saveStorage('currentPage', currentPage.value)
  saveStorage('pageSize', pageSize.value)
})

onMounted(loadFiles)
</script>

<template>
  <div>
    <AppBreadcrumb />

    <!-- Search & Filters -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="relative flex-1">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
        <input
          :value="searchInput"
          type="text"
          class="input pl-9 w-full"
          placeholder="Rechercher par UUID ou nom de fichier..."
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

    <!-- Files table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Aperçu</th>
            <th class="p-2">Nom original</th>
            <th class="p-2">UUID</th>
            <th class="p-2">Type</th>
            <th class="p-2">Taille</th>
            <th class="p-2">Propriétaire</th>
            <th class="p-2">Créé le</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && !files.length">
            <td colspan="8" class="p-4 text-center text-gray-500">Chargement...</td>
          </tr>
          <tr v-else-if="!files.length">
            <td colspan="8" class="p-4 text-center text-gray-500">Aucun fichier</td>
          </tr>
          <tr
            v-for="file in files"
            :key="file.id"
            class="border-b hover:bg-gray-50"
          >
            <td class="p-2">
              <img
                v-if="file.type === 1"
                :src="fileUrl(file.uuid)"
                class="w-10 h-10 object-cover rounded"
                loading="lazy"
              />
              <i v-else-if="file.type === 2" class="fa-solid fa-file-pdf text-red-500 text-xl"></i>
              <i v-else class="fa-solid fa-file text-gray-400 text-xl"></i>
            </td>
            <td class="p-2 font-medium">{{ file.original_name ?? '-' }}</td>
            <td class="p-2 font-mono text-xs text-gray-500" :title="file.uuid">
              {{ file.uuid.substring(0, 8) }}...
            </td>
            <td class="p-2">
              <span
                class="inline-block px-2 py-0.5 rounded-full text-xs font-medium"
                :class="{
                  'bg-blue-100 text-blue-800': file.type === 1,
                  'bg-red-100 text-red-800': file.type === 2,
                  'bg-gray-100 text-gray-800': file.type !== 1 && file.type !== 2,
                }"
              >
                {{ file.type_as_string ?? 'inconnu' }}
              </span>
            </td>
            <td class="p-2 whitespace-nowrap">{{ formatFileSize(file.size) }}</td>
            <td class="p-2">{{ file.owner_nickname ?? '-' }}</td>
            <td class="p-2 whitespace-nowrap">{{ formatDateTime(file.created_at) }}</td>
            <td class="p-2 whitespace-nowrap">
              <a
                :href="fileUrl(file.uuid)"
                target="_blank"
                class="text-veaf-600 hover:text-veaf-800 text-sm mr-3"
                title="Télécharger"
              >
                <i class="fa-solid fa-download"></i>
              </a>
              <button
                class="text-red-600 hover:text-red-800 text-sm"
                title="Supprimer"
                @click="handleDelete(file)"
              >
                <i class="fa-solid fa-trash"></i>
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
          {{ total }} fichier{{ total > 1 ? 's' : '' }}
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
