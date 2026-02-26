<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminPages, createAdminPage, updateAdminPage, deleteAdminPage } from '@/api/pages'
import type { Page } from '@/types/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { confirm } = useConfirm()
const toast = useToast()

// Data
const pages = ref<Page[]>([])
const total = ref(0)
const loading = ref(false)

// Search & filters
const searchInput = ref('')
const search = ref('')
const enabledFilter = ref<boolean | null>(null)
const restrictionFilter = ref<number | null>(null)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// Pagination
const currentPage = ref(1)
const pageSize = 50

// Form
const showForm = ref(false)
const editingPageId = ref<number | null>(null)
const pageForm = ref({
  title: '',
  route: '',
  path: '',
  enabled: false,
  restriction: 0,
})

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

const pathManuallyEdited = ref(false)
const routeManuallyEdited = ref(false)

function routeSlugify(value: string): string {
  return 'page_' + value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
}

watch(
  () => pageForm.value.title,
  (title) => {
    if (!editingPageId.value && !pathManuallyEdited.value) {
      pageForm.value.path = slugify(title)
    }
    if (!editingPageId.value && !routeManuallyEdited.value) {
      pageForm.value.route = routeSlugify(title)
    }
  },
)

function onPathInput() {
  pathManuallyEdited.value = true
}

function onRouteInput() {
  routeManuallyEdited.value = true
}

const restrictionLabels: Record<number, string> = {
  0: 'Tout le monde',
  1: 'Au moins invité',
  2: 'Au moins cadet',
  3: 'Membre',
}

const restrictionOptions = [
  { value: 0, label: 'Tout le monde' },
  { value: 1, label: 'Au moins invité' },
  { value: 2, label: 'Au moins cadet' },
  { value: 3, label: 'Membre' },
]

function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchInput.value = value
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    search.value = value
  }, 300)
}

const totalPages = ref(1)

async function loadPages() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    if (search.value) params.search = search.value
    if (enabledFilter.value !== null) params.enabled = enabledFilter.value
    if (restrictionFilter.value !== null) params.restriction = restrictionFilter.value

    const result = await getAdminPages(params as Parameters<typeof getAdminPages>[0])
    pages.value = result.items
    total.value = result.total
    totalPages.value = Math.max(1, Math.ceil(result.total / pageSize))
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

watch([search, enabledFilter, restrictionFilter], () => {
  currentPage.value = 1
  loadPages()
})

function goToPage(page: number) {
  currentPage.value = page
  loadPages()
}

function openNew() {
  pathManuallyEdited.value = false
  routeManuallyEdited.value = false
  editingPageId.value = null
  pageForm.value = { title: '', route: '', path: '', enabled: false, restriction: 0 }
  showForm.value = true
}

function openEdit(p: Page) {
  editingPageId.value = p.id
  pageForm.value = {
    title: p.title,
    route: p.route,
    path: p.path,
    enabled: p.enabled,
    restriction: p.restriction,
  }
  showForm.value = true
}

