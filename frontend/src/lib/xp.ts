/**
 * Modules whose id starts with this (AI or faculty made) earn no XP; they still extend the streak.
 * Mirrors GENERATED_MODULE_PREFIX in backend/app/services/gamification_rules.py.
 */
const GENERATED_MODULE_PREFIX = 'generated-'

/** Whether work in this module can ever earn XP (the server decides; this only picks the right wording). */
export const moduleEarnsXp = (moduleId: string | undefined): boolean => !(moduleId ?? '').startsWith(GENERATED_MODULE_PREFIX)

export const NO_XP_MODULE_TEXT = 'Practice modules do not earn XP, but your work still keeps your streak going.'
