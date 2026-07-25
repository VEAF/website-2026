import { onUnmounted, ref, type Ref } from 'vue'

const TICK_INTERVAL = 30_000 // 30 seconds

/**
 * Reactive clock returning the current timestamp, refreshed every `intervalMs`.
 * The interval is cleared when the calling component is unmounted.
 */
export function useNow(intervalMs: number = TICK_INTERVAL): Ref<number> {
  const now = ref(Date.now())
  const timer = setInterval(() => {
    now.value = Date.now()
  }, intervalMs)

  onUnmounted(() => clearInterval(timer))

  return now
}
