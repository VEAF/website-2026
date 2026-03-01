<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRecruitmentHistory } from '@/api/recruitment'
import type { RecruitmentEvent } from '@/api/recruitment'

const route = useRoute()
const router = useRouter()
const userId = Number(route.params.userId)
const events = ref<RecruitmentEvent[]>([])

onMounted(async () => {
  events.value = await getRecruitmentHistory(userId)
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Historique de recrutement</h1>
      <button class="btn-secondary text-sm" @click="router.back()">
        <i class="fa-solid fa-arrow-left mr-1"></i>Retour
      </button>
    </div>

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
