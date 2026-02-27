<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getAdminServers, createAdminServer, updateAdminServer, deleteAdminServer } from '@/api/servers'
import AdminBreadcrumb from '@/components/admin/AdminBreadcrumb.vue'
import type { Server } from '@/types/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const { confirm } = useConfirm()
const toast = useToast()

// Data
const servers = ref<Server[]>([])
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
const editingServerId = ref<number | null>(null)
const codeManuallyEdited = ref(false)
const serverForm = ref({
  name: '',
  code: '',
})

function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function onNameInput() {
  if (!codeManuallyEdited.value) {
    serverForm.value.code = slugify(serverForm.value.name)
  }
}

function onCodeInput() {
  codeManuallyEdited.value = true
}

function onSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchInput.value = value
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    search.value = value
  }, 300)
}

async function loadServers() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    }
    if (search.value) params.search = search.value

    const result = await getAdminServers(params as Parameters<typeof getAdminServers>[0])
    servers.value = result.items
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
  loadServers()
})

function goToPage(page: number) {
  currentPage.value = page
  loadServers()
}

function openNew() {
  editingServerId.value = null
  codeManuallyEdited.value = false
  serverForm.value = { name: '', code: '' }
  showForm.value = true
}

function openEdit(s: Server) {
  editingServerId.value = s.id
  codeManuallyEdited.value = true
  serverForm.value = {
    name: s.name,
    code: s.code,
  }
  showForm.value = true
}

async function handleSubmit() {
  loading.value = true
  try {
    if (editingServerId.value) {
      await updateAdminServer(editingServerId.value, serverForm.value)
      toast.success('Serveur modifié avec succès')
    } else {
      await createAdminServer(serverForm.value)
      toast.success('Serveur créé avec succès')
    }
    showForm.value = false
    await loadServers()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(s: Server) {
  if (!(await confirm(`Supprimer le serveur "${s.name}" ?`))) return
  loading.value = true
  try {
    await deleteAdminServer(s.id)
    toast.success('Serveur supprimé avec succès')
    await loadServers()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadServers)
</script>

<template>
  <div>
    <AdminBreadcrumb />

    <!-- Search & Actions -->
    <div class="flex flex-wrap gap-4 mb-4">
      <div class="relative flex-1 min-w-[200px]">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
        <input
          :value="searchInput"
          @input="onSearchInput"
          type="text"
          placeholder="Rechercher par nom ou code..."
          class="input pl-9 w-full"
        />
      </div>
      <button class="btn-primary" @click="openNew">
        <i class="fa-solid fa-plus mr-1"></i>Ajouter un serveur
      </button>
    </div>

    <!-- Server form -->
    <div v-if="showForm" class="card mb-6">
      <h3 class="text-lg font-semibold mb-4">
        {{ editingServerId ? 'Modifier le serveur' : 'Ajouter un serveur' }}
      </h3>
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Nom</label>
            <input v-model="serverForm.name" @input="onNameInput" type="text" class="input" maxlength="64" required />
            <p class="text-xs text-gray-500 mt-1">Nom d'affichage du serveur</p>
          </div>
          <div>
            <label class="label">Code</label>
            <input v-model="serverForm.code" @input="onCodeInput" type="text" class="input" maxlength="64" required />
            <p class="text-xs text-gray-500 mt-1">Identifiant technique (auto-généré depuis le nom)</p>
          </div>
        </div>

        <div class="flex justify-end space-x-3">
          <button type="button" class="btn-secondary" @click="showForm = false">
            <i class="fa-solid fa-xmark mr-1"></i>Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingServerId ? 'Modifier' : 'Créer' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Servers table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="p-2">Nom</th>
            <th class="p-2">Code</th>
            <th class="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!servers.length">
            <td colspan="3" class="p-4 text-center text-gray-500">Aucun serveur</td>
          </tr>
          <tr v-for="s in servers" :key="s.id" class="border-b hover:bg-gray-50">
            <td class="p-2 font-medium">{{ s.name }}</td>
            <td class="p-2 font-mono text-xs">{{ s.code }}</td>
            <td class="p-2 space-x-3">
              <button class="text-veaf-600 hover:text-veaf-800 text-sm" @click="openEdit(s)">
                <i class="fa-solid fa-edit mr-1"></i>Modifier
              </button>
              <button class="text-red-600 hover:text-red-800 text-sm" @click="handleDelete(s)">
                <i class="fa-solid fa-trash mr-1"></i>Supprimer
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4">
      <span class="text-sm text-gray-600">{{ total }} serveur(s) au total</span>
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
