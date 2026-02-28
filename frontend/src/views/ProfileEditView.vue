<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { updateMe, updateMyModuleLevel, updateMyModuleActive } from '@/api/users'
import { getModules } from '@/api/modules'
import { useToast } from '@/composables/useToast'
import ProfileEditModal from '@/components/ui/ProfileEditModal.vue'
import type { Module } from '@/types/module'
import type { UserUpdate } from '@/types/user'
import { TYPES_WITH_LEVEL, MODULE_TYPE_LABELS_PLURAL, MODULE_TYPE_ORDER, MODULE_TYPE_AIRCRAFT } from '@/constants/modules'

const auth = useAuthStore()
const toast = useToast()

const showEditModal = ref(false)
const saving = ref(false)

const allModules = ref<Module[]>([])
const loadingModules = ref(true)

// Local reactive map of user's modules: module_id → { active, level }
const myModulesMap = ref(new Map<number, { active: boolean; level: number }>())

// Brief check mark feedback per module row
const savedFeedback = ref(new Set<number>())

const PERIOD_LABELS: Record<number, string> = {
  1: 'WW2',
  2: 'COLD WAR',
  3: 'MODERN',
}

interface PeriodGroup {
  period: number | null
  label: string
  modules: Module[]
}

interface TypeGroup {
  type: number
  label: string
  periods: PeriodGroup[]
}

const groupedModules = computed<TypeGroup[]>(() => {
  const typeOrder = MODULE_TYPE_ORDER
  const groups: TypeGroup[] = []

  for (const type of typeOrder) {
    const modulesOfType = allModules.value
      .filter((m) => m.type === type)
      .sort((a, b) => {
        // For aircraft: sort by period desc, then name asc
        if (type === MODULE_TYPE_AIRCRAFT) {
          const pa = a.period ?? 0
          const pb = b.period ?? 0
          if (pb !== pa) return pb - pa
        }
        return a.long_name.localeCompare(b.long_name)
      })

    if (modulesOfType.length === 0) continue

    if (type === MODULE_TYPE_AIRCRAFT) {
      // Sub-group aircraft by period
      const periodMap = new Map<number, Module[]>()
      for (const m of modulesOfType) {
        const p = m.period ?? 0
        if (!periodMap.has(p)) periodMap.set(p, [])
        periodMap.get(p)!.push(m)
      }
      const periods = [...periodMap.entries()]
        .sort(([a], [b]) => b - a)
        .map(([period, modules]) => ({
          period,
          label: PERIOD_LABELS[period] || '',
          modules,
        }))
      groups.push({ type, label: MODULE_TYPE_LABELS_PLURAL[type], periods })
    } else {
      groups.push({
        type,
        label: MODULE_TYPE_LABELS_PLURAL[type],
        periods: [{ period: null, label: '', modules: modulesOfType }],
      })
    }
  }
  return groups
})

onMounted(async () => {
  await auth.fetchUser()
  if (auth.user) {
    for (const um of auth.user.modules) {
      myModulesMap.value.set(um.module_id, { active: um.active, level: um.level })
    }
  }
  try {
    allModules.value = await getModules()
  } catch (e) {
    toast.error(e)
  } finally {
    loadingModules.value = false
  }
})

function getMyModule(moduleId: number) {
  return myModulesMap.value.get(moduleId) ?? null
}

function showSavedFeedback(moduleId: number) {
  savedFeedback.value.add(moduleId)
  setTimeout(() => {
    savedFeedback.value.delete(moduleId)
  }, 1500)
}

async function handleLevelChange(moduleId: number, level: number) {
  try {
    const result = await updateMyModuleLevel(moduleId, level)
    if (result.deleted) {
      myModulesMap.value.delete(moduleId)
    } else {
      myModulesMap.value.set(moduleId, { active: result.active, level: result.level })
    }
    showSavedFeedback(moduleId)
  } catch (e) {
    toast.error(e)
  }
}

async function handleActiveChange(moduleId: number, active: boolean) {
  try {
    const result = await updateMyModuleActive(moduleId, active)
    myModulesMap.value.set(moduleId, { active: result.active, level: result.level })
    showSavedFeedback(moduleId)
  } catch (e) {
    toast.error(e)
  }
}

async function handleNotOwned(moduleId: number) {
  await handleLevelChange(moduleId, 0)
}

