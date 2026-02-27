<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import NavMenu from './NavMenu.vue'

const auth = useAuthStore()
const menu = useMenuStore()
const router = useRouter()
const route = useRoute()
const mobileMenuOpen = ref(false)
const userDropdownOpen = ref(false)
const userDropdownRef = ref<HTMLElement | null>(null)

function toggleUserDropdown() {
  userDropdownOpen.value = !userDropdownOpen.value
}

function closeUserDropdown() {
  userDropdownOpen.value = false
}

function onClickOutside(event: MouseEvent) {
  if (userDropdownRef.value && !userDropdownRef.value.contains(event.target as Node)) {
    closeUserDropdown()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
})

watch(() => route.fullPath, () => {
  closeUserDropdown()
  mobileMenuOpen.value = false
})

async function handleLogout() {
  closeUserDropdown()
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <header class="bg-gray-900 text-white shadow-lg">
    <div class="page-container">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center space-x-2 text-white hover:text-gray-300">
          <span class="text-xl font-bold">VEAF</span>
        </RouterLink>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex items-center space-x-1">
          <NavMenu :items="menu.items" />
        </nav>

        <!-- User actions -->
        <div class="flex items-center space-x-4">
          <!-- Authenticated: dropdown menu -->
          <div v-if="auth.isAuthenticated" ref="userDropdownRef" class="relative hidden md:block">
            <button
              @click="toggleUserDropdown"
              class="flex items-center text-gray-300 hover:text-white text-sm px-3 py-2 rounded-md hover:bg-gray-800"
            >
              <i class="fa-solid fa-user mr-1"></i>
              {{ auth.user?.nickname }}
              <i
                class="fa-solid fa-chevron-down ml-1 text-xs transition-transform"
                :class="{ 'rotate-180': userDropdownOpen }"
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
                v-if="userDropdownOpen"
                class="absolute right-0 mt-1 w-48 bg-gray-800 rounded-md shadow-lg py-1 z-50"
              >
                <RouterLink
                  to="/profile"
                  class="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-700"
                >
                  <i class="fa-solid fa-user mr-1"></i>Mon profil
                </RouterLink>
                <RouterLink
                  v-if="auth.isAdmin"
                  to="/admin"
                  class="block px-4 py-2 text-sm text-yellow-400 hover:text-yellow-300 hover:bg-gray-700"
                >
                  <i class="fa-solid fa-gear mr-1"></i>Administration
                </RouterLink>
                <div class="border-t border-gray-700 my-1"></div>
                <button
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-700"
                >
                  <i class="fa-solid fa-right-from-bracket mr-1"></i>Déconnexion
                </button>
              </div>
            </Transition>
          </div>

          <!-- Not authenticated -->
          <template v-if="!auth.isAuthenticated">
            <RouterLink to="/login" class="text-gray-300 hover:text-white text-sm"><i class="fa-solid fa-right-to-bracket mr-1"></i>Connexion</RouterLink>
          </template>

          <!-- Mobile menu button -->
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden text-gray-400 hover:text-white">
            <i :class="mobileMenuOpen ? 'fa-solid fa-xmark' : 'fa-solid fa-bars'" class="text-xl"></i>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="mobileMenuOpen" class="md:hidden pb-4">
        <NavMenu :items="menu.items" :mobile="true" />

        <!-- Mobile user actions -->
        <div class="border-t border-gray-700 mt-2 pt-2">
          <template v-if="auth.isAuthenticated">
            <RouterLink
              to="/profile"
              class="block px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md"
            >
              <i class="fa-solid fa-user mr-1"></i>Mon profil
            </RouterLink>
            <RouterLink
              v-if="auth.isAdmin"
              to="/admin"
              class="block px-3 py-2 text-sm text-yellow-400 hover:text-yellow-300 hover:bg-gray-800 rounded-md"
            >
              <i class="fa-solid fa-gear mr-1"></i>Administration
            </RouterLink>
            <button
              @click="handleLogout"
              class="block w-full text-left px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-md"
            >
              <i class="fa-solid fa-right-from-bracket mr-1"></i>Déconnexion
            </button>
          </template>
          <template v-else>
            <RouterLink
              to="/login"
              class="block px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md"
            >
              <i class="fa-solid fa-right-to-bracket mr-1"></i>Connexion
            </RouterLink>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>
