<script setup lang="ts">
import ErrorPage from '@/components/ui/ErrorPage.vue'
</script>

<template>
  <ErrorPage
    :code="403"
    title="No Fly Zone"
    subtitle="« Vous entrez dans un espace aérien contrôlé. »"
    description="Vous n'avez pas l'autorisation d'accéder à cette zone. Faites demi-tour."
    icon="fa-solid fa-lock"
    icon-color="text-danger-500"
  />
</template>
