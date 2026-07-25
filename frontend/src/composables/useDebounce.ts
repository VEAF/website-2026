import { onBeforeUnmount } from 'vue'

export interface DebouncedFn<T extends unknown[]> {
  (...args: T): void
  cancel: () => void
}

/**
 * Wrap a function so rapid successive calls collapse into a single deferred call.
 *
 * The pending call is cancelled automatically when the component unmounts, and can
 * be cancelled manually through `cancel()` (e.g. when the input becomes too short
 * to be worth searching). Must be called during component setup.
 */
export function useDebounce<T extends unknown[]>(
  fn: (...args: T) => void,
  delay = 300,
): DebouncedFn<T> {
  let timeout: ReturnType<typeof setTimeout> | null = null

  function cancel() {
    if (timeout) {
      clearTimeout(timeout)
      timeout = null
    }
  }

  const debounced = (...args: T) => {
    cancel()
    timeout = setTimeout(() => {
      timeout = null
      fn(...args)
    }, delay)
  }

  onBeforeUnmount(cancel)

  return Object.assign(debounced, { cancel })
}
