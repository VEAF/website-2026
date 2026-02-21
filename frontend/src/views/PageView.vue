<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getPage } from '@/api/pages'
import type { Page } from '@/types/api'

const route = useRoute()
const page = ref<Page | null>(null)
const loading = ref(true)
const error = ref('')

async function fetchPage() {
  loading.value = true
  error.value = ''
  try {
    page.value = await getPage(route.params.slug as string)
  } catch {
    error.value = 'Page non trouvée'
  } finally {
    loading.value = false
  }
}

onMounted(fetchPage)
watch(() => route.params.slug, fetchPage)
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>
  <div v-else-if="error" class="text-center py-12 text-red-500">{{ error }}</div>
  <div v-else-if="page" class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">{{ page.title }}</h1>
    <div v-for="block in page.blocks" :key="block.id" class="prose max-w-none mb-6">
      <div v-if="block.type === 1" class="whitespace-pre-wrap">{{ block.content }}</div>
    </div>
  </div>
</template>
