<script setup lang="ts">
import { useVersionCheck } from '@/composables/useVersionCheck'

const { newVersionAvailable, reload } = useVersionCheck()
</script>

<template>
  <Transition name="slide-up">
    <div
      v-if="newVersionAvailable"
      class="fixed bottom-4 right-4 z-50 max-w-sm rounded-lg bg-veaf-700 text-white shadow-lg p-4 flex items-center gap-3"
    >
      <i class="fa-solid fa-arrow-rotate-right text-lg"></i>
      <div class="flex-1">
        <p class="text-sm font-medium">Une nouvelle version du site est disponible.</p>
      </div>
      <button
        class="btn-primary text-sm px-3 py-1.5 rounded whitespace-nowrap"
        @click="reload"
      >
        Recharger
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
</style>
