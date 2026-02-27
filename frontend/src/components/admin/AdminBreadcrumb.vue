<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  label: string
  to?: string
  icon?: string
}

const props = defineProps<{
  pageTitle?: string
}>()

const route = useRoute()

const items = computed<BreadcrumbItem[]>(() => {
  const meta = (route.meta.breadcrumb as BreadcrumbItem[] | undefined) ?? []
  if (!meta.length) return []

  const result = meta.map((item) => ({ ...item }))

  if (props.pageTitle && result.length > 0) {
    result[result.length - 1].label = props.pageTitle
  }

  return result
})

const lastItem = computed(() => items.value[items.value.length - 1] ?? null)
</script>

<template>
  <div class="mb-6">
    <nav v-if="items.length" class="flex items-center text-sm text-gray-500 mb-1">
      <template v-for="(item, index) in items" :key="index">
        <i v-if="index > 0" class="fa-solid fa-chevron-right mx-2 text-xs text-gray-400"></i>
        <RouterLink
          :to="{ name: item.to ?? route.name as string }"
          class="transition-colors"
          :class="index === items.length - 1 ? 'text-gray-700 hover:text-veaf-600' : 'hover:text-veaf-600'"
        >
          <i v-if="item.icon" :class="item.icon" class="mr-1"></i>{{ item.label }}
        </RouterLink>
      </template>
    </nav>
    <h1 v-if="lastItem" class="text-2xl font-bold">{{ lastItem.label }}</h1>
  </div>
</template>
