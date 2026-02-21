<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getModules } from '@/api/modules'
import type { Module } from '@/types/module'

const maps = ref<Module[]>([])
const aircrafts = ref<Module[]>([])
const helicopters = ref<Module[]>([])

onMounted(async () => {
  const allModules = await getModules()
  maps.value = allModules.filter(m => m.type === 1 && m.landing_page).sort((a, b) => (a.landing_page_number ?? 0) - (b.landing_page_number ?? 0))
  aircrafts.value = allModules.filter(m => m.type === 2 && m.landing_page).sort((a, b) => (a.landing_page_number ?? 0) - (b.landing_page_number ?? 0))
  helicopters.value = allModules.filter(m => m.type === 3 && m.landing_page).sort((a, b) => (a.landing_page_number ?? 0) - (b.landing_page_number ?? 0))
})
</script>

<template>
  <div>
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">VEAF</h1>
      <p class="text-lg text-gray-600">Virtual European Air Force - Escadron de simulation DCS World</p>
    </div>

    <!-- Maps -->
    <section v-if="maps.length" class="mb-10">
      <h2 class="text-2xl font-bold mb-4">Cartes</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div v-for="m in maps" :key="m.id" class="card text-center p-4">
          <img v-if="m.image_uuid" :src="`/api/files/${m.image_uuid}`" :alt="m.long_name" class="w-full h-24 object-cover rounded mb-2" />
          <p class="font-medium text-sm">{{ m.long_name }}</p>
        </div>
      </div>
    </section>

    <!-- Aircrafts -->
    <section v-if="aircrafts.length" class="mb-10">
      <h2 class="text-2xl font-bold mb-4">Avions</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div v-for="m in aircrafts" :key="m.id" class="card text-center p-4">
          <img v-if="m.image_uuid" :src="`/api/files/${m.image_uuid}`" :alt="m.long_name" class="w-full h-24 object-cover rounded mb-2" />
          <p class="font-medium text-sm">{{ m.long_name }}</p>
        </div>
      </div>
    </section>

    <!-- Helicopters -->
    <section v-if="helicopters.length" class="mb-10">
      <h2 class="text-2xl font-bold mb-4">Hélicoptères</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div v-for="m in helicopters" :key="m.id" class="card text-center p-4">
          <img v-if="m.image_uuid" :src="`/api/files/${m.image_uuid}`" :alt="m.long_name" class="w-full h-24 object-cover rounded mb-2" />
          <p class="font-medium text-sm">{{ m.long_name }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
