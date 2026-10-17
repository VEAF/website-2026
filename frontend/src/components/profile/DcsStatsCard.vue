<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getUserDcsStats } from '@/api/users'
import type { UserDcsStats } from '@/types/user'

const props = defineProps<{ userId: number }>()

const data = ref<UserDcsStats | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    data.value = await getUserDcsStats(props.userId)
  } catch {
    data.value = null
  } finally {
    loading.value = false
  }
})

const stats = computed(() => data.value?.stats ?? null)

function formatPlaytime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return hours > 0 ? `${hours} h ${minutes.toString().padStart(2, '0')}` : `${minutes} min`
}

const tiles = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { label: 'Temps de vol', value: formatPlaytime(s.playtime), icon: 'fa-solid fa-clock' },
    { label: 'Victoires', value: s.kills, icon: 'fa-solid fa-crosshairs' },
    { label: 'Morts', value: s.deaths, icon: 'fa-solid fa-skull' },
    { label: 'Ratio V/M', value: s.kdr.toFixed(2), icon: 'fa-solid fa-scale-balanced' },
    { label: 'Décollages', value: s.takeoffs, icon: 'fa-solid fa-plane-departure' },
    { label: 'Atterrissages', value: s.landings, icon: 'fa-solid fa-plane-arrival' },
  ]
})

const killDetails = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { label: 'Avions', value: s.kills_planes },
    { label: 'Hélicoptères', value: s.kills_helicopters },
    { label: 'Sol', value: s.kills_ground },
    { label: 'Navires', value: s.kills_ships },
    { label: 'SAM', value: s.kills_sams },
    { label: 'PvP', value: s.kills_pvp },
  ].filter((d) => d.value > 0)
})

const topModules = computed(() =>
  (stats.value?.kills_by_module ?? []).filter((m) => (m.kills ?? 0) > 0).slice(0, 5),
)
</script>

<template>
  <div v-if="!loading && data?.has_player" class="card mb-6">
    <h2 class="text-lg font-semibold mb-4">
      <i class="fa-solid fa-chart-line mr-1"></i>Statistiques DCS
    </h2>

    <p v-if="!stats" class="text-sm text-gray-500">Statistiques indisponibles pour le moment.</p>

    <template v-else>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
        <div v-for="t in tiles" :key="t.label" class="border border-gray-200 rounded-md p-3 text-center">
          <div class="text-xs text-gray-500"><i :class="t.icon" class="mr-1"></i>{{ t.label }}</div>
          <div class="text-xl font-bold text-veaf-600">{{ t.value }}</div>
        </div>
      </div>

      <div v-if="killDetails.length" class="text-sm text-gray-600 mb-2">
        <span class="font-medium">Victoires :</span>
        <span v-for="(d, i) in killDetails" :key="d.label">
          {{ d.label }} {{ d.value }}<template v-if="i < killDetails.length - 1"> · </template>
        </span>
      </div>

      <div v-if="topModules.length" class="text-sm text-gray-600">
        <span class="font-medium">Modules les plus efficaces :</span>
        <span v-for="(m, i) in topModules" :key="m.module">
          {{ m.module }} ({{ m.kills }})<template v-if="i < topModules.length - 1"> · </template>
        </span>
      </div>

      <p class="text-xs text-gray-400 mt-3">Tous serveurs VEAF confondus, d'après DCSServerBot.</p>
    </template>
  </div>
</template>
