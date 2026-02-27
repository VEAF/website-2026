<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getUser } from '@/api/users'
import type { UserPublic } from '@/types/user'

const route = useRoute()
const user = ref<UserPublic | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    user.value = await getUser(Number(route.params.id))
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>

  <div v-else-if="user">
    <div class="card">
      <h1 class="text-2xl font-bold mb-4">{{ user.nickname }}</h1>

      <div class="grid grid-cols-2 gap-4 text-sm">
        <div><strong>Statut :</strong> <span class="capitalize">{{ user.status_as_string }}</span></div>
        <div><strong>DCS :</strong> {{ user.sim_dcs ? 'Oui' : 'Non' }}</div>
        <div><strong>BMS :</strong> {{ user.sim_bms ? 'Oui' : 'Non' }}</div>
        <div v-if="user.discord"><strong>Discord :</strong> {{ user.discord }}</div>
        <div v-if="user.forum"><strong>Forum :</strong> {{ user.forum }}</div>
        <div v-if="user.created_at"><strong>Inscrit le :</strong> {{ new Date(user.created_at).toLocaleDateString('fr-FR') }}</div>
      </div>
    </div>
  </div>
</template>
