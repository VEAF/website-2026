<script setup lang="ts">
import type { MenuItem } from '@/types/api'

defineProps<{
  items: MenuItem[]
  mobile?: boolean
}>()

function getItemLink(item: MenuItem): string | null {
  // Type-based routing
  switch (item.type) {
    case 2: // TYPE_LINK
      return item.link
    case 3: // TYPE_URL
      return item.url_slug ? `/${item.url_slug}` : null
    case 4: // TYPE_PAGE
      return item.page_path ? `/pages/${item.page_path}` : null
    case 6: // TYPE_OFFICE
      return '/office'
    case 7: // TYPE_SERVERS
      return null // Dynamic
    case 8: // TYPE_ROSTER
      return '/roster'
    case 9: // TYPE_CALENDAR
      return '/calendar'
    case 10: // TYPE_MISSION_MAKER
      return '/mission-maker'
    case 11: // TYPE_TEAMSPEAK
      return '/teamspeak'
    default:
      return null
  }
}
</script>

<template>
  <div :class="mobile ? 'flex flex-col space-y-1' : 'flex items-center space-x-1'">
    <template v-for="item in items" :key="item.id">
      <!-- Divider -->
      <div v-if="item.type === 5" :class="mobile ? 'border-t border-gray-700 my-2' : 'w-px h-6 bg-gray-600'" />

      <!-- Dropdown menu -->
      <div v-else-if="item.type === 1 && item.items.length > 0" class="relative group">
        <button class="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md">
          <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
          {{ item.label }}
          <svg class="inline-block w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <div class="absolute left-0 mt-1 w-48 bg-gray-800 rounded-md shadow-lg py-1 z-50 hidden group-hover:block">
          <template v-for="child in item.items" :key="child.id">
            <div v-if="child.type === 5" class="border-t border-gray-700 my-1" />
            <RouterLink
              v-else-if="getItemLink(child)"
              :to="getItemLink(child)!"
              class="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-700"
            >
              {{ child.label }}
            </RouterLink>
          </template>
        </div>
      </div>

      <!-- Regular link -->
      <RouterLink
        v-else-if="getItemLink(item)"
        :to="getItemLink(item)!"
        class="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md"
        :class="item.theme_classes"
      >
        <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
        {{ item.label }}
      </RouterLink>
    </template>
  </div>
</template>
