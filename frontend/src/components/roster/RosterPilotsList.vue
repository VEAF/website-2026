<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { getRosterPilots } from '@/api/roster'
import type { RosterUser } from '@/api/roster'
import { useRosterHelpers } from '@/composables/useRosterHelpers'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  group: string
}>()

const { statusIcon } = useRosterHelpers()
const authStore = useAuthStore()

const users = ref<RosterUser[]>([])
const loading = ref(true)

async function fetchPilots() {
  loading.value = true
  try {
    users.value = await getRosterPilots(props.group)
  } finally {
    loading.value = false
  }
}

watch(() => props.group, fetchPilots, { immediate: true })
</script>

<template>
  <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

  <div v-else class="card overflow-x-auto">
    <table class="w-full text-sm">
      <tbody>
        <tr v-for="u in users" :key="u.id" class="border-b hover:bg-gray-50">
          <td class="py-2 px-3">
            <i
              :class="[statusIcon(u.status).icon, statusIcon(u.status).class]"
              :title="statusIcon(u.status).title"
              class="mr-2"
            ></i>
            <RouterLink
              :to="`/user/${u.nickname}`"
              class="text-veaf-600 hover:text-veaf-800 font-medium"
            >
              {{ u.nickname }}
            </RouterLink>
            <span
              v-if="authStore.isMember && u.need_presentation"
              class="ml-2 inline-flex items-center px-1.5 py-0.5 rounded-full text-xs bg-yellow-100 text-yellow-700"
              title="Ce pilote a besoin d'une présentation de l'association"
            >
              <i class="fa-solid fa-bullhorn"></i>
            </span>
          </td>
          <td class="py-2 px-3 text-right">
            <span
              v-if="u.active_module_count > 0"
              class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-veaf-100 text-veaf-800"
              :title="`${u.active_module_count} module(s) actif(s)`"
            >
              {{ u.active_module_count }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
