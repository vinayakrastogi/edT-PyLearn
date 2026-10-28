/**
 * Gamification API contract. Mirrors backend/app/schemas/gamification.py: keep both identical.
 * See GAMIFICATION.md at the repository root.
 */

export type BadgeCategory = 'learning' | 'quizzes' | 'coding' | 'streaks' | 'modules' | 'levels'
export type BadgeRarity = 'common' | 'rare' | 'epic' | 'legendary'

export const ALLOWED_DAILY_GOALS = [20, 30, 50, 80] as const
export type DailyGoal = (typeof ALLOWED_DAILY_GOALS)[number]

export interface BadgeProgress {
  current: number
  target: number
}

export interface BadgeInfo {
  id: string
  name: string
  description: string
  icon: string // icon key from ICONS in @/lib/icons (kebab-case, e.g. "book-open"); render with <AppIcon/>
  category: BadgeCategory
  rarity: BadgeRarity
  earned: boolean
  earned_at: string | null
  progress: BadgeProgress
}

export interface RewardEvent {
  kind: string
  label: string
  amount: number
}

export interface StreakInfo {
  count: number
  longest: number
  freezes: number
  extended: boolean
  used_freeze: boolean
  milestone: number | null
  broken_from: number | null
  active_today: boolean
  at_risk: boolean
}

export interface DailyInfo {
  goal: number
  xp_today: number
  goal_met: boolean
  just_met: boolean
}

/** Attached as `rewards` to lesson-view, quiz submit and problem submit responses. */
export interface RewardSummary {
  xp_gained: number
  events: RewardEvent[]
  total_xp: number
  level: number
  previous_level: number
  level_title: string
  level_up: boolean
  xp_into_level: number
  xp_for_next_level: number
  streak: StreakInfo
  new_badges: BadgeInfo[]
  daily: DailyInfo
}

export interface WeeklyPoint {
  date: string // YYYY-MM-DD
  xp: number
}

export interface RecentEvent {
  kind: string
  label: string
  amount: number
  created_at: string
}

export interface GamificationSummary {
  xp_total: number
  level: number
  level_title: string
  xp_into_level: number
  xp_for_next_level: number
  next_level_xp: number
  streak: StreakInfo
  daily: DailyInfo
  weekly: WeeklyPoint[]
  badges_earned: number
  badges_total: number
  recent_badges: BadgeInfo[]
  recent_events: RecentEvent[]
  show_on_leaderboard: boolean
}

export interface BadgeListResponse {
  badges: BadgeInfo[]
}

export interface LeaderboardEntry {
  rank: number
  name: string
  xp: number
  level: number
  is_me: boolean
}

export interface LeaderboardResponse {
  period: 'week'
  entries: LeaderboardEntry[]
  me: { rank: number | null; xp: number; opted_in: boolean }
}

export interface SettingsUpdate {
  daily_goal?: DailyGoal
  show_on_leaderboard?: boolean
}
