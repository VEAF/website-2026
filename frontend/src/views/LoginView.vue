<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Erreur de connexion'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-16">
    <div class="card">
      <h1 class="text-2xl font-bold text-center mb-6">Connexion</h1>

      <div v-if="error" class="bg-red-50 text-red-600 p-3 rounded-md mb-4 text-sm">{{ error }}</div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="label" for="email">Email</label>
          <input id="email" v-model="email" type="email" class="input" required autocomplete="email" />
        </div>

        <div>
          <label class="label" for="password">Mot de passe</label>
          <input id="password" v-model="password" type="password" class="input" required autocomplete="current-password" />
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>

      <div class="mt-4 text-center text-sm space-y-2">
        <p>
          <RouterLink to="/reset-password" class="text-veaf-600 hover:text-veaf-800">Mot de passe oublié ?</RouterLink>
        </p>
        <p>
          Pas de compte ?
          <RouterLink to="/register" class="text-veaf-600 hover:text-veaf-800">S'inscrire</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
