import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { getServers, getHeaderData } from '@/api/servers'
import type { Server, HeaderData } from '@/types/api'

const POLL_INTERVAL = 60_000 // 60 seconds

export const useHeaderStore = defineStore('header', () => {
  const servers = ref<Server[]>([])
  const headerData = ref<HeaderData | null>(null)
  let pollTimer: ReturnType<typeof setInterval> | null = null

  const connectedPlayers = computed(() => headerData.value?.connected_players ?? 0)
  const nextEventsCount = computed(() => headerData.value?.next_events_count ?? 0)

  async function fetchServers() {
    servers.value = await getServers()
  }

  async function fetchHeaderData() {
    try {
      headerData.value = await getHeaderData()
    } catch {
      headerData.value = null
    }
  }

  function startPolling() {
    if (pollTimer !== null) return
    fetchHeaderData()
    pollTimer = setInterval(fetchHeaderData, POLL_INTERVAL)
  }

  function stopPolling() {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return {
    servers,
    headerData,
    connectedPlayers,
    nextEventsCount,
    fetchServers,
    fetchHeaderData,
    startPolling,
    stopPolling,
  }
})
