import { describe, expect, it } from 'vitest'
import { eventTimeBadge, formatTimeUntil } from './date'

const MINUTE = 60_000
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR

describe('formatTimeUntil', () => {
  it('reports an event starting in a bit over an hour in hours and minutes', () => {
    // GIVEN the case reported in issue #184: 19:59, event starting the same day at 21:00
    // WHEN / THEN the delay must not be rounded up to a full day
    expect(formatTimeUntil(HOUR + MINUTE)).toBe('dans 1h01')
  })

  it('reports a delay under a minute as imminent', () => {
    expect(formatTimeUntil(30_000)).toBe('imminent')
    expect(formatTimeUntil(0)).toBe('imminent')
  })

  it('reports a delay under an hour in minutes', () => {
    expect(formatTimeUntil(45 * MINUTE)).toBe('dans 45min')
    expect(formatTimeUntil(MINUTE)).toBe('dans 1min')
    expect(formatTimeUntil(HOUR - 1)).toBe('dans 59min')
  })

  it('omits the minutes on a whole number of hours', () => {
    expect(formatTimeUntil(2 * HOUR)).toBe('dans 2h')
  })

  it('keeps hours and minutes up to the last minute before a day', () => {
    expect(formatTimeUntil(23 * HOUR + 59 * MINUTE)).toBe('dans 23h59')
  })

  it('reports a delay over a day in days and hours', () => {
    expect(formatTimeUntil(DAY + HOUR)).toBe('dans 1j 1h')
    expect(formatTimeUntil(3 * DAY + 4 * HOUR)).toBe('dans 3j 4h')
  })

  it('omits the hours on a whole number of days', () => {
    expect(formatTimeUntil(DAY)).toBe('dans 1j')
    expect(formatTimeUntil(3 * DAY)).toBe('dans 3j')
  })

  it('truncates instead of rounding up', () => {
    // GIVEN 25h59: floor to 1 day + 1 hour, never 2 days
    expect(formatTimeUntil(DAY + HOUR + 59 * MINUTE)).toBe('dans 1j 1h')
  })
})

describe('eventTimeBadge', () => {
  const start = '2026-04-15T21:00:00+00:00'
  const end = '2026-04-15T23:00:00+00:00'

  it('shows the remaining delay for an upcoming event', () => {
    // GIVEN now is 19:59 on the day of the event
    const now = new Date('2026-04-15T19:59:00+00:00').getTime()

    // WHEN
    const badge = eventTimeBadge(start, end, now)

    // THEN
    expect(badge).toEqual({ text: 'dans 1h01', cssClass: 'bg-green-100 text-green-800' })
  })

  it('marks a running event', () => {
    const now = new Date('2026-04-15T22:00:00+00:00').getTime()
    expect(eventTimeBadge(start, end, now)).toEqual({
      text: 'en cours !',
      cssClass: 'bg-yellow-100 text-yellow-800',
    })
  })

  it('marks a finished event', () => {
    const now = new Date('2026-04-16T00:00:00+00:00').getTime()
    expect(eventTimeBadge(start, end, now)).toEqual({
      text: 'terminé',
      cssClass: 'bg-red-100 text-red-800',
    })
  })

  it('treats the exact start instant as running and the exact end instant as finished', () => {
    expect(eventTimeBadge(start, end, new Date(start).getTime()).text).toBe('en cours !')
    expect(eventTimeBadge(start, end, new Date(end).getTime()).text).toBe('terminé')
  })
})
