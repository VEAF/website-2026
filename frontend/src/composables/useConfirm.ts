import { ref } from 'vue'

export interface ConfirmButton {
  label: string
  icon: string
}

const defaultButton: ConfirmButton = { label: 'Supprimer', icon: 'fa-solid fa-trash' }

const visible = ref(false)
const message = ref('')
const button = ref<ConfirmButton>({ ...defaultButton })
let resolvePromise: ((value: boolean) => void) | null = null

export function useConfirm() {
  function confirm(msg: string, opts?: { button?: ConfirmButton }): Promise<boolean> {
    message.value = msg
    button.value = opts?.button ?? { ...defaultButton }
    visible.value = true

    return new Promise<boolean>((resolve) => {
      resolvePromise = resolve
    })
  }

  function handleResponse(value: boolean) {
    visible.value = false
    if (resolvePromise) {
      resolvePromise(value)
      resolvePromise = null
    }
  }

  return {
    visible,
    message,
    button,
    handleResponse,
    confirm,
  }
}
