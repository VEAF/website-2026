<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getAdminUsers, updateAdminUser } from '@/api/users'
import { getAdminStats } from '@/api/admin'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'
import type { AdminUser, AdminUserUpdate } from '@/types/user'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const route = useRoute()

// localStorage persistence helpers
const STORAGE_PREFIX = 'admin.users.'

function loadStorage<T>(key: string, defaultValue: T): T {
  const raw = localStorage.getItem(STORAGE_PREFIX + key)
  if (raw === null) return defaultValue
  try { return JSON.parse(raw) } catch { return defaultValue }
}

function saveStorage(key: string, value: unknown): void {
  localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value))
}

// Data
const users = ref<AdminUser[]>([])
const total = ref(0)
const loading = ref(false)
const cadetsReadyCount = ref(0)

// Search and filters
const searchInput = ref('')
const search = ref('')
const statusFilter = ref<number | null>(
  route.query.status !== undefined ? Number(route.query.status) : null,
)
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

const statusOptions = [
  { value: 0, label: 'Inconnu' },
  { value: 1, label: 'Cadet' },
  { value: 2, label: 'Membre' },
  { value: 3, label: 'Secrétaire adjoint' },
  { value: 4, label: 'Secrétaire' },
  { value: 5, label: 'Trésorier adjoint' },
  { value: 6, label: 'Trésorier' },
  { value: 7, label: 'Président adjoint' },
  { value: 8, label: 'Président' },
  { value: 9, label: 'Invité' },
]

const availableRoles = [
  { value: 'ROLE_USER', label: 'Utilisateur' },
  { value: 'ROLE_RECRUITER', label: 'Recruteur' },
  { value: 'ROLE_ADMIN', label: 'Administrateur' },
]

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// Edit form
const showEditForm = ref(false)
const editingUserId = ref<number | null>(null)
const editForm = ref<AdminUserUpdate>({
  email: '',
  nickname: '',
  roles: [],
  status: 0,
  discord: null,
  forum: null,
  sim_dcs: false,
  sim_bms: false,
  need_presentation: false,
})

