<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import NavMenu from './NavMenu.vue'

const auth = useAuthStore()
const menu = useMenuStore()
const router = useRouter()
const mobileMenuOpen = ref(false)

async function handleLogout() {
  await auth.logout()
  router.push('/')
}
</script>

<template>
  <header class="bg-gray-900 text-white shadow-lg">
    <div class="container mx-auto px-4">
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
          <template v-if="auth.isAuthenticated">
            <RouterLink to="/profile" class="text-gray-300 hover:text-white text-sm">
              {{ auth.user?.nickname }}
            </RouterLink>
            <RouterLink v-if="auth.isAdmin" to="/admin" class="text-yellow-400 hover:text-yellow-300 text-sm">
              Admin
            </RouterLink>
            <button @click="handleLogout" class="text-gray-400 hover:text-white text-sm">
              Déconnexion
            </button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="text-gray-300 hover:text-white text-sm">Connexion</RouterLink>
            <RouterLink to="/register" class="btn-primary text-sm !py-1">Inscription</RouterLink>
          </template>

          <!-- Mobile menu button -->
          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden text-gray-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <div v-if="mobileMenuOpen" class="md:hidden pb-4">
        <NavMenu :items="menu.items" :mobile="true" />
      </div>
    </div>
  </header>
</template>
