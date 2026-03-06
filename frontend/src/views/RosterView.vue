<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getRosterStats } from '@/api/roster'
import type { RosterStats } from '@/api/roster'
import RosterPilotsList from '@/components/roster/RosterPilotsList.vue'
import RosterModuleList from '@/components/roster/RosterModuleList.vue'
import RosterModuleDetail from '@/components/roster/RosterModuleDetail.vue'
import { TAB_TO_MODULE_TYPE } from '@/constants/modules'
import { useAuthStore } from '@/stores/auth'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'

const route = useRoute()
const authStore = useAuthStore()

const group = ref('all')
const tab = ref('pilots')
const selectedModuleId = ref<number | null>(null)
const stats = ref<RosterStats>({ all: 0, cadets: 0, members: 0, cadets_need_presentation: 0, cadets_ready_to_promote: 0 })
const loading = ref(true)

const groups = [
  { value: 'all', label: 'Tout le monde', icon: 'fa-solid fa-users' },
  { value: 'cadets', label: 'Cadets', icon: 'fa-solid fa-user-graduate' },
  { value: 'members', label: 'Membres', icon: 'fa-solid fa-user' },
]

const tabs = [
  { value: 'pilots', label: 'Pilotes', icon: 'fa-solid fa-users' },
  { value: 'maps', label: 'Cartes', icon: 'fa-solid fa-map' },
  { value: 'aircrafts', label: 'Avions', icon: 'fa-solid fa-plane' },
  { value: 'helicopters', label: 'Hélicoptères', icon: 'fa-solid fa-helicopter' },
  { value: 'specials', label: 'Spéciaux', icon: 'fa-solid fa-ship' },
]

const tabToModuleType = TAB_TO_MODULE_TYPE

function statValue(groupValue: string): number {
  return stats.value[groupValue as keyof RosterStats] ?? 0
}

async function loadStats() {
  stats.value = await getRosterStats()
}

function changeGroup(newGroup: string) {
  group.value = newGroup
  loadStats()
}

function changeTab(newTab: string) {
  tab.value = newTab
  selectedModuleId.value = null
}

onMounted(async () => {
  const queryTab = route.query.tab as string | undefined
  const queryModuleId = route.query.moduleId as string | undefined
  if (queryTab && queryTab in tabToModuleType) {
    tab.value = queryTab
  }
  if (queryModuleId) {
    selectedModuleId.value = Number(queryModuleId)
  }
  await loadStats()
  loading.value = false
})
</script>

<template>
  <div>
    <AppBreadcrumb :show-title="false" />

    <!-- Top bar: group selector + tabs -->
    <div
      class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6"
    >
      <!-- Group selector -->
      <div class="flex space-x-2">
        <button
          v-for="g in groups"
          :key="g.value"
          :class="[group === g.value ? 'btn-primary' : 'btn-secondary']"
          class="text-sm"
          @click="changeGroup(g.value)"
        >
          <i :class="g.icon" class="mr-1"></i>
          <span class="hidden xl:inline">{{ g.label }}</span>
          <span
            class="ml-1 inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-white/20"
          >
            {{ statValue(g.value) }}
          </span>
        </button>
      </div>

      <!-- Tab selector -->
      <div class="flex space-x-1">
        <button
          v-for="t in tabs"
          :key="t.value"
          :class="[tab === t.value ? 'btn-primary' : 'btn-secondary']"
          class="text-sm"
          @click="changeTab(t.value)"
        >
          <i :class="t.icon" class="mr-1"></i>
          <span class="hidden xl:inline">{{ t.label }}</span>
        </button>
      </div>
    </div>

    <!-- Alert: cadets needing presentation -->
    <div
      v-if="authStore.isMember && stats.cadets_need_presentation > 0"
      class="mb-6 rounded-lg bg-yellow-50 border border-yellow-200 px-4 py-3 text-sm text-yellow-800"
    >
      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-200 text-yellow-900 mr-2">
        {{ stats.cadets_need_presentation }}
      </span>
      <i class="fa-solid fa-user-graduate text-yellow-500 mr-1"></i>
      cadet(s) n'ont pas encore eu la
      <i class="fa-solid fa-bullhorn text-yellow-500 mx-1"></i>
      présentation de l'association
    </div>

    <!-- Alert: cadets ready to promote -->
    <div
      v-if="authStore.isMember && stats.cadets_ready_to_promote > 0"
      class="mb-6 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800"
    >
      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-200 text-green-900 mr-2">
        {{ stats.cadets_ready_to_promote }}
      </span>
      <i class="fa-solid fa-circle-check text-green-600 mr-1"></i>
      cadet{{ stats.cadets_ready_to_promote > 1 ? 's' : '' }}
      prêt{{ stats.cadets_ready_to_promote > 1 ? 's' : '' }} à rejoindre l'association
    </div>

    <!-- Content area -->
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Chargement...
    </div>

    <template v-else>
      <!-- Pilots tab -->
      <RosterPilotsList v-if="tab === 'pilots'" :group="group" />

      <!-- Module tabs -->
      <template v-else>
        <!-- Module detail -->
        <RosterModuleDetail
          v-if="selectedModuleId !== null"
          :module-id="selectedModuleId"
          :group="group"
          :module-type="tabToModuleType[tab]"
          @back="selectedModuleId = null"
        />

        <!-- Module list -->
        <RosterModuleList
          v-else
          :module-type="tabToModuleType[tab]"
          :group="group"
          @select-module="selectedModuleId = $event"
        />
      </template>
    </template>
  </div>
</template>
