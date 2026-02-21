<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/api/client'

const route = useRoute()
const userId = Number(route.params.userId)
const events = ref<any[]>([])

onMounted(async () => {
  const { data } = await apiClient.get(`/recruitment/${userId}`)
  events.value = data
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Historique de recrutement</h1>

    <div v-if="events.length === 0" class="text-center py-8 text-gray-500">Aucun événement</div>

    <div class="space-y-3">
      <div v-for="e in events" :key="e.id" class="card !p-4">
        <div class="flex justify-between">
          <span class="font-medium capitalize">{{ e.type_as_string }}</span>
          <span class="text-sm text-gray-500">{{ e.event_at ? new Date(e.event_at).toLocaleDateString('fr-FR') : '' }}</span>
        </div>
        <p v-if="e.comment" class="text-sm text-gray-600 mt-1">{{ e.comment }}</p>
        <p v-if="e.validator_nickname" class="text-xs text-gray-400 mt-1">Validé par {{ e.validator_nickname }}</p>
      </div>
    </div>
  </div>
</template>
