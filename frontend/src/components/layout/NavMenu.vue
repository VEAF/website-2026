<script setup lang="ts">
import type { MenuItem } from '@/types/api'
import { useHeaderStore } from '@/stores/header'

defineProps<{
  items: MenuItem[]
  mobile?: boolean
}>()

const headerStore = useHeaderStore()

function getItemLink(item: MenuItem): string | null {
  // Type-based routing
  switch (item.type) {
    case 2: // TYPE_LINK
      return item.link
    case 3: // TYPE_URL
      return item.url_slug ? `/${item.url_slug}` : null
    case 4: // TYPE_PAGE
      return item.page_path ? `/${item.page_path}` : null
    case 6: // TYPE_OFFICE
      return '/office'
    case 7: // TYPE_SERVERS
      return '/servers'
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
          <i class="fa-solid fa-chevron-down ml-1 text-xs"></i>
        </button>
        <div class="absolute left-0 mt-1 w-48 bg-gray-800 rounded-md shadow-lg py-1 z-50 hidden group-hover:block">
          <template v-for="child in item.items" :key="child.id">
            <div v-if="child.type === 5" class="border-t border-gray-700 my-1" />
            <RouterLink
              v-else-if="getItemLink(child)"
              :to="getItemLink(child)!"
              class="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-700"
            >
              <span v-if="child.icon" class="mr-1"><i :class="child.icon" /></span>
              {{ child.label }}
            </RouterLink>
          </template>
        </div>
      </div>

      <!-- Servers link with player count badge -->
      <RouterLink
        v-else-if="item.type === 7"
        to="/servers"
        class="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md"
        :class="item.theme_classes"
        :title="headerStore.connectedPlayers > 0 ? `${headerStore.connectedPlayers} joueur(s) connecté(s)` : undefined"
      >
        <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
        <template v-if="headerStore.connectedPlayers > 0">
          <span class="inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-white">
            {{ headerStore.connectedPlayers }}
          </span>
          <span class="ml-1">joueur(s)</span>
        </template>
        <template v-else>
          {{ item.label }}
        </template>
      </RouterLink>

      <!-- Calendar link with events count badge -->
      <RouterLink
        v-else-if="item.type === 9"
        to="/calendar"
        class="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md"
        :class="item.theme_classes"
        :title="headerStore.nextEventsCount > 0 ? `${headerStore.nextEventsCount} événement(s) dans les 7 prochains jours` : undefined"
      >
        <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
        <template v-if="headerStore.nextEventsCount > 0">
          <span class="inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-white">
            {{ headerStore.nextEventsCount }}
          </span>
          <span class="ml-1">événement(s)</span>
        </template>
        <template v-else>
          {{ item.label }}
        </template>
      </RouterLink>

      <!-- TeamSpeak link with client count badge -->
      <RouterLink
        v-else-if="item.type === 11"
        to="/teamspeak"
        class="px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md"
        :class="item.theme_classes"
        :title="headerStore.tsClientCount > 0 ? `${headerStore.tsClientCount} client(s) connecté(s) sur TeamSpeak` : undefined"
      >
        <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
        <template v-if="headerStore.tsClientCount > 0">
          <span class="inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-white">
            {{ headerStore.tsClientCount }}
          </span>
          <span class="ml-1">client(s)</span>
        </template>
        <template v-else>
          {{ item.label }}
        </template>
      </RouterLink>

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
