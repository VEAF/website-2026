import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
let resolvePromise: ((value: boolean) => void) | null = null

export function useConfirm() {
  function confirm(msg: string): Promise<boolean> {
    message.value = msg
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
    handleResponse,
    confirm,
  }
}
