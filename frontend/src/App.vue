<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import { useHeaderStore } from '@/stores/header'
import { useVersionCheck } from '@/composables/useVersionCheck'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'
import VersionNotification from '@/components/ui/VersionNotification.vue'

const auth = useAuthStore()
const menu = useMenuStore()
const headerStore = useHeaderStore()
const { startVersionCheck, stopVersionCheck } = useVersionCheck()

onMounted(async () => {
  if (auth.isAuthenticated) {
    await auth.fetchUser()
  }
  await menu.fetchMenu()
  headerStore.startPolling()
  startVersionCheck()
})

onUnmounted(() => {
  headerStore.stopPolling()
  stopVersionCheck()
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
  <VersionNotification />
</template>
