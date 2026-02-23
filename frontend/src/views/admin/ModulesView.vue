<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import {
  getModules,
  getRoles,
  getSystems,
  createModule,
  updateModule,
  uploadModuleImage,
  deleteModuleImage,
  uploadModuleImageHeader,
  deleteModuleImageHeader,
  createRole,
  updateRole,
  deleteRole,
  createSystem,
  updateSystem,
  deleteSystem,
} from '@/api/modules'
import type { Module, ModuleRole, ModuleSystem } from '@/types/module'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const { confirm } = useConfirm()
const toast = useToast()

type Tab = 'modules' | 'roles' | 'systems'

const currentTab = ref<Tab>('modules')

// Data
const modules = ref<Module[]>([])
const roles = ref<ModuleRole[]>([])
const systems = ref<ModuleSystem[]>([])
const loading = ref(false)

// --- Module form ---
const showModuleForm = ref(false)
const editingModuleId = ref<number | null>(null)
const moduleForm = ref({
  type: 2,
  name: '',
  long_name: '',
  code: '',
  landing_page: false,
  landing_page_number: null as number | null,
  period: null as number | null,
  role_ids: [] as number[],
  system_ids: [] as number[],
})

const imageUploading = ref(false)
const currentImageUuid = ref<string | null>(null)
const currentImageHeaderUuid = ref<string | null>(null)

const moduleTypes = [
  { value: 0, label: 'Aucun' },
  { value: 1, label: 'Carte' },
  { value: 2, label: 'Avion' },
  { value: 3, label: 'Hélicoptère' },
  { value: 4, label: 'Spécial' },
]

const modulePeriods = [
  { value: 0, label: '(aucune)' },
  { value: 1, label: 'WW2' },
  { value: 2, label: 'COLD WAR' },
  { value: 3, label: 'MODERN' },
]

function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

const codeManuallyEdited = ref(false)

watch(
  () => moduleForm.value.name,
  (name) => {
    if (!editingModuleId.value && !codeManuallyEdited.value) {
      moduleForm.value.code = slugify(name)
    }
  },
)

function onCodeInput() {
  codeManuallyEdited.value = true
}

function openNewModule() {
  codeManuallyEdited.value = false
  editingModuleId.value = null
  currentImageUuid.value = null
  currentImageHeaderUuid.value = null
  moduleForm.value = {
    type: 2,
    name: '',
    long_name: '',
    code: '',
    landing_page: false,
    landing_page_number: null,
    period: null,
    role_ids: [],
    system_ids: [],
  }
  showModuleForm.value = true
}

function openEditModule(m: Module) {
  editingModuleId.value = m.id
  currentImageUuid.value = m.image_uuid
  currentImageHeaderUuid.value = m.image_header_uuid
  moduleForm.value = {
    type: m.type,
    name: m.name,
    long_name: m.long_name,
    code: m.code,
    landing_page: m.landing_page,
    landing_page_number: m.landing_page_number,
    period: m.period,
    role_ids: m.roles.map((r) => r.id),
    system_ids: m.systems.map((s) => s.id),
  }
  showModuleForm.value = true
}

async function handleModuleSubmit() {
  loading.value = true
  try {
    if (editingModuleId.value) {
      await updateModule(editingModuleId.value, moduleForm.value)
      toast.success('Module modifié avec succès')
    } else {
      await createModule(moduleForm.value)
      toast.success('Module créé avec succès')
    }
    showModuleForm.value = false
    modules.value = await getModules()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

// --- Module image handlers ---

async function handleImageUpload(event: Event, type: 'image' | 'image-header') {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !editingModuleId.value) return

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!allowedTypes.includes(file.type)) {
    toast.error(new Error('Format accepté : uniquement les images jpg et png'))
    input.value = ''
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    toast.error(new Error('La taille du fichier ne doit pas dépasser 20 Mo'))
    input.value = ''
    return
  }

  imageUploading.value = true
  try {
    const uploadFn = type === 'image' ? uploadModuleImage : uploadModuleImageHeader
    const updated = await uploadFn(editingModuleId.value, file)
    currentImageUuid.value = updated.image_uuid
    currentImageHeaderUuid.value = updated.image_header_uuid
    modules.value = await getModules()
    toast.success(type === 'image' ? 'Image uploadée avec succès' : 'Image header uploadée avec succès')
  } catch (e) {
    toast.error(e)
  } finally {
    imageUploading.value = false
    input.value = ''
  }
}

