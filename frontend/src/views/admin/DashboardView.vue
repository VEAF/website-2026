<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAdminStats, type AdminStats } from '@/api/admin'
import AdminBreadcrumb from '@/components/admin/AdminBreadcrumb.vue'

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
    <AdminBreadcrumb />
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <RouterLink to="/admin/users" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-users text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">{{ stats?.users ?? '-' }}</div>
        <div class="text-sm text-gray-600">Utilisateurs</div>
      </RouterLink>
      <RouterLink to="/admin/modules" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-puzzle-piece text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">{{ stats?.modules ?? '-' }}</div>
        <div class="text-sm text-gray-600">Modules</div>
      </RouterLink>
      <RouterLink to="/admin/calendar" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-calendar-days text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Événements</div>
      </RouterLink>
      <RouterLink to="/admin/pages" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-file-lines text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">{{ stats?.pages ?? '-' }}</div>
        <div class="text-sm text-gray-600">Pages</div>
      </RouterLink>
      <RouterLink to="/admin/files" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-folder-open text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Fichiers</div>
      </RouterLink>
      <RouterLink to="/admin/servers" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-server text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Serveurs</div>
      </RouterLink>
      <RouterLink to="/admin/urls" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-link text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">{{ stats?.urls ?? '-' }}</div>
        <div class="text-sm text-gray-600">URLs</div>
      </RouterLink>
      <RouterLink to="/admin/menu" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-bars text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-600 mb-2">-</div>
        <div class="text-sm text-gray-600">Menu</div>
      </RouterLink>
    </div>
  </div>
</template>
