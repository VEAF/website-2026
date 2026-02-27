<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useDragAndDrop } from '@formkit/drag-and-drop/vue'
import { getAdminMenuTree, reorderAdminMenuItems } from '@/api/menu'
import type { AdminMenuItemTree, MenuItemReorderEntry } from '@/types/api'
import { useToast } from '@/composables/useToast'
import { useMenuStore } from '@/stores/menu'
import MenuTreeNode from '@/components/admin/MenuTreeNode.vue'

const toast = useToast()
const menuStore = useMenuStore()

const loading = ref(false)
const saving = ref(false)
const hasChanges = ref(false)

function onChanged() {
  hasChanges.value = true
}

const [rootRef, rootItems] = useDragAndDrop<AdminMenuItemTree>([], {
  group: 'menu-tree',
  dragHandle: '.drag-handle',
  draggingClass: 'opacity-50',
  dropZoneClass: 'bg-veaf-50',
  onSort: () => {
    hasChanges.value = true
  },
  onTransfer: () => {
    hasChanges.value = true
  },
})

function flattenTree(items: AdminMenuItemTree[], parentId: number | null = null): MenuItemReorderEntry[] {
  const result: MenuItemReorderEntry[] = []
  items.forEach((item, index) => {
    result.push({
      id: item.id,
      menu_id: parentId,
      position: index + 1,
    })
    if (item.items?.length) {
      result.push(...flattenTree(item.items, item.id))
    }
  })
  return result
}

async function loadTree() {
  loading.value = true
  try {
    const tree = await getAdminMenuTree()
    // Clear then reassign after nextTick so the MutationObserver
    // sees a clean DOM transition (0 → N nodes) instead of
    // partial swaps that desync node count vs values count.
    rootItems.value = []
    await nextTick()
    rootItems.value = tree
    hasChanges.value = false
  } catch (e) {
    toast.error(e)
  } finally {
    loading.value = false
  }
}

async function saveOrder() {
  saving.value = true
  try {
    const entries = flattenTree(rootItems.value)
    const updatedTree = await reorderAdminMenuItems(entries)
    rootItems.value = []
    await nextTick()
    rootItems.value = updatedTree
    hasChanges.value = false
    await menuStore.fetchMenu()
    toast.success('Ordre du menu mis à jour')
  } catch (e) {
    toast.error(e)
  } finally {
    saving.value = false
  }
}

onMounted(loadTree)
</script>

<template>
  <div>
    <!-- Toolbar -->
    <div class="flex items-center gap-3 mb-4">
      <button
        v-if="hasChanges"
        class="btn-primary"
        :disabled="saving"
        @click="saveOrder"
      >
        <i class="fa-solid fa-floppy-disk mr-1"></i>{{ saving ? 'Enregistrement...' : "Enregistrer l'ordre" }}
      </button>
      <span v-if="hasChanges" class="text-sm text-amber-600">
        <i class="fa-solid fa-triangle-exclamation mr-1"></i>Modifications non enregistrées
      </span>
      <button class="btn-secondary" :disabled="loading" @click="loadTree">
        <i class="fa-solid fa-arrows-rotate mr-1"></i>Recharger
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="card text-center py-12 text-gray-500">
      <i class="fa-solid fa-spinner fa-spin mr-2"></i>Chargement...
    </div>

    <!-- Empty state -->
    <div v-else-if="!rootItems.length" class="card text-center py-12 text-gray-500">
      Aucun élément de menu
    </div>

    <!-- Tree (always mounted to keep drag-and-drop parent element stable) -->
    <div v-show="!loading && rootItems.length" ref="rootRef" class="space-y-1">
      <MenuTreeNode
        v-for="item in rootItems"
        :key="item.id"
        :item="item"
        @changed="onChanged"
      />
    </div>

    <p class="text-xs text-gray-500 mt-4">
      <i class="fa-solid fa-circle-info mr-1"></i>Glissez-déposez les éléments pour réorganiser le menu. Les éléments de type "Menu" peuvent contenir des sous-éléments.
    </p>
  </div>
</template>
