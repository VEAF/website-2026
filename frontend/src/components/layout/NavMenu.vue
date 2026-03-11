<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { MenuItem } from '@/types/api'
import { useHeaderStore } from '@/stores/header'

defineProps<{
  items: MenuItem[]
  mobile?: boolean
}>()

const route = useRoute()
const headerStore = useHeaderStore()
const openDropdownId = ref<number | null>(null)
const navRef = ref<HTMLElement | null>(null)

function toggleDropdown(itemId: number) {
  openDropdownId.value = openDropdownId.value === itemId ? null : itemId
}

function closeAllDropdowns() {
  openDropdownId.value = null
}

function onClickOutside(event: MouseEvent) {
  if (navRef.value && !navRef.value.contains(event.target as Node)) {
    closeAllDropdowns()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
})

watch(() => route.fullPath, () => {
  closeAllDropdowns()
})

function isExternalLink(link: string | null): boolean {
  return !!link && link.includes('://')
}

// Badge config for menu items that show a count indicator
const badgeItems: Record<number, { to: string; count: () => number; label: string; tooltip: string }> = {
  7: { to: '/servers', count: () => headerStore.connectedPlayers, label: 'joueur(s)', tooltip: 'joueur(s) connecté(s)' },
  9: { to: '/calendar', count: () => headerStore.nextEventsCount, label: 'événement(s)', tooltip: 'événement(s) dans les 7 prochains jours' },
  11: { to: '/teamspeak', count: () => headerStore.tsClientCount, label: 'client(s)', tooltip: 'client(s) connecté(s) sur TeamSpeak' },
  12: { to: '/discord', count: () => headerStore.discordVoiceCount, label: 'en vocal', tooltip: 'utilisateur(s) en vocal sur Discord' },
}

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
    case 12: // TYPE_DISCORD_VOICE
      return '/discord'
    default:
      return null
  }
}
</script>

<template>
  <div ref="navRef" :class="mobile ? 'flex flex-col space-y-1' : 'flex items-center space-x-1'">
    <template v-for="item in items" :key="item.id">
      <!-- Divider -->
      <div v-if="item.type === 5" :class="mobile ? 'border-t border-white/20 my-2' : 'w-px h-6 bg-white/30'" />

      <!-- Dropdown menu (desktop) -->
      <div v-else-if="item.type === 1 && item.items.length > 0 && !mobile" class="relative">
        <button
          @click="toggleDropdown(item.id)"
          class="px-3 py-2 text-sm text-white hover:text-white hover:bg-white/10 rounded-md"
        >
          <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
          {{ item.label }}
          <i
            class="fa-solid fa-chevron-down ml-1 text-xs transition-transform"
            :class="{ 'rotate-180': openDropdownId === item.id }"
          ></i>
        </button>
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <div
            v-if="openDropdownId === item.id"
            class="absolute left-0 mt-1 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
          >
            <template v-for="child in item.items" :key="child.id">
              <div v-if="child.type === 5" class="border-t border-gray-200 my-1" />
              <a
                v-else-if="isExternalLink(getItemLink(child))"
                :href="getItemLink(child)!"
                target="_blank"
                rel="noopener noreferrer"
                class="block px-4 py-2 text-sm text-gray-700 hover:text-veaf-600 hover:bg-gray-50"
              >
                <span v-if="child.icon" class="mr-1"><i :class="child.icon" /></span>
                {{ child.label }}
              </a>
              <RouterLink
                v-else-if="getItemLink(child)"
                :to="getItemLink(child)!"
                class="block px-4 py-2 text-sm text-gray-700 hover:text-veaf-600 hover:bg-gray-50"
              >
                <span v-if="child.icon" class="mr-1"><i :class="child.icon" /></span>
                {{ child.label }}
              </RouterLink>
            </template>
          </div>
        </Transition>
      </div>

      <!-- Dropdown menu (mobile - accordion) -->
      <div v-else-if="item.type === 1 && item.items.length > 0 && mobile">
        <button
          @click="toggleDropdown(item.id)"
          class="w-full text-left px-3 py-2 text-sm text-white hover:text-white hover:bg-white/10 rounded-md"
        >
          <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
          {{ item.label }}
          <i
            class="fa-solid fa-chevron-down ml-1 text-xs transition-transform"
            :class="{ 'rotate-180': openDropdownId === item.id }"
          ></i>
        </button>
        <div v-if="openDropdownId === item.id" class="pl-4 space-y-1">
          <template v-for="child in item.items" :key="child.id">
            <div v-if="child.type === 5" class="border-t border-white/20 my-1" />
            <a
              v-else-if="isExternalLink(getItemLink(child))"
              :href="getItemLink(child)!"
              target="_blank"
              rel="noopener noreferrer"
              class="block px-3 py-2 text-sm text-white hover:text-white hover:bg-white/10 rounded-md"
            >
              <span v-if="child.icon" class="mr-1"><i :class="child.icon" /></span>
              {{ child.label }}
            </a>
            <RouterLink
              v-else-if="getItemLink(child)"
              :to="getItemLink(child)!"
              class="block px-3 py-2 text-sm text-white hover:text-white hover:bg-white/10 rounded-md"
            >
              <span v-if="child.icon" class="mr-1"><i :class="child.icon" /></span>
              {{ child.label }}
            </RouterLink>
          </template>
        </div>
      </div>

      <!-- Badge link (servers, calendar, teamspeak, discord) -->
      <RouterLink
        v-else-if="badgeItems[item.type]"
        :to="badgeItems[item.type].to"
        class="px-3 py-2 text-sm text-white hover:text-white hover:bg-white/10 rounded-md"
        :class="item.theme_classes"
        :title="badgeItems[item.type].count() > 0 ? `${badgeItems[item.type].count()} ${badgeItems[item.type].tooltip}` : undefined"
      >
        <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
        <template v-if="badgeItems[item.type].count() > 0">
          <span class="inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white">
            {{ badgeItems[item.type].count() }}
          </span>
          <span class="ml-1">{{ badgeItems[item.type].label }}</span>
        </template>
        <template v-else>
          {{ item.label }}
        </template>
      </RouterLink>

      <!-- External link -->
      <a
        v-else-if="isExternalLink(getItemLink(item))"
        :href="getItemLink(item)!"
        target="_blank"
        rel="noopener noreferrer"
        class="px-3 py-2 text-sm text-white hover:text-white hover:bg-white/10 rounded-md"
        :class="item.theme_classes"
      >
        <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
        {{ item.label }}
      </a>

      <!-- Regular link -->
      <RouterLink
        v-else-if="getItemLink(item)"
        :to="getItemLink(item)!"
        class="px-3 py-2 text-sm text-white hover:text-white hover:bg-white/10 rounded-md"
        :class="item.theme_classes"
      >
        <span v-if="item.icon" class="mr-1"><i :class="item.icon" /></span>
        {{ item.label }}
      </RouterLink>
    </template>
  </div>
</template>
