import { useToast as useVueToast, TYPE } from 'vue-toastification'

export function useToast() {
  const toast = useVueToast()

  function success(message: string) {
    toast(message, { type: TYPE.SUCCESS })
  }

  function error(err: unknown) {
    let message = 'Une erreur est survenue'
    if (typeof err === 'string') {
      message = err
    } else if (err instanceof Error) {
      message = err.message
    } else if (err && typeof err === 'object' && 'response' in err) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      message = axiosErr.response?.data?.detail || message
    }
    toast(message, { type: TYPE.ERROR })
  }

  function info(message: string) {
    toast(message, { type: TYPE.INFO })
  }

  function warning(message: string) {
    toast(message, { type: TYPE.WARNING })
  }

  return { success, error, info, warning }
}
