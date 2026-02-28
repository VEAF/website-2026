// Module types (mirrors backend Module.TYPE_* in app/models/module.py)
export const MODULE_TYPE_NONE = 0
export const MODULE_TYPE_MAP = 1
export const MODULE_TYPE_AIRCRAFT = 2
export const MODULE_TYPE_HELICOPTER = 3
export const MODULE_TYPE_SPECIAL = 4

// Types that have a skill level
export const TYPES_WITH_LEVEL = [MODULE_TYPE_AIRCRAFT, MODULE_TYPE_HELICOPTER, MODULE_TYPE_SPECIAL]

// Types that are "flyable" (aircraft, helicopter, special) — used for event module filtering
export const FLYABLE_MODULE_TYPES = [MODULE_TYPE_AIRCRAFT, MODULE_TYPE_HELICOPTER, MODULE_TYPE_SPECIAL]

// Ordered list for iteration (profile views, admin)
export const MODULE_TYPE_ORDER = [MODULE_TYPE_MAP, MODULE_TYPE_AIRCRAFT, MODULE_TYPE_HELICOPTER, MODULE_TYPE_SPECIAL]

// Labels (French, singular)
export const MODULE_TYPE_LABELS: Record<number, string> = {
  [MODULE_TYPE_NONE]: 'Aucun',
  [MODULE_TYPE_MAP]: 'Carte',
  [MODULE_TYPE_AIRCRAFT]: 'Avion',
  [MODULE_TYPE_HELICOPTER]: 'Hélicoptère',
  [MODULE_TYPE_SPECIAL]: 'Spécial',
}

// Labels (French, plural — for section headers)
export const MODULE_TYPE_LABELS_PLURAL: Record<number, string> = {
  [MODULE_TYPE_MAP]: 'Cartes',
  [MODULE_TYPE_AIRCRAFT]: 'Avions',
  [MODULE_TYPE_HELICOPTER]: 'Hélicoptères',
  [MODULE_TYPE_SPECIAL]: 'Spécial',
}

// Tab key → module type mapping (for RosterView)
export const TAB_TO_MODULE_TYPE: Record<string, number> = {
  maps: MODULE_TYPE_MAP,
  aircrafts: MODULE_TYPE_AIRCRAFT,
  helicopters: MODULE_TYPE_HELICOPTER,
  specials: MODULE_TYPE_SPECIAL,
}

// Module type → FontAwesome icon class
export function moduleTypeIcon(moduleType: number | null): string {
  if (moduleType === MODULE_TYPE_HELICOPTER) return 'fa-solid fa-helicopter'
  if (moduleType === MODULE_TYPE_SPECIAL) return 'fa-solid fa-gear'
  return 'fa-solid fa-plane'
}
