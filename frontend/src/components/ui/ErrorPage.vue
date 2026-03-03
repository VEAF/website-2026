<script setup lang="ts">
import { useRouter } from 'vue-router'

defineProps<{
  code: number | string
  title: string
  subtitle: string
  description: string
  icon: string
  iconColor?: string
}>()

const router = useRouter()
</script>

<template>
  <div class="flex items-center justify-center py-16 px-4">
    <div class="max-w-lg w-full card text-center">
      <div class="mb-6">
        <i :class="[icon, iconColor ?? 'text-veaf-400']" class="text-7xl"></i>
      </div>

      <div class="text-8xl font-black text-gray-200 leading-none mb-4 select-none">
        {{ code }}
      </div>

      <h1 class="text-2xl font-bold text-gray-700 mb-2">{{ title }}</h1>

      <p class="text-lg text-gray-500 mb-4 italic">{{ subtitle }}</p>

      <p class="text-gray-500 mb-8">{{ description }}</p>

      <div class="flex flex-wrap justify-center gap-3">
        <RouterLink to="/" class="btn-primary">
          <i class="fa-solid fa-house mr-1"></i>Retour à l'accueil
        </RouterLink>
        <button class="btn-secondary" @click="router.back()">
          <i class="fa-solid fa-arrow-left mr-1"></i>Page précédente
        </button>
      </div>
    </div>
  </div>
</template>
