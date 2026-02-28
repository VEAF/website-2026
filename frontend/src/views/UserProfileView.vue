<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { getUser } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import type { UserProfile } from '@/types/user'
import type { UserModule } from '@/types/user'

const route = useRoute()
const auth = useAuthStore()
const user = ref<UserProfile | null>(null)
const loading = ref(true)

const TYPES_WITH_LEVEL = [2, 3, 4] // AIRCRAFT, HELICOPTER, SPECIAL

const MODULE_TYPE_LABELS: Record<number, string> = {
  1: 'Cartes',
  2: 'Avions',
  3: 'Hélicoptères',
  4: 'Spécial',
}

const PERIOD_LABELS: Record<number, string> = {
  1: 'WW2',
  2: 'COLD WAR',
  3: 'MODERN',
}

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

const groupedModules = computed<TypeGroup[]>(() => {
  if (!user.value?.modules?.length) return []

  const typeOrder = [1, 2, 3, 4]
  const groups: TypeGroup[] = []

  for (const type of typeOrder) {
    const modulesOfType = user.value.modules
      .filter((m) => m.module_type === type)
      .sort((a, b) => {
        if (type === 2) {
          const pa = a.module_period ?? 0
          const pb = b.module_period ?? 0
          if (pb !== pa) return pb - pa
        }
        return (a.module_long_name ?? '').localeCompare(b.module_long_name ?? '')
      })

    if (modulesOfType.length === 0) continue

    if (type === 2) {
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
          label: PERIOD_LABELS[period] || '',
          modules,
        }))
      groups.push({ type, label: MODULE_TYPE_LABELS[type], count: modulesOfType.length, periods })
    } else {
      groups.push({
        type,
        label: MODULE_TYPE_LABELS[type],
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
    user.value = await getUser(Number(route.params.id))
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
