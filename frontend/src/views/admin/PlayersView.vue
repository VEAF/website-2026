<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { getAdminPlayers, createAdminPlayer, updateAdminPlayer, deleteAdminPlayer } from '@/api/players'
import { getAdminUsers } from '@/api/users'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'
import type { Player } from '@/types/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const { confirm } = useConfirm()
const toast = useToast()

// Data
const players = ref<Player[]>([])
const total = ref(0)
const loading = ref(false)

// Search
const searchInput = ref('')
const search = ref('')
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// Pagination
const currentPage = ref(1)
const pageSize = 50
const totalPages = ref(1)

// Form
const showForm = ref(false)
const editingPlayerId = ref<number | null>(null)
const playerForm = ref({
  ucid: '',
  nickname: '',
})

// User link (autocomplete)
const linkedUserId = ref<number | null>(null)
const linkedUserNickname = ref<string | null>(null)
const userSearch = ref('')
const userResults = ref<{ id: number; nickname: string }[]>([])
const userDropdownOpen = ref(false)
const userSearching = ref(false)
const userPickerRef = ref<HTMLElement | null>(null)
let userSearchTimeout: ReturnType<typeof setTimeout> | null = null

function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchInput.value = value
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    search.value = value
  }, 300)
}

async function loadPlayers() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    if (search.value) params.search = search.value

    const result = await getAdminPlayers(params as Parameters<typeof getAdminPlayers>[0])
    players.value = result.items
    total.value = result.total
    totalPages.value = Math.max(1, Math.ceil(result.total / pageSize))
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

watch(search, () => {
  currentPage.value = 1
  loadPlayers()
})

function goToPage(page: number) {
  currentPage.value = page
  loadPlayers()
}

// --- User autocomplete ---

function onUserSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  userSearch.value = value
  if (userSearchTimeout) clearTimeout(userSearchTimeout)
  if (value.trim().length < 2) {
    userResults.value = []
    userDropdownOpen.value = false
    return
  }
  userSearchTimeout = setTimeout(searchUsers, 300)
}

async function searchUsers() {
  userSearching.value = true
  try {
    const result = await getAdminUsers({ search: userSearch.value.trim(), limit: 10 })
    userResults.value = result.items.map((u) => ({ id: u.id, nickname: u.nickname }))
    userDropdownOpen.value = true
  } catch (e) {
    toast.error(e)
  } finally {
    userSearching.value = false
  }
}

function selectUser(user: { id: number; nickname: string }) {
  linkedUserId.value = user.id
  linkedUserNickname.value = user.nickname
  userSearch.value = ''
  userResults.value = []
  userDropdownOpen.value = false
}

function unlinkUser() {
  linkedUserId.value = null
  linkedUserNickname.value = null
}

function onUserPickerClickOutside(event: MouseEvent) {
  if (userPickerRef.value && !userPickerRef.value.contains(event.target as Node)) {
    userDropdownOpen.value = false
  }
}

// --- Form ---

function openNew() {
  editingPlayerId.value = null
  playerForm.value = { ucid: '', nickname: '' }
  unlinkUser()
  userSearch.value = ''
  userResults.value = []
  showForm.value = true
}

function openEdit(p: Player) {
  editingPlayerId.value = p.id
  playerForm.value = {
    ucid: p.ucid,
    nickname: p.nickname ?? '',
  }
  linkedUserId.value = p.user_id
  linkedUserNickname.value = p.user_nickname
  userSearch.value = ''
  userResults.value = []
  showForm.value = true
}

