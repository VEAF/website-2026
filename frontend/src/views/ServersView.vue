<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getDcsBotServers } from '@/api/servers'
import { formatMissionName, shortMissionName } from '@/utils/format'
import type { DcsBotPage } from '@/types/api'

const pageData = ref<DcsBotPage | null>(null)
const loading = ref(true)
const error = ref(false)

async function fetchData() {
  loading.value = true
  error.value = false
  try {
    pageData.value = await getDcsBotServers()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function shortName(name: string): string {
  const parts = name.split('-', 2)
  return parts.length > 1 ? parts[1].trim() : name
}

function statusBadgeClass(status: string): string {
  switch (status) {
    case 'Running':
      return 'bg-green-100 text-green-800'
    case 'Paused':
      return 'bg-yellow-100 text-yellow-800'
    case 'Shutdown':
      return 'bg-gray-200 text-gray-600'
    default:
      return 'bg-blue-100 text-blue-800'
  }
}

function statusIcon(status: string): string {
  switch (status) {
    case 'Running':
      return 'fa-solid fa-play'
    case 'Paused':
      return 'fa-solid fa-pause'
    case 'Shutdown':
      return 'fa-solid fa-stop'
    default:
      return 'fa-solid fa-question'
  }
}

function formatUptime(seconds: number): string {
  return Math.round(seconds / 60) + 'min'
}

function formatAvgPlaytime(seconds: number): string {
  return (seconds / 3600).toFixed(1) + 'h'
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">
      <i class="fa-solid fa-server mr-2"></i>Liste des serveurs
    </h1>

    <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

    <div v-else-if="error" class="card text-center py-8 text-red-600">
      <i class="fa-solid fa-exclamation-triangle mr-1"></i>
      Impossible de contacter le service DCSServerBot
      <button @click="fetchData" class="btn-primary text-sm ml-4">Réessayer</button>
    </div>

    <template v-else-if="pageData">
      <!-- Servers table -->
      <div class="card mb-6 overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b bg-gray-50">
              <th class="text-left py-2 px-3"><i class="fa-solid fa-hdd mr-1"></i>Serveur</th>
              <th class="text-left py-2 px-3"><i class="fa-solid fa-power-off mr-1"></i>Status</th>
              <th class="text-left py-2 px-3"><i class="fa-solid fa-globe mr-1"></i>Théâtre</th>
              <th class="text-left py-2 px-3"><i class="fa-solid fa-fighter-jet mr-1"></i>Mission</th>
              <th class="text-left py-2 px-3"><i class="fa-solid fa-sun mr-1"></i>Heure</th>
              <th class="text-center py-2 px-3"><i class="fa-solid fa-users mr-1"></i>Joueurs</th>
              <th class="text-left py-2 px-3"><i class="fa-solid fa-clock mr-1"></i>Uptime</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pageData.servers.length === 0">
              <td colspan="7" class="py-4 px-3 text-center text-gray-500 italic">
                Pas de serveurs disponibles
              </td>
            </tr>
            <tr
              v-for="server in pageData.servers"
              :key="server.name"
              class="border-b hover:bg-gray-50"
            >
              <td class="py-2 px-3 font-medium">
                <RouterLink
                  :to="{ name: 'server-detail', params: { serverName: server.name } }"
                  class="text-veaf-600 hover:text-veaf-800 hover:underline"
                >
                  {{ shortName(server.name) }}
                </RouterLink>
              </td>
              <td class="py-2 px-3">
                <span
                  :class="statusBadgeClass(server.status)"
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                >
                  <i :class="statusIcon(server.status)" class="mr-1"></i>
                  {{ server.status }}
                </span>
              </td>
              <td class="py-2 px-3">
                {{ server.mission ? server.mission.theatre : '-' }}
              </td>
              <td class="py-2 px-3" :title="server.mission ? formatMissionName(server.mission.name) : undefined">
                {{ server.mission ? shortMissionName(server.mission.name) : '-' }}
              </td>
              <td class="py-2 px-3">
                <template v-if="server.mission?.date_time">
                  <i
                    v-if="server.mission.sun_state"
                    :class="server.mission.sun_state.icon"
                    :style="{ color: server.mission.sun_state.color }"
                    :title="server.mission.sun_state.tooltip"
                    class="mr-1"
                  ></i>
                  <span :title="server.mission.mission_date_time ?? undefined">
                    {{ server.mission.mission_time ?? server.mission.date_time }}
                  </span>
                </template>
                <template v-else>-</template>
              </td>
              <td class="py-2 px-3 text-center">
                {{ server.status === 'Running' ? server.num_players : '-' }}
              </td>
              <td class="py-2 px-3">
                {{ server.mission ? formatUptime(server.mission.uptime) : '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Global statistics -->
      <div v-if="pageData.stats">
        <h2 class="text-xl font-bold mb-4">
          <i class="fa-solid fa-chart-bar mr-2"></i>Statistiques globales
        </h2>

        <!-- Primary stats row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div class="rounded-lg p-4 text-center text-white bg-veaf-600">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-users mr-1"></i>Joueurs total</div>
            <div class="text-3xl font-bold">{{ pageData.stats.total_players }}</div>
          </div>
          <div class="rounded-lg p-4 text-center text-white bg-green-600">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-user-check mr-1"></i>Joueurs actifs</div>
            <div class="text-3xl font-bold">{{ pageData.stats.active_players }}</div>
          </div>
          <div class="rounded-lg p-4 text-center text-white bg-sky-600">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-plane-departure mr-1"></i>Sorties</div>
            <div class="text-3xl font-bold">{{ pageData.stats.total_sorties }}</div>
          </div>
          <div class="rounded-lg p-4 text-center text-white bg-gray-500">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-hourglass-half mr-1"></i>Temps moyen</div>
            <div class="text-3xl font-bold">{{ formatAvgPlaytime(pageData.stats.avg_playtime) }}</div>
          </div>
        </div>

        <!-- Secondary stats row -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-crosshairs mr-1"></i>Kills</div>
            <div class="text-2xl font-bold">{{ pageData.stats.total_kills }}</div>
          </div>
          <div class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-skull mr-1"></i>Deaths</div>
            <div class="text-2xl font-bold">{{ pageData.stats.total_deaths }}</div>
          </div>
          <div class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-crosshairs mr-1"></i>PvP Kills</div>
            <div class="text-2xl font-bold">{{ pageData.stats.total_pvp_kills }}</div>
          </div>
          <div class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-skull-crossbones mr-1"></i>PvP Deaths</div>
            <div class="text-2xl font-bold">{{ pageData.stats.total_pvp_deaths }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
