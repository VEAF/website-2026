<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAdminStats, type AdminStats } from '@/api/admin'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'

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
    <AppBreadcrumb :show-title="false" />
    <!-- Cadet readiness notification -->
    <RouterLink
      v-if="stats?.cadets_ready_to_promote"
      to="/admin/users?status=1"
      class="card mb-4 flex items-center gap-3 hover:shadow-md transition-shadow border-green-200 bg-green-50"
    >
      <div class="text-green-600"><i class="fa-solid fa-circle-check text-2xl"></i></div>
      <div>
        <span class="text-lg font-bold text-green-700">{{ stats.cadets_ready_to_promote }}</span>
        <span class="text-sm text-green-800 ml-1">
          cadet{{ stats.cadets_ready_to_promote > 1 ? 's' : '' }}
          prêt{{ stats.cadets_ready_to_promote > 1 ? 's' : '' }} à rejoindre l'association
        </span>
      </div>
    </RouterLink>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <RouterLink to="/admin/users" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-users text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.users ?? '-' }}</div>
        <div class="text-sm text-gray-900">Utilisateurs</div>
      </RouterLink>
      <RouterLink to="/admin/modules" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-puzzle-piece text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.modules ?? '-' }}</div>
        <div class="text-sm text-gray-900">Modules</div>
      </RouterLink>
      <RouterLink to="/admin/calendar" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-calendar-days text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.events ?? '-' }}</div>
        <div class="text-sm text-gray-900">Événements</div>
      </RouterLink>
      <RouterLink to="/admin/pages" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-file-lines text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.pages ?? '-' }}</div>
        <div class="text-sm text-gray-900">Pages</div>
      </RouterLink>
      <RouterLink to="/admin/files" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-folder-open text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.files ?? '-' }}</div>
        <div class="text-sm text-gray-900">Fichiers</div>
      </RouterLink>
      <RouterLink to="/admin/servers" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-server text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.servers ?? '-' }}</div>
        <div class="text-sm text-gray-900">Serveurs</div>
      </RouterLink>
      <RouterLink to="/admin/urls" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-link text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.urls ?? '-' }}</div>
        <div class="text-sm text-gray-900">URLs</div>
      </RouterLink>
      <RouterLink to="/admin/menu" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-bars text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.menu_items ?? '-' }}</div>
        <div class="text-sm text-gray-900">Menu</div>
      </RouterLink>
      <RouterLink to="/admin/activities" class="card text-center hover:shadow-md transition-shadow">
        <div class="text-veaf-400 mb-2"><i class="fa-solid fa-clipboard-list text-2xl"></i></div>
        <div class="text-3xl font-bold text-veaf-500 mb-2">{{ stats?.recruitment_events ?? '-' }}</div>
        <div class="text-sm text-gray-900">Activités</div>
      </RouterLink>
    </div>
  </div>
</template>
