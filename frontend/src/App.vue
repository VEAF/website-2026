<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'

const auth = useAuthStore()
const menu = useMenuStore()

onMounted(async () => {
  if (auth.isAuthenticated) {
    await auth.fetchUser()
  }
  await menu.fetchMenu()
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1" :class="$route.meta.fullWidth ? '' : 'container mx-auto px-4 py-6'">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>