async function handleSubmit() {
  loading.value = true
  try {
    const payload = {
      ucid: playerForm.value.ucid.trim(),
      nickname: playerForm.value.nickname.trim() || null,
      user_id: linkedUserId.value,
    }
    if (editingPlayerId.value) {
      await updateAdminPlayer(editingPlayerId.value, payload)
      toast.success('Joueur modifié avec succès')
    } else {
      await createAdminPlayer(payload)
      toast.success('Joueur créé avec succès')
    }
    showForm.value = false
    await loadPlayers()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(p: Player) {
  if (!(await confirm(`Supprimer le joueur DCS "${p.nickname ?? p.ucid}" ?`))) return
  loading.value = true
  try {
    await deleteAdminPlayer(p.id)
    toast.success('Joueur supprimé avec succès')
    await loadPlayers()
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

onMounted(() => {
  document.addEventListener('mousedown', onUserPickerClickOutside)
  loadPlayers()
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onUserPickerClickOutside)
})
</script>

<template>
  <div>
    <AppBreadcrumb :show-title="false" />

    <!-- Search & Actions -->
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="relative flex-1 min-w-[200px]">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <input
          :value="searchInput"
          @input="onSearchInput"
          type="text"
          placeholder="Rechercher par pseudo, UCID ou utilisateur..."
          class="input pl-9 w-full"
        />
      </div>
      <button class="btn-primary" @click="openNew">
        <i class="fa-solid fa-plus mr-1"></i>Ajouter un joueur
      </button>
    </div>

    <!-- Player form -->
    <div v-if="showForm" class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">
        {{ editingPlayerId ? 'Modifier le joueur DCS' : 'Ajouter un joueur DCS' }}
      </h3>
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">UCID</label>
            <input v-model="playerForm.ucid" type="text" class="input font-mono" maxlength="64" required />
            <p class="text-xs text-gray-500 mt-1">Identifiant unique du joueur DCS</p>
          </div>
          <div>
            <label class="label">Pseudo</label>
            <input v-model="playerForm.nickname" type="text" class="input" maxlength="128" />
            <p class="text-xs text-gray-500 mt-1">Dernier pseudo utilisé en jeu</p>
          </div>
        </div>

        <!-- User link -->
        <div ref="userPickerRef" class="relative">
          <label class="label">Utilisateur associé</label>
          <div v-if="linkedUserNickname" class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-veaf-100 text-veaf-800">
              {{ linkedUserNickname }}
              <button type="button" class="opacity-60 hover:opacity-100" aria-label="Dissocier l'utilisateur" @click="unlinkUser">
                <i class="fa-solid fa-xmark text-xs"></i>
              </button>
            </span>
          </div>
          <template v-else>
            <input
              :value="userSearch"
              @input="onUserSearchInput"
              type="text"
              placeholder="Rechercher un utilisateur (2 caractères minimum)..."
              class="input w-full"
              autocomplete="off"
            />
            <div
              v-if="userDropdownOpen"
              class="absolute z-50 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
            >
              <div
                v-for="u in userResults"
                :key="u.id"
                class="px-3 py-1.5 text-sm text-gray-900 cursor-pointer hover:bg-gray-100"
                @click="selectUser(u)"
              >
                {{ u.nickname }}
              </div>
              <div v-if="!userResults.length" class="px-3 py-3 text-sm text-gray-500 text-center">
                {{ userSearching ? 'Recherche...' : 'Aucun résultat' }}
              </div>
            </div>
          </template>
          <p class="text-xs text-gray-500 mt-1">Compte VEAF lié à ce joueur DCS (facultatif)</p>
        </div>

        <div class="flex justify-end space-x-3">
          <button type="button" class="btn-secondary" @click="showForm = false">
            <i class="fa-solid fa-xmark mr-1"></i>Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingPlayerId ? 'Modifier' : 'Créer' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Players table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Pseudo</th>
            <th class="p-2">UCID</th>
            <th class="p-2">Utilisateur</th>
            <th class="p-2">Première connexion</th>
            <th class="p-2">Dernière connexion</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!players.length">
            <td colspan="6" class="p-4 text-center text-gray-500">Aucun joueur DCS</td>
          </tr>
          <tr v-for="p in players" :key="p.id" class="border-b hover:bg-gray-50">
            <td class="p-2 font-medium">{{ p.nickname ?? '-' }}</td>
            <td class="p-2 font-mono text-xs">{{ p.ucid }}</td>
            <td class="p-2">
              <span v-if="p.user_nickname">{{ p.user_nickname }}</span>
              <span v-else class="text-gray-500 italic">non associé</span>
            </td>
            <td class="p-2">{{ formatDate(p.join_at) }}</td>
            <td class="p-2">{{ formatDate(p.last_join_at) }}</td>
            <td class="p-2 space-x-3">
              <button class="text-veaf-600 hover:text-veaf-800 text-sm" title="Modifier" @click="openEdit(p)">
                <i class="fa-solid fa-edit"></i>
              </button>
              <button class="text-red-600 hover:text-red-800 text-sm" title="Supprimer" @click="handleDelete(p)">
                <i class="fa-solid fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between p-3 border-t">
        <span class="text-sm text-gray-600">{{ total }} joueur(s) au total</span>
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
  </div>
</template>
