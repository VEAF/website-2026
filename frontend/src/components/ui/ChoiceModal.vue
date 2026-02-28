<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { getModules } from '@/api/modules'
import { useCalendarStore } from '@/stores/calendar'
import type { Module } from '@/types/module'
import type { Choice } from '@/types/calendar'
import { FLYABLE_MODULE_TYPES, MODULE_TYPE_AIRCRAFT, MODULE_TYPE_HELICOPTER, MODULE_TYPE_SPECIAL } from '@/constants/modules'

const calendarStore = useCalendarStore()

const props = defineProps<{
  visible: boolean
  priority: number
  choice: Choice | null
  eventModuleIds: number[]
}>()

const emit = defineEmits<{
  close: []
  save: [data: { module_id: number; task: number; comment: string }]
  delete: [choiceId: number]
}>()

const modules = ref<Module[]>([])
const selectedModuleId = ref<number | null>(null)
const selectedTask = ref(0)
const comment = ref('')

// Autocomplete state
const moduleSearch = ref('')
const dropdownOpen = ref(false)
const highlightedIndex = ref(-1)
const containerRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)


const isEdit = computed(() => props.choice !== null)

const selectedModule = computed(() => {
  if (!selectedModuleId.value) return null
  return modules.value.find(m => m.id === selectedModuleId.value) ?? null
})

// Group filtered modules by type for the dropdown
interface ModuleGroup {
  name: string
  modules: Module[]
}

const filteredGroups = computed((): ModuleGroup[] => {
  const query = moduleSearch.value.toLowerCase().trim()
  const groupMap = new Map<string, Module[]>()
  const groupOrder: string[] = []

  for (const m of modules.value) {
    if (query && !m.name.toLowerCase().includes(query)) continue
    const typeName = m.type_as_string ?? 'Autre'
    if (!groupMap.has(typeName)) {
      groupMap.set(typeName, [])
      groupOrder.push(typeName)
    }
    groupMap.get(typeName)!.push(m)
  }

  return groupOrder.map(name => ({ name, modules: groupMap.get(name)! }))
})

const flatFilteredModules = computed(() =>
  filteredGroups.value.flatMap(g => g.modules)
)

function flatIndex(groupIndex: number, moduleIndex: number): number {
  let idx = 0
  for (let gi = 0; gi < groupIndex; gi++) {
    idx += filteredGroups.value[gi].modules.length
  }
  return idx + moduleIndex
}

function selectModule(m: Module) {
  selectedModuleId.value = m.id
  moduleSearch.value = ''
  dropdownOpen.value = false
}

function clearModule() {
  selectedModuleId.value = null
  moduleSearch.value = ''
  nextTick(() => inputRef.value?.focus())
}

function openDropdown() {
  dropdownOpen.value = true
  highlightedIndex.value = -1
}

function closeDropdown() {
  dropdownOpen.value = false
  moduleSearch.value = ''
  highlightedIndex.value = -1
}

function handleModuleKeydown(event: KeyboardEvent) {
  const options = flatFilteredModules.value

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!dropdownOpen.value) {
        openDropdown()
      } else {
        highlightedIndex.value = Math.min(highlightedIndex.value + 1, options.length - 1)
        scrollToHighlighted()
      }
      break
    case 'ArrowUp':
      event.preventDefault()
      if (dropdownOpen.value) {
        highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
        scrollToHighlighted()
      }
      break
    case 'Enter':
      event.preventDefault()
      if (dropdownOpen.value && highlightedIndex.value >= 0 && highlightedIndex.value < options.length) {
        selectModule(options[highlightedIndex.value])
      }
      break
    case 'Escape':
      if (dropdownOpen.value) {
        event.stopPropagation()
        closeDropdown()
      }
      break
  }
}

function scrollToHighlighted() {
  nextTick(() => {
    const listbox = containerRef.value?.querySelector('[role="listbox"]')
    if (!listbox) return
    const items = listbox.querySelectorAll('[role="option"]')
    const item = items[highlightedIndex.value] as HTMLElement | undefined
    item?.scrollIntoView({ block: 'nearest' })
  })
}

// Click outside to close dropdown
function onClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

onMounted(async () => {
  document.addEventListener('mousedown', onClickOutside)
  await calendarStore.fetchTasks()
  const allModules = await getModules()
  let filtered = allModules.filter(m => FLYABLE_MODULE_TYPES.includes(m.type))
  if (props.eventModuleIds.length > 0) {
    filtered = filtered.filter(m => props.eventModuleIds.includes(m.id))
  }
  modules.value = filtered
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
})

watch(moduleSearch, () => {
  highlightedIndex.value = 0
  if (moduleSearch.value && !dropdownOpen.value) {
    openDropdown()
  }
})

watch(() => props.visible, (v) => {
  if (v) {
    if (props.choice) {
      selectedModuleId.value = props.choice.module_id
      selectedTask.value = props.choice.task ?? 0
      comment.value = props.choice.comment ?? ''
    } else {
      selectedModuleId.value = null
      selectedTask.value = 0
      comment.value = ''
    }
    moduleSearch.value = ''
    dropdownOpen.value = false
  }
})

