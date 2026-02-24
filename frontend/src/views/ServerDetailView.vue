<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getDcsBotServer } from '@/api/servers'
import { formatMissionName, shortMissionName } from '@/utils/format'
import type { DcsBotServerDetailPage } from '@/types/api'

const POLL_INTERVAL = 60_000

const props = defineProps<{ serverName: string }>()

const pageData = ref<DcsBotServerDetailPage | null>(null)
const loading = ref(true)
const error = ref(false)
const showPassword = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchData() {
  loading.value = true
  error.value = false
  try {
    pageData.value = await getDcsBotServer(props.serverName)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  try {
    pageData.value = await getDcsBotServer(props.serverName)
    error.value = false
  } catch {
    // Keep previous data on refresh error
  }
}

onMounted(() => {
  fetchData()
  pollTimer = setInterval(refreshData, POLL_INTERVAL)
})

onUnmounted(() => {
  if (pollTimer !== null) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})

// --- Helper functions ---

function statusBadgeClass(status: string): string {
  switch (status) {
    case 'Running': return 'bg-green-100 text-green-800'
    case 'Paused': return 'bg-yellow-100 text-yellow-800'
    case 'Shutdown': return 'bg-gray-200 text-gray-600'
    default: return 'bg-blue-100 text-blue-800'
  }
}

function statusIcon(status: string): string {
  switch (status) {
    case 'Running': return 'fa-solid fa-play'
    case 'Paused': return 'fa-solid fa-pause'
    case 'Shutdown': return 'fa-solid fa-stop'
    default: return 'fa-solid fa-question'
  }
}

function sideBadgeClass(side: string | null): string {
  switch (side?.toLowerCase()) {
    case 'blue': return 'bg-blue-100 text-blue-800'
    case 'red': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-200 text-gray-600'
  }
}

function formatUptime(seconds: number): string {
  return Math.round(seconds / 60) + 'min'
}

function formatAvgPlaytime(seconds: number): string {
  return (seconds / 3600).toFixed(1) + 'h'
}

function formatRestartTime(raw: string): string {
  try {
    const d = new Date(raw)
    return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return raw
  }
}

// Weather conversions
function tempF(c: number): string {
  return ((c * 9 / 5) + 32).toFixed(1)
}

function pressureHpa(mmHg: number): string {
  return Math.round(mmHg * 1013.25 / 760).toString()
}

function pressureInHg(mmHg: number): string {
  return (mmHg / 25.4).toFixed(2)
}

function windDir(dir: number): string {
  return Math.round((dir + 180) % 360).toString()
}

function windKts(ms: number): string {
  return (ms * 1.94384).toFixed(1)
}

function windKmh(ms: number): string {
  return (ms * 3.6).toFixed(1)
}

function cloudBaseFt(m: number): string {
  return Math.round(m * 3.28084).toString()
}

function visKm(m: number): string {
  return (m / 1000).toFixed(1)
}

function visNm(m: number): string {
  return (m / 1852).toFixed(1)
}
</script>

<template>
  <div>
    <!-- Breadcrumb -->
    <nav class="text-sm text-gray-500 mb-4">
      <RouterLink to="/servers" class="text-veaf-600 hover:text-veaf-800 hover:underline">
        Serveurs DCS
      </RouterLink>
      <span class="mx-2">/</span>
      <span class="text-gray-700">{{ props.serverName }}</span>
    </nav>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

    <!-- Error -->
    <div v-else-if="error" class="card text-center py-8 text-red-600">
      <i class="fa-solid fa-exclamation-triangle mr-1"></i>
      Impossible de contacter le service DCSServerBot
      <button @click="fetchData" class="btn-primary text-sm ml-4">Réessayer</button>
    </div>

    <template v-else-if="pageData">
      <!-- Title + status badge -->
      <h1 class="text-2xl font-bold mb-6">
        <i class="fa-solid fa-server mr-2"></i>{{ pageData.server.name }}
        <span
          :class="statusBadgeClass(pageData.server.status)"
          class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ml-2 align-middle"
        >
          <i :class="statusIcon(pageData.server.status)" class="mr-1"></i>
          {{ pageData.server.status }}
        </span>
      </h1>

      <!-- Server info + Mission (two-column) -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Server info card -->
        <div class="card">
          <h2 class="font-bold text-lg mb-3 border-b pb-2">
            <i class="fa-solid fa-server mr-1"></i> Informations serveur
          </h2>
          <table class="w-full text-sm">
            <tbody>
              <tr v-if="pageData.server.address">
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-network-wired mr-1"></i> Adresse
                </th>
                <td>{{ pageData.server.address }}</td>
              </tr>
              <tr v-if="pageData.server.password">
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-key mr-1"></i> Mot de passe
                </th>
                <td>
                  <i
                    :class="showPassword ? 'fa-solid fa-eye' : 'fa-solid fa-eye-slash'"
                    class="cursor-pointer mr-2 text-gray-500 hover:text-gray-700"
                    title="Cliquer pour révéler"
                    @click="showPassword = !showPassword"
                  ></i>
                  <span>{{ showPassword ? pageData.server.password : '******' }}</span>
                </td>
              </tr>
              <tr v-if="pageData.server.restart_time">
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-arrows-rotate mr-1"></i> Prochain redémarrage
                </th>
                <td>{{ formatRestartTime(pageData.server.restart_time) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mission card -->
        <div v-if="pageData.server.mission" class="card">
          <h2 class="font-bold text-lg mb-3 border-b pb-2">
            <i class="fa-solid fa-fighter-jet mr-1"></i> Mission en cours
          </h2>
          <table class="w-full text-sm">
            <tbody>
              <tr>
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-file-lines mr-1"></i> Nom
                </th>
                <td :title="formatMissionName(pageData.server.mission.name)">
                  {{ shortMissionName(pageData.server.mission.name) }}
                </td>
              </tr>
              <tr>
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-map mr-1"></i> Théâtre
                </th>
                <td>{{ pageData.server.mission.theatre }}</td>
              </tr>
              <tr v-if="pageData.server.mission.date_time">
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-sun mr-1"></i> Heure mission
                </th>
                <td>
                  <span :title="pageData.server.mission.mission_date_time ?? undefined">
                    {{ pageData.server.mission.mission_time ?? pageData.server.mission.date_time }}
                  </span>
                  <i
                    v-if="pageData.server.mission.sun_state"
                    :class="pageData.server.mission.sun_state.icon"
                    :style="{ color: pageData.server.mission.sun_state.color }"
                    :title="pageData.server.mission.sun_state.tooltip"
                    class="ml-2"
                  ></i>
                </td>
              </tr>
              <tr>
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-clock mr-1"></i> Uptime
                </th>
                <td>{{ formatUptime(pageData.server.mission.uptime) }}</td>
              </tr>
              <tr>
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-users mr-1 text-blue-600"></i> Slots bleus
                </th>
                <td>{{ pageData.server.mission.blue_slots_used ?? 0 }} / {{ pageData.server.mission.blue_slots ?? '?' }}</td>
              </tr>
              <tr>
                <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                  <i class="fa-solid fa-users mr-1 text-red-600"></i> Slots rouges
                </th>
                <td>{{ pageData.server.mission.red_slots_used ?? 0 }} / {{ pageData.server.mission.red_slots ?? '?' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Weather -->
      <template v-if="pageData.server.weather">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Temperature / QNH -->
          <div class="card">
            <h2 class="font-bold text-lg mb-3 border-b pb-2">
              <i class="fa-solid fa-cloud-sun mr-1"></i> Conditions météo
            </h2>
            <table class="w-full text-sm">
              <tbody>
                <tr v-if="pageData.server.weather.temperature != null">
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-temperature-high mr-1"></i> Température
                  </th>
                  <td>{{ pageData.server.weather.temperature.toFixed(1) }} °C</td>
                  <td>{{ tempF(pageData.server.weather.temperature) }} °F</td>
                </tr>
                <tr v-if="pageData.server.weather.pressure != null">
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-gauge mr-1"></i> QNH
                  </th>
                  <td>{{ pressureHpa(pageData.server.weather.pressure) }} hPa</td>
                  <td>{{ pressureInHg(pageData.server.weather.pressure) }} inHg</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Wind -->
          <div class="card">
            <h2 class="font-bold text-lg mb-3 border-b pb-2">
              <i class="fa-solid fa-wind mr-1"></i> Vent au sol
            </h2>
            <table class="w-full text-sm">
              <tbody>
                <tr v-if="pageData.server.weather.wind_direction != null">
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-compass mr-1"></i> Direction
                  </th>
                  <td colspan="3">{{ windDir(pageData.server.weather.wind_direction) }}°</td>
                </tr>
                <tr v-if="pageData.server.weather.wind_speed != null">
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-gauge mr-1"></i> Vitesse
                  </th>
                  <td>{{ windKts(pageData.server.weather.wind_speed) }} kts</td>
                  <td>{{ windKmh(pageData.server.weather.wind_speed) }} km/h</td>
                  <td>{{ pageData.server.weather.wind_speed.toFixed(0) }} m/s</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <!-- Clouds -->
          <div class="card">
            <h2 class="font-bold text-lg mb-3 border-b pb-2">
              <i class="fa-solid fa-cloud mr-1"></i> Nuages
            </h2>
            <table class="w-full text-sm">
              <tbody>
                <tr>
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-arrows-up-down mr-1"></i> Base
                  </th>
                  <td>{{ pageData.server.weather.clouds_base ? pageData.server.weather.clouds_base + ' m' : '-' }}</td>
                  <td>{{ pageData.server.weather.clouds_base ? cloudBaseFt(pageData.server.weather.clouds_base) + ' ft' : '-' }}</td>
                </tr>
                <tr>
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-th mr-1"></i> Densité
                  </th>
                  <td colspan="2">{{ pageData.server.weather.clouds_density ?? '-' }}/10</td>
                </tr>
                <tr v-if="pageData.server.weather.precipitation && pageData.server.weather.precipitation > 0">
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-cloud-rain mr-1"></i> Précipitations
                  </th>
                  <td colspan="2">Oui</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Visibility -->
          <div class="card">
            <h2 class="font-bold text-lg mb-3 border-b pb-2">
              <i class="fa-solid fa-eye mr-1"></i> Visibilité
            </h2>
            <table class="w-full text-sm">
              <tbody>
                <tr>
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-binoculars mr-1"></i> Distance
                  </th>
                  <td>{{ pageData.server.weather.visibility ? visKm(pageData.server.weather.visibility) + ' km' : '-' }}</td>
                  <td>{{ pageData.server.weather.visibility ? visNm(pageData.server.weather.visibility) + ' NM' : '-' }}</td>
                </tr>
                <tr v-if="pageData.server.weather.fog_enabled">
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-smog mr-1"></i> Brouillard
                  </th>
                  <td colspan="2">{{ pageData.server.weather.fog_visibility }} m</td>
                </tr>
                <tr v-if="pageData.server.weather.dust_enabled">
                  <th class="text-left py-1.5 pr-4 text-gray-600 w-40">
                    <i class="fa-solid fa-wind mr-1"></i> Poussière
                  </th>
                  <td colspan="2">{{ pageData.server.weather.dust_visibility }} m</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- Online players -->
      <div v-if="pageData.server.status === 'Running' && pageData.server.players.length > 0" class="mb-6">
        <h2 class="text-xl font-bold mb-4">
          <i class="fa-solid fa-users mr-2"></i>Joueurs en ligne ({{ pageData.server.players.length }})
        </h2>
        <div class="card overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b bg-gray-50">
                <th class="text-left py-2 px-3"><i class="fa-solid fa-user mr-1"></i>Pseudo</th>
                <th class="text-left py-2 px-3"><i class="fa-solid fa-id-badge mr-1"></i>Callsign</th>
                <th class="text-left py-2 px-3"><i class="fa-solid fa-flag mr-1"></i>Camp</th>
                <th class="text-left py-2 px-3"><i class="fa-solid fa-plane mr-1"></i>Appareil</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(player, index) in pageData.server.players"
                :key="index"
                class="border-b hover:bg-gray-50"
              >
                <td class="py-2 px-3">{{ player.nick }}</td>
                <td class="py-2 px-3">{{ player.callsign ?? '-' }}</td>
                <td class="py-2 px-3">
                  <span
                    v-if="player.side"
                    :class="sideBadgeClass(player.side)"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                  >
                    {{ player.side }}
                  </span>
                  <span v-else class="text-gray-400">-</span>
                </td>
                <td class="py-2 px-3">{{ player.unit_type ?? '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Server statistics -->
      <div v-if="pageData.stats" class="mb-6">
        <h2 class="text-xl font-bold mb-4">
          <i class="fa-solid fa-chart-bar mr-2"></i>Statistiques du serveur
        </h2>

        <!-- Primary stats -->
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

        <!-- Secondary stats -->
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
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-crosshairs mr-1 text-red-600"></i>PvP Kills</div>
            <div class="text-2xl font-bold">{{ pageData.stats.total_pvp_kills }}</div>
          </div>
          <div class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-skull-crossbones mr-1 text-red-600"></i>PvP Deaths</div>
            <div class="text-2xl font-bold">{{ pageData.stats.total_pvp_deaths }}</div>
          </div>
        </div>
      </div>

      <!-- Attendance -->
      <template v-if="pageData.attendance">
        <h2 class="text-xl font-bold mb-4">
          <i class="fa-solid fa-chart-line mr-2"></i>Fréquentation du serveur
        </h2>

        <!-- Summary cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="rounded-lg p-4 text-center text-white bg-veaf-600">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-user-clock mr-1"></i>Joueurs actuels</div>
            <div class="text-3xl font-bold">{{ pageData.attendance.current_players }}</div>
          </div>
          <div class="rounded-lg p-4 text-center text-white bg-green-600">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-calendar-day mr-1"></i>Uniques 24h</div>
            <div class="text-3xl font-bold">{{ pageData.attendance.unique_players_24h }}</div>
          </div>
          <div class="rounded-lg p-4 text-center text-white bg-sky-600">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-calendar-week mr-1"></i>Uniques 7j</div>
            <div class="text-3xl font-bold">{{ pageData.attendance.unique_players_7d }}</div>
          </div>
          <div class="rounded-lg p-4 text-center text-white bg-gray-500">
            <div class="text-sm font-medium mb-1"><i class="fa-solid fa-calendar mr-1"></i>Uniques 30j</div>
            <div class="text-3xl font-bold">{{ pageData.attendance.unique_players_30d }}</div>
          </div>
        </div>

        <!-- Period comparison table -->
        <div class="card mb-6 overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b bg-gray-50">
                <th class="text-left py-2 px-3"><i class="fa-solid fa-calendar mr-1"></i>Période</th>
                <th class="text-left py-2 px-3"><i class="fa-solid fa-user mr-1"></i>Joueurs uniques</th>
                <th class="text-left py-2 px-3"><i class="fa-solid fa-clock mr-1"></i>Temps de jeu total</th>
                <th class="text-left py-2 px-3"><i class="fa-brands fa-discord mr-1"></i>Membres Discord</th>
              </tr>
            </thead>
            <tbody>
              <tr class="border-b hover:bg-gray-50">
                <td class="py-2 px-3">24 heures</td>
                <td class="py-2 px-3">{{ pageData.attendance.unique_players_24h }}</td>
                <td class="py-2 px-3">{{ pageData.attendance.total_playtime_hours_24h.toFixed(1) }}h</td>
                <td class="py-2 px-3">{{ pageData.attendance.discord_members_24h }}</td>
              </tr>
              <tr class="border-b hover:bg-gray-50">
                <td class="py-2 px-3">7 jours</td>
                <td class="py-2 px-3">{{ pageData.attendance.unique_players_7d }}</td>
                <td class="py-2 px-3">{{ pageData.attendance.total_playtime_hours_7d.toFixed(1) }}h</td>
                <td class="py-2 px-3">{{ pageData.attendance.discord_members_7d }}</td>
              </tr>
              <tr class="hover:bg-gray-50">
                <td class="py-2 px-3">30 jours</td>
                <td class="py-2 px-3">{{ pageData.attendance.unique_players_30d }}</td>
                <td class="py-2 px-3">{{ pageData.attendance.total_playtime_hours_30d.toFixed(1) }}h</td>
                <td class="py-2 px-3">{{ pageData.attendance.discord_members_30d }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Combat stats -->
        <div v-if="pageData.attendance.total_sorties != null" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
          <div class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-plane-departure mr-1"></i>Sorties</div>
            <div class="text-xl font-bold">{{ pageData.attendance.total_sorties }}</div>
          </div>
          <div v-if="pageData.attendance.total_kills != null" class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-crosshairs mr-1"></i>Kills</div>
            <div class="text-xl font-bold">{{ pageData.attendance.total_kills }}</div>
          </div>
          <div v-if="pageData.attendance.total_deaths != null" class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-skull mr-1"></i>Deaths</div>
            <div class="text-xl font-bold">{{ pageData.attendance.total_deaths }}</div>
          </div>
          <div v-if="pageData.attendance.total_pvp_kills != null" class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-crosshairs mr-1 text-red-600"></i>PvP Kills</div>
            <div class="text-xl font-bold">{{ pageData.attendance.total_pvp_kills }}</div>
          </div>
          <div v-if="pageData.attendance.total_pvp_deaths != null" class="card text-center">
            <div class="text-sm text-gray-600 mb-1"><i class="fa-solid fa-skull-crossbones mr-1 text-red-600"></i>PvP Deaths</div>
            <div class="text-xl font-bold">{{ pageData.attendance.total_pvp_deaths }}</div>
          </div>
        </div>

        <!-- Top lists -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div v-if="pageData.attendance.top_theatres.length > 0" class="card">
            <h3 class="font-bold mb-3 border-b pb-2">
              <i class="fa-solid fa-globe mr-1"></i> Top Théâtres
            </h3>
            <table class="w-full text-sm">
              <tbody>
                <tr v-for="t in pageData.attendance.top_theatres" :key="t.theatre" class="border-b last:border-b-0">
                  <td class="py-1.5">{{ t.theatre }}</td>
                  <td class="py-1.5 text-right text-gray-600">{{ t.playtime_hours.toFixed(1) }}h</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="pageData.attendance.top_missions.length > 0" class="card">
            <h3 class="font-bold mb-3 border-b pb-2">
              <i class="fa-solid fa-list-check mr-1"></i> Top Missions
            </h3>
            <table class="w-full text-sm">
              <tbody>
                <tr v-for="m in pageData.attendance.top_missions" :key="m.mission_name" class="border-b last:border-b-0">
                  <td class="py-1.5">{{ formatMissionName(m.mission_name) }}</td>
                  <td class="py-1.5 text-right text-gray-600">{{ m.playtime_hours.toFixed(1) }}h</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="pageData.attendance.top_modules.length > 0" class="card">
            <h3 class="font-bold mb-3 border-b pb-2">
              <i class="fa-solid fa-fighter-jet mr-1"></i> Top Modules
            </h3>
            <table class="w-full text-sm">
              <tbody>
                <tr v-for="m in pageData.attendance.top_modules" :key="m.module" class="border-b last:border-b-0">
                  <td class="py-1.5">{{ formatMissionName(m.module) }}</td>
                  <td class="py-1.5 text-right text-gray-600">{{ m.playtime_hours.toFixed(1) }}h</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>
