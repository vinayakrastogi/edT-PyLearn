import React, { useCallback, useEffect, useId, useRef, useState } from 'react'
import { Medal, Sprout, TriangleAlert, Trophy } from 'lucide-react'
import { Card } from '@/components/Card'
import { Skeleton } from '@/components/Skeleton'
import { getLeaderboard, updateGamificationSettings } from '@/api/gamification'
import { useGamificationStore } from '@/store/gamificationStore'
import { IconTile } from '@/lib/icons'
import type { LeaderboardEntry, LeaderboardResponse } from '@/types/gamification'

/**
 * The privacy model, in plain words. Shown by the leaderboard card and (identically) by the
 * leaderboard switch in Settings, so learners always see the same promise.
 */
export const LeaderboardPrivacyNote: React.FC<{ className?: string }> = ({ className = '' }) => (
  <ul className={`space-y-1 font-body text-xs text-text-muted leading-snug list-disc pl-4 ${className}`}>
    <li>
      <strong className="text-text-primary">Opt-in only.</strong> You stay hidden unless you choose to join.
    </li>
    <li>
      Only your <strong className="text-text-primary">first name and last initial</strong> are shown, for example
      &ldquo;Asha K.&rdquo;.
    </li>
    <li>
      Only your level and the <strong className="text-text-primary">XP you earned in the last 7 days</strong> are
      shared. Nothing else.
    </li>
    <li>You can leave at any time.</li>
  </ul>
)

/**
 * Medal fills for the top three (gold, silver, bronze). The medal keeps a dark outline, like XpIcon,
 * so it stays visible on every row background, the yellow "you" row included. Decorative: the rank
 * number is always printed.
 */
const MEDAL_FILLS: Record<number, string> = { 1: 'fill-yellow-400', 2: 'fill-gray-300', 3: 'fill-amber-600' }

type Status = 'loading' | 'ready' | 'error'

const EntryRow: React.FC<{ entry: LeaderboardEntry }> = ({ entry }) => (
  <li
    className={`flex items-center gap-3 px-3 py-2 border-2 ${
      entry.is_me ? 'border-border-dark bg-brand-yellow/30 shadow-neo-sm' : 'border-border-dark/20 bg-bg-card'
    }`}
    style={{ borderRadius: '4px' }}
  >
    <span className="w-14 shrink-0 flex items-center gap-1 font-mono font-bold text-sm text-text-primary">
      <span className="sr-only">Rank </span>#{entry.rank}
      {MEDAL_FILLS[entry.rank] && (
        <Medal aria-hidden className={`w-4 h-4 shrink-0 text-border-dark ${MEDAL_FILLS[entry.rank]}`} strokeWidth={2.25} />
      )}
    </span>
    <span className="min-w-0 flex-1 font-body font-bold text-sm truncate" title={entry.name}>
      {entry.name}
      {entry.is_me && (
        <span className="ml-2 align-middle bg-border-dark text-white font-mono text-[10px] font-bold px-1.5 py-0.5">
          YOU
        </span>
      )}
    </span>
    <span className="shrink-0 font-mono text-xs text-text-muted">
      <span aria-hidden>Lv {entry.level}</span>
      <span className="sr-only">Level {entry.level}</span>
    </span>
    <span className="shrink-0 min-w-[4.5rem] whitespace-nowrap text-right font-mono text-sm font-bold">{entry.xp.toLocaleString()} XP</span>
  </li>
)

/**
 * Weekly leaderboard (rolling 7 days) among opted-in learners. Self-contained: it loads its own
 * data, handles loading / error / empty states and lets the learner join or leave.
 */