async function handleSubmit() {
  loading.value = true
  try {
    if (editingPageId.value) {
      await updateAdminPage(editingPageId.value, pageForm.value)
      toast.success('Page modifiée avec succès')
    } else {
      await createAdminPage(pageForm.value)
      toast.success('Page créée avec succès')
    }
    showForm.value = false
    await loadPages()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(p: Page) {
  if (!(await confirm(`Supprimer la page "${p.title}" ? Les blocs associés seront également supprimés.`))) return
  loading.value = true
  try {
    await deleteAdminPage(p.id)
    toast.success('Page supprimée avec succès')
    await loadPages()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

function goToDetail(p: Page) {
  router.push({ name: 'admin-page-detail', params: { id: p.id } })
}

function formatDate(date: string | null): string {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(loadPages)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Gestion des pages</h1>

    <!-- Search & Filters -->
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="relative flex-1 min-w-[200px]">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <input
          :value="searchInput"
          @input="onSearchInput"
          type="text"
          placeholder="Rechercher par titre, route ou chemin..."
          class="input pl-9 w-full"
        />
      </div>
      <select
        :value="enabledFilter ?? ''"
        @change="enabledFilter = ($event.target as HTMLSelectElement).value === '' ? null : ($event.target as HTMLSelectElement).value === 'true'"
        class="input w-40"
      >
        <option value="">Tous les statuts</option>
        <option value="true">Activé</option>
        <option value="false">Désactivé</option>
      </select>
      <select
        :value="restrictionFilter ?? ''"
        @change="restrictionFilter = ($event.target as HTMLSelectElement).value === '' ? null : Number(($event.target as HTMLSelectElement).value)"
        class="input w-48"
      >
        <option value="">Toutes les restrictions</option>
        <option v-for="opt in restrictionOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      <button class="btn-primary" @click="openNew">
        <i class="fa-solid fa-plus mr-1"></i>Ajouter une page
      </button>
    </div>

    <!-- Page form -->
    <div v-if="showForm" class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">
        {{ editingPageId ? 'Modifier la page' : 'Ajouter une page' }}
      </h3>
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div>
          <label class="label">Titre</label>
          <input v-model="pageForm.title" type="text" class="input" maxlength="255" required />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Route</label>
            <input v-model="pageForm.route" type="text" class="input" maxlength="255" required @input="onRouteInput" />
            <p class="text-xs text-gray-500 mt-1">Identifiant unique interne (ex: page_about) — généré automatiquement depuis le titre</p>
          </div>
          <div>
            <label class="label">Chemin (URL)</label>
            <input v-model="pageForm.path" type="text" class="input" maxlength="255" required @input="onPathInput" />
            <p class="text-xs text-gray-500 mt-1">Chemin dans l'URL (ex: about/us) — généré automatiquement depuis le titre</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Restriction d'accès</label>
            <select v-model.number="pageForm.restriction" class="input">
              <option v-for="opt in restrictionOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="flex items-end">
            <label class="flex items-center space-x-2 pb-2">
              <input v-model="pageForm.enabled" type="checkbox" class="rounded" />
              <span class="text-sm">Page activée</span>
            </label>
          </div>
        </div>

        <div class="flex justify-end space-x-3">
          <button type="button" class="btn-secondary" @click="showForm = false">
            <i class="fa-solid fa-xmark mr-1"></i>Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingPageId ? 'Modifier' : 'Créer' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Pages table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Titre</th>
            <th class="p-2">Route</th>
            <th class="p-2">Chemin</th>
            <th class="p-2">Activé</th>
            <th class="p-2">Restriction</th>
            <th class="p-2">Modifié le</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!pages.length">
            <td colspan="7" class="p-4 text-center text-gray-500">Aucune page</td>
          </tr>
          <tr v-for="p in pages" :key="p.id" class="border-b hover:bg-gray-50">
            <td class="p-2">
              <button class="text-veaf-600 hover:text-veaf-800 hover:underline font-medium" @click="goToDetail(p)">
                {{ p.title }}
              </button>
            </td>
            <td class="p-2 font-mono text-xs">{{ p.route }}</td>
            <td class="p-2 font-mono text-xs">{{ p.path }}</td>
            <td class="p-2">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :class="p.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ p.enabled ? 'Oui' : 'Non' }}
              </span>
            </td>
            <td class="p-2 text-xs">{{ restrictionLabels[p.restriction] ?? '-' }}</td>
            <td class="p-2 text-xs">{{ formatDate(p.updated_at) }}</td>
            <td class="p-2 space-x-3">
              <button class="text-veaf-600 hover:text-veaf-800 text-sm" @click="goToDetail(p)">
                <i class="fa-solid fa-eye mr-1"></i>Voir
              </button>
              <button class="text-veaf-600 hover:text-veaf-800 text-sm" @click="openEdit(p)">
                <i class="fa-solid fa-pen mr-1"></i>Modifier
              </button>
              <button class="text-red-600 hover:text-red-800 text-sm" @click="handleDelete(p)">
                <i class="fa-solid fa-trash mr-1"></i>Supprimer
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4">
      <span class="text-sm text-gray-600">{{ total }} page(s) au total</span>
      <div class="flex items-center space-x-2">
        <button
          class="btn-secondary text-sm"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          <i class="fa-solid fa-chevron-left mr-1"></i>Précédent
        </button>
        <span class="text-sm text-gray-600">Page {{ currentPage }} sur {{ totalPages }}</span>
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
