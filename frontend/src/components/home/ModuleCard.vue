<script setup lang="ts">
import { computed } from 'vue'
import type { Module } from '@/types/module'

const props = defineProps<{
  module: Module
  variant: 'card' | 'banner'
}>()

const imageSrc = computed(() => {
  const uuid = props.variant === 'banner' ? props.module.image_header_uuid : props.module.image_uuid
  return uuid ? `/api/files/${uuid}` : null
})

const displayText = computed(() => props.module.code.toUpperCase())
</script>

<template>
  <RouterLink to="/roster" class="block group">
    <div class="relative overflow-hidden rounded">
      <img
        v-if="imageSrc"
        :src="imageSrc"
        :alt="module.long_name"
        loading="lazy"
        class="w-full object-cover"
        :class="variant === 'banner' ? 'h-[56px] sm:h-[112px] md:h-[160px] lg:h-[200px]' : 'aspect-video'"
      />
      <div
        v-else
        class="w-full bg-gray-700 flex items-center justify-center"
        :class="variant === 'banner' ? 'h-[56px] sm:h-[112px] md:h-[160px] lg:h-[200px]' : 'aspect-video'"
      >
        <span class="text-gray-400 font-bold text-lg">{{ displayText }}</span>
      </div>
      <!-- Hover overlay -->
      <div class="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <span class="text-white font-bold translate-y-3 group-hover:translate-y-0 transition-transform duration-200"
              :class="variant === 'banner' ? 'text-xl md:text-3xl' : 'text-sm md:text-lg'">
          {{ displayText }}
        </span>
      </div>
    </div>
  </RouterLink>
</template>
