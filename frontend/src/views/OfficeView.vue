<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

const members = ref<any[]>([])

onMounted(async () => {
  const { data } = await apiClient.get('/roster', { params: { group: 'office' } })
  members.value = data
})

const statusLabels: Record<number, string> = {
  8: 'Président',
  7: 'Vice-Président',
  4: 'Secrétaire',
  3: 'Secrétaire adjoint',
  6: 'Trésorier',
  5: 'Trésorier adjoint',
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Le Bureau</h1>
    <div class="space-y-4">
      <div v-for="m in members" :key="m.id" class="card !p-4 flex items-center justify-between">
        <div>
          <RouterLink :to="`/user/${m.id}`" class="font-semibold text-veaf-600">{{ m.nickname }}</RouterLink>
          <p class="text-sm text-gray-500 capitalize">{{ statusLabels[m.status] || m.status_as_string }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
