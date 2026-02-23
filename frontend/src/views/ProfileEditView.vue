<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { updateMe } from '@/api/users'
import { useToast } from '@/composables/useToast'

const auth = useAuthStore()
const toast = useToast()
const saving = ref(false)

const form = ref({
  nickname: '',
  discord: '',
  forum: '',
  sim_dcs: false,
  sim_bms: false,
})

onMounted(async () => {
  await auth.fetchUser()
  if (auth.user) {
    form.value = {
      nickname: auth.user.nickname,
      discord: auth.user.discord || '',
      forum: auth.user.forum || '',
      sim_dcs: auth.user.sim_dcs,
      sim_bms: auth.user.sim_bms,
    }
  }
})

async function handleSave() {
  saving.value = true
  try {
    await updateMe(form.value)
    await auth.fetchUser()
    toast.success('Profil mis à jour')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto">
    <h1 class="text-2xl font-bold mb-6">Mon profil</h1>

    <form @submit.prevent="handleSave" class="card space-y-4">
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

      <button type="submit" class="btn-primary" :disabled="saving">
        {{ saving ? 'Sauvegarde...' : 'Sauvegarder' }}
      </button>
    </form>
  </div>
</template>
