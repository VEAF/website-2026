<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import {
  getAdminMenuItems,
  createAdminMenuItem,
  updateAdminMenuItem,
  deleteAdminMenuItem,
} from '@/api/menu'
import { getAdminUrls } from '@/api/urls'
import { getAdminPages } from '@/api/pages'
import type { AdminMenuItem, MenuItemCreate, Url, Page } from '@/types/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const { confirm } = useConfirm()
const toast = useToast()

// Type constants
const typeOptions = [
  { value: 1, label: 'Menu' },
  { value: 2, label: 'Url personnalisée' },
  { value: 3, label: 'Url (redirection)' },
  { value: 4, label: 'Page' },
  { value: 5, label: 'Séparateur' },
  { value: 6, label: 'Bureau' },
  { value: 7, label: 'Serveurs' },
  { value: 8, label: 'Roster' },
  { value: 9, label: 'Calendrier' },
  { value: 10, label: 'Mission Maker' },
  { value: 11, label: 'Team Speak' },
]

const typeLabels: Record<number, string> = Object.fromEntries(typeOptions.map((t) => [t.value, t.label]))

const restrictionOptions = [
  { value: 0, label: 'Tout le monde' },
  { value: 1, label: 'Au moins invité' },
  { value: 2, label: 'Au moins cadet' },
  { value: 3, label: 'Membre' },
]

const restrictionLabels: Record<number, string> = Object.fromEntries(
  restrictionOptions.map((r) => [r.value, r.label]),
)

// Data
const items = ref<AdminMenuItem[]>([])
const total = ref(0)
const loading = ref(false)

// Reference data for selects
const parentMenuItems = ref<AdminMenuItem[]>([])
const availableUrls = ref<Url[]>([])
const availablePages = ref<Page[]>([])

// Search & filters
const searchInput = ref('')
const search = ref('')
const typeFilter = ref<number | null>(null)
const enabledFilter = ref<boolean | null>(null)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// Pagination
const currentPage = ref(1)
const pageSize = 50
const totalPages = ref(1)

// Form
const showForm = ref(false)
const editingItemId = ref<number | null>(null)
const itemForm = ref<MenuItemCreate>({
  label: '',
  type: 2,
  icon: null,
  theme_classes: null,
  enabled: false,
  position: null,
  link: null,
  restriction: 0,
  menu_id: null,
  url_id: null,
  page_id: null,
})

function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchInput.value = value
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    search.value = value
  }, 300)
}

async function loadItems() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    if (search.value) params.search = search.value
    if (typeFilter.value !== null) params.type = typeFilter.value
    if (enabledFilter.value !== null) params.enabled = enabledFilter.value

    const result = await getAdminMenuItems(params as Parameters<typeof getAdminMenuItems>[0])
    items.value = result.items
    total.value = result.total
    totalPages.value = Math.max(1, Math.ceil(result.total / pageSize))
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function loadReferenceData() {
  try {
    const [menuResult, urlResult, pageResult] = await Promise.all([
      getAdminMenuItems({ type: 1, limit: 100 }),
      getAdminUrls({ limit: 100 }),
      getAdminPages({ limit: 100 }),
    ])
    parentMenuItems.value = menuResult.items
    availableUrls.value = urlResult.items
    availablePages.value = pageResult.items
  } catch (e) {
    toast.error(e)
  }
}

watch([search, typeFilter, enabledFilter], () => {
  currentPage.value = 1
  loadItems()
})

function goToPage(page: number) {
  currentPage.value = page
  loadItems()
}

function openNew() {
  editingItemId.value = null
  itemForm.value = {
    label: '',
    type: 2,
    icon: null,
    theme_classes: null,
    enabled: false,
    position: null,
    link: null,
    restriction: 0,
    menu_id: null,
    url_id: null,
    page_id: null,
  }
  showForm.value = true
}

