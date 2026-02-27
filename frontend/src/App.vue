<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import { useHeaderStore } from '@/stores/header'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

const auth = useAuthStore()
const menu = useMenuStore()
const headerStore = useHeaderStore()

onMounted(async () => {
  if (auth.isAuthenticated) {
    await auth.fetchUser()
  }
  await menu.fetchMenu()
  headerStore.startPolling()
})

onUnmounted(() => {
  headerStore.stopPolling()
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1" :class="$route.meta.fullWidth ? '' : 'page-container py-6'">
      <RouterView />
    </main>
    <AppFooter />
  </div>
  <ConfirmModal />
</template>
