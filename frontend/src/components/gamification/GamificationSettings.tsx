import React, { useCallback, useEffect, useId, useRef, useState } from 'react'
import { Check, Target, TriangleAlert } from 'lucide-react'
import { Card } from '@/components/Card'
import { Skeleton } from '@/components/Skeleton'
import { LeaderboardPrivacyNote } from '@/components/gamification/LeaderboardCard'
import { updateGamificationSettings } from '@/api/gamification'
import { useGamificationStore } from '@/store/gamificationStore'
import { ALLOWED_DAILY_GOALS } from '@/types/gamification'
import type { DailyGoal, SettingsUpdate } from '@/types/gamification'

const GOAL_NAMES: Record<DailyGoal, string> = {
  20: 'Relaxed',
  30: 'Steady',
  50: 'Focused',
  80: 'Intense',
}

/** Daily goal chips and the leaderboard opt-in. Reads the store summary and refreshes it after each change. */
export const GamificationSettings: React.FC = () => {
  const groupName = useId()
  const goalHintId = useId()
  const switchLabelId = useId()
  const switchDescId = useId()

  const summary = useGamificationStore((s) => s.summary)
  const refresh = useGamificationStore((s) => s.refresh)

  const [tried, setTried] = useState(false)
  const [saving, setSaving] = useState(false)
  // Optimistic values: shown while a request is in flight, dropped (= rolled back) if it fails.
  const [pendingGoal, setPendingGoal] = useState<DailyGoal | null>(null)
  const [pendingOptIn, setPendingOptIn] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [announce, setAnnounce] = useState('')
  const alive = useRef(true)

  useEffect(() => {
    alive.current = true
    return () => {
      alive.current = false
    }
  }, [])

  const load = useCallback(() => {
    setTried(false)
    void refresh().finally(() => {
      if (alive.current) setTried(true)
    })
  }, [refresh])

  useEffect(() => {
    load()
  }, [load])

  /**
   * Latest-choice-wins save queue: each choice is shown at once, and the PATCH requests go out one at a
   * time with the newest unsaved values. Arrow-keying through the goal radios therefore saves only
   * where the learner stopped (never silently dropping a choice) and focus never fights the selection.
   */
  const wanted = useRef<SettingsUpdate>({})
  const draining = useRef(false)

  const drain = async () => {
    if (draining.current) return
    draining.current = true
    setSaving(true)
    setError(null)
    setAnnounce('Saving your changes...')
    let saved: SettingsUpdate = {}
    let failed = false
    try {
      while (Object.keys(wanted.current).length > 0) {
        const update = wanted.current
        wanted.current = {}
        try {
          const next = await updateGamificationSettings(update)
          useGamificationStore.setState({ summary: next })
          saved = { ...saved, ...update }
        } catch {
          // Roll back: drop whatever else was waiting too, so the screen shows what the server has.
          wanted.current = {}
          failed = true
          if (alive.current) {
            setError(
              update.daily_goal !== undefined && update.show_on_leaderboard === undefined
                ? 'We could not save your daily goal, so it was left as it was. Please try again.'
                : update.show_on_leaderboard !== undefined && update.daily_goal === undefined
                  ? 'We could not save your leaderboard choice, so it was left as it was. Please try again.'
                  : 'We could not save your changes, so they were left as they were. Please try again.',
            )
          }
        }
      }
    } finally {
      draining.current = false
      if (!failed) void refresh()
      if (alive.current) {
        const parts: string[] = []
        if (!failed && saved.daily_goal !== undefined) parts.push(`Daily goal set to ${saved.daily_goal} XP.`)
        if (!failed && saved.show_on_leaderboard !== undefined) {
          parts.push(saved.show_on_leaderboard ? 'You joined the weekly leaderboard.' : 'You left the weekly leaderboard.')
        }
        setAnnounce(parts.join(' '))
        setPendingGoal(null)
        setPendingOptIn(null)
        setSaving(false)
      }
    }
  }

  const chooseGoal = (goal: DailyGoal) => {
    if (!summary || goal === (pendingGoal ?? summary.daily.goal)) return
    setPendingGoal(goal)
    wanted.current = { ...wanted.current, daily_goal: goal }
    void drain()
  }

  const toggleLeaderboard = () => {
    if (!summary) return
    const next = !(pendingOptIn ?? summary.show_on_leaderboard)
    setPendingOptIn(next)
    wanted.current = { ...wanted.current, show_on_leaderboard: next }
    void drain()
  }

  const goal = summary ? (pendingGoal ?? summary.daily.goal) : null
  const optedIn = summary ? (pendingOptIn ?? summary.show_on_leaderboard) : false

  return (
    <Card accent="purple" className="mb-8">
      <h2 className="font-heading font-bold text-2xl mb-4 flex items-center gap-2">
        <Target aria-hidden className="w-6 h-6 shrink-0" strokeWidth={2.5} />
        Goals &amp; Leaderboard
      </h2>

      {!summary && !tried && (
        <div role="status" aria-label="Loading your goal settings" className="space-y-3">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-6 w-56" />
          <Skeleton className="h-16 w-full" />
        </div>
      )}

      {!summary && tried && (
        <div role="alert" className="border-2 border-border-dark bg-brand-pink/10 p-4" style={{ borderRadius: '4px' }}>
          <p className="font-body font-bold text-sm mb-1">Your goal settings did not load.</p>
          <p className="font-body text-sm text-text-muted mb-3">Check your connection and try again.</p>
          <button
            type="button"
            onClick={load}
            className="neo-btn bg-bg-card text-text-primary px-3 py-1.5 text-sm hover:bg-brand-yellow/20"
          >
            Try again
          </button>
        </div>
      )}

      {summary && goal !== null && (
        <div className="space-y-6">
          {error && (
            <div role="alert" className="flex items-start gap-2 bg-brand-pink/20 text-text-primary font-bold text-sm p-3 border-2 border-border-dark">
              <TriangleAlert aria-hidden className="w-4 h-4 shrink-0 mt-0.5" strokeWidth={2.5} />
              <span>{error}</span>
            </div>
          )}

          {/* Daily goal */}
          <fieldset aria-describedby={goalHintId} aria-busy={saving} className="border-b border-border-dark pb-6 min-w-0">
            <legend className="font-body font-bold mb-1 p-0">Daily XP goal</legend>
            <p id={goalHintId} className="text-sm text-text-muted mb-3">
              How much XP you want to earn each day. Reading a lesson is worth 10 XP, so 30 XP is about three lessons.
              You can change this whenever you like.
            </p>
            <div className="flex flex-wrap gap-3">
              {ALLOWED_DAILY_GOALS.map((g) => {
                const selected = goal === g
                return (
                  <label key={g} className="relative cursor-pointer">
                    <input
                      type="radio"
                      name={groupName}
                      value={g}
                      checked={selected}
                      onChange={() => chooseGoal(g)}
                      className="peer sr-only"
                    />
                    <span
                      className={`block min-w-[104px] px-4 py-2 border-2 border-border-dark text-center transition-all duration-150 peer-focus-visible:outline peer-focus-visible:outline-[3px] peer-focus-visible:outline-brand-blue peer-focus-visible:outline-offset-2 ${
                        selected
                          ? 'bg-brand-yellow shadow-neo-sm'
                          : 'bg-bg-card hover:bg-brand-yellow/20'
                      } ${saving ? 'opacity-70' : ''}`}
                      style={{ borderRadius: '4px' }}
                    >
                      <span className="flex items-center justify-center gap-1 font-mono font-bold text-sm">
                        {selected && <Check aria-hidden className="w-3.5 h-3.5 shrink-0" strokeWidth={3} />}
                        {g} XP
                      </span>
                      <span className="block font-body text-xs text-text-muted">{GOAL_NAMES[g]}</span>
                    </span>
                  </label>
                )
              })}
            </div>
          </fieldset>

          {/* Leaderboard opt-in */}
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div id={switchLabelId} className="font-body font-bold">
                Show me on the weekly leaderboard
              </div>
              <div id={switchDescId} className="mt-2">
                <LeaderboardPrivacyNote />
              </div>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={optedIn}
              aria-labelledby={switchLabelId}
              aria-describedby={switchDescId}
              onClick={toggleLeaderboard}
              className={`shrink-0 flex items-center gap-2 cursor-pointer ${saving ? 'opacity-70' : ''}`}
            >
              <span
                aria-hidden
                className={`relative block w-14 h-8 border-2 border-border-dark transition-colors duration-150 ${
                  optedIn ? 'bg-brand-green' : 'bg-bg-card'
                }`}
                style={{ borderRadius: '4px' }}
              >
                <span
                  className={`absolute top-0.5 block w-6 h-6 bg-bg-dark border-2 border-border-dark transition-all duration-150 ${
                    optedIn ? 'left-[26px]' : 'left-0.5'
                  }`}
                  style={{ borderRadius: '2px' }}
                />
              </span>
              <span aria-hidden className="w-8 text-left font-mono font-bold text-sm">
                {optedIn ? 'ON' : 'OFF'}
              </span>
            </button>
          </div>
        </div>
      )}

      <p role="status" aria-live="polite" className="sr-only">
        {announce}
      </p>
    </Card>
  )
}
