<script setup lang="ts">
import { useDiscordSupport } from '@/composables/useDiscordSupport'

const { visible, discordUrl, close } = useDiscordSupport()

function openDiscord() {
  window.open(discordUrl.value, '_blank')
  close()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    close()
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @keydown="onKeydown"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50"
          @click="close"
        />

        <!-- Modal panel -->
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="discord-support-title"
          aria-describedby="discord-support-message"
          class="relative bg-white rounded-lg shadow-lg border border-gray-200 p-6 max-w-md w-full mx-4"
        >
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
              <i class="fa-brands fa-discord text-indigo-600 text-xl"></i>
            </div>

            <div class="flex-1">
              <h3 id="discord-support-title" class="text-lg font-semibold text-gray-900">
                Support Discord
              </h3>
              <p id="discord-support-message" class="mt-2 text-sm text-gray-600">
                Pour toute question ou besoin d'aide, rejoignez notre canal Discord.
                Vous pourrez y échanger avec les membres de la communauté VEAF.
              </p>
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <button class="btn-secondary" @click="close">
              <i class="fa-solid fa-xmark mr-1"></i>Fermer
            </button>
            <button
              class="text-white font-medium py-2 px-4 rounded-md text-sm transition-colors hover:opacity-90"
              style="background-color: #5865F2"
              @click="openDiscord"
            >
              <i class="fa-brands fa-discord mr-1"></i>Rejoindre le Discord
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
