<script lang="ts">
export interface MultiSelectOption {
  id: number
  label: string
  section?: string
  group?: string
  colorClass?: string
}
</script>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount, useId } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: number[]
  options: MultiSelectOption[]
  placeholder?: string
  noResultsText?: string
}>(), {
  placeholder: 'Rechercher...',
  noResultsText: 'Aucun résultat',
})

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
}>()

const listboxId = `multiselect-${useId()}`

const search = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const containerRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

// Selected options resolved from modelValue IDs
const selectedOptions = computed(() => {
  const idSet = new Set(props.modelValue)
  return props.options.filter(o => idSet.has(o.id))
})

// Two-level group structure: section > group > options
interface OptionGroup {
  name: string
  options: MultiSelectOption[]
}

interface OptionSection {
  name: string
  groups: OptionGroup[]
}

const filteredSections = computed((): OptionSection[] => {
  const query = search.value.toLowerCase().trim()

  // Build section > group > options structure
  const sectionMap = new Map<string, Map<string, MultiSelectOption[]>>()

  for (const option of props.options) {
    const sectionName = option.section ?? ''
    const groupName = option.group ?? ''
    if (query && !option.label.toLowerCase().includes(query)) continue

    if (!sectionMap.has(sectionName)) sectionMap.set(sectionName, new Map())
    const groupMap = sectionMap.get(sectionName)!
    if (!groupMap.has(groupName)) groupMap.set(groupName, [])
    groupMap.get(groupName)!.push(option)
  }

  // Preserve original ordering
  const sectionOrder: string[] = []
  const groupOrderPerSection = new Map<string, string[]>()

  for (const option of props.options) {
    const s = option.section ?? ''
    const g = option.group ?? ''
    if (!sectionOrder.includes(s)) sectionOrder.push(s)
    if (!groupOrderPerSection.has(s)) groupOrderPerSection.set(s, [])
    const groups = groupOrderPerSection.get(s)!
    if (!groups.includes(g)) groups.push(g)
  }

  return sectionOrder
    .filter(s => sectionMap.has(s))
    .map(s => ({
      name: s,
      groups: groupOrderPerSection.get(s)!
        .filter(g => sectionMap.get(s)!.has(g))
        .map(g => ({ name: g, options: sectionMap.get(s)!.get(g)! })),
    }))
})

// Flat list for keyboard navigation
const flatFilteredOptions = computed(() =>
  filteredSections.value.flatMap(s => s.groups.flatMap(g => g.options))
)

// Convert section+group+option position to flat index
function flatIndex(sectionIndex: number, groupIndex: number, optionIndex: number): number {
  let idx = 0
  for (let si = 0; si < sectionIndex; si++) {
    for (const g of filteredSections.value[si].groups) {
      idx += g.options.length
    }
  }
  for (let gi = 0; gi < groupIndex; gi++) {
    idx += filteredSections.value[sectionIndex].groups[gi].options.length
  }
  return idx + optionIndex
}

function isSelected(id: number): boolean {
  return props.modelValue.includes(id)
}

function toggleOption(id: number) {
  const newValue = isSelected(id)
    ? props.modelValue.filter(v => v !== id)
    : [...props.modelValue, id]
  emit('update:modelValue', newValue)
  search.value = ''
  inputRef.value?.focus()
}

function removeOption(id: number) {
  emit('update:modelValue', props.modelValue.filter(v => v !== id))
}

function openDropdown() {
  isOpen.value = true
  highlightedIndex.value = -1
}

function closeDropdown() {
  isOpen.value = false
  search.value = ''
  highlightedIndex.value = -1
}

function focusInput() {
  inputRef.value?.focus()
}

function scrollToHighlighted() {
  nextTick(() => {
    const listbox = document.getElementById(listboxId)
    if (!listbox) return
    const items = listbox.querySelectorAll('[role="option"]')
    const item = items[highlightedIndex.value] as HTMLElement | undefined
    item?.scrollIntoView({ block: 'nearest' })
  })
}

