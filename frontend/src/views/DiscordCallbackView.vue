<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const toast = useToast()

const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const code = route.query.code as string
  const state = route.query.state as string

  if (!code || !state) {
    error.value = 'Paramètres de connexion Discord manquants.'
    loading.value = false
    setTimeout(() => router.push('/login'), 3000)
    return
  }

  try {
    await auth.loginWithDiscord(code, state)
    toast.success('Connexion réussie')
    const redirect = sessionStorage.getItem('discord_redirect') || '/'
    sessionStorage.removeItem('discord_redirect')
    router.push(redirect)
  } catch (e: unknown) {
    toast.error(e)
    error.value = 'La connexion via Discord a échoué. Redirection...'
    loading.value = false
    setTimeout(() => router.push('/login'), 3000)
  }
})
</script>

<template>
  <div class="max-w-md mx-auto mt-16">
    <div class="card text-center py-12">
      <i class="fa-brands fa-discord text-5xl mb-4" style="color: #5865F2;"></i>
      <p v-if="loading" class="text-gray-600">Connexion via Discord en cours...</p>
      <p v-if="error" class="text-red-600">{{ error }}</p>
    </div>
  </div>
</template>
