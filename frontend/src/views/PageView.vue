<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPage } from '@/api/pages'
import { getUrlBySlug } from '@/api/urls'
import { renderMarkdown } from '@/composables/useMarkdown'
import type { Page, Url } from '@/types/api'

const route = useRoute()
const page = ref<Page | null>(null)
const redirectUrl = ref<Url | null>(null)
const countdown = ref(0)
const loading = ref(true)
const error = ref('')
let countdownTimer: ReturnType<typeof setInterval> | null = null

function clearCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

function startCountdown(seconds: number, target: string) {
  countdown.value = seconds
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearCountdown()
      window.location.href = target
    }
  }, 1000)
}

async function fetchContent() {
  loading.value = true
  error.value = ''
  page.value = null
  redirectUrl.value = null
  clearCountdown()

  const slug = route.params.slug as string

  // Step 1: Try loading as a CMS page
  try {
    page.value = await getPage(slug)
    loading.value = false
    return
  } catch {
    // Page not found — try URL redirect
  }

  // Step 2: Try loading as a URL redirect
  try {
    const url = await getUrlBySlug(slug)
    if (url.delay === 0) {
      // Instant redirect — keep loading state while browser navigates
      window.location.href = url.target
      return
    }
    // Delayed redirect: show banner with countdown
    redirectUrl.value = url
    startCountdown(url.delay, url.target)
  } catch {
    // Neither page nor URL found
    error.value = 'Page non trouvée'
  }

  loading.value = false
}

onMounted(fetchContent)
watch(() => route.params.slug, fetchContent)
onUnmounted(clearCountdown)
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>

  <!-- Redirect banner with countdown -->
  <div v-else-if="redirectUrl" class="max-w-2xl mx-auto py-20 text-center">
    <div class="card p-8">
      <div class="text-veaf-400 mb-4">
        <i class="fa-solid fa-arrow-up-right-from-square text-4xl"></i>
      </div>
      <h1 class="text-2xl font-semibold mb-4">Redirection en cours...</h1>
      <p class="text-gray-600 mb-6">
        Vous allez être redirigé vers
        <a :href="redirectUrl.target" class="text-veaf-600 hover:text-veaf-800 underline break-all">
          {{ redirectUrl.target }}
        </a>
        dans <span class="font-bold text-veaf-600">{{ countdown }}</span> seconde(s).
      </p>
      <a :href="redirectUrl.target" class="btn-primary">
        <i class="fa-solid fa-arrow-up-right-from-square mr-1"></i>Aller maintenant
      </a>
    </div>
  </div>

  <!-- 404 -->
  <div v-else-if="error" class="text-center py-20">
    <div class="text-6xl font-bold text-gray-300 mb-4">404</div>
    <h1 class="text-2xl font-semibold text-gray-400 mb-2">Page non trouvée</h1>
    <p class="text-gray-500 mb-6">La page que vous recherchez n'existe pas ou a été déplacée.</p>
    <RouterLink to="/" class="btn-primary">
      <i class="fa-solid fa-house mr-1"></i>Retour à l'accueil
    </RouterLink>
  </div>

  <!-- CMS page content -->
  <div v-else-if="page" class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">{{ page.title }}</h1>
    <div v-for="block in page.blocks" :key="block.id" class="prose max-w-none mb-6">
      <div v-if="block.type === 1" v-html="renderMarkdown(block.content)"></div>
    </div>
  </div>
</template>