function openEdit(item: AdminMenuItem) {
  editingItemId.value = item.id
  itemForm.value = {
    label: item.label,
    type: item.type,
    icon: item.icon,
    theme_classes: item.theme_classes,
    enabled: item.enabled,
    position: item.position,
    link: item.link,
    restriction: item.restriction,
    menu_id: item.menu_id,
    url_id: item.url_id,
    page_id: item.page_id,
  }
  showForm.value = true
}

async function handleSubmit() {
  loading.value = true
  try {
    if (editingItemId.value) {
      await updateAdminMenuItem(editingItemId.value, itemForm.value)
      toast.success('Élément modifié avec succès')
    } else {
      await createAdminMenuItem(itemForm.value)
      toast.success('Élément créé avec succès')
    }
    showForm.value = false
    await loadItems()
    await loadReferenceData()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(item: AdminMenuItem) {
  const label = item.label || `#${item.id}`
  if (!(await confirm(`Supprimer l'élément "${label}" ?`))) return
  loading.value = true
  try {
    await deleteAdminMenuItem(item.id)
    toast.success('Élément supprimé avec succès')
    await loadItems()
    await loadReferenceData()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadItems(), loadReferenceData()])
})
</script>

<template>
  <div>
    <!-- Search & Filters -->
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="relative flex-1 min-w-[200px]">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <input
          :value="searchInput"
          @input="onSearchInput"
          type="text"
          placeholder="Rechercher par libellé..."
          class="input pl-9 w-full"
        />
      </div>
      <select
        :value="typeFilter ?? ''"
        @change="
          typeFilter =
            ($event.target as HTMLSelectElement).value === ''
              ? null
              : Number(($event.target as HTMLSelectElement).value)
        "
        class="input w-48"
      >
        <option value="">Tous les types</option>
        <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      <select
        :value="enabledFilter ?? ''"
        @change="
          enabledFilter =
            ($event.target as HTMLSelectElement).value === ''
              ? null
              : ($event.target as HTMLSelectElement).value === 'true'
        "
        class="input w-40"
      >
        <option value="">Tous les statuts</option>
        <option value="true">Activé</option>
        <option value="false">Désactivé</option>
      </select>
      <button class="btn-primary" @click="openNew">
        <i class="fa-solid fa-plus mr-1"></i>Ajouter un élément
      </button>
    </div>

    <!-- Form -->
    <div v-if="showForm" class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">
        {{ editingItemId ? "Modifier l'élément" : 'Ajouter un élément' }}
      </h3>
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Libellé</label>
            <input v-model="itemForm.label" type="text" class="input" maxlength="64" />
          </div>
          <div>
            <label class="label">Type</label>
            <select v-model.number="itemForm.type" class="input" required>
              <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="label">Icône (classe FA)</label>
            <input v-model="itemForm.icon" type="text" class="input" maxlength="64" placeholder="ex: fa-solid fa-home" />
          </div>
          <div>
            <label class="label">Classes CSS</label>
            <input v-model="itemForm.theme_classes" type="text" class="input" maxlength="255" />
          </div>
          <div>
            <label class="label">Position</label>
            <input v-model.number="itemForm.position" type="number" class="input" min="0" />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="label">Restriction d'accès</label>
            <select v-model.number="itemForm.restriction" class="input">
              <option v-for="opt in restrictionOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Menu parent</label>
            <select
              :value="itemForm.menu_id ?? ''"
              @change="
                itemForm.menu_id =
                  ($event.target as HTMLSelectElement).value === ''
                    ? null
                    : Number(($event.target as HTMLSelectElement).value)
              "
              class="input"
            >
              <option value="">Aucun (racine)</option>
              <option
                v-for="parent in parentMenuItems"
                :key="parent.id"
                :value="parent.id"
                :disabled="editingItemId === parent.id"
              >
                {{ parent.label || `Menu #${parent.id}` }}
              </option>
            </select>
          </div>
          <div class="flex items-end">
            <label class="flex items-center space-x-2 pb-2">
              <input v-model="itemForm.enabled" type="checkbox" class="rounded" />
              <span class="text-sm">Activé</span>
            </label>
          </div>
        </div>

        <!-- Type-specific fields -->
        <div v-if="itemForm.type === 2">
          <label class="label">URL personnalisée</label>
          <input v-model="itemForm.link" type="url" class="input" placeholder="https://..." />
        </div>

        <div v-if="itemForm.type === 3">
          <label class="label">URL (redirection)</label>
          <select
            :value="itemForm.url_id ?? ''"
            @change="
              itemForm.url_id =
                ($event.target as HTMLSelectElement).value === ''
                  ? null
                  : Number(($event.target as HTMLSelectElement).value)
            "
            class="input"
          >
            <option value="">-- Sélectionner une URL --</option>
            <option v-for="u in availableUrls" :key="u.id" :value="u.id">
              {{ u.slug }} → {{ u.target }}
            </option>
          </select>
        </div>

        <div v-if="itemForm.type === 4">
          <label class="label">Page</label>
          <select
            :value="itemForm.page_id ?? ''"
            @change="
              itemForm.page_id =
                ($event.target as HTMLSelectElement).value === ''
                  ? null
                  : Number(($event.target as HTMLSelectElement).value)
            "
            class="input"
          >
            <option value="">-- Sélectionner une page --</option>
            <option v-for="p in availablePages" :key="p.id" :value="p.id">
              {{ p.title }} ({{ p.path }})
            </option>
          </select>
        </div>

        <div class="flex justify-end space-x-3">
          <button type="button" class="btn-secondary" @click="showForm = false">
            <i class="fa-solid fa-xmark mr-1"></i>Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingItemId ? 'Modifier' : 'Créer' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Position</th>
            <th class="p-2">Parent</th>
            <th class="p-2">Libellé</th>
            <th class="p-2">Type</th>
            <th class="p-2">Activé</th>
            <th class="p-2">Restriction</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!items.length">
            <td colspan="7" class="p-4 text-center text-gray-500">Aucun élément de menu</td>
          </tr>
          <tr v-for="item in items" :key="item.id" class="border-b hover:bg-gray-50">
            <td class="p-2 text-center">{{ item.position ?? '-' }}</td>
            <td class="p-2 text-xs text-gray-600">{{ item.menu_label || '-' }}</td>
            <td class="p-2">
              <div class="flex items-center gap-2">
                <i v-if="item.icon" :class="item.icon" class="text-gray-500"></i>
                <span class="font-medium">{{ item.label || '-' }}</span>
              </div>
            </td>
            <td class="p-2">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-veaf-100 text-veaf-800">
                {{ typeLabels[item.type] ?? 'Inconnu' }}
              </span>
            </td>
            <td class="p-2">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :class="item.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ item.enabled ? 'Oui' : 'Non' }}
              </span>
            </td>
            <td class="p-2 text-xs">{{ restrictionLabels[item.restriction] ?? '-' }}</td>
            <td class="p-2 space-x-3">
              <button class="text-veaf-600 hover:text-veaf-800 text-sm" @click="openEdit(item)">
                <i class="fa-solid fa-edit mr-1"></i>Modifier
              </button>
              <button class="text-red-600 hover:text-red-800 text-sm" @click="handleDelete(item)">
                <i class="fa-solid fa-trash mr-1"></i>Supprimer
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4">
      <span class="text-sm text-gray-600">{{ total }} élément(s) au total</span>
      <div class="flex items-center space-x-2">
        <button class="btn-secondary text-sm" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
          <i class="fa-solid fa-chevron-left mr-1"></i>Précédent
        </button>
        <span class="text-sm text-gray-600">Page {{ currentPage }} sur {{ totalPages }}</span>
        <button class="btn-secondary text-sm" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
          Suivant<i class="fa-solid fa-chevron-right ml-1"></i>
        </button>
      </div>
    </div>
  </div>
</template>