function handleKeydown(event: KeyboardEvent) {
  const options = flatFilteredOptions.value

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) {
        openDropdown()
      } else {
        highlightedIndex.value = Math.min(highlightedIndex.value + 1, options.length - 1)
        scrollToHighlighted()
      }
      break

    case 'ArrowUp':
      event.preventDefault()
      if (isOpen.value) {
        highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
        scrollToHighlighted()
      }
      break

    case 'Enter':
      event.preventDefault()
      if (isOpen.value && highlightedIndex.value >= 0 && highlightedIndex.value < options.length) {
        toggleOption(options[highlightedIndex.value].id)
      }
      break

    case 'Escape':
      closeDropdown()
      break

    case 'Backspace':
      if (search.value === '' && props.modelValue.length > 0) {
        removeOption(props.modelValue[props.modelValue.length - 1])
      }
      break
  }
}

// Click outside detection
function onClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
})

// Reset highlight when search changes
watch(search, () => {
  highlightedIndex.value = 0
  if (search.value && !isOpen.value) {
    openDropdown()
  }
})
</script>

<template>
  <div ref="containerRef" class="relative">
    <!-- Selected tags + search input wrapper -->
    <div
      class="flex flex-wrap items-center gap-2 min-h-[38px] rounded-md border border-gray-300 px-2 py-1.5
             focus-within:border-veaf-500 focus-within:ring-1 focus-within:ring-veaf-500 bg-white cursor-text"
      @click="focusInput"
    >
      <!-- Tags -->
      <span
        v-for="selected in selectedOptions"
        :key="selected.id"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium"
        :class="selected.colorClass || 'bg-veaf-100 text-veaf-800'"
      >
        {{ selected.label }}
        <button
          type="button"
          class="opacity-60 hover:opacity-100"
          @click.stop="removeOption(selected.id)"
          @mousedown.prevent
          :aria-label="`Retirer ${selected.label}`"
        >
          <i class="fa-solid fa-xmark text-xs"></i>
        </button>
      </span>

      <!-- Search input -->
      <input
        ref="inputRef"
        v-model="search"
        type="text"
        class="flex-1 min-w-[120px] outline-none text-sm bg-transparent"
        :placeholder="selectedOptions.length === 0 ? placeholder : ''"
        @focus="openDropdown"
        @keydown="handleKeydown"
        role="combobox"
        aria-autocomplete="list"
        :aria-expanded="isOpen"
        :aria-controls="listboxId"
      />

      <!-- Chevron -->
      <i
        class="fa-solid fa-chevron-down text-gray-400 text-xs ml-auto transition-transform"
        :class="{ 'rotate-180': isOpen }"
      ></i>
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
        v-if="isOpen"
        :id="listboxId"
        role="listbox"
        aria-multiselectable="true"
        class="absolute z-50 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
      >
        <template v-for="(section, sectionIndex) in filteredSections" :key="section.name">
          <!-- Section header (époque) -->
          <div
            v-if="section.name"
            class="px-3 py-1.5 text-xs font-bold text-gray-600 uppercase tracking-wide bg-gray-100 border-b border-gray-200"
            :class="{ 'border-t': sectionIndex > 0 }"
          >
            {{ section.name }}
          </div>

          <template v-for="(group, groupIndex) in section.groups" :key="group.name">
            <!-- Group header (type de module) -->
            <div
              v-if="group.name"
              class="px-3 py-1 text-xs font-semibold text-gray-500 tracking-wide bg-gray-50"
            >
              {{ group.name }}
            </div>

            <!-- Options -->
            <div
              v-for="(option, optionIndex) in group.options"
              :key="option.id"
              role="option"
              :aria-selected="isSelected(option.id)"
              class="flex items-center px-3 py-1.5 text-sm cursor-pointer"
              :class="{
                'bg-gray-100': highlightedIndex === flatIndex(sectionIndex, groupIndex, optionIndex),
                'font-medium': isSelected(option.id),
              }"
              @click="toggleOption(option.id)"
              @mouseenter="highlightedIndex = flatIndex(sectionIndex, groupIndex, optionIndex)"
            >
              <span
                class="w-2 h-2 rounded-full mr-2 flex-shrink-0"
                :class="{
                  'bg-blue-500': option.colorClass === 'module-aircraft',
                  'bg-emerald-500': option.colorClass === 'module-helicopter',
                  'bg-amber-500': option.colorClass === 'module-special',
                  'bg-gray-400': !option.colorClass,
                }"
              ></span>
              {{ option.label }}
            </div>
          </template>
        </template>

        <!-- No results -->
        <div v-if="flatFilteredOptions.length === 0" class="px-3 py-3 text-sm text-gray-500 text-center">
          {{ noResultsText }}
        </div>
      </div>
    </Transition>
  </div>
</template>
