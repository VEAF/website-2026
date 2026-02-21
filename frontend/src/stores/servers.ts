import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getServers, getHeaderData } from '@/api/servers'
import type { Server, HeaderData } from '@/types/api'

export const useServersStore = defineStore('servers', () => {
  const servers = ref<Server[]>([])
  const headerData = ref<HeaderData | null>(null)

  async function fetchServers() {
    servers.value = await getServers()
  }

  async function fetchHeaderData() {
    headerData.value = await getHeaderData()
  }

  return { servers, headerData, fetchServers, fetchHeaderData }
})
