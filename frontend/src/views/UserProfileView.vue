<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getUser } from '@/api/users'
import { addRecruitmentEvent, getRecruitmentHistory, TYPE_PRESENTATION, TYPE_ACTIVITY } from '@/api/recruitment'
import type { RecruitmentEvent } from '@/api/recruitment'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import AddActivityModal from '@/components/recruitment/AddActivityModal.vue'
import type { UserProfile } from '@/types/user'
import type { UserModule } from '@/types/user'
import { TYPES_WITH_LEVEL, MODULE_TYPE_AIRCRAFT, MODULE_TYPE_ORDER } from '@/constants/modules'

const CADET_MIN_FLIGHTS = 5

const route = useRoute()
const auth = useAuthStore()
const { confirm } = useConfirm()
const user = ref<UserProfile | null>(null)
const loading = ref(true)
const showActivityModal = ref(false)
const showHistoryModal = ref(false)
const historyEvents = ref<RecruitmentEvent[]>([])
const historyLoading = ref(false)
const actionLoading = ref(false)

interface PeriodGroup {
  period: number | null
  label: string
  modules: UserModule[]
}

interface TypeGroup {
  type: number
  label: string
  count: number
  periods: PeriodGroup[]
}

const isOwnProfile = computed(() => {
  return auth.user && user.value && auth.user.id === user.value.id
})

const showCadetSection = computed(() => {
  return user.value && user.value.status === 1 && user.value.need_presentation != null && auth.isMember
})

async function markPresentation() {
  if (!user.value) return
  const ok = await confirm(
    `J'indique avoir présenté au cadet ${user.value.nickname} le fonctionnement de l'association, sans avoir oublié de préciser quelles sont nos valeurs et comment se déroule la période d'essai.`,
  )
  if (!ok) return
  actionLoading.value = true
  try {
    await addRecruitmentEvent(user.value.id, TYPE_PRESENTATION)
    user.value.need_presentation = false
  } finally {
    actionLoading.value = false
  }
}

async function openHistory() {
  if (!user.value) return
  showHistoryModal.value = true
  historyLoading.value = true
  try {
    historyEvents.value = await getRecruitmentHistory(user.value.id)
  } finally {
    historyLoading.value = false
  }
}

async function handleAddActivity(comment: string) {
  if (!user.value) return
  showActivityModal.value = false
  actionLoading.value = true
  try {
    await addRecruitmentEvent(user.value.id, TYPE_ACTIVITY, comment || undefined)
    user.value.cadet_flights = (user.value.cadet_flights ?? 0) + 1
  } finally {
    actionLoading.value = false
  }
}

const groupedModules = computed<TypeGroup[]>(() => {
  if (!user.value?.modules?.length) return []

  const typeOrder = MODULE_TYPE_ORDER
  const groups: TypeGroup[] = []

  for (const type of typeOrder) {
    const modulesOfType = user.value.modules
      .filter((m) => m.module_type === type)
      .sort((a, b) => {
        if (type === MODULE_TYPE_AIRCRAFT) {
          const pa = a.module_period ?? 0
          const pb = b.module_period ?? 0
          if (pb !== pa) return pb - pa
        }
        return (a.module_long_name ?? '').localeCompare(b.module_long_name ?? '')
      })

    if (modulesOfType.length === 0) continue

    // Use the type label from the backend (first module of the group)
    const typeLabel = modulesOfType[0].module_type_as_string ?? ''

    if (type === MODULE_TYPE_AIRCRAFT) {
      const periodMap = new Map<number, UserModule[]>()
      for (const m of modulesOfType) {
        const p = m.module_period ?? 0
        if (!periodMap.has(p)) periodMap.set(p, [])
        periodMap.get(p)!.push(m)
      }
      const periods = [...periodMap.entries()]
        .sort(([a], [b]) => b - a)
        .map(([period, modules]) => ({
          period,
          label: modules[0].module_period_as_string ?? '',
          modules,
        }))
      groups.push({ type, label: typeLabel, count: modulesOfType.length, periods })
    } else {
      groups.push({
        type,
        label: typeLabel,
        count: modulesOfType.length,
        periods: [{ period: null, label: '', modules: modulesOfType }],
      })
    }
  }
  return groups
})

