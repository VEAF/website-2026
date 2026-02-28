export function useRosterHelpers() {
  function statusIcon(status: number): { icon: string; class: string; title: string } {
    if (status >= 2 && status <= 8)
      return { icon: 'fa-solid fa-user', class: 'text-green-600', title: 'Membre' }
    if (status === 1)
      return { icon: 'fa-solid fa-user-graduate', class: 'text-yellow-500', title: 'Cadet' }
    return { icon: 'fa-solid fa-user', class: 'text-gray-400', title: 'Invit\u00e9' }
  }

  function levelBadge(level: number): string {
    if (level === 3) return 'I'
    if (level === 2) return 'M'
    if (level === 1) return 'R'
    return ''
  }

  function levelClass(level: number): string {
    if (level === 3) return 'bg-green-100 text-green-800'
    if (level === 2) return 'bg-blue-100 text-blue-800'
    if (level === 1) return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-500'
  }

  return { statusIcon, levelBadge, levelClass }
}
