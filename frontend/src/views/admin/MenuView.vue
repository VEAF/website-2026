<script setup lang="ts">
import { ref } from 'vue'
import AdminBreadcrumb from '@/components/admin/AdminBreadcrumb.vue'
import MenuListView from '@/components/admin/MenuListView.vue'
import MenuTreeView from '@/components/admin/MenuTreeView.vue'

const activeTab = ref<'list' | 'tree'>('list')
</script>

<template>
  <div>
    <AdminBreadcrumb />

    <!-- Tab switcher -->
    <div class="flex space-x-1 mb-6 border-b">
      <button
        class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="
          activeTab === 'list'
            ? 'border-veaf-500 text-veaf-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        "
        @click="activeTab = 'list'"
      >
        <i class="fa-solid fa-list mr-1"></i>Vue liste
      </button>
      <button
        class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="
          activeTab === 'tree'
            ? 'border-veaf-500 text-veaf-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        "
        @click="activeTab = 'tree'"
      >
        <i class="fa-solid fa-sitemap mr-1"></i>Vue arborescence
      </button>
    </div>

    <MenuListView v-if="activeTab === 'list'" />
    <MenuTreeView v-else />
  </div>
</template>
