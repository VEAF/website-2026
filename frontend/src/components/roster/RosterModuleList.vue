<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getRosterModules } from '@/api/roster'
import type { RosterModule } from '@/api/roster'
import { MODULE_TYPE_AIRCRAFT } from '@/constants/modules'

const props = defineProps<{
  moduleType: number
  group: string
}>()

const emit = defineEmits<{
  'select-module': [id: number]
}>()

const modules = ref<RosterModule[]>([])
const loading = ref(true)
const sortBy = ref<'name' | 'count'>('name')

function percentage(mod: RosterModule): number {
  if (!mod.total_group_count) return 0
  return Math.round((mod.user_count / mod.total_group_count) * 100)
}

function sortModules(list: RosterModule[]): RosterModule[] {
  if (sortBy.value === 'count') {
    return [...list].sort((a, b) => b.user_count - a.user_count)
  }
  return list
}

interface PeriodGroup {
  period: number
  label: string
  modules: RosterModule[]
}

const groupedByPeriod = computed<PeriodGroup[]>(() => {
  const periodMap = new Map<number, PeriodGroup>()
  for (const m of modules.value) {
    const p = m.period ?? 0
    if (!periodMap.has(p)) {
      periodMap.set(p, { period: p, label: m.period_as_string ?? '', modules: [] })
    }
    periodMap.get(p)!.modules.push(m)
  }
  return [...periodMap.values()]
    .sort((a, b) => b.period - a.period)
    .map((g) => ({ ...g, modules: sortModules(g.modules) }))
})

const sortedModules = computed(() => sortModules(modules.value))

async function fetchModules() {
  loading.value = true
  try {
    modules.value = await getRosterModules(props.moduleType, props.group)
  } finally {
    loading.value = false
  }
}

watch([() => props.moduleType, () => props.group], fetchModules, { immediate: true })
</script>

<template>
  <div v-if="loading" class="text-center py-8 text-gray-500">Chargement...</div>

  <div v-else class="card">
    <!-- Sort controls -->
    <div class="flex items-center gap-2 mb-4 text-xs text-gray-500">
      <span>Trier par :</span>
      <button
        :class="[sortBy === 'name' ? 'font-bold text-veaf-700' : 'hover:text-veaf-600']"
        @click="sortBy = 'name'"
      >
        <i class="fa-solid fa-arrow-down-a-z mr-0.5"></i> Nom
      </button>
      <span class="text-gray-300">|</span>
      <button
        :class="[sortBy === 'count' ? 'font-bold text-veaf-700' : 'hover:text-veaf-600']"
        @click="sortBy = 'count'"
      >
        <i class="fa-solid fa-arrow-down-wide-short mr-0.5"></i> Nombre
      </button>
    </div>

    <!-- Aircraft: grouped by period -->
    <template v-if="moduleType === MODULE_TYPE_AIRCRAFT">
      <template v-for="periodGroup in groupedByPeriod" :key="periodGroup.period">
        <div
          v-if="periodGroup.label"
          class="text-xs font-bold text-gray-500 uppercase tracking-wide mt-4 mb-2 px-2 first:mt-0"
        >
          {{ periodGroup.label }}
        </div>
        <div
          v-for="mod in periodGroup.modules"
          :key="mod.id"
          class="flex items-center gap-3 py-2 px-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer text-sm"
          @click="emit('select-module', mod.id)"
        >
          <span class="w-48 shrink-0 truncate">{{ mod.long_name }}</span>
          <div class="progress flex-1">
            <div
              class="progress-bar"
              :style="{ width: percentage(mod) + '%' }"
            >
              <span v-if="percentage(mod) >= 10">{{ percentage(mod) }}%</span>
            </div>
          </div>
          <span
            class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 shrink-0"
          >
            {{ mod.user_count }}
          </span>
        </div>
      </template>
    </template>

    <!-- Other types: flat list -->
    <template v-else>
      <div
        v-for="mod in sortedModules"
        :key="mod.id"
        class="flex items-center gap-3 py-2 px-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer text-sm"
        @click="emit('select-module', mod.id)"
      >
        <span class="w-48 shrink-0 truncate">{{ mod.long_name }}</span>
        <div class="progress flex-1">
          <div
            class="progress-bar"
            :style="{ width: percentage(mod) + '%' }"
          >
            <span v-if="percentage(mod) >= 10">{{ percentage(mod) }}%</span>
          </div>
        </div>
        <span
          class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 shrink-0"
        >
          {{ mod.user_count }}
        </span>
      </div>
    </template>
  </div>
</template>
