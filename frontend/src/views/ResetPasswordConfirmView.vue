<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { confirmResetPassword } from '@/api/auth'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const toast = useToast()
const token = route.params.token as string

const password = ref('')
const passwordConfirm = ref('')
const success = ref(false)
const loading = ref(false)

async function handleConfirm() {
  if (password.value !== passwordConfirm.value) {
    toast.error('Les mots de passe ne correspondent pas.')
    return
  }
  loading.value = true
  try {
    await confirmResetPassword(token, password.value)
    success.value = true
  } catch (e: unknown) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-16">
    <div class="card">
      <h1 class="text-2xl font-bold text-center mb-6">Nouveau mot de passe</h1>

      <div v-if="success" class="bg-green-50 text-green-600 p-3 rounded-md mb-4 text-sm">
        Votre mot de passe a été mis à jour avec succès.
        <div class="mt-2">
          <RouterLink to="/login" class="text-veaf-600 hover:text-veaf-800 font-medium">
            Se connecter
          </RouterLink>
        </div>
      </div>

      <form v-else @submit.prevent="handleConfirm" class="space-y-4">
        <div>
          <label class="label" for="password">Nouveau mot de passe</label>
          <input id="password" v-model="password" type="password" class="input" required minlength="8" />
        </div>

        <div>
          <label class="label" for="passwordConfirm">Confirmer le mot de passe</label>
          <input id="passwordConfirm" v-model="passwordConfirm" type="password" class="input" required minlength="8" />
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          <i class="fa-solid fa-key mr-1"></i>{{ loading ? 'Mise à jour...' : 'Mettre à jour le mot de passe' }}
        </button>
      </form>

      <div class="mt-4 text-center text-sm">
        <RouterLink to="/login" class="text-veaf-600 hover:text-veaf-800">Retour à la connexion</RouterLink>
      </div>
    </div>
  </div>
</template>