async function handleImageDelete(type: 'image' | 'image-header') {
  if (!editingModuleId.value) return

  const label = type === 'image' ? "l'image" : "l'image header"
  if (!(await confirm(`Supprimer ${label} ?`))) return

  imageUploading.value = true
  try {
    const deleteFn = type === 'image' ? deleteModuleImage : deleteModuleImageHeader
    const updated = await deleteFn(editingModuleId.value)
    currentImageUuid.value = updated.image_uuid
    currentImageHeaderUuid.value = updated.image_header_uuid
    modules.value = await getModules()
    toast.success(type === 'image' ? 'Image supprimée avec succès' : 'Image header supprimée avec succès')
  } catch (e) {
    toast.error(e)
  } finally {
    imageUploading.value = false
  }
}

// --- Role form ---
const showRoleForm = ref(false)
const editingRoleId = ref<number | null>(null)
const roleForm = ref({ name: '', code: '', position: 0 })

function openNewRole() {
  editingRoleId.value = null
  roleForm.value = { name: '', code: '', position: 0 }
  showRoleForm.value = true
}

function openEditRole(r: ModuleRole) {
  editingRoleId.value = r.id
  roleForm.value = { name: r.name, code: r.code, position: r.position }
  showRoleForm.value = true
}

async function handleRoleSubmit() {
  loading.value = true
  try {
    if (editingRoleId.value) {
      await updateRole(editingRoleId.value, roleForm.value)
      toast.success('Rôle modifié avec succès')
    } else {
      await createRole(roleForm.value)
      toast.success('Rôle créé avec succès')
    }
    showRoleForm.value = false
    roles.value = await getRoles()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDeleteRole(r: ModuleRole) {
  if (!(await confirm(`Supprimer le rôle "${r.name}" ?`))) return
  loading.value = true
  try {
    await deleteRole(r.id)
    toast.success('Rôle supprimé avec succès')
    roles.value = await getRoles()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

// --- System form ---
const showSystemForm = ref(false)
const editingSystemId = ref<number | null>(null)
const systemForm = ref({ code: '', name: '', position: 0 })

function openNewSystem() {
  editingSystemId.value = null
  systemForm.value = { code: '', name: '', position: 0 }
  showSystemForm.value = true
}

function openEditSystem(s: ModuleSystem) {
  editingSystemId.value = s.id
  systemForm.value = { code: s.code, name: s.name, position: s.position }
  showSystemForm.value = true
}

async function handleSystemSubmit() {
  loading.value = true
  try {
    if (editingSystemId.value) {
      await updateSystem(editingSystemId.value, systemForm.value)
      toast.success('Système modifié avec succès')
    } else {
      await createSystem(systemForm.value)
      toast.success('Système créé avec succès')
    }
    showSystemForm.value = false
    systems.value = await getSystems()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDeleteSystem(s: ModuleSystem) {
  if (!(await confirm(`Supprimer le système "${s.name}" ?`))) return
  loading.value = true
  try {
    await deleteSystem(s.id)
    toast.success('Système supprimé avec succès')
    systems.value = await getSystems()
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

// --- Load data ---
async function loadAll() {
  loading.value = true
  try {
    const [m, r, s] = await Promise.all([getModules(), getRoles(), getSystems()])
    modules.value = m
    roles.value = r
    systems.value = s
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Gestion des modules</h1>

    <!-- Tabs -->
    <div class="flex space-x-1 mb-6 border-b border-gray-200">
      <button
        v-for="tab in [
          { key: 'modules' as Tab, label: 'Modules' },
          { key: 'roles' as Tab, label: 'Rôles' },
          { key: 'systems' as Tab, label: 'Systèmes' },
        ]"
        :key="tab.key"
        class="px-4 py-2 text-sm font-medium -mb-px"
        :class="
          currentTab === tab.key
            ? 'border-b-2 border-veaf-600 text-veaf-600'
            : 'text-gray-500 hover:text-gray-700'
        "
        @click="currentTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- ==================== MODULES TAB ==================== -->
    <div v-if="currentTab === 'modules'">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Modules</h2>
        <button class="btn-primary" @click="openNewModule"><i class="fa-solid fa-plus mr-1"></i>Ajouter un module</button>
      </div>

      <!-- Module form -->
      <div v-if="showModuleForm" class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingModuleId ? 'Modifier le module' : 'Ajouter un module' }}
        </h3>
        <form class="space-y-4" @submit.prevent="handleModuleSubmit">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Type</label>
              <select v-model.number="moduleForm.type" class="input">
                <option v-for="t in moduleTypes" :key="t.value" :value="t.value">
                  {{ t.label }}
                </option>
              </select>
            </div>
            <div>
              <label class="label">Période</label>
              <select v-model="moduleForm.period" class="input">
                <option :value="null">(aucune)</option>
                <option v-for="p in modulePeriods" :key="p.value" :value="p.value">
                  {{ p.label }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Nom court (max 8 car.)</label>
              <input
                v-model="moduleForm.name"
                type="text"
                class="input"
                maxlength="8"
                required
              />
            </div>
            <div>
              <label class="label">Code (max 16 car.)</label>
              <input
                v-model="moduleForm.code"
                type="text"
                class="input"
                maxlength="16"
                required
                @input="onCodeInput"
              />
            </div>
          </div>

          <div>
            <label class="label">Nom complet</label>
            <input
              v-model="moduleForm.long_name"
              type="text"
              class="input"
              maxlength="64"
              required
            />
          </div>

          <div class="flex items-center space-x-4">
            <label class="flex items-center space-x-2">
              <input v-model="moduleForm.landing_page" type="checkbox" class="rounded" />
              <span class="text-sm">Landing page</span>
            </label>
            <div v-if="moduleForm.landing_page">
              <label class="label">Numéro</label>
              <input
                v-model.number="moduleForm.landing_page_number"
                type="number"
                class="input w-24"
              />
            </div>
          </div>

          <!-- Roles checkboxes -->
          <div v-if="roles.length">
            <label class="label">Rôles</label>
            <div class="flex flex-wrap gap-3">
              <label
                v-for="role in roles"
                :key="role.id"
                class="flex items-center space-x-2"
              >
                <input
                  v-model="moduleForm.role_ids"
                  type="checkbox"
                  :value="role.id"
                  class="rounded"
                />
                <span class="text-sm">{{ role.name }}</span>
              </label>
            </div>
          </div>

          <!-- Systems checkboxes -->
          <div v-if="systems.length">
            <label class="label">Systèmes</label>
            <div class="flex flex-wrap gap-3">
              <label
                v-for="sys in systems"
                :key="sys.id"
                class="flex items-center space-x-2"
              >
                <input
                  v-model="moduleForm.system_ids"
                  type="checkbox"
                  :value="sys.id"
                  class="rounded"
                />
                <span class="text-sm">{{ sys.name }}</span>
              </label>
            </div>
          </div>

          <!-- Images (only when editing an existing module) -->
          <div v-if="editingModuleId" class="space-y-4 border-t pt-4">
            <h4 class="text-sm font-semibold text-gray-700">Images</h4>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Image (16:9) -->
              <div>
                <label class="label">Image (format 16/9)</label>
                <div v-if="currentImageUuid" class="mb-2">
                  <img
                    :src="`/api/files/${currentImageUuid}`"
                    alt="Image du module"
                    class="max-w-full max-h-40 rounded border border-gray-300"
                  />
                  <button
                    type="button"
                    class="mt-1 text-red-600 hover:text-red-800 text-sm"
                    :disabled="imageUploading"
                    @click="handleImageDelete('image')"
                  >
                    <i class="fa-solid fa-trash mr-1"></i>Supprimer
                  </button>
                </div>
                <input
                  type="file"
                  accept="image/jpeg,image/png"
                  class="input"
                  :disabled="imageUploading"
                  @change="handleImageUpload($event, 'image')"
                />
                <p class="text-xs text-gray-500 mt-1">JPG ou PNG, max 20 Mo</p>
              </div>

              <!-- Image Header (5:1) -->
              <div>
                <label class="label">Image header (format 5:1)</label>
                <div v-if="currentImageHeaderUuid" class="mb-2">
                  <img
                    :src="`/api/files/${currentImageHeaderUuid}`"
                    alt="Image header du module"
                    class="max-w-full max-h-40 rounded border border-gray-300"
                  />
                  <button
                    type="button"
                    class="mt-1 text-red-600 hover:text-red-800 text-sm"
                    :disabled="imageUploading"
                    @click="handleImageDelete('image-header')"
                  >
                    <i class="fa-solid fa-trash mr-1"></i>Supprimer
                  </button>
                </div>
                <input
                  type="file"
                  accept="image/jpeg,image/png"
                  class="input"
                  :disabled="imageUploading"
                  @change="handleImageUpload($event, 'image-header')"
                />
                <p class="text-xs text-gray-500 mt-1">JPG ou PNG, max 20 Mo, ratio 5:1 conseillé</p>
              </div>
            </div>
          </div>

          <div class="flex justify-end space-x-3">
            <button type="button" class="btn-secondary" @click="showModuleForm = false">
              <i class="fa-solid fa-xmark mr-1"></i>Annuler
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingModuleId ? 'Modifier' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Module list -->
      <div class="card overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b text-left">
              <th class="p-2">Type</th>
              <th class="p-2">Image</th>
              <th class="p-2">Code</th>
              <th class="p-2">Nom</th>
              <th class="p-2">Nom complet</th>
              <th class="p-2">Période</th>
              <th class="p-2">Rôles</th>
              <th class="p-2">Systèmes</th>
              <th class="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!modules.length">
              <td colspan="9" class="p-4 text-center text-gray-500">Aucun module</td>
            </tr>
            <tr
              v-for="m in modules"
              :key="m.id"
              class="border-b hover:bg-gray-50"
            >
              <td class="p-2">{{ m.type_as_string }}</td>
              <td class="p-2">
                <img
                  v-if="m.image_uuid"
                  :src="`/api/files/${m.image_uuid}`"
                  :alt="m.code"
                  class="w-10 h-10 object-cover rounded"
                />
                <span v-else class="text-gray-400 text-xs">-</span>
              </td>
              <td class="p-2 font-mono">{{ m.code }}</td>
              <td class="p-2">{{ m.name }}</td>
              <td class="p-2">{{ m.long_name }}</td>
              <td class="p-2">{{ m.period_as_string }}</td>
              <td class="p-2">{{ m.roles.map((r) => r.name).join(', ') }}</td>
              <td class="p-2">{{ m.systems.map((s) => s.name).join(', ') }}</td>
              <td class="p-2">
                <button
                  class="text-veaf-600 hover:text-veaf-800 text-sm"
                  @click="openEditModule(m)"
                >
                  <i class="fa-solid fa-pen mr-1"></i>Modifier
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== ROLES TAB ==================== -->
    <div v-if="currentTab === 'roles'">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Rôles</h2>
        <button class="btn-primary" @click="openNewRole"><i class="fa-solid fa-plus mr-1"></i>Ajouter un rôle</button>
      </div>

      <!-- Role form -->
      <div v-if="showRoleForm" class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingRoleId ? 'Modifier le rôle' : 'Ajouter un rôle' }}
        </h3>
        <form class="space-y-4" @submit.prevent="handleRoleSubmit">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="label">Code</label>
              <input v-model="roleForm.code" type="text" class="input" required />
            </div>
            <div>
              <label class="label">Nom</label>
              <input v-model="roleForm.name" type="text" class="input" required />
            </div>
            <div>
              <label class="label">Position</label>
              <input v-model.number="roleForm.position" type="number" class="input" required />
            </div>
          </div>
          <div class="flex justify-end space-x-3">
            <button type="button" class="btn-secondary" @click="showRoleForm = false">
              <i class="fa-solid fa-xmark mr-1"></i>Annuler
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingRoleId ? 'Modifier' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Role list -->
      <div class="card overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b text-left">
              <th class="p-2">Code</th>
              <th class="p-2">Nom</th>
              <th class="p-2">Position</th>
              <th class="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!roles.length">
              <td colspan="4" class="p-4 text-center text-gray-500">Aucun rôle</td>
            </tr>
            <tr v-for="r in roles" :key="r.id" class="border-b hover:bg-gray-50">
              <td class="p-2 font-mono">{{ r.code }}</td>
              <td class="p-2">{{ r.name }}</td>
              <td class="p-2">{{ r.position }}</td>
              <td class="p-2 space-x-3">
                <button
                  class="text-veaf-600 hover:text-veaf-800 text-sm"
                  @click="openEditRole(r)"
                >
                  <i class="fa-solid fa-pen mr-1"></i>Modifier
                </button>
                <button
                  class="text-red-600 hover:text-red-800 text-sm"
                  @click="handleDeleteRole(r)"
                >
                  <i class="fa-solid fa-trash mr-1"></i>Supprimer
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== SYSTEMS TAB ==================== -->
    <div v-if="currentTab === 'systems'">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">Systèmes</h2>
        <button class="btn-primary" @click="openNewSystem"><i class="fa-solid fa-plus mr-1"></i>Ajouter un système</button>
      </div>

      <!-- System form -->
      <div v-if="showSystemForm" class="card mb-6">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingSystemId ? 'Modifier le système' : 'Ajouter un système' }}
        </h3>
        <form class="space-y-4" @submit.prevent="handleSystemSubmit">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="label">Code</label>
              <input v-model="systemForm.code" type="text" class="input" required />
            </div>
            <div>
              <label class="label">Nom</label>
              <input v-model="systemForm.name" type="text" class="input" required />
            </div>
            <div>
              <label class="label">Position</label>
              <input v-model.number="systemForm.position" type="number" class="input" required />
            </div>
          </div>
          <div class="flex justify-end space-x-3">
            <button type="button" class="btn-secondary" @click="showSystemForm = false">
              <i class="fa-solid fa-xmark mr-1"></i>Annuler
            </button>
            <button type="submit" class="btn-primary" :disabled="loading">
              <i class="fa-solid fa-floppy-disk mr-1"></i>{{ loading ? 'Enregistrement...' : editingSystemId ? 'Modifier' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>

      <!-- System list -->
      <div class="card overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b text-left">
              <th class="p-2">Code</th>
              <th class="p-2">Nom</th>
              <th class="p-2">Position</th>
              <th class="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!systems.length">
              <td colspan="4" class="p-4 text-center text-gray-500">Aucun système</td>
            </tr>
            <tr v-for="s in systems" :key="s.id" class="border-b hover:bg-gray-50">
              <td class="p-2 font-mono">{{ s.code }}</td>
              <td class="p-2">{{ s.name }}</td>
              <td class="p-2">{{ s.position }}</td>
              <td class="p-2 space-x-3">
                <button
                  class="text-veaf-600 hover:text-veaf-800 text-sm"
                  @click="openEditSystem(s)"
                >
                  <i class="fa-solid fa-pen mr-1"></i>Modifier
                </button>
                <button
                  class="text-red-600 hover:text-red-800 text-sm"
                  @click="handleDeleteSystem(s)"
                >
                  <i class="fa-solid fa-trash mr-1"></i>Supprimer
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
