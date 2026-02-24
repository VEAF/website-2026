/**
 * Format a raw mission name by replacing underscores with spaces.
 */
export function formatMissionName(name: string): string {
  return name.replace(/_/g, ' ')
}

/**
 * Format a mission name for display, stripping the trailing "ICAO XXXX" suffix.
 * The full name (with ICAO) should be kept in tooltips.
 */
export function shortMissionName(name: string): string {
  return formatMissionName(name).replace(/\s+ICAO\s+\S+$/i, '')
}
