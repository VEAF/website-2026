import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMenu } from '@/api/pages'
import type { MenuItem } from '@/types/api'

export const useMenuStore = defineStore('menu', () => {
  const items = ref<MenuItem[]>([])
  const loaded = ref(false)

  async function fetchMenu() {
    items.value = await getMenu()
    loaded.value = true
  }

  return { items, loaded, fetchMenu }
})
