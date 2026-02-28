<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { getRosterModuleDetail } from '@/api/roster'
import type { RosterModuleDetail } from '@/api/roster'
import { useRosterHelpers } from '@/composables/useRosterHelpers'

const props = defineProps<{
  moduleId: number
  group: string
  moduleType: number
}>()

const emit = defineEmits<{
  back: []
}>()

const { statusIcon } = useRosterHelpers()

const TYPES_WITH_LEVEL = [2, 3, 4]

const detail = ref<RosterModuleDetail | null>(null)
const loading = ref(true)

const hasLevel = computed(() => TYPES_WITH_LEVEL.includes(props.moduleType))

async function fetchDetail() {
  loading.value = true
  try {
    detail.value = await getRosterModuleDetail(props.moduleId, props.group)
  } finally {
    loading.value = false
  }
}

watch([() => props.moduleId, () => props.group], fetchDetail, { immediate: true })
</script>

<template>
  <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

  <div v-else-if="detail">
    <!-- Back button -->
    <button class="btn-secondary text-sm mb-4" @click="emit('back')">
      <i class="fa-solid fa-arrow-left mr-1"></i>Retour
    </button>

    <!-- Header image -->
    <div
      v-if="detail.module.image_header_uuid"
      class="mb-4 relative rounded-lg overflow-hidden"
    >
      <img
        :src="`/api/files/${detail.module.image_header_uuid}`"
        :alt="detail.module.long_name"
        class="w-full h-48 object-cover"
      />
      <div class="absolute inset-0 bg-black/30 flex items-end p-4">
        <h2 class="text-white text-xl font-bold">{{ detail.module.long_name }}</h2>
      </div>
    </div>
    <h2 v-else class="text-lg font-semibold mb-4">{{ detail.module.long_name }}</h2>

    <!-- Legend (only for types with level) -->
    <div
      v-if="hasLevel"
      class="bg-gray-50 rounded-lg p-4 mb-4 text-sm text-gray-700"
    >
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p class="font-medium mb-1">Activit&eacute; :</p>
          <ul class="space-y-1 ml-1">
            <li>
              <i class="fa-solid fa-plane text-green-600 mr-2 w-4 text-center"></i>Vole
              dessus
            </li>
            <li>
              <i class="fa-solid fa-warehouse text-gray-400 mr-2 w-4 text-center"></i>Au
              hangar
            </li>
          </ul>
        </div>
        <div>
          <p class="font-medium mb-1">Niveau :</p>
          <ul class="space-y-1 ml-1">
            <li>
              <i
                class="fa-solid fa-book-open-reader text-yellow-500 mr-2 w-4 text-center"
              ></i>D&eacute;butant
            </li>
            <li>
              <i
                class="fa-solid fa-shield-halved text-green-600 mr-2 w-4 text-center"
              ></i>Mission
            </li>
            <li>
              <i
                class="fa-solid fa-user-tie text-veaf-600 mr-2 w-4 text-center"
              ></i>Instructeur
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Pilots table -->
    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <tbody>
          <tr
            v-for="u in detail.users"
            :key="u.id"
            class="border-b hover:bg-gray-50"
          >
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
              <div class="flex items-center justify-end gap-3">
                <!-- Activity icon -->
                <i
                  v-if="u.active"
                  class="fa-solid fa-plane text-green-600"
                  title="Vole dessus"
                ></i>
                <i
                  v-else
                  class="fa-solid fa-warehouse text-gray-400"
                  title="Au hangar"
                ></i>
                <!-- Level icon (only for types with level) -->
                <template v-if="hasLevel">
                  <i
                    v-if="u.level === 3"
                    class="fa-solid fa-user-tie text-veaf-600"
                    title="Instructeur"
                  ></i>
                  <i
                    v-else-if="u.level === 2"
                    class="fa-solid fa-shield-halved text-green-600"
                    title="Mission"
                  ></i>
                  <i
                    v-else
                    class="fa-solid fa-book-open-reader text-yellow-500"
                    title="D&eacute;butant"
                  ></i>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
