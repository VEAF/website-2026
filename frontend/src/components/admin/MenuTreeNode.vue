<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { dragAndDrop } from '@formkit/drag-and-drop/vue'
import { tearDown } from '@formkit/drag-and-drop'
import type { AdminMenuItemTree } from '@/types/api'

const props = defineProps<{
  item: AdminMenuItemTree
  depth?: number
}>()

const emit = defineEmits<{
  changed: []
}>()

const TYPE_MENU = 1

const typeLabels: Record<number, string> = {
  1: 'Menu',
  2: 'Lien',
  3: 'Url',
  4: 'Page',
  5: 'Séparateur',
  6: 'Bureau',
  7: 'Serveurs',
  8: 'Roster',
  9: 'Calendrier',
  10: 'Mission Maker',
  11: 'Team Speak',
}

const restrictionLabels: Record<number, string> = {
  1: 'Invité+',
  2: 'Cadet+',
  3: 'Membre',
}

const childrenRef = ref<HTMLElement>()
const children = ref<AdminMenuItemTree[]>([...props.item.items])
const expanded = ref(true)

onMounted(async () => {
  if (props.item.type === TYPE_MENU && childrenRef.value) {
    await nextTick()
    dragAndDrop({
      parent: childrenRef.value,
      values: children,
      group: 'menu-tree',
      dragHandle: '.drag-handle',
      draggingClass: 'opacity-50',
      dropZoneClass: 'bg-veaf-50',
      onSort: () => {
        props.item.items = children.value
        emit('changed')
      },
      onTransfer: () => {
        props.item.items = children.value
        emit('changed')
      },
    })
  }
})

onUnmounted(() => {
  if (childrenRef.value) {
    tearDown(childrenRef.value)
  }
})
</script>

<template>
  <div class="menu-tree-node" :data-id="item.id">
    <div
      class="flex items-center gap-2 px-3 py-2 rounded border bg-white transition-opacity"
      :class="{ 'opacity-50': !item.enabled }"
    >
      <i class="fa-solid fa-grip-vertical text-gray-400 cursor-grab drag-handle"></i>

      <button
        v-if="item.type === TYPE_MENU"
        class="text-gray-400 hover:text-gray-600 w-4 text-center"
        @click="expanded = !expanded"
      >
        <i :class="expanded ? 'fa-solid fa-chevron-down' : 'fa-solid fa-chevron-right'" class="text-xs"></i>
      </button>
      <span v-else class="w-4"></span>

      <i v-if="item.icon" :class="item.icon" class="text-gray-500 w-5 text-center"></i>
      <i v-else class="fa-solid fa-minus text-gray-300 w-5 text-center"></i>

      <span class="font-medium text-sm flex-1">{{ item.label || '(sans libellé)' }}</span>

      <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-veaf-100 text-veaf-800">
        {{ typeLabels[item.type] ?? '?' }}
      </span>

      <span
        v-if="!item.enabled"
        class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600"
      >
        <i class="fa-solid fa-eye-slash mr-1"></i>Masqué
      </span>

      <span
        v-if="item.restriction > 0"
        class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800"
      >
        <i class="fa-solid fa-lock mr-1"></i>{{ restrictionLabels[item.restriction] }}
      </span>
    </div>

    <!-- Children (only for TYPE_MENU) -->
    <div
      v-if="item.type === TYPE_MENU"
      v-show="expanded"
      ref="childrenRef"
      class="ml-6 mt-1 space-y-1 border-l-2 border-gray-200 pl-3 min-h-[8px]"
    >
      <MenuTreeNode
        v-for="child in children"
        :key="child.id"
        :item="child"
        :depth="(depth ?? 0) + 1"
        @changed="emit('changed')"
      />
    </div>
  </div>
</template>
