<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { getRosterPilots } from '@/api/roster'
import type { RosterUser, RosterUserModule } from '@/api/roster'
import { useRosterHelpers } from '@/composables/useRosterHelpers'

const props = defineProps<{
  group: string
}>()

const { statusIcon, levelBadge, levelClass } = useRosterHelpers()

const users = ref<RosterUser[]>([])
const loading = ref(true)

function activeModules(user: RosterUser): RosterUserModule[] {
  return user.modules.filter((m) => m.active && m.level > 0)
}

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

  <div v-else class="overflow-x-auto">
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
          </td>
          <td class="py-2 px-3 text-right">
            <div class="flex flex-wrap justify-end gap-1">
              <span
                v-for="m in activeModules(u)"
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
</template>
