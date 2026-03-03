<script setup lang="ts">
import ErrorPage from '@/components/ui/ErrorPage.vue'
</script>

<template>
  <ErrorPage
    :code="500"
    title="Master Caution"
    subtitle="« Mayday, Mayday ! »"
    description="Défaillance système majeure. Ejection, Ejection !"
    icon="fa-solid fa-explosion"
    icon-color="text-warning-500"
  />
</template>