async function loadUsers() {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (search.value) params.search = search.value
    if (statusFilter.value !== null) params.status = statusFilter.value

    const result = await getAdminUsers(params)
    users.value = result.items
    total.value = result.total
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

function openEditUser(u: AdminUser) {
  editingUserId.value = u.id
  editForm.value = {
    email: u.email,
    nickname: u.nickname,
    roles: [...u.roles],
    status: u.status,
    discord: u.discord,
    forum: u.forum,
    sim_dcs: u.sim_dcs,
    sim_bms: u.sim_bms,
    need_presentation: u.need_presentation,
  }
  showEditForm.value = true
}

async function handleEditSubmit() {
  if (!editingUserId.value) return
  loading.value = true
  try {
    await updateAdminUser(editingUserId.value, editForm.value)
    toast.success('Utilisateur modifié avec succès')
    showEditForm.value = false
    await loadUsers()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('fr-FR')
}

function statusClass(status: number): string {
  if (status >= 3 && status <= 8) return 'bg-veaf-100 text-veaf-800'
  if (status === 2) return 'bg-green-100 text-green-800'
  if (status === 1) return 'bg-yellow-100 text-yellow-800'
  return 'bg-gray-100 text-gray-800'
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  loadUsers()
}

watch([search, statusFilter, pageSize], () => {
  currentPage.value = 1
  loadUsers()
})

// Persist filter/pagination state to localStorage
watch([search, statusFilter, currentPage, pageSize], () => {
  saveStorage('search', search.value)
  saveStorage('statusFilter', statusFilter.value)
  saveStorage('currentPage', currentPage.value)
  saveStorage('pageSize', pageSize.value)
})

onMounted(async () => {
  loadUsers()
  try {
    const stats = await getAdminStats()
    cadetsReadyCount.value = stats.cadets_ready_to_promote
  } catch {
    // silently fail
  }
})
</script>

<template>
  <div>
    <AppBreadcrumb :show-title="false" />

    <!-- Cadet readiness notification -->
    <div
      v-if="cadetsReadyCount > 0"
      class="bg-green-50 border border-green-200 rounded-lg p-3 mb-4 flex items-center justify-between"
    >
      <div class="flex items-center text-green-800 text-sm">
        <i class="fa-solid fa-circle-check text-green-600 mr-2"></i>
        <span class="font-medium">
          {{ cadetsReadyCount }} cadet{{ cadetsReadyCount > 1 ? 's' : '' }}
          prêt{{ cadetsReadyCount > 1 ? 's' : '' }} à rejoindre l'association
        </span>
      </div>
      <button
        class="text-green-700 hover:text-green-900 text-sm font-medium underline"
        @click="statusFilter = 1"
      >
        Voir les cadets
      </button>
    </div>

    <!-- Search & Filter -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <div class="relative flex-1">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></i>
        <input
          :value="searchInput"
          type="text"
          class="input pl-9 w-full"
          placeholder="Rechercher par pseudo ou email..."
          @input="searchInput = ($event.target as HTMLInputElement).value; onSearchInput()"
        />
      </div>
      <select
        :value="statusFilter ?? ''"
        class="input w-full sm:w-48"
        @change="statusFilter = ($event.target as HTMLSelectElement).value === '' ? null : Number(($event.target as HTMLSelectElement).value)"
      >
        <option value="">Tous les statuts</option>
        <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </div>

    <!-- Edit form -->
    <div v-if="showEditForm" class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">Modifier l'utilisateur</h3>
      <form class="space-y-4" @submit.prevent="handleEditSubmit">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Email</label>
            <input v-model="editForm.email" type="email" class="input" required />
          </div>
          <div>
            <label class="label">Pseudo</label>
            <input v-model="editForm.nickname" type="text" class="input" required />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Statut</label>
            <select v-model.number="editForm.status" class="input">
              <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Rôles</label>
            <div class="flex flex-wrap gap-3 mt-1">
              <label
                v-for="role in availableRoles"
                :key="role.value"
                class="flex items-center space-x-2"
              >
                <input
                  v-model="editForm.roles"
                  type="checkbox"
                  :value="role.value"
                  class="rounded"
                />
                <span class="text-sm">{{ role.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Discord</label>
            <input v-model="editForm.discord" type="text" class="input" />
          </div>
          <div>
            <label class="label">Forum</label>
            <input v-model="editForm.forum" type="text" class="input" />
          </div>
        </div>

        <div class="flex items-center space-x-6">
          <label class="flex items-center space-x-2">
            <input v-model="editForm.sim_dcs" type="checkbox" class="rounded" />
            <span class="text-sm">DCS</span>
          </label>
          <label class="flex items-center space-x-2">
            <input v-model="editForm.sim_bms" type="checkbox" class="rounded" />
            <span class="text-sm">BMS</span>
          </label>
          <label class="flex items-center space-x-2">
            <input v-model="editForm.need_presentation" type="checkbox" class="rounded" />
            <span class="text-sm">Besoin de présentation</span>
          </label>
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

    <!-- Users table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Pseudo</th>
            <th class="p-2">Email</th>
            <th class="p-2">Statut</th>
            <th class="p-2">Discord</th>
            <th class="p-2">Forum</th>
            <th class="p-2">DCS</th>
            <th class="p-2">BMS</th>
            <th class="p-2">Inscription</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading && !users.length">
            <td colspan="9" class="p-4 text-center text-gray-500">Chargement...</td>
          </tr>
          <tr v-else-if="!users.length">
            <td colspan="9" class="p-4 text-center text-gray-500">Aucun utilisateur</td>
          </tr>
          <tr
            v-for="u in users"
            :key="u.id"
            class="border-b hover:bg-gray-50"
          >
            <td class="p-2 font-medium">
              <i
                v-if="u.is_ready_to_promote"
                class="fa-solid fa-circle-check text-green-600 mr-1"
                title="Prêt à rejoindre l'association"
              ></i>{{ u.nickname }}
            </td>
            <td class="p-2">{{ u.email }}</td>
            <td class="p-2">
              <span
                class="inline-block px-2 py-0.5 rounded-full text-xs font-medium"
                :class="statusClass(u.status)"
              >
                {{ u.status_as_string }}
              </span>
            </td>
            <td class="p-2">{{ u.discord ?? '-' }}</td>
            <td class="p-2">{{ u.forum ?? '-' }}</td>
            <td class="p-2">{{ u.sim_dcs ? 'oui' : 'non' }}</td>
            <td class="p-2">{{ u.sim_bms ? 'oui' : 'non' }}</td>
            <td class="p-2">{{ formatDate(u.created_at) }}</td>
            <td class="p-2">
              <button
                class="text-veaf-600 hover:text-veaf-800 text-sm"
                @click="openEditUser(u)"
              >
                <i class="fa-solid fa-edit mr-1"></i>Modifier
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="flex items-center justify-between p-3 border-t">
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-600">
            {{ total }} utilisateur{{ total > 1 ? 's' : '' }}
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
