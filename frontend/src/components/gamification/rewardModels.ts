import { BookOpen, Brain, Crosshair, Flag, Flame, Gem, Puzzle, Sparkles, Sprout, Target } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { BadgeInfo, BadgeRarity, RewardEvent, RewardSummary } from '@/types/gamification'

/**
 * Pure helpers that turn a server RewardSummary into what <RewardHost/> shows: an itemised toast
 * and a short sequence of celebration dialogs. Kept free of React so it is easy to reason about.
 */

/** One celebration dialog. `keys` identify what it celebrates so the same thing is never shown twice. */
export type RewardModal =
  | { type: 'level_up'; keys: string[]; level: number; previousLevel: number; title: string; xpIntoLevel: number; xpForNextLevel: number }
  | { type: 'badges'; keys: string[]; badges: BadgeInfo[] }
  | { type: 'streak_milestone'; keys: string[]; days: number; bonusXp: number }
  | { type: 'used_freeze'; keys: string[]; count: number; freezes: number }
  | { type: 'comeback'; keys: string[]; badge: BadgeInfo; count: number }

export interface RewardPlan {
  reward: RewardSummary
  modals: RewardModal[]
}

export interface ToastNote {
  /** Decorative; the text carries the meaning. */
  icon: LucideIcon
  text: string
}

export interface ToastParts {
  xp: number
  events: RewardEvent[]
  notes: ToastNote[]
}

const COMEBACK_BADGE_ID = 'comeback'

/** Decorative icon for an XP ledger kind (shown next to the event label, never instead of it). */
export function eventIcon(kind: string): LucideIcon {
  switch (kind) {
    case 'lesson':
      return BookOpen
    case 'quiz':
      return Brain
    case 'quiz_perfect':
      return Gem
    case 'problem':
      return Puzzle
    case 'problem_first_try':
      return Crosshair
    case 'module_complete':
      return Flag
    case 'daily_goal':
      return Target
    case 'streak_milestone':
      return Flame
    default:
      return Sparkles
  }
}

export const RARITY_LABEL: Record<BadgeRarity, string> = {
  common: 'Common',
  rare: 'Rare',
  epic: 'Epic',
  legendary: 'Legendary',
}

/** Background of the badge tile. */
export const RARITY_TILE: Record<BadgeRarity, string> = {
  common: 'bg-brand-yellow/30',
  rare: 'bg-brand-blue/25',
  epic: 'bg-brand-purple/25',
  legendary: 'bg-brand-orange/35',
}

/**
 * The rarity is always printed as text; this only adds colour to the tag. Dark text on blue and orange
 * (white on them is only about 3.4:1, below the 4.5:1 that 10px text needs); white on purple is 5.6:1.
 */
export const RARITY_TAG: Record<BadgeRarity, string> = {
  common: 'bg-bg-card text-text-primary',
  rare: 'bg-brand-blue text-text-primary',
  epic: 'bg-brand-purple text-white',
  legendary: 'bg-brand-orange text-text-primary',
}

/** What the XP toast should say for a reward, or null when there is nothing to toast. */
export function toastParts(reward: RewardSummary): ToastParts | null {
  const notes: ToastNote[] = []
  if (reward.daily.just_met && !reward.events.some((e) => e.kind === 'daily_goal')) {
    notes.push({ icon: Target, text: 'Daily goal reached!' })
  }
  if (reward.streak.broken_from !== null && reward.streak.broken_from > 1) {
    notes.push({ icon: Sprout, text: `Fresh start! Your ${reward.streak.broken_from}-day streak was a great run.` })
  }
  if (reward.xp_gained <= 0 && reward.events.length === 0 && notes.length === 0) return null
  return { xp: Math.max(0, reward.xp_gained), events: reward.events, notes }
}

/** Dialogs for one reward, skipping anything whose key is already in `seen`. */
function buildModals(reward: RewardSummary, seen: ReadonlySet<string>): RewardModal[] {
  const modals: RewardModal[] = []

  if (reward.level_up) {
    const key = `level:${reward.level}`
    if (!seen.has(key)) {
      modals.push({
        type: 'level_up',
        keys: [key],
        level: reward.level,
        previousLevel: reward.previous_level,
        title: reward.level_title,
        xpIntoLevel: reward.xp_into_level,
        xpForNextLevel: reward.xp_for_next_level,
      })
    }
  }

  // The comeback badge gets its own, kinder dialog instead of the generic badge card.
  const fresh = reward.new_badges.filter((b) => !seen.has(`badge:${b.id}`))
  const comeback = fresh.find((b) => b.id === COMEBACK_BADGE_ID)
  const badges = fresh.filter((b) => b.id !== COMEBACK_BADGE_ID)
  if (badges.length > 0) {
    modals.push({ type: 'badges', keys: badges.map((b) => `badge:${b.id}`), badges })
  }

  const milestone = reward.streak.milestone
  if (milestone !== null && !seen.has(`milestone:${milestone}`)) {
    const bonusXp = reward.events.filter((e) => e.kind === 'streak_milestone').reduce((sum, e) => sum + e.amount, 0)
    modals.push({ type: 'streak_milestone', keys: [`milestone:${milestone}`], days: milestone, bonusXp })
  }

  if (reward.streak.used_freeze && !seen.has(`freeze:${reward.streak.count}`)) {
    modals.push({
      type: 'used_freeze',
      keys: [`freeze:${reward.streak.count}`],
      count: reward.streak.count,
      freezes: reward.streak.freezes,
    })
  }

  if (comeback) {
    modals.push({ type: 'comeback', keys: [`badge:${comeback.id}`], badge: comeback, count: reward.streak.count })
  }

  return modals
}

/**
 * One plan per queued reward. `shown` holds the keys already celebrated; keys that repeat inside the
 * queue itself are also skipped, so a replayed response can never show the same celebration twice.
 */
export function buildPlans(queue: RewardSummary[], shown: ReadonlySet<string>): RewardPlan[] {
  const seen = new Set(shown)
  return queue.map((reward) => {
    const modals = buildModals(reward, seen)
    for (const m of modals) for (const k of m.keys) seen.add(k)
    return { reward, modals }
  })
}
