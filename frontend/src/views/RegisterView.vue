<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { getDiscordAuthUrl } from '@/api/auth'
import { useDiscordSupport } from '@/composables/useDiscordSupport'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const email = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')
const loading = ref(false)
const discordLoading = ref(false)
const { discordUrl, open: openDiscordSupport } = useDiscordSupport()

async function handleRegister() {
  if (password.value !== passwordConfirm.value) {
    toast.error('Les mots de passe ne correspondent pas')
    return
  }

  if (password.value.length < 6) {
    toast.error('Le mot de passe doit faire au moins 6 caractères')
    return
  }

  loading.value = true
  try {
    await auth.register(email.value, password.value, nickname.value)
    router.push('/')
  } catch (e: unknown) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDiscordRegister() {
  discordLoading.value = true
  try {
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
      <h1 class="text-2xl font-bold text-center mb-6">Inscription</h1>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="label" for="email">Email</label>
          <input id="email" v-model="email" type="email" class="input" required />
        </div>

        <div>
          <label class="label" for="nickname">Pseudo</label>
          <input id="nickname" v-model="nickname" type="text" class="input" required minlength="3" />
        </div>

        <div>
          <label class="label" for="password">Mot de passe</label>
          <input id="password" v-model="password" type="password" class="input" required minlength="6" />
        </div>

        <div>
          <label class="label" for="passwordConfirm">Confirmer le mot de passe</label>
          <input id="passwordConfirm" v-model="passwordConfirm" type="password" class="input" required />
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          <i class="fa-solid fa-user-plus mr-1"></i>{{ loading ? 'Inscription...' : "S'inscrire" }}
        </button>
      </form>

      <div class="relative my-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="bg-white px-2 text-gray-500">ou</span>
        </div>
      </div>

      <button
        type="button"
        class="btn w-full text-white hover:opacity-90"
        style="background-color: #5865F2;"
        :disabled="discordLoading"
        @click="handleDiscordRegister"
      >
        <i class="fa-brands fa-discord mr-2"></i>
        {{ discordLoading ? 'Redirection...' : "S'inscrire avec Discord" }}
      </button>

      <div class="mt-4 text-center text-sm">
        <p>
          Déjà un compte ?
          <RouterLink to="/login" class="text-veaf-600 hover:text-veaf-800">Se connecter</RouterLink>
        </p>
      </div>

      <div v-if="discordUrl" class="mt-6 pt-4 border-t border-gray-200 text-center">
        <button
          type="button"
          class="text-sm text-gray-500 hover:text-indigo-600 transition-colors"
          @click="openDiscordSupport()"
        >
          <i class="fa-brands fa-discord mr-1"></i>Besoin d'aide ? Contactez-nous sur Discord
        </button>
      </div>
    </div>
  </div>
</template>
