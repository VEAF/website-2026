<script setup lang="ts">
import { ref } from 'vue'
import { resetPassword } from '@/api/auth'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const email = ref('')
const success = ref(false)
const loading = ref(false)

async function handleReset() {
  loading.value = true
  try {
    await resetPassword(email.value)
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
      <h1 class="text-2xl font-bold text-center mb-6">Réinitialisation du mot de passe</h1>

      <div v-if="success" class="bg-green-50 text-green-600 p-3 rounded-md mb-4 text-sm">
        Si cette adresse email existe, un lien de réinitialisation a été envoyé.
      </div>

      <form v-if="!success" @submit.prevent="handleReset" class="space-y-4">
        <div>
          <label class="label" for="email">Email</label>
          <input id="email" v-model="email" type="email" class="input" required />
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Envoi...' : 'Envoyer le lien' }}
        </button>
      </form>

      <div class="mt-4 text-center text-sm">
        <RouterLink to="/login" class="text-veaf-600 hover:text-veaf-800">Retour à la connexion</RouterLink>
      </div>
    </div>
  </div>
</template>
