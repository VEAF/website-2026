<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getTeamSpeakStatus } from '@/api/teamspeak'
import type { TSStatus, TSChannel } from '@/types/teamspeak'

const POLL_INTERVAL = 60_000 // 60 seconds

const statusData = ref<TSStatus | null>(null)
const loading = ref(true)
const error = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchData() {
  loading.value = true
  error.value = false
  try {
    statusData.value = await getTeamSpeakStatus()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  try {
    statusData.value = await getTeamSpeakStatus()
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

const activeChannels = computed<TSChannel[]>(() => {
  if (!statusData.value) return []
  return statusData.value.channels.filter(ch => ch.clients.length > 0)
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">
      <i class="fa-brands fa-teamspeak mr-2"></i>Clients connectés sur TeamSpeak
    </h1>

    <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

    <div v-else-if="error" class="card text-center py-8 text-red-600">
      <i class="fa-solid fa-exclamation-triangle mr-1"></i>
      Impossible de charger le statut TeamSpeak
      <button @click="fetchData" class="btn-primary text-sm ml-4">Réessayer</button>
    </div>

    <template v-else-if="statusData">
      <div v-if="!statusData.configured" class="card text-center py-8 text-gray-500">
        Le serveur TeamSpeak n'est pas configuré.
      </div>

      <template v-else>
        <div v-if="statusData.client_count === 0" class="card py-4 px-6 mb-6 bg-yellow-50 border-yellow-200 text-yellow-800">
          <i class="fa-solid fa-info-circle mr-1"></i>
          Aucun client connecté sur le serveur pour l'instant.
        </div>

        <div v-if="activeChannels.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div
            v-for="channel in activeChannels"
            :key="channel.cid"
            class="card"
          >
            <div class="font-semibold text-veaf-700 border-b pb-2 mb-2">
              <i class="fa-solid fa-hashtag mr-1 text-xs"></i>{{ channel.name }}
            </div>
            <ul class="space-y-1">
              <li v-for="client in channel.clients" :key="client.clid" class="text-sm text-gray-700">
                <i class="fa-solid fa-user text-gray-400 mr-1 text-xs"></i>{{ client.nickname }}
              </li>
            </ul>
          </div>
        </div>

        <div class="card">
          <h2 class="text-xl font-bold mb-4">
            <i class="fa-solid fa-headset mr-2"></i>Pour nous rejoindre sur TeamSpeak
          </h2>
          <ul class="list-disc list-inside space-y-2 text-gray-700">
            <li>
              Télécharger le client TeamSpeak sur la page officielle :
              <a
                href="https://www.teamspeak.com/fr/downloads/"
                target="_blank"
                rel="noopener"
                class="text-veaf-600 hover:text-veaf-800 underline"
              >
                télécharger TeamSpeak
              </a>
            </li>
            <li v-if="statusData.server_host">
              Une fois installé,
              <a
                :href="`ts3server://${statusData.server_host}`"
                class="text-veaf-600 hover:text-veaf-800 underline"
              >
                cliquer ici pour une connexion rapide
              </a>
            </li>
          </ul>
        </div>
      </template>
    </template>
  </div>
</template>
