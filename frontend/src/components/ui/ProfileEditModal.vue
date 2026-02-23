<script setup lang="ts">
import { ref, watch } from 'vue'
import type { UserUpdate } from '@/types/user'

const props = defineProps<{
  visible: boolean
  initialData: {
    nickname: string
    discord: string
    forum: string
    sim_dcs: boolean
    sim_bms: boolean
  }
}>()

const emit = defineEmits<{
  save: [data: UserUpdate]
  close: []
}>()

const form = ref({ ...props.initialData })

watch(
  () => props.visible,
  (isVisible) => {
    if (isVisible) {
      form.value = { ...props.initialData }
    }
  },
)

function onSubmit() {
  emit('save', { ...form.value })
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
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
        <div class="absolute inset-0 bg-black/50" @click="emit('close')" />

        <!-- Modal panel -->
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="profile-edit-title"
          class="relative bg-white rounded-lg shadow-lg border border-gray-200 p-6 max-w-lg w-full mx-4"
        >
          <h3 id="profile-edit-title" class="text-lg font-semibold text-gray-900 mb-4">
            Modifier mon profil
          </h3>

          <form @submit.prevent="onSubmit" class="space-y-4">
            <div>
              <label class="label">Pseudo</label>
              <input v-model="form.nickname" type="text" class="input" required minlength="3" />
            </div>

            <div>
              <label class="label">Discord</label>
              <input v-model="form.discord" type="text" class="input" />
            </div>

            <div>
              <label class="label">Forum</label>
              <input v-model="form.forum" type="text" class="input" />
            </div>

            <div class="flex space-x-6">
              <label class="flex items-center space-x-2">
                <input v-model="form.sim_dcs" type="checkbox" class="rounded" />
                <span class="text-sm">DCS World</span>
              </label>
              <label class="flex items-center space-x-2">
                <input v-model="form.sim_bms" type="checkbox" class="rounded" />
                <span class="text-sm">Falcon BMS</span>
              </label>
            </div>

            <div class="flex justify-end space-x-3 pt-2">
              <button type="button" class="btn-secondary" @click="emit('close')">
                <i class="fa-solid fa-xmark mr-1"></i>Annuler
              </button>
              <button type="submit" class="btn-primary">
                <i class="fa-solid fa-floppy-disk mr-1"></i>Sauvegarder
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
