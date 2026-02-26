<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getAdminPage,
  updateAdminPage,
  createAdminBlock,
  updateAdminBlock,
  deleteAdminBlock,
} from '@/api/pages'
import type { Page, PageBlock } from '@/types/api'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const { confirm } = useConfirm()
const toast = useToast()

const page = ref<Page | null>(null)
const loading = ref(false)

// Page edit
const showPageForm = ref(false)
const pageForm = ref({
  title: '',
  route: '',
  path: '',
  enabled: false,
  restriction: 0,
})

// Block edit
const showBlockForm = ref(false)
const editingBlockId = ref<number | null>(null)
const insertAtNumber = ref(1)
const blockForm = ref({
  content: '',
  number: 1,
  enabled: true,
})

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

const pageId = computed(() => Number(route.params.id))

const sortedBlocks = computed(() => {
  if (!page.value) return []
  return [...page.value.blocks].sort((a, b) => a.number - b.number)
})

async function loadPage() {
  loading.value = true
  try {
    page.value = await getAdminPage(pageId.value)
  } catch (e) {
    toast.error(e)
    router.push({ name: 'admin-pages' })
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

// --- Page edit ---

function openPageEdit() {
  if (!page.value) return
  pageForm.value = {
    title: page.value.title,
    route: page.value.route,
    path: page.value.path,
    enabled: page.value.enabled,
    restriction: page.value.restriction,
  }
  showPageForm.value = true
  showBlockForm.value = false
}

async function handlePageSubmit() {
  loading.value = true
  try {
    page.value = await updateAdminPage(pageId.value, pageForm.value)
    showPageForm.value = false
    toast.success('Page modifiée avec succès')
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

// --- Block management ---

function openNewBlock(atNumber: number) {
  editingBlockId.value = null
  insertAtNumber.value = atNumber
  blockForm.value = {
    content: '',
    number: atNumber,
    enabled: true,
  }
  showBlockForm.value = true
  showPageForm.value = false
}

function openEditBlock(block: PageBlock) {
  editingBlockId.value = block.id
  blockForm.value = {
    content: block.content,
    number: block.number,
    enabled: block.enabled,
  }
  showBlockForm.value = true
  showPageForm.value = false
}

async function handleBlockSubmit() {
  loading.value = true
  try {
    if (editingBlockId.value) {
      page.value = await updateAdminBlock(pageId.value, editingBlockId.value, blockForm.value)
      toast.success('Bloc modifié avec succès')
    } else {
      page.value = await createAdminBlock(pageId.value, blockForm.value)
      toast.success('Bloc créé avec succès')
    }
    showBlockForm.value = false
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDeleteBlock(block: PageBlock) {
  if (!(await confirm(`Supprimer le bloc n°${block.number} ?`))) return
  loading.value = true
  try {
    page.value = await deleteAdminBlock(pageId.value, block.id)
    toast.success('Bloc supprimé avec succès')
    if (editingBlockId.value === block.id) {
      showBlockForm.value = false
    }
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadPage)
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">{{ page?.title ?? 'Chargement...' }}</h1>
      <button class="btn-secondary" @click="router.push({ name: 'admin-pages' })">
        <i class="fa-solid fa-arrow-left mr-1"></i>Retour à la liste
      </button>
    </div>

    <div v-if="page">
      <!-- Page info card -->
      <div v-if="!showPageForm" class="card mb-6">
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-lg font-semibold">Propriétés de la page</h2>
          <button class="text-veaf-600 hover:text-veaf-800 text-sm" @click="openPageEdit">
            <i class="fa-solid fa-pen mr-1"></i>Modifier
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
          <div>
            <span class="text-gray-500">Titre</span>
            <p class="font-medium">{{ page.title }}</p>
          </div>
          <div>
            <span class="text-gray-500">Route</span>
            <p class="font-mono text-xs">{{ page.route }}</p>
          </div>
          <div>
            <span class="text-gray-500">Chemin (URL)</span>
            <p class="font-mono text-xs">{{ page.path }}</p>
          </div>
          <div>
            <span class="text-gray-500">Statut</span>
            <p>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :class="page.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ page.enabled ? 'Activé' : 'Désactivé' }}
              </span>
            </p>
          </div>
          <div>
            <span class="text-gray-500">Restriction</span>
            <p>{{ restrictionLabels[page.restriction] ?? '-' }}</p>
          </div>
          <div>
            <span class="text-gray-500">Dernière modification</span>
            <p>{{ formatDate(page.updated_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Page edit form -->
      <div v-if="showPageForm" class="card mb-6">
        <h2 class="text-lg font-semibold mb-4">Modifier les propriétés</h2>
        <form class="space-y-4" @submit.prevent="handlePageSubmit">
          <div>
            <label class="label">Titre</label>
            <input v-model="pageForm.title" type="text" class="input" maxlength="255" required />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Route</label>
              <input v-model="pageForm.route" type="text" class="input" maxlength="255" required />
            </div>
            <div>
              <label class="label">Chemin (URL)</label>
              <input v-model="pageForm.path" type="text" class="input" maxlength="255" required />
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
            <button type="button" class="btn-secondary" @click="showPageForm = false">
              <i class="fa-solid fa-xmark mr-1"></i>Annuler
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Blocks section -->
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-lg font-semibold">Blocs de contenu ({{ sortedBlocks.length }})</h2>
        <button class="btn-primary" @click="openNewBlock(sortedBlocks.length + 1)">
          <i class="fa-solid fa-plus mr-1"></i>Ajouter un bloc
        </button>
      </div>

      <!-- Block form -->
      <div v-if="showBlockForm" class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingBlockId ? `Modifier le bloc` : `Ajouter un bloc (position ${insertAtNumber})` }}
        </h3>
        <form class="space-y-4" @submit.prevent="handleBlockSubmit">
          <div>
            <label class="label">Contenu (Markdown)</label>
            <textarea
              v-model="blockForm.content"
              class="input font-mono text-sm"
              rows="15"
              required
            ></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Position (numéro)</label>
              <input v-model.number="blockForm.number" type="number" class="input w-32" min="1" required />
            </div>
            <div class="flex items-end">
              <label class="flex items-center space-x-2 pb-2">
                <input v-model="blockForm.enabled" type="checkbox" class="rounded" />
                <span class="text-sm">Bloc activé</span>
              </label>
            </div>
          </div>

          <div class="flex justify-end space-x-3">
            <button type="button" class="btn-secondary" @click="showBlockForm = false">
              <i class="fa-solid fa-xmark mr-1"></i>Annuler
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingBlockId ? 'Modifier' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Block list -->
      <div v-if="!sortedBlocks.length && !showBlockForm" class="card text-center py-8 text-gray-500">
        Aucun bloc de contenu. Cliquez sur "Ajouter un bloc" pour commencer.
      </div>

      <div class="space-y-4">
        <div v-for="block in sortedBlocks" :key="block.id" class="card">
          <div class="flex justify-between items-center mb-3">
            <div class="flex items-center space-x-3">
              <h3 class="font-semibold text-sm">Bloc n°{{ block.number }}</h3>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                :class="block.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ block.enabled ? 'Activé' : 'Désactivé' }}
              </span>
            </div>
            <div class="space-x-3">
              <button class="text-veaf-600 hover:text-veaf-800 text-sm" @click="openEditBlock(block)">
                <i class="fa-solid fa-pen mr-1"></i>Modifier
              </button>
              <button class="text-red-600 hover:text-red-800 text-sm" @click="handleDeleteBlock(block)">
                <i class="fa-solid fa-trash mr-1"></i>Supprimer
              </button>
            </div>
          </div>
          <div class="bg-gray-50 rounded p-3 text-sm font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">{{ block.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
