import { ref } from 'vue'

const CHECK_INTERVAL = 120_000 // 2 minutes
const newVersionAvailable = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

async function checkVersion() {
  try {
    const res = await fetch(`/version.json?t=${Date.now()}`)
    if (!res.ok) return
    const data = await res.json()
    if (data.version && data.version !== __APP_VERSION__) {
      newVersionAvailable.value = true
    }
  } catch {
    // silently ignore network errors
  }
}

export function useVersionCheck() {
  function startVersionCheck() {
    if (import.meta.env.DEV || timer !== null) return
    checkVersion()
    timer = setInterval(checkVersion, CHECK_INTERVAL)
  }

  function stopVersionCheck() {
    if (timer !== null) {
      clearInterval(timer)
      timer = null
    }
  }

  function reload() {
    window.location.reload()
  }

  return { newVersionAvailable, startVersionCheck, stopVersionCheck, reload }
}
