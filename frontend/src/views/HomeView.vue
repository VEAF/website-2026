<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getModules } from '@/api/modules'
import type { Module } from '@/types/module'
import { MODULE_TYPE } from '@/config'
import HeroBanner from '@/components/home/HeroBanner.vue'
import ModuleCard from '@/components/home/ModuleCard.vue'

const modules = ref<Module[]>([])
const loading = ref(true)

function sortByLandingPage(a: Module, b: Module) {
  return (a.landing_page_number ?? 0) - (b.landing_page_number ?? 0)
}

const aircrafts = computed(() =>
  modules.value
    .filter(m => m.type === MODULE_TYPE.AIRCRAFT && m.landing_page)
    .sort(sortByLandingPage)
)

const helicopters = computed(() =>
  modules.value
    .filter(m => m.type === MODULE_TYPE.HELICOPTER && m.landing_page)
    .sort(sortByLandingPage)
)

const maps = computed(() =>
  modules.value
    .filter(m => m.type === MODULE_TYPE.MAP && m.landing_page)
    .sort(sortByLandingPage)
)

const specials = computed(() =>
  modules.value
    .filter(m => m.type === MODULE_TYPE.SPECIAL && m.landing_page)
    .sort(sortByLandingPage)
)

onMounted(async () => {
  try {
    modules.value = await getModules()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <!-- Hero Banner -->
    <HeroBanner />

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>

    <template v-else>
      <!-- Aircrafts -->
      <section v-if="aircrafts.length" class="page-container mb-6">
        <div class="bg-white shadow-lg rounded-lg p-4">
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <ModuleCard v-for="m in aircrafts" :key="m.id" :module="m" variant="card" />
          </div>
        </div>
      </section>

      <!-- Helicopters -->
      <section v-if="helicopters.length" class="page-container mb-6">
        <div class="bg-white shadow-lg rounded-lg p-4">
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <ModuleCard v-for="m in helicopters" :key="m.id" :module="m" variant="card" />
          </div>
        </div>
      </section>

      <!-- Maps -->
      <section v-if="maps.length" class="page-container mb-6">
        <div class="bg-white shadow-lg rounded-lg p-4 space-y-4">
          <ModuleCard v-for="m in maps" :key="m.id" :module="m" variant="banner" />
        </div>
      </section>

      <!-- Specials -->
      <section v-if="specials.length" class="page-container mb-6">
        <div class="bg-white shadow-lg rounded-lg p-4 space-y-4">
          <ModuleCard v-for="m in specials" :key="m.id" :module="m" variant="banner" />
        </div>
      </section>

      <!-- Bottom Banners -->
      <section class="page-container mb-6">
        <div class="bg-white shadow-lg rounded-lg overflow-hidden">
          <img src="/img/bms.jpg" alt="BMS" class="w-full" />
        </div>
      </section>

      <section class="page-container mb-6">
        <div class="bg-white shadow-lg rounded-lg overflow-hidden">
          <img src="/img/uh-1h-boat.jpg" alt="UH-1H" class="w-full" />
        </div>
      </section>
    </template>
  </div>
</template>
