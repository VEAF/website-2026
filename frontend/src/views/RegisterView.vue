<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

const email = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')
const loading = ref(false)

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

      <div class="mt-4 text-center text-sm">
        <p>
          Déjà un compte ?
          <RouterLink to="/login" class="text-veaf-600 hover:text-veaf-800">Se connecter</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
