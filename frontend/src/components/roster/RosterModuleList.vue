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
  return [...periodMap.values()].sort((a, b) => b.period - a.period)
})

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
          class="flex items-center justify-between py-2 px-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer text-sm"
          @click="emit('select-module', mod.id)"
        >
          <span>{{ mod.long_name }}</span>
          <span
            class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
          >
            {{ mod.user_count }}
          </span>
        </div>
      </template>
    </template>

    <!-- Other types: flat list -->
    <template v-else>
      <div
        v-for="mod in modules"
        :key="mod.id"
        class="flex items-center justify-between py-2 px-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer text-sm"
        @click="emit('select-module', mod.id)"
      >
        <span>{{ mod.long_name }}</span>
        <span
          class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
        >
          {{ mod.user_count }}
        </span>
      </div>
    </template>
  </div>
</template>
