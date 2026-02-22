<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAdminStats, type AdminStats } from '@/api/admin'

const stats = ref<AdminStats | null>(null)

onMounted(async () => {
  try {
    stats.value = await getAdminStats()
  } catch {
    // silently fail — dashboard still usable with "-"
  }
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Administration</h1>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <RouterLink to="/admin/users" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">{{ stats?.users ?? '-' }}</div>
        <div class="text-sm text-gray-600">Utilisateurs</div>
      </RouterLink>
      <RouterLink to="/admin/modules" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">{{ stats?.modules ?? '-' }}</div>
        <div class="text-sm text-gray-600">Modules</div>
      </RouterLink>
      <RouterLink to="/admin/calendar" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Événements</div>
      </RouterLink>
      <RouterLink to="/admin/pages" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Pages</div>
      </RouterLink>
      <RouterLink to="/admin/files" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Fichiers</div>
      </RouterLink>
      <RouterLink to="/admin/servers" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Serveurs</div>
      </RouterLink>
      <RouterLink to="/admin/urls" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">URLs</div>
      </RouterLink>
      <RouterLink to="/admin/menu" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Menu</div>
      </RouterLink>
    </div>
  </div>
</template>
