<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getAdminUsers, updateAdminUser } from '@/api/users'
import type { AdminUser, AdminUserUpdate } from '@/types/user'

// Data
const users = ref<AdminUser[]>([])
const total = ref(0)
const loading = ref(false)

// Feedback
const error = ref<string | null>(null)
const success = ref<string | null>(null)

function showSuccess(msg: string) {
  success.value = msg
  error.value = null
  setTimeout(() => (success.value = null), 3000)
}

function showError(err: unknown) {
  const msg = err instanceof Error ? err.message : 'Une erreur est survenue'
  error.value = msg
  success.value = null
}

// Search and filters
const searchInput = ref('')
const search = ref('')
const statusFilter = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = 50

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

const totalPages = computed(() => Math.ceil(total.value / pageSize))

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
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    if (search.value) params.search = search.value
    if (statusFilter.value !== null) params.status = statusFilter.value

    const result = await getAdminUsers(params)
    users.value = result.items
    total.value = result.total
  } catch (e) {
    showError(e)
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
    showSuccess('Utilisateur modifié avec succès')
    showEditForm.value = false
    await loadUsers()
  } catch (e) {
    showError(e)
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

watch([search, statusFilter], () => {
  currentPage.value = 1
  loadUsers()
})

onMounted(loadUsers)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Gestion des utilisateurs</h1>

    <!-- Feedback -->
    <div v-if="success" class="bg-green-50 text-green-700 p-3 rounded-md text-sm mb-4">
      {{ success }}
    </div>
    <div v-if="error" class="bg-red-50 text-red-700 p-3 rounded-md text-sm mb-4">
      {{ error }}
    </div>

    <!-- Search & Filter -->
    <div class="flex flex-col sm:flex-row gap-3 mb-4">
      <input
        :value="searchInput"
        type="text"
        class="input flex-1"
        placeholder="Rechercher par pseudo ou email..."
        @input="searchInput = ($event.target as HTMLInputElement).value; onSearchInput()"
      />
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
            Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Enregistrement...' : 'Modifier' }}
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
            <td class="p-2 font-medium">{{ u.nickname }}</td>
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
                Modifier
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4">
      <span class="text-sm text-gray-600">
        {{ total }} utilisateur{{ total > 1 ? 's' : '' }}
      </span>
      <div class="flex items-center space-x-2">
        <button
          class="btn-secondary text-sm"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          Précédent
        </button>
        <span class="text-sm text-gray-600">
          Page {{ currentPage }} sur {{ totalPages }}
        </span>
        <button
          class="btn-secondary text-sm"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Suivant
        </button>
      </div>
    </div>
  </div>
</template>
