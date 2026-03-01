<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  visible: boolean
  nickname: string
}>()

const emit = defineEmits<{
  submit: [comment: string]
  close: []
}>()

const comment = ref('')
const commentRef = ref<HTMLTextAreaElement | null>(null)

watch(() => props.visible, async (isVisible) => {
  if (isVisible) {
    comment.value = ''
    await nextTick()
    commentRef.value?.focus()
  }
})

function onSubmit() {
  emit('submit', comment.value)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('close')
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
        <div
          class="absolute inset-0 bg-black/50"
          @click="emit('close')"
        />

        <div
          role="dialog"
          aria-modal="true"
          class="relative bg-white rounded-lg shadow-lg border border-gray-200 p-6 max-w-md w-full mx-4"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Ajouter un vol</h3>

          <p class="text-sm text-gray-600 mb-3">
            J'ai effectué un vol avec le
            <i class="fa-solid fa-user-graduate text-yellow-500"></i>
            cadet <span class="font-semibold">{{ nickname }}</span>.
          </p>

          <p class="text-sm text-gray-600 mb-2">
            Je peux ajouter un commentaire qui sera utilisé dans la prise de décision
            à l'issue de la période d'essai :
          </p>

          <textarea
            ref="commentRef"
            v-model="comment"
            class="input w-full h-24 resize-none"
            placeholder="Commentaire (optionnel)"
          ></textarea>

          <div class="mt-4 flex justify-end space-x-3">
            <button class="btn-secondary" @click="emit('close')">
              <i class="fa-solid fa-xmark mr-1"></i>Annuler
            </button>
            <button class="btn-primary" @click="onSubmit">
              <i class="fa-solid fa-floppy-disk mr-1"></i>Enregistrer
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