function handleSave() {
  if (!selectedModuleId.value) return
  emit('save', {
    module_id: selectedModuleId.value,
    task: selectedTask.value,
    comment: comment.value,
  })
}

function handleDelete() {
  if (props.choice) {
    emit('delete', props.choice.id)
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @keydown="onKeydown"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50" @click="emit('close')" />

        <!-- Modal panel -->
        <div class="relative bg-white rounded-lg shadow-lg border border-gray-200 p-6 max-w-md w-full mx-4">
          <h3 class="text-lg font-semibold mb-4">
            {{ isEdit ? 'Modifier' : 'Définir' }} le choix n°{{ priority }}
          </h3>

          <!-- Module (autocomplete) -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Module</label>
            <div ref="containerRef" class="relative">
              <!-- Selected module display -->
              <div v-if="selectedModule" class="flex items-center justify-between rounded-md border border-gray-300 px-3 py-2 bg-white">
                <span class="text-sm">
                  <span class="text-xs text-gray-400 mr-1">{{ selectedModule.type_as_string }}</span>
                  {{ selectedModule.name }}
                </span>
                <button type="button" class="text-gray-400 hover:text-gray-600" @click="clearModule">
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </div>

              <!-- Search input (shown when no module selected) -->
              <div v-else>
                <div class="flex items-center rounded-md border border-gray-300 px-3 py-2 bg-white focus-within:border-veaf-500 focus-within:ring-1 focus-within:ring-veaf-500">
                  <i class="fa-solid fa-magnifying-glass text-gray-400 text-xs mr-2"></i>
                  <input
                    ref="inputRef"
                    v-model="moduleSearch"
                    type="text"
                    class="flex-1 outline-none text-sm bg-transparent"
                    placeholder="Rechercher un module..."
                    @focus="openDropdown"
                    @keydown="handleModuleKeydown"
                  />
                </div>

                <!-- Dropdown -->
                <Transition
                  enter-active-class="transition duration-150 ease-out"
                  enter-from-class="opacity-0 -translate-y-1"
                  enter-to-class="opacity-100 translate-y-0"
                  leave-active-class="transition duration-100 ease-in"
                  leave-from-class="opacity-100 translate-y-0"
                  leave-to-class="opacity-0 -translate-y-1"
                >
                  <div
                    v-if="dropdownOpen"
                    role="listbox"
                    class="absolute z-50 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-auto"
                  >
                    <template v-for="(group, groupIndex) in filteredGroups" :key="group.name">
                      <div class="px-3 py-1 text-xs font-semibold text-gray-500 tracking-wide bg-gray-50">
                        {{ group.name }}
                      </div>
                      <div
                        v-for="(m, moduleIndex) in group.modules"
                        :key="m.id"
                        role="option"
                        :aria-selected="false"
                        class="flex items-center px-3 py-1.5 text-sm cursor-pointer"
                        :class="{
                          'bg-veaf-50 text-veaf-800': highlightedIndex === flatIndex(groupIndex, moduleIndex),
                          'text-gray-900': highlightedIndex !== flatIndex(groupIndex, moduleIndex),
                        }"
                        @click="selectModule(m)"
                        @mouseenter="highlightedIndex = flatIndex(groupIndex, moduleIndex)"
                      >
                        <span
                          class="w-2 h-2 rounded-full mr-2 flex-shrink-0"
                          :class="{
                            'bg-blue-500': m.type === MODULE_TYPE_AIRCRAFT,
                            'bg-emerald-500': m.type === MODULE_TYPE_HELICOPTER,
                            'bg-amber-500': m.type === MODULE_TYPE_SPECIAL,
                          }"
                        ></span>
                        {{ m.name }}
                      </div>
                    </template>

                    <div v-if="flatFilteredModules.length === 0" class="px-3 py-3 text-sm text-gray-500 text-center">
                      Aucun module trouvé
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <!-- Task (exclusive buttons) -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Tâche</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="t in calendarStore.tasks"
                :key="t.value"
                type="button"
                class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors border"
                :class="selectedTask === t.value
                  ? 'bg-veaf-600 text-white border-veaf-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'"
                @click="selectedTask = t.value"
              >
                <i :class="t.icon" class="mr-1"></i>{{ t.label }}
              </button>
            </div>
          </div>

          <!-- Comment -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-1">Commentaire</label>
            <input v-model="comment" type="text" class="input" maxlength="255" placeholder="Optionnel" />
          </div>

          <!-- Actions -->
          <div class="flex justify-between">
            <div>
              <button v-if="isEdit" type="button" class="btn-danger text-sm" @click="handleDelete">
                <i class="fa-solid fa-trash mr-1"></i>Supprimer
              </button>
            </div>
            <div class="flex space-x-3">
              <button type="button" class="btn-secondary" @click="emit('close')">
                <i class="fa-solid fa-xmark mr-1"></i>Annuler
              </button>
              <button type="button" class="btn-primary" :disabled="!selectedModuleId" @click="handleSave">
                <i class="fa-solid fa-floppy-disk mr-1"></i>Enregistrer
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
