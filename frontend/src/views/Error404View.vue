<script setup lang="ts">
import ErrorPage from '@/components/ui/ErrorPage.vue'
</script>

<template>
  <ErrorPage
    :code="404"
    title="Target lost"
    subtitle="« Magic, faded contact... »"
    description="La page demandée n'a pas été trouvée."
    icon="fa-solid fa-plane-slash"
    icon-color="text-gray-400"
  />
</template>
