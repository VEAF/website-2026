<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbItem {
  label: string
  to?: string
  icon?: string
}

const props = withDefaults(
  defineProps<{
    pageTitle?: string
    showTitle?: boolean
  }>(),
  { showTitle: true },
)

const route = useRoute()

const items = computed<BreadcrumbItem[]>(() => {
  const meta = (route.meta.breadcrumb as BreadcrumbItem[] | undefined) ?? []
  const result: BreadcrumbItem[] = [
    { label: 'Accueil', to: 'home', icon: 'fa-solid fa-house' },
    ...meta.map((item) => ({ ...item })),
  ]

  if (props.pageTitle && result.length > 1) {
    result[result.length - 1].label = props.pageTitle
  }

  return result
})

const lastItem = computed(() => items.value[items.value.length - 1] ?? null)
</script>

<template>
  <div v-if="items.length > 1" class="mb-6">
    <nav class="flex items-center overflow-x-auto scrollbar-hide" aria-label="Fil d'Ariane">
      <ol class="flex items-center flex-nowrap">
        <li v-for="(item, index) in items" :key="index" class="flex-shrink-0">
          <component
            :is="index < items.length - 1 && item.to ? 'RouterLink' : 'span'"
            v-bind="index < items.length - 1 && item.to ? { to: { name: item.to } } : {}"
            class="breadcrumb-segment"
            :class="[
              index === 0 ? 'breadcrumb-segment-first' : '',
              index === items.length - 1
                ? 'breadcrumb-segment-active breadcrumb-segment-info'
                : 'breadcrumb-segment-primary',
            ]"
            :style="{ zIndex: items.length - index }"
          >
            <i v-if="item.icon" :class="item.icon" class="mr-1.5 text-xs"></i>
            <span>{{ item.label }}</span>
          </component>
        </li>
      </ol>
      <slot name="after" />
    </nav>
    <h1 v-if="showTitle && lastItem" class="text-2xl font-bold mt-3">
      {{ lastItem.label }}
    </h1>
  </div>
</template>
