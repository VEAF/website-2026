<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import apiClient from '@/api/client'
import { getDiscordVoiceStatus } from '@/api/discord-voice'
import type { DiscordVoiceStatus, DiscordVoiceChannel } from '@/types/discord-voice'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'

const POLL_INTERVAL = 60_000 // 60 seconds

const statusData = ref<DiscordVoiceStatus | null>(null)
const loading = ref(true)
const error = ref(false)
const discordSupportUrl = ref<string | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchDiscordSupportUrl() {
  try {
    const { data } = await apiClient.get('/')
    discordSupportUrl.value = data.discord_support_url || null
  } catch {
    // Ignore
  }
}

async function fetchData() {
  loading.value = true
  error.value = false
  try {
    statusData.value = await getDiscordVoiceStatus()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  try {
    statusData.value = await getDiscordVoiceStatus()
    error.value = false
  } catch {
    // Keep previous data on refresh error
  }
}

onMounted(() => {
  fetchData()
  fetchDiscordSupportUrl()
  pollTimer = setInterval(refreshData, POLL_INTERVAL)
})

onUnmounted(() => {
  if (pollTimer !== null) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})

const activeChannels = computed<DiscordVoiceChannel[]>(() => {
  if (!statusData.value) return []
  return statusData.value.channels.filter(ch => ch.users.length > 0)
})
</script>

<template>
  <div>
    <AppBreadcrumb :show-title="false" />
    <h1 class="text-2xl font-bold mb-6">
      <i class="fa-brands fa-discord mr-2"></i>Utilisateurs connectés en vocal sur Discord
    </h1>

    <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

    <div v-else-if="error" class="card text-center py-8 text-red-600">
      <i class="fa-solid fa-exclamation-triangle mr-1"></i>
      Impossible de charger le statut Discord
      <button @click="fetchData" class="btn-primary text-sm ml-4">Réessayer</button>
    </div>

    <template v-else-if="statusData">
      <div v-if="!statusData.configured" class="card text-center py-8 text-gray-500">
        Le serveur Discord n'est pas configuré.
      </div>

      <template v-else>
        <div v-if="statusData.user_count === 0" class="card py-4 px-6 mb-6 bg-yellow-50 border-yellow-200 text-yellow-800">
          <i class="fa-solid fa-info-circle mr-1"></i>
          Aucun utilisateur connecté en vocal pour l'instant.
        </div>

        <div v-if="activeChannels.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div
            v-for="channel in activeChannels"
            :key="channel.channel_id"
            class="card"
          >
            <div class="font-semibold text-veaf-700 border-b pb-2 mb-2">
              <i class="fa-solid fa-volume-high mr-1 text-xs"></i>{{ channel.name }}
            </div>
            <ul class="space-y-1">
              <li v-for="user in channel.users" :key="user.user_id" class="text-sm text-gray-700">
                <i class="fa-solid fa-user text-gray-400 mr-1 text-xs"></i>{{ user.nickname }}
              </li>
            </ul>
          </div>
        </div>

        <div class="card">
          <h2 class="text-xl font-bold mb-4">
            <i class="fa-brands fa-discord mr-2"></i>Pour nous rejoindre sur Discord
          </h2>
          <div v-if="discordSupportUrl" class="mt-2">
            <a
              :href="discordSupportUrl"
              target="_blank"
              rel="noopener"
              class="btn-primary inline-flex items-center"
            >
              <i class="fa-brands fa-discord mr-2"></i>
              Rejoindre le serveur Discord VEAF
            </a>
          </div>
          <p v-else class="text-gray-700">
            Contactez un membre de la VEAF pour obtenir une invitation Discord.
          </p>
        </div>
      </template>
    </template>
  </div>
</template>