export const LeaderboardCard: React.FC = () => {
  const titleId = useId()
  const [data, setData] = useState<LeaderboardResponse | null>(null)
  const [status, setStatus] = useState<Status>('loading')
  const [busy, setBusy] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [announce, setAnnounce] = useState('')
  const alive = useRef(true)

  const myLevel = useGamificationStore((s) => s.summary?.level ?? null)

  useEffect(() => {
    alive.current = true
    return () => {
      alive.current = false
    }
  }, [])

  const load = useCallback(async (keepVisible = false) => {
    if (!keepVisible) setStatus('loading')
    try {
      const res = await getLeaderboard()
      if (!alive.current) return
      setData(res)
      setStatus('ready')
    } catch {
      if (!alive.current) return
      setStatus('error')
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const optedIn = data?.me.opted_in ?? false

  const toggleMembership = async () => {
    if (busy || !data) return
    const joining = !optedIn
    setBusy(true)
    setActionError(null)
    try {
      const summary = await updateGamificationSettings({ show_on_leaderboard: joining })
      // The response is the fresh summary: put it straight into the store, then resync.
      useGamificationStore.setState({ summary })
      void useGamificationStore.getState().refresh()
      await load(true)
      if (alive.current) {
        setAnnounce(joining ? 'You joined the weekly leaderboard.' : 'You left the weekly leaderboard.')
      }
    } catch {
      if (alive.current) {
        setActionError(
          joining
            ? 'We could not add you to the leaderboard. Please try again.'
            : 'We could not remove you from the leaderboard. Please try again.',
        )
      }
    } finally {
      if (alive.current) setBusy(false)
    }
  }

  const entries = data?.entries ?? []
  const meInList = entries.some((e) => e.is_me)
  const meRank = data?.me.rank ?? null

  return (
    <Card accent="purple" className="flex flex-col">
      <section aria-labelledby={titleId} className="flex flex-col flex-1">
        <div className="flex items-start gap-3 mb-4 border-b-2 border-border-dark pb-3">
          <IconTile icon={Trophy} color="yellow" size="sm" />
          <div>
            <h2 id={titleId} className="font-heading font-bold text-xl leading-tight">
              Weekly Leaderboard
            </h2>
            <p className="font-mono text-xs text-text-muted">XP earned in the last 7 days</p>
          </div>
        </div>

        {status === 'loading' && !data && (
          <div role="status" aria-label="Loading leaderboard" className="space-y-2">
            {[0, 1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        )}

        {status === 'error' && (
          <div role="alert" className="border-2 border-border-dark bg-brand-pink/10 p-4" style={{ borderRadius: '4px' }}>
            <p className="font-body font-bold text-sm mb-1">The leaderboard did not load.</p>
            <p className="font-body text-sm text-text-muted mb-3">
              Check your connection and try again. Your progress is safe.
            </p>
            <button
              type="button"
              onClick={() => void load()}
              className="neo-btn bg-bg-card text-text-primary px-3 py-1.5 text-sm hover:bg-brand-yellow/20"
            >
              Try again
            </button>
          </div>
        )}

        {data && status !== 'error' && (
          <>
            {/* One block for both states so the same button keeps keyboard focus when it flips. */}
            <div
              className={`mb-4 p-3 border-2 border-border-dark ${optedIn ? 'bg-bg-base' : 'bg-brand-purple/10'}`}
              style={{ borderRadius: '4px' }}
            >
              <p className="font-body text-sm mb-3">
                {optedIn
                  ? meRank !== null
                    ? `You are on the leaderboard at rank #${meRank} this week.`
                    : 'You are on the leaderboard. Earn some XP to get a rank.'
                  : 'You are not on the leaderboard. Join to compare your week with other learners. It is completely optional.'}
              </p>
              <button
                type="button"
                onClick={() => void toggleMembership()}
                aria-disabled={busy}
                aria-busy={busy}
                className={`neo-btn px-3 py-1.5 text-sm ${
                  optedIn ? 'bg-bg-card text-text-primary hover:bg-brand-yellow/20' : 'bg-brand-purple text-white'
                } ${busy ? 'opacity-60 cursor-wait' : ''}`}
              >
                {busy ? 'Saving…' : optedIn ? 'Leave leaderboard' : 'Join the leaderboard'}
              </button>
              {actionError && (
                <p role="alert" className="mt-2 flex items-start gap-1.5 font-body text-sm font-bold text-text-primary">
                  <TriangleAlert aria-hidden className="w-4 h-4 shrink-0 mt-0.5" strokeWidth={2.5} />
                  <span>{actionError}</span>
                </p>
              )}
            </div>

            {entries.length === 0 ? (
              <div className="border-2 border-dashed border-border-dark/40 p-5 text-center" style={{ borderRadius: '4px' }}>
                <Sprout aria-hidden className="block w-8 h-8 mx-auto mb-1 text-brand-green" strokeWidth={2.5} />
                <p className="font-body font-bold text-sm">
                  {optedIn ? 'No one has earned XP this week yet.' : 'Nobody has joined yet.'}
                </p>
                <p className="font-body text-xs text-text-muted mt-1">
                  {optedIn
                    ? 'Read a lesson or take a quiz and you will be first on the board.'
                    : 'Be the first to join the weekly leaderboard.'}
                </p>
              </div>
            ) : (
              <ol className="space-y-2" aria-label="Top learners this week">
                {entries.map((entry, i) => (
                  <EntryRow key={i} entry={entry} />
                ))}
              </ol>
            )}

            {/* The learner is opted in but outside the top entries. */}
            {optedIn && meRank !== null && !meInList && (
              <ol className="mt-2" aria-label="Your position">
                <li
                  className="flex items-center gap-3 px-3 py-2 border-2 border-border-dark bg-brand-yellow/30 shadow-neo-sm"
                  style={{ borderRadius: '4px' }}
                >
                  <span className="w-14 shrink-0 font-mono font-bold text-sm">
                    <span className="sr-only">Rank </span>#{meRank}
                  </span>
                  <span className="min-w-0 flex-1 font-body font-bold text-sm">
                    You
                    <span className="ml-2 align-middle bg-border-dark text-white font-mono text-[10px] font-bold px-1.5 py-0.5">
                      YOU
                    </span>
                  </span>
                  {myLevel !== null && (
                    <span className="shrink-0 font-mono text-xs text-text-muted">
                      <span aria-hidden>Lv {myLevel}</span>
                      <span className="sr-only">Level {myLevel}</span>
                    </span>
                  )}
                  <span className="shrink-0 min-w-[4.5rem] whitespace-nowrap text-right font-mono text-sm font-bold">
                    {data.me.xp.toLocaleString()} XP
                  </span>
                </li>
              </ol>
            )}

            <div className="mt-4 pt-3 border-t-2 border-border-dark/15">
              <h3 className="font-mono text-[11px] font-bold uppercase tracking-wide text-text-muted mb-1.5">
                Your privacy
              </h3>
              <LeaderboardPrivacyNote />
            </div>
          </>
        )}

        <p role="status" aria-live="polite" className="sr-only">
          {announce}
        </p>
      </section>
    </Card>
  )
}
