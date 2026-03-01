<script setup lang="ts">
import { watch, nextTick, ref } from 'vue'
import { useConfirm } from '@/composables/useConfirm'

const { visible, message, button, handleResponse } = useConfirm()

const confirmButtonRef = ref<HTMLButtonElement | null>(null)

watch(visible, async (isVisible) => {
  if (isVisible) {
    await nextTick()
    confirmButtonRef.value?.focus()
  }
})

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    handleResponse(false)
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
          @click="handleResponse(false)"
        />

        <!-- Modal panel -->
        <div
          role="alertdialog"
          aria-modal="true"
          aria-labelledby="confirm-title"
          aria-describedby="confirm-message"
          class="relative bg-white rounded-lg shadow-lg border border-gray-200 p-6 max-w-md w-full mx-4"
        >
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
              <i class="fa-solid fa-triangle-exclamation text-red-600 text-xl"></i>
            </div>

            <div class="flex-1">
              <h3 id="confirm-title" class="text-lg font-semibold text-gray-900">
                Confirmation
              </h3>
              <p id="confirm-message" class="mt-2 text-sm text-gray-600">
                {{ message }}
              </p>
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <button class="btn-secondary" @click="handleResponse(false)">
              <i class="fa-solid fa-xmark mr-1"></i>Annuler
            </button>
            <button
              ref="confirmButtonRef"
              class="btn-danger"
              @click="handleResponse(true)"
            >
              <i :class="[button.icon, 'mr-1']"></i>{{ button.label }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
