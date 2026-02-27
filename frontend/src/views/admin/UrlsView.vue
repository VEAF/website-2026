<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getAdminUrls, createAdminUrl, updateAdminUrl, deleteAdminUrl } from '@/api/urls'
import type { Url } from '@/types/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const { confirm } = useConfirm()
const toast = useToast()

// Data
const urls = ref<Url[]>([])
const total = ref(0)
const loading = ref(false)

// Search & filters
const searchInput = ref('')
const search = ref('')
const statusFilter = ref<boolean | null>(null)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// Pagination
const currentPage = ref(1)
const pageSize = 50
const totalPages = ref(1)

// Form
const showForm = ref(false)
const editingUrlId = ref<number | null>(null)
const urlForm = ref({
  slug: '',
  target: '',
  delay: 0,
  status: true,
})

function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchInput.value = value
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    search.value = value
  }, 300)
}

async function loadUrls() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    if (search.value) params.search = search.value
    if (statusFilter.value !== null) params.status = statusFilter.value

    const result = await getAdminUrls(params as Parameters<typeof getAdminUrls>[0])
    urls.value = result.items
    total.value = result.total
    totalPages.value = Math.max(1, Math.ceil(result.total / pageSize))
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

watch([search, statusFilter], () => {
  currentPage.value = 1
  loadUrls()
})

function goToPage(page: number) {
  currentPage.value = page
  loadUrls()
}

function openNew() {
  editingUrlId.value = null
  urlForm.value = { slug: '', target: '', delay: 0, status: true }
  showForm.value = true
}

function openEdit(u: Url) {
  editingUrlId.value = u.id
  urlForm.value = {
    slug: u.slug,
    target: u.target,
    delay: u.delay,
    status: u.status,
  }
  showForm.value = true
}

async function handleSubmit() {
  loading.value = true
  try {
    if (editingUrlId.value) {
      await updateAdminUrl(editingUrlId.value, urlForm.value)
      toast.success('URL modifiée avec succès')
    } else {
      await createAdminUrl(urlForm.value)
      toast.success('URL créée avec succès')
    }
    showForm.value = false
    await loadUrls()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(u: Url) {
  if (!(await confirm(`Supprimer l'URL "${u.slug}" ?`))) return
  loading.value = true
  try {
    await deleteAdminUrl(u.id)
    toast.success('URL supprimée avec succès')
    await loadUrls()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
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

function truncateTarget(target: string, maxLen = 50): string {
  return target.length > maxLen ? target.substring(0, maxLen) + '...' : target
}

onMounted(loadUrls)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Gestion des URLs</h1>

    <!-- Search & Filters -->
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="relative flex-1 min-w-[200px]">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <input
          :value="searchInput"
          @input="onSearchInput"
          type="text"
          placeholder="Rechercher par slug ou cible..."
          class="input pl-9 w-full"
        />
      </div>
      <select
        :value="statusFilter ?? ''"
        @change="statusFilter = ($event.target as HTMLSelectElement).value === '' ? null : ($event.target as HTMLSelectElement).value === 'true'"
        class="input w-40"
      >
        <option value="">Tous les statuts</option>
        <option value="true">Activé</option>
        <option value="false">Désactivé</option>
      </select>
      <button class="btn-primary" @click="openNew">
        <i class="fa-solid fa-plus mr-1"></i>Ajouter une URL
      </button>
    </div>

    <!-- URL form -->
    <div v-if="showForm" class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">
        {{ editingUrlId ? 'Modifier l\'URL' : 'Ajouter une URL' }}
      </h3>
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Slug</label>
            <input v-model="urlForm.slug" type="text" class="input" maxlength="255" required />
            <p class="text-xs text-gray-500 mt-1">Identifiant dans l'URL (ex: discord, facebook)</p>
          </div>
          <div>
            <label class="label">Cible</label>
            <input v-model="urlForm.target" type="text" class="input" maxlength="255" required />
            <p class="text-xs text-gray-500 mt-1">URL de destination</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Délai (secondes)</label>
            <input v-model.number="urlForm.delay" type="number" min="0" class="input" required />
            <p class="text-xs text-gray-500 mt-1">0 = redirection instantanée, > 0 = affiche un bandeau avec décompte</p>
          </div>
          <div class="flex items-end">
            <label class="flex items-center space-x-2 pb-2">
              <input v-model="urlForm.status" type="checkbox" class="rounded" />
              <span class="text-sm">URL activée</span>
            </label>
          </div>
        </div>

        <div class="flex justify-end space-x-3">
          <button type="button" class="btn-secondary" @click="showForm = false">
            <i class="fa-solid fa-xmark mr-1"></i>Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingUrlId ? 'Modifier' : 'Créer' }}
          </button>
        </div>
      </form>
    </div>

    <!-- URLs table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Slug</th>
            <th class="p-2">Cible</th>
            <th class="p-2">Délai</th>
            <th class="p-2">Activé</th>
            <th class="p-2">Modifié le</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!urls.length">
            <td colspan="6" class="p-4 text-center text-gray-500">Aucune URL</td>
          </tr>
          <tr v-for="u in urls" :key="u.id" class="border-b hover:bg-gray-50">
            <td class="p-2 font-mono text-xs font-medium">{{ u.slug }}</td>
            <td class="p-2">
              <a :href="u.target" target="_blank" rel="noopener" class="text-veaf-600 hover:text-veaf-800 text-xs break-all" :title="u.target">
                {{ truncateTarget(u.target) }}
              </a>
            </td>
            <td class="p-2 text-xs">
              <span v-if="u.delay === 0" class="text-gray-500">Instantané</span>
              <span v-else>{{ u.delay }}s</span>
            </td>
            <td class="p-2">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :class="u.status ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ u.status ? 'Oui' : 'Non' }}
              </span>
            </td>
            <td class="p-2 text-xs">{{ formatDate(u.updated_at) }}</td>
            <td class="p-2 space-x-3">
              <a :href="'/' + u.slug" target="_blank" class="text-veaf-600 hover:text-veaf-800 text-sm" title="Tester la redirection">
                <i class="fa-solid fa-up-right-from-square mr-1"></i>Tester
              </a>
              <button class="text-veaf-600 hover:text-veaf-800 text-sm" @click="openEdit(u)">
                <i class="fa-solid fa-edit mr-1"></i>Modifier
              </button>
              <button class="text-red-600 hover:text-red-800 text-sm" @click="handleDelete(u)">
                <i class="fa-solid fa-trash mr-1"></i>Supprimer
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4">
      <span class="text-sm text-gray-600">{{ total }} URL(s) au total</span>
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
