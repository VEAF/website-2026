<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getRosterStats } from '@/api/roster'
import type { RosterStats } from '@/api/roster'
import RosterPilotsList from '@/components/roster/RosterPilotsList.vue'
import RosterModuleList from '@/components/roster/RosterModuleList.vue'
import RosterModuleDetail from '@/components/roster/RosterModuleDetail.vue'
import { TAB_TO_MODULE_TYPE } from '@/constants/modules'

const group = ref('all')
const tab = ref('pilots')
const selectedModuleId = ref<number | null>(null)
const stats = ref<RosterStats>({ all: 0, cadets: 0, members: 0 })
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
  await loadStats()
  loading.value = false
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Roster</h1>

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
