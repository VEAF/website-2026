const MINUTE = 60_000
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR

export interface EventTimeBadge {
  text: string
  cssClass: string
}

/**
 * Format the delay before an event start, with two units at most and no rounding up:
 * "dans 3j 4h", "dans 2j", "dans 1h01", "dans 2h", "dans 45min", "imminent".
 */
export function formatTimeUntil(deltaMs: number): string {
  if (deltaMs < MINUTE) return 'imminent'

  if (deltaMs < HOUR) {
    return `dans ${Math.floor(deltaMs / MINUTE)}min`
  }

  if (deltaMs < DAY) {
    const hours = Math.floor(deltaMs / HOUR)
    const minutes = Math.floor((deltaMs % HOUR) / MINUTE)
    return minutes > 0 ? `dans ${hours}h${String(minutes).padStart(2, '0')}` : `dans ${hours}h`
  }

  const days = Math.floor(deltaMs / DAY)
  const hours = Math.floor((deltaMs % DAY) / HOUR)
  return hours > 0 ? `dans ${days}j ${hours}h` : `dans ${days}j`
}

/**
 * Build the state badge of an event: upcoming (with the remaining delay), running, or over.
 * `now` is injectable so the caller can pass a reactive clock (see `useNow`).
 */
export function eventTimeBadge(startDate: string, endDate: string, now: number = Date.now()): EventTimeBadge {
  const start = new Date(startDate).getTime()
  const end = new Date(endDate).getTime()

  if (now < start) {
    return { text: formatTimeUntil(start - now), cssClass: 'bg-green-100 text-green-800' }
  }
  if (now < end) {
    return { text: 'en cours !', cssClass: 'bg-yellow-100 text-yellow-800' }
  }
  return { text: 'terminé', cssClass: 'bg-red-100 text-red-800' }
}