async function handleProfileSave(data: UserUpdate) {
  saving.value = true
  try {
    await updateMe(data)
    await auth.fetchUser()
    showEditModal.value = false
    toast.success('Profil mis à jour')
  } catch (e) {
    toast.error(e)
  } finally {
    saving.value = false
  }
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

function activityClass(moduleId: number, button: 'active' | 'hangar' | 'notowned'): string {
  const myMod = getMyModule(moduleId)
  const owned = myMod !== null
  const active = myMod?.active ?? false

  if (button === 'active' && owned && active) return 'bg-green-600 text-white border-green-600'
  if (button === 'hangar' && owned && !active) return 'bg-yellow-500 text-white border-yellow-500'
  if (button === 'notowned' && !owned) return 'bg-red-600 text-white border-red-600'
  return 'bg-white text-gray-500 border-gray-300 hover:bg-gray-50'
}

function levelClass(moduleId: number, level: number): string {
  const myMod = getMyModule(moduleId)
  const currentLevel = myMod?.level ?? 0

  if (currentLevel === level) {
    if (level === 1) return 'bg-yellow-500 text-white border-yellow-500'
    if (level === 2) return 'bg-green-600 text-white border-green-600'
    if (level === 3) return 'bg-veaf-600 text-white border-veaf-600'
  }
  return 'bg-white text-gray-500 border-gray-300 hover:bg-gray-50'
}

function isLevelDisabled(moduleType: number, level: number): boolean {
  if (!TYPES_WITH_LEVEL.includes(moduleType)) return true
  if (level === 3 && !auth.isMember) return true
  return false
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Mon profil</h1>
      <RouterLink
        v-if="auth.user"
        :to="`/user/${auth.user.nickname}`"
        class="btn-secondary text-sm"
      >
        <i class="fa-solid fa-eye mr-1"></i>Voir mon profil public
      </RouterLink>
    </div>

    <div v-if="!auth.user" class="text-center py-12 text-gray-500">Chargement...</div>

    <template v-else>
      <!-- Profile info card -->
      <div class="card mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">Informations</h2>
          <button class="btn-secondary text-sm" @click="showEditModal = true">
            <i class="fa-solid fa-edit mr-1"></i>Modifier
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div><span class="font-medium text-gray-500">Pseudo :</span> {{ auth.user.nickname }}</div>
          <div><span class="font-medium text-gray-500">Email :</span> {{ auth.user.email }}</div>
          <div>
            <span class="font-medium text-gray-500">Statut :</span>
            <span class="capitalize ml-1">{{ auth.user.status_as_string }}</span>
          </div>
          <div><span class="font-medium text-gray-500">Inscrit le :</span> {{ formatDate(auth.user.created_at) }}</div>
          <div><span class="font-medium text-gray-500">Discord :</span> {{ auth.user.discord || '-' }}</div>
          <div><span class="font-medium text-gray-500">Forum :</span> {{ auth.user.forum || '-' }}</div>
        </div>

        <!-- Simulators -->
        <div class="mt-4 pt-4 border-t border-gray-200 text-sm">
          <h3 class="font-semibold mb-2">Mes simulateurs</h3>
          <div class="space-y-1">
            <p>
              <i
                :class="auth.user.sim_dcs ? 'fa-solid fa-square-check text-green-600' : 'fa-regular fa-square text-gray-400'"
                class="mr-2"
              ></i>
              Digital Combat Simulator (DCS World)
            </p>
            <p>
              <i
                :class="auth.user.sim_bms ? 'fa-solid fa-square-check text-green-600' : 'fa-regular fa-square text-gray-400'"
                class="mr-2"
              ></i>
              Falcon 4 - BMS
            </p>
          </div>
        </div>
      </div>

      <!-- Modules section -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Mes modules</h2>

        <!-- Legend -->
        <div class="bg-gray-50 rounded-lg p-4 mb-6 text-sm text-gray-700">
          <p class="font-semibold mb-2">Aide :</p>
          <p class="mb-3">
            Indiquez pour chaque module si vous le possédez et votre niveau de compétence.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="font-medium mb-1">Mon activité du moment :</p>
              <ul class="space-y-1 ml-1">
                <li><i class="fa-solid fa-plane text-green-600 mr-2 w-4 text-center"></i><strong>Je vole dessus</strong> : module actif</li>
                <li><i class="fa-solid fa-warehouse text-yellow-500 mr-2 w-4 text-center"></i><strong>Au hangar</strong> : possédé mais inactif</li>
                <li><i class="fa-solid fa-circle-xmark text-red-500 mr-2 w-4 text-center"></i><strong>Pas le module</strong> : non possédé</li>
              </ul>
            </div>
            <div>
              <p class="font-medium mb-1">Mon niveau :</p>
              <ul class="space-y-1 ml-1">
                <li><i class="fa-solid fa-book-open-reader text-yellow-500 mr-2 w-4 text-center"></i><strong>Débutant</strong></li>
                <li><i class="fa-solid fa-shield-halved text-green-600 mr-2 w-4 text-center"></i><strong>Mission</strong></li>
                <li><i class="fa-solid fa-user-tie text-veaf-600 mr-2 w-4 text-center"></i><strong>Instructeur</strong> (membres uniquement)</li>
              </ul>
            </div>
          </div>
        </div>

        <div v-if="loadingModules" class="text-center py-8 text-gray-500">
          Chargement des modules...
        </div>

        <!-- Module groups -->
        <div v-else>
          <div v-for="group in groupedModules" :key="group.type" class="mb-6 last:mb-0">
            <h3 class="text-md font-semibold border-b border-gray-300 pb-2 mb-3">
              {{ group.label }}
            </h3>

            <template v-for="periodGroup in group.periods" :key="periodGroup.period ?? 'none'">
              <div
                v-if="periodGroup.label"
                class="text-xs font-bold text-gray-500 uppercase tracking-wide mt-3 mb-2 px-2"
              >
                {{ periodGroup.label }}
              </div>

              <div
                v-for="mod in periodGroup.modules"
                :key="mod.id"
                class="flex items-center justify-between py-2 px-2 border-b border-gray-100 hover:bg-gray-50 text-sm"
              >
                <span class="flex-1 min-w-0 truncate mr-3">{{ mod.long_name }}</span>

                <div class="flex items-center gap-3 flex-shrink-0">
                  <!-- Saved feedback -->
                  <Transition
                    enter-active-class="transition duration-200 ease-out"
                    enter-from-class="opacity-0 scale-75"
                    enter-to-class="opacity-100 scale-100"
                    leave-active-class="transition duration-300 ease-in"
                    leave-from-class="opacity-100"
                    leave-to-class="opacity-0"
                  >
                    <i
                      v-if="savedFeedback.has(mod.id)"
                      class="fa-solid fa-circle-check text-green-500 text-sm"
                    ></i>
                  </Transition>

                  <!-- Activity buttons -->
                  <div class="inline-flex rounded-md shadow-sm">
                    <button
                      :class="activityClass(mod.id, 'active')"
                      class="px-2 py-1.5 text-xs rounded-l-md border transition-colors"
                      title="Je vole dessus"
                      @click="handleActiveChange(mod.id, true)"
                    >
                      <i class="fa-solid fa-plane"></i>
                    </button>
                    <button
                      :class="activityClass(mod.id, 'hangar')"
                      class="px-2 py-1.5 text-xs border-t border-b transition-colors"
                      title="Au hangar"
                      @click="handleActiveChange(mod.id, false)"
                    >
                      <i class="fa-solid fa-warehouse"></i>
                    </button>
                    <button
                      :class="activityClass(mod.id, 'notowned')"
                      class="px-2 py-1.5 text-xs rounded-r-md border transition-colors"
                      title="Je ne l'ai pas"
                      @click="handleNotOwned(mod.id)"
                    >
                      <i class="fa-solid fa-circle-xmark"></i>
                    </button>
                  </div>

                  <!-- Level buttons -->
                  <div class="inline-flex rounded-md shadow-sm">
                    <button
                      :class="levelClass(mod.id, 1)"
                      :disabled="isLevelDisabled(mod.type, 1)"
                      class="px-2 py-1.5 text-xs rounded-l-md border transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Débutant"
                      @click="handleLevelChange(mod.id, 1)"
                    >
                      <i class="fa-solid fa-book-open-reader"></i>
                    </button>
                    <button
                      :class="levelClass(mod.id, 2)"
                      :disabled="isLevelDisabled(mod.type, 2)"
                      class="px-2 py-1.5 text-xs border-t border-b transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Mission"
                      @click="handleLevelChange(mod.id, 2)"
                    >
                      <i class="fa-solid fa-shield-halved"></i>
                    </button>
                    <button
                      :class="levelClass(mod.id, 3)"
                      :disabled="isLevelDisabled(mod.type, 3)"
                      class="px-2 py-1.5 text-xs rounded-r-md border transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Instructeur"
                      @click="handleLevelChange(mod.id, 3)"
                    >
                      <i class="fa-solid fa-user-tie"></i>
                    </button>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </template>

    <!-- Profile Edit Modal -->
    <ProfileEditModal
      v-if="auth.user"
      :visible="showEditModal"
      :initial-data="{
        discord: auth.user.discord || '',
        forum: auth.user.forum || '',
        sim_dcs: auth.user.sim_dcs,
        sim_bms: auth.user.sim_bms,
      }"
      @save="handleProfileSave"
      @close="showEditModal = false"
    />
  </div>
</template>
