<script setup lang="ts">
import { ref, computed } from 'vue'
import { uploadFile } from '@/api/files'
import { renderMarkdown } from '@/composables/useMarkdown'
import { useToast } from '@/composables/useToast'

const props = withDefaults(defineProps<{
  modelValue: string
  rows?: number
  placeholder?: string
}>(), {
  rows: 8,
  placeholder: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const toast = useToast()
const textarea = ref<HTMLTextAreaElement | null>(null)
const activeTab = ref<'edit' | 'preview'>('edit')
const dragging = ref(false)
const uploading = ref(false)

const preview = computed(() => renderMarkdown(props.modelValue))

// --- Toolbar actions ---

interface ToolbarAction {
  icon: string
  title: string
  size?: string
  action: () => void
}

const toolbarActions: ToolbarAction[] = [
  { icon: 'fa-solid fa-bold', title: 'Gras', action: () => wrapSelection('**', '**') },
  { icon: 'fa-solid fa-italic', title: 'Italique', action: () => wrapSelection('*', '*') },
  { icon: 'fa-solid fa-heading', title: 'Titre 2', action: () => prefixLine('## ') },
  { icon: 'fa-solid fa-heading', title: 'Titre 3', size: 'text-xs', action: () => prefixLine('### ') },
  { icon: 'fa-solid fa-list-ul', title: 'Liste', action: () => prefixLine('- ') },
  { icon: 'fa-solid fa-list-ol', title: 'Liste numérotée', action: () => prefixLine('1. ') },
  { icon: 'fa-solid fa-link', title: 'Lien', action: () => insertLink() },
  { icon: 'fa-solid fa-image', title: 'Image', action: () => triggerImageUpload() },
  { icon: 'fa-solid fa-code', title: 'Code', action: () => wrapSelection('`', '`') },
  { icon: 'fa-solid fa-quote-left', title: 'Citation', action: () => prefixLine('> ') },
]

function wrapSelection(before: string, after: string) {
  const el = textarea.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const text = props.modelValue
  const selected = text.slice(start, end) || 'texte'
  const newText = text.slice(0, start) + before + selected + after + text.slice(end)
  emit('update:modelValue', newText)
  // Restore cursor after Vue re-renders
  const cursorPos = start + before.length + selected.length
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(cursorPos, cursorPos)
  })
}

function prefixLine(prefix: string) {
  const el = textarea.value
  if (!el) return
  const start = el.selectionStart
  const text = props.modelValue
  // Find the start of the current line
  const lineStart = text.lastIndexOf('\n', start - 1) + 1
  const newText = text.slice(0, lineStart) + prefix + text.slice(lineStart)
  emit('update:modelValue', newText)
  const cursorPos = start + prefix.length
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(cursorPos, cursorPos)
  })
}

function insertLink() {
  const el = textarea.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const text = props.modelValue
  const selected = text.slice(start, end) || 'texte'
  const insertion = `[${selected}](url)`
  const newText = text.slice(0, start) + insertion + text.slice(end)
  emit('update:modelValue', newText)
  // Select "url" so user can type the actual URL
  const urlStart = start + selected.length + 3
  const urlEnd = urlStart + 3
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(urlStart, urlEnd)
  })
}

function insertAtCursor(insertion: string) {
  const el = textarea.value
  if (!el) return
  const start = el.selectionStart
  const text = props.modelValue
  const newText = text.slice(0, start) + insertion + text.slice(start)
  emit('update:modelValue', newText)
  const cursorPos = start + insertion.length
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(cursorPos, cursorPos)
  })
}

// --- Image upload ---

const fileInput = ref<HTMLInputElement | null>(null)

function triggerImageUpload() {
  fileInput.value?.click()
}

async function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) await handleImageFile(file)
  input.value = ''
}

async function handleImageFile(file: File) {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!allowedTypes.includes(file.type)) {
    toast.error('Format accepté : JPG ou PNG uniquement')
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    toast.error('La taille du fichier ne doit pas dépasser 20 Mo')
    return
  }

  uploading.value = true
  try {
    const result = await uploadFile(file)
    const markdown = `![${file.name}](/api/files/${result.uuid})`
    insertAtCursor(markdown + '\n')
    toast.success('Image uploadée')
  } catch (e) {
    toast.error(e)
  } finally {
    uploading.value = false
  }
}

// --- Drag & drop ---

function onDragEnter(e: DragEvent) {
  e.preventDefault()
  if (e.dataTransfer?.types.includes('Files')) {
    dragging.value = true
  }
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
}

function onDragLeave(e: DragEvent) {
  e.preventDefault()
  // Only reset when leaving the container (not child elements)
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const { clientX, clientY } = e
  if (clientX < rect.left || clientX > rect.right || clientY < rect.top || clientY > rect.bottom) {
    dragging.value = false
  }
}

async function onDrop(e: DragEvent) {
  e.preventDefault()
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    await handleImageFile(file)
  }
}

// --- Paste images ---

async function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      e.preventDefault()
      const file = item.getAsFile()
      if (file) await handleImageFile(file)
      return
    }
  }
}
</script>

<template>
  <div class="border border-gray-300 rounded-md overflow-hidden">
    <!-- Tabs + Toolbar -->
    <div class="bg-gray-50 border-b border-gray-300">
      <!-- Tabs -->
      <div class="flex items-center border-b border-gray-200">
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === 'edit'
            ? 'border-veaf-600 text-veaf-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'edit'"
        >
          Éditer
        </button>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === 'preview'
            ? 'border-veaf-600 text-veaf-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = 'preview'"
        >
          Aperçu
        </button>
        <span v-if="uploading" class="ml-auto mr-3 text-xs text-gray-500">
          <i class="fa-solid fa-spinner fa-spin mr-1"></i>Upload en cours...
        </span>
      </div>

      <!-- Toolbar (only in edit mode) -->
      <div v-if="activeTab === 'edit'" class="flex items-center gap-1 px-2 py-1.5">
        <button
          v-for="(btn, idx) in toolbarActions"
          :key="idx"
          type="button"
          class="p-1.5 rounded hover:bg-gray-200 text-gray-600 hover:text-gray-900 transition-colors"
          :title="btn.title"
          @click="btn.action"
        >
          <i :class="[btn.icon, btn.size || 'text-sm']"></i>
        </button>
      </div>
    </div>

    <!-- Edit mode -->
    <div
      v-show="activeTab === 'edit'"
      class="relative"
      @dragenter="onDragEnter"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <textarea
        ref="textarea"
        :value="modelValue"
        :rows="rows"
        :placeholder="placeholder"
        class="w-full px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-veaf-500 resize-y"
        @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        @paste="onPaste"
      ></textarea>

      <!-- Drag overlay -->
      <div
        v-if="dragging"
        class="absolute inset-0 bg-veaf-50/80 border-2 border-dashed border-veaf-400 rounded flex items-center justify-center pointer-events-none"
      >
        <div class="text-veaf-600 font-medium">
          <i class="fa-solid fa-cloud-arrow-up text-2xl mb-1 block text-center"></i>
          Déposez l'image ici
        </div>
      </div>
    </div>

    <!-- Preview mode -->
    <div
      v-show="activeTab === 'preview'"
      class="prose max-w-none px-3 py-2 min-h-[100px]"
      :style="{ minHeight: `${rows * 1.5}rem` }"
    >
      <div v-if="modelValue" v-html="preview"></div>
      <p v-else class="text-gray-400 italic text-sm">Aucun contenu à afficher.</p>
    </div>

    <!-- Hidden file input for image toolbar button -->
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png"
      class="hidden"
      @change="handleFileSelect"
    />
  </div>
</template>
