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
              <i class="fa-solid fa-user mr-1"></i>{{ auth.user?.nickname }}
            </RouterLink>
            <RouterLink v-if="auth.isAdmin" to="/admin" class="text-yellow-400 hover:text-yellow-300 text-sm">
              <i class="fa-solid fa-gear mr-1"></i>Admin
            </RouterLink>
            <button @click="handleLogout" class="text-gray-400 hover:text-white text-sm">
              <i class="fa-solid fa-right-from-bracket mr-1"></i>Déconnexion
            </button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="text-gray-300 hover:text-white text-sm"><i class="fa-solid fa-right-to-bracket mr-1"></i>Connexion</RouterLink>
            <RouterLink to="/register" class="btn-primary text-sm !py-1">Inscription</RouterLink>
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
      </div>
    </div>
  </header>
</template>
