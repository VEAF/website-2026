<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

const matrix = ref<any>(null)
const group = ref('members')

async function fetchMatrix() {
  const { data } = await apiClient.get('/mission-maker/matrix', { params: { group: group.value } })
  matrix.value = data
}

async function exportCsv() {
  const response = await apiClient.post('/mission-maker/export', null, {
    params: { group: group.value },
    responseType: 'blob',
  })
  const url = URL.createObjectURL(response.data)
  const a = document.createElement('a')
  a.href = url
  a.download = 'mission-maker.csv'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(fetchMatrix)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Mission Maker</h1>
      <button @click="exportCsv" class="btn-secondary text-sm">Export CSV</button>
    </div>

    <div class="flex space-x-2 mb-4">
      <button @click="group = 'members'; fetchMatrix()" :class="group === 'members' ? 'btn-primary' : 'btn-secondary'" class="text-sm">Membres</button>
      <button @click="group = 'cadets-members'; fetchMatrix()" :class="group === 'cadets-members' ? 'btn-primary' : 'btn-secondary'" class="text-sm">Cadets + Membres</button>
    </div>

    <div v-if="matrix" class="overflow-x-auto">
      <table class="text-xs border-collapse">
        <thead>
          <tr>
            <th class="border px-2 py-1 bg-gray-50 sticky left-0">Pilote</th>
            <th v-for="m in matrix.modules" :key="m.id" class="border px-2 py-1 bg-gray-50 whitespace-nowrap">{{ m.code }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in matrix.matrix" :key="row.user_id">
            <td class="border px-2 py-1 sticky left-0 bg-white font-medium">{{ row.nickname }}</td>
            <td v-for="m in matrix.modules" :key="m.id" class="border px-2 py-1 text-center"
              :class="{
                'bg-green-100': row.modules[m.code]?.level === 3,
                'bg-blue-100': row.modules[m.code]?.level === 2,
                'bg-yellow-100': row.modules[m.code]?.level === 1,
              }">
              {{ row.modules[m.code]?.level === 3 ? 'I' : row.modules[m.code]?.level === 2 ? 'M' : row.modules[m.code]?.level === 1 ? 'R' : '' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
