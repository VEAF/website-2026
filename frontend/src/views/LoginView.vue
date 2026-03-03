<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { getDiscordAuthUrl } from '@/api/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const toast = useToast()

const email = ref('')
const password = ref('')
const loading = ref(false)
const discordLoading = ref(false)
const showLocalLogin = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (e: unknown) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDiscordLogin() {
  discordLoading.value = true
  try {
    const redirect = route.query.redirect as string
    if (redirect) {
      sessionStorage.setItem('discord_redirect', redirect)
    }
    const { authorization_url } = await getDiscordAuthUrl()
    window.location.href = authorization_url
  } catch (e: unknown) {
    toast.error(e)
    discordLoading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto mt-16">
    <div class="card">
      <h1 class="text-2xl font-bold text-center mb-6">Connexion</h1>

      <button
        type="button"
        class="btn w-full text-white hover:opacity-90 text-lg py-3"
        style="background-color: #5865F2;"
        :disabled="discordLoading"
        @click="handleDiscordLogin"
      >
        <i class="fa-brands fa-discord mr-2"></i>
        {{ discordLoading ? 'Redirection...' : 'Se connecter avec Discord' }}
      </button>

      <p class="text-center text-sm text-gray-500 mt-3">
        Connectez-vous avec votre compte Discord pour accéder au site.
      </p>

      <div class="mt-6 text-center">
        <button
          v-if="!showLocalLogin"
          type="button"
          class="text-sm text-gray-400 hover:text-gray-600 transition-colors"
          @click="showLocalLogin = true"
        >
          <i class="fa-solid fa-envelope mr-1"></i>Se connecter avec un email et mot de passe
        </button>
      </div>

      <template v-if="showLocalLogin">
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="bg-white px-2 text-gray-500">ou</span>
          </div>
        </div>

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
            <i class="fa-solid fa-right-to-bracket mr-1"></i>{{ loading ? 'Connexion...' : 'Se connecter' }}
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
      </template>
    </div>
  </div>
</template>
