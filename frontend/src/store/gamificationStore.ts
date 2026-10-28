import { create } from 'zustand'
import { getGamificationSummary } from '@/api/gamification'
import type { GamificationSummary, RewardSummary } from '@/types/gamification'

interface GamificationState {
  /** Latest summary from the server (null until first load or when signed out). */
  summary: GamificationSummary | null
  loading: boolean
  /** Celebrations waiting to be shown by <RewardHost/>, oldest first. */
  rewardQueue: RewardSummary[]

  /** Fetch /api/gamification/me. Safe to call often; concurrent calls are merged. */
  refresh: () => Promise<void>
  /**
   * Feed the `rewards` object from a lesson/quiz/problem response. Immediately patches the
   * summary (so the navbar updates without waiting), queues a celebration when there is
   * something to show, and schedules a background refresh to resync with the server.
   */
  handleRewards: (rewards: RewardSummary | null | undefined) => void
  /** Remove and return nothing; used by <RewardHost/> once a celebration has been shown. */
  shiftReward: () => void
  reset: () => void
}

let inflight: Promise<void> | null = null
// Bumped by reset(): a refresh that was started for a previous learner must not write its result back.
let epoch = 0
let refreshTimer: ReturnType<typeof setTimeout> | null = null

export const useGamificationStore = create<GamificationState>((set, get) => ({
  summary: null,
  loading: false,
  rewardQueue: [],

  refresh: async () => {
    if (inflight) return inflight
    set({ loading: true })
    const startedAt = epoch
    const request: Promise<void> = getGamificationSummary()
      .then((summary) => {
        if (startedAt === epoch) set({ summary, loading: false })
      })
      .catch(() => {
        if (startedAt === epoch) set({ loading: false })
      })
      .finally(() => {
        if (inflight === request) inflight = null
      })
    inflight = request
    return request
  },

  handleRewards: (rewards) => {
    if (!rewards) return
    const current = get().summary
    if (current) {
      set({
        summary: {
          ...current,
          xp_total: rewards.total_xp,
          level: rewards.level,
          level_title: rewards.level_title,
          xp_into_level: rewards.xp_into_level,
          xp_for_next_level: rewards.xp_for_next_level,
          streak: { ...current.streak, ...rewards.streak },
          daily: rewards.daily,
        },
      })
    }
    const worthShowing =
      rewards.xp_gained > 0 ||
      rewards.level_up ||
      rewards.new_badges.length > 0 ||
      rewards.streak.milestone !== null ||
      rewards.streak.used_freeze ||
      // A streak that restarted must be explained, even when this activity earned no XP.
      (rewards.streak.broken_from ?? 0) > 1
    if (worthShowing) set((s) => ({ rewardQueue: [...s.rewardQueue, rewards] }))

    if (refreshTimer) clearTimeout(refreshTimer)
    refreshTimer = setTimeout(() => void get().refresh(), 600)
  },

  shiftReward: () => set((s) => ({ rewardQueue: s.rewardQueue.slice(1) })),

  reset: () => {
    if (refreshTimer) clearTimeout(refreshTimer)
    epoch += 1
    inflight = null
    set({ summary: null, loading: false, rewardQueue: [] })
  },
}))
