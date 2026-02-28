<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

interface RosterUser {
  id: number
  nickname: string
  status: number
  status_as_string: string
  sim_dcs: boolean
  sim_bms: boolean
  modules: {
    module_id: number
    module_name: string
    module_code: string
    module_type: number
    active: boolean
    level: number
    level_as_string: string
  }[]
}

const users = ref<RosterUser[]>([])
const group = ref('members')
const loading = ref(true)

async function fetchRoster() {
  loading.value = true
  const { data } = await apiClient.get('/roster', { params: { group: group.value } })
  users.value = data
  loading.value = false
}

onMounted(fetchRoster)

const groups = [
  { value: 'all', label: 'Tous' },
  { value: 'members', label: 'Membres' },
  { value: 'cadets', label: 'Cadets' },
  { value: 'cadets-members', label: 'Cadets + Membres' },
]

function levelBadge(level: number): string {
  if (level === 3) return 'I'
  if (level === 2) return 'M'
  if (level === 1) return 'R'
  return ''
}

function levelClass(level: number): string {
  if (level === 3) return 'bg-green-100 text-green-800'
  if (level === 2) return 'bg-blue-100 text-blue-800'
  if (level === 1) return 'bg-yellow-100 text-yellow-800'
  return 'bg-gray-100 text-gray-500'
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Roster</h1>

    <div class="flex space-x-2 mb-6">
      <button
        v-for="g in groups" :key="g.value"
        @click="group = g.value; fetchRoster()"
        :class="[group === g.value ? 'btn-primary' : 'btn-secondary']"
        class="text-sm"
      >
        {{ g.label }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b bg-gray-50">
            <th class="text-left py-2 px-3">Pilote</th>
            <th class="text-left py-2 px-3">Statut</th>
            <th class="text-center py-2 px-3">Modules</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" class="border-b hover:bg-gray-50">
            <td class="py-2 px-3">
              <RouterLink :to="`/user/${u.nickname}`" class="text-veaf-600 hover:text-veaf-800 font-medium">{{ u.nickname }}</RouterLink>
            </td>
            <td class="py-2 px-3 capitalize">{{ u.status_as_string }}</td>
            <td class="py-2 px-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="m in u.modules.filter(m => m.active && m.level > 0)"
                  :key="m.module_id"
                  :class="levelClass(m.level)"
                  class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium"
                  :title="`${m.module_name} - ${m.level_as_string}`"
                >
                  {{ m.module_code }}
                  <span class="ml-0.5 font-bold">{{ levelBadge(m.level) }}</span>
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