function statusIcon(status: number): { icon: string; class: string; title: string } {
  if (status >= 2 && status <= 8) return { icon: 'fa-solid fa-user', class: 'text-green-600', title: 'Membre' }
  if (status === 1) return { icon: 'fa-solid fa-user-graduate', class: 'text-yellow-500', title: 'Cadet' }
  return { icon: 'fa-solid fa-user', class: 'text-gray-400', title: 'Invité' }
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

onMounted(async () => {
  try {
    user.value = await getUser(route.params.nickname as string)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>

  <div v-else-if="user">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">
        <i
          :class="[statusIcon(user.status).icon, statusIcon(user.status).class]"
          :title="statusIcon(user.status).title"
          class="mr-2"
        ></i>
        Profil de {{ user.nickname }}
      </h1>
      <RouterLink
        v-if="isOwnProfile"
        to="/profile"
        class="btn-secondary text-sm"
      >
        <i class="fa-solid fa-edit mr-1"></i>Modifier mon profil
      </RouterLink>
    </div>

    <!-- Info card -->
    <div class="card mb-6">
      <h2 class="text-lg font-semibold mb-4">Informations</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div>
          <span class="font-medium text-gray-500">Statut :</span>
          <span class="capitalize ml-1">{{ user.status_as_string }}</span>
        </div>
        <div>
          <span class="font-medium text-gray-500">Inscrit le :</span>
          {{ formatDate(user.created_at) }}
        </div>
        <div v-if="user.discord">
          <span class="font-medium text-gray-500">Discord :</span>
          {{ user.discord }}
        </div>
        <div v-if="user.forum">
          <span class="font-medium text-gray-500">Forum :</span>
          {{ user.forum }}
        </div>
      </div>

      <!-- Simulators -->
      <div class="mt-4 pt-4 border-t border-gray-200 text-sm">
        <h3 class="font-semibold mb-2">Simulateurs</h3>
        <div class="space-y-1">
          <p>
            <i
              :class="user.sim_dcs ? 'fa-solid fa-square-check text-green-600' : 'fa-regular fa-square text-gray-400'"
              class="mr-2"
            ></i>
            Digital Combat Simulator (DCS World)
          </p>
          <p>
            <i
              :class="user.sim_bms ? 'fa-solid fa-square-check text-green-600' : 'fa-regular fa-square text-gray-400'"
              class="mr-2"
            ></i>
            Falcon 4 - BMS
          </p>
        </div>
      </div>
    </div>

    <!-- Cadet integration section -->
    <div v-if="showCadetSection" class="card mb-6">
      <h2 class="text-lg font-semibold mb-4">Intégration du cadet</h2>

      <div class="space-y-2 text-sm">
        <p>
          <i
            :class="user.sim_dcs ? 'fa-solid fa-square-check text-green-600' : 'fa-regular fa-square text-red-500'"
            class="mr-2"
          ></i>
          Simulateur DCS
        </p>

        <p>
          <i
            :class="!user.need_presentation ? 'fa-solid fa-square-check text-green-600' : 'fa-regular fa-square text-red-500'"
            class="mr-2"
          ></i>
          <template v-if="user.need_presentation">
            <button
              class="text-veaf-600 hover:text-veaf-800 underline"
              :disabled="actionLoading"
              @click="markPresentation"
            >
              Présentation de l'association par un membre
            </button>
          </template>
          <template v-else>
            Présentation de l'association par un membre
          </template>
        </p>

        <p>
          <i
            :class="(user.cadet_flights ?? 0) >= CADET_MIN_FLIGHTS ? 'fa-solid fa-square-check text-green-600' : 'fa-regular fa-square text-red-500'"
            class="mr-2"
          ></i>
          {{ user.cadet_flights ?? 0 }} / {{ CADET_MIN_FLIGHTS }}
          <button
            class="text-veaf-600 hover:text-veaf-800 underline"
            @click="openHistory"
          >activité(s)</button>
          <button
            class="text-veaf-600 hover:text-veaf-800 underline ml-1"
            :disabled="actionLoading"
            @click="showActivityModal = true"
          >
            - ajouter une activité ...
          </button>
        </p>
      </div>
    </div>

    <AddActivityModal
      v-if="user"
      :visible="showActivityModal"
      :nickname="user.nickname"
      @submit="handleAddActivity"
      @close="showActivityModal = false"
    />

    <!-- History modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showHistoryModal"
          class="fixed inset-0 z-50 flex items-center justify-center"
          @keydown.escape="showHistoryModal = false"
        >
          <div class="absolute inset-0 bg-black/50" @click="showHistoryModal = false" />
          <div
            role="dialog"
            aria-modal="true"
            class="relative bg-white rounded-lg shadow-lg border border-gray-200 p-6 max-w-lg w-full mx-4 max-h-[80vh] flex flex-col"
          >
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Evénements de {{ user?.nickname }}
            </h3>

            <div v-if="historyLoading" class="text-center py-6 text-gray-500">Chargement...</div>

            <div v-else-if="historyEvents.length === 0" class="text-center py-6 text-gray-500">
              Aucun événement
            </div>

            <div v-else class="overflow-y-auto space-y-2 text-sm">
              <div v-for="e in historyEvents" :key="e.id" class="border-b border-gray-100 pb-2">
                <span class="text-gray-500">{{ e.event_at ? new Date(e.event_at).toLocaleDateString('fr-FR') : '' }}</span>
                - <span class="font-medium capitalize">{{ e.type_as_string }}</span>
                <template v-if="e.validator_nickname">
                  avec <span class="font-medium">{{ e.validator_nickname }}</span>
                </template>
                <template v-if="e.comment">
                  - <span class="italic text-gray-600">{{ e.comment }}</span>
                </template>
              </div>
            </div>

            <div class="mt-4 flex justify-end">
              <button class="btn-secondary" @click="showHistoryModal = false">
                <i class="fa-solid fa-xmark mr-1"></i>Fermer
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Modules section -->
    <div v-if="groupedModules.length > 0" class="card">
      <h2 class="text-lg font-semibold mb-4">Modules</h2>

      <!-- Legend -->
      <div class="bg-gray-50 rounded-lg p-4 mb-6 text-sm text-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="font-medium mb-1">Activité :</p>
            <ul class="space-y-1 ml-1">
              <li><i class="fa-solid fa-plane text-green-600 mr-2 w-4 text-center"></i>Vole dessus</li>
              <li><i class="fa-solid fa-warehouse text-gray-400 mr-2 w-4 text-center"></i>Au hangar</li>
            </ul>
          </div>
          <div>
            <p class="font-medium mb-1">Niveau :</p>
            <ul class="space-y-1 ml-1">
              <li><i class="fa-solid fa-book-open-reader text-yellow-500 mr-2 w-4 text-center"></i>Débutant</li>
              <li><i class="fa-solid fa-shield-halved text-green-600 mr-2 w-4 text-center"></i>Mission</li>
              <li><i class="fa-solid fa-user-tie text-veaf-600 mr-2 w-4 text-center"></i>Instructeur</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Module groups -->
      <div v-for="group in groupedModules" :key="group.type" class="mb-6 last:mb-0">
        <h3 class="text-md font-semibold border-b border-gray-300 pb-2 mb-3 flex items-center justify-between">
          {{ group.label }}
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-veaf-100 text-veaf-800">
            {{ group.count }}
          </span>
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
            class="flex items-center justify-between py-2 px-2 border-b border-gray-100 text-sm"
          >
            <span class="flex-1 min-w-0 truncate mr-3">{{ mod.module_long_name }}</span>

            <div class="flex items-center gap-3 flex-shrink-0">
              <!-- Activity icon -->
              <i
                v-if="mod.active"
                class="fa-solid fa-plane text-green-600"
                title="Vole dessus en ce moment"
              ></i>
              <i
                v-else
                class="fa-solid fa-warehouse text-gray-400"
                title="Au hangar"
              ></i>

              <!-- Level icon -->
              <template v-if="mod.module_type !== null && TYPES_WITH_LEVEL.includes(mod.module_type)">
                <i
                  v-if="mod.level === 3"
                  class="fa-solid fa-user-tie text-veaf-600"
                  title="Instructeur"
                ></i>
                <i
                  v-else-if="mod.level === 2"
                  class="fa-solid fa-shield-halved text-green-600"
                  title="Mission"
                ></i>
                <i
                  v-else
                  class="fa-solid fa-book-open-reader text-yellow-500"
                  title="Débutant"
                ></i>
              </template>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
