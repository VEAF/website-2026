<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getOffice, type OfficeData, type OfficeMember } from '@/api/roster'

const office = ref<OfficeData | null>(null)

onMounted(async () => {
  office.value = await getOffice()
})

interface Section {
  title: string
  icon: string
  titular: { label: string; member: OfficeMember | null | undefined }
  deputy: { label: string; member: OfficeMember | null | undefined }
}

function sections(): Section[] {
  if (!office.value) return []
  return [
    {
      title: 'Présidence',
      icon: 'fa-solid fa-crown',
      titular: { label: 'Président', member: office.value.president },
      deputy: { label: 'Adjoint', member: office.value.president_deputy },
    },
    {
      title: 'Trésorerie',
      icon: 'fa-solid fa-coins',
      titular: { label: 'Trésorier', member: office.value.treasurer },
      deputy: { label: 'Adjoint', member: office.value.treasurer_deputy },
    },
    {
      title: 'Secrétariat',
      icon: 'fa-solid fa-pen',
      titular: { label: 'Secrétaire', member: office.value.secretary },
      deputy: { label: 'Adjoint', member: office.value.secretary_deputy },
    },
  ]
}
</script>

<template>
  <div class="max-w-5xl mx-auto">
    <div class="card mb-8">
      <h1 class="text-2xl font-bold mb-4">Le Bureau de l'association</h1>
      <p class="text-gray-700">
        La VEAF est une association française à but non lucratif — loi 1901.<br />
        Elle dispose ainsi d'un cadre juridique pour encadrer la mise à disposition de moyens techniques afin de
        promouvoir des activités de loisir liées à la simulation de combat aérien.
      </p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="section in sections()" :key="section.title" class="card !p-0 overflow-hidden">
        <!-- Header with gradient and icon -->
        <div class="bg-veaf-gradient text-white text-center py-6">
          <i :class="section.icon" class="text-5xl mb-2"></i>
          <h2 class="text-lg font-semibold">{{ section.title }}</h2>
        </div>

        <!-- Body with titular + deputy -->
        <div class="p-6 space-y-4">
          <div>
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">{{ section.titular.label }}</p>
            <p class="text-lg font-semibold">
              <RouterLink
                v-if="section.titular.member"
                :to="`/user/${section.titular.member.nickname}`"
                class="text-veaf-600 hover:text-veaf-800"
              >
                {{ section.titular.member.nickname }}
              </RouterLink>
              <span v-else class="text-gray-400">–</span>
            </p>
          </div>
          <div>
            <p class="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">{{ section.deputy.label }}</p>
            <p class="text-lg font-semibold">
              <RouterLink
                v-if="section.deputy.member"
                :to="`/user/${section.deputy.member.nickname}`"
                class="text-veaf-600 hover:text-veaf-800"
              >
                {{ section.deputy.member.nickname }}
              </RouterLink>
              <span v-else class="text-gray-400">–</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
