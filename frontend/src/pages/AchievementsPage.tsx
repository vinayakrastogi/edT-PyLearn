import React, { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Brain,
  Check,
  CodeXml,
  Flame,
  Layers,
  LayoutGrid,
  TrendingUp,
  Trophy,
  Zap,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { Button } from '@/components/Button'
import { Card } from '@/components/Card'
import { Mascot } from '@/components/Mascot'
import type { MascotMood } from '@/components/Mascot'
import { Skeleton } from '@/components/Skeleton'
import { BadgeCard } from '@/components/gamification/BadgeCard'
import { LeaderboardCard } from '@/components/gamification/LeaderboardCard'
import { LevelBar } from '@/components/gamification/LevelBar'
import { StreakFlame } from '@/components/gamification/StreakFlame'
import { eventIcon } from '@/components/gamification/rewardModels'
import { getBadges } from '@/api/gamification'
import { useGamificationStore } from '@/store/gamificationStore'
import { IconTile } from '@/lib/icons'
import type { BadgeCategory, BadgeInfo, GamificationSummary, RecentEvent } from '@/types/gamification'

type Tab = 'all' | 'earned' | 'locked'
type CategoryFilter = BadgeCategory | 'all'
type LoadState = 'loading' | 'ready' | 'error'

const TABS: ReadonlyArray<{ id: Tab; label: string }> = [
  { id: 'all', label: 'All' },
  { id: 'earned', label: 'Earned' },
  { id: 'locked', label: 'Locked' },
]

const CATEGORIES: ReadonlyArray<{ id: BadgeCategory; label: string; icon: LucideIcon }> = [
  { id: 'learning', label: 'Learning', icon: BookOpen },
  { id: 'quizzes', label: 'Quizzes', icon: Brain },
  { id: 'coding', label: 'Coding', icon: CodeXml },
  { id: 'streaks', label: 'Streaks', icon: Flame },
  { id: 'modules', label: 'Modules', icon: Layers },
  { id: 'levels', label: 'Levels', icon: TrendingUp },
]

const MAX_LEVEL = 99

/** The API sends UTC; a timestamp without a zone designator is treated as UTC rather than local. */
const parseServerDate = (iso: string): Date | null => {
  const hasZone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(iso)
  const d = new Date(hasZone || !iso.includes('T') ? iso : `${iso}Z`)
  return Number.isNaN(d.getTime()) ? null : d
}

const sameDay = (a: Date, b: Date) =>
  a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()

/** "Today, 3:05 PM", "Yesterday" or "Oct 1". */
const formatWhen = (iso: string): string => {
  const d = parseServerDate(iso)
  if (!d) return ''
  const now = new Date()
  const yesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1)
  if (sameDay(d, now)) {
    return `Today, ${d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })}`
  }
  if (sameDay(d, yesterday)) return 'Yesterday'
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

const progressRatio = (b: BadgeInfo) => (b.progress.target > 0 ? b.progress.current / b.progress.target : 0)

/** Earned badges first (newest first), then locked ones, closest to being earned first. */
const sortBadges = (list: BadgeInfo[]): BadgeInfo[] =>
  [...list].sort((a, b) => {
    if (a.earned !== b.earned) return a.earned ? -1 : 1
    if (a.earned) return (b.earned_at ?? '').localeCompare(a.earned_at ?? '')
    return progressRatio(b) - progressRatio(a)
  })

const StatTile: React.FC<{ label: string; accent: string; children: React.ReactNode }> = ({ label, accent, children }) => (
  <div className={`neo-card p-4 border-t-4 ${accent}`}>
    <p className="font-mono text-xs font-bold uppercase tracking-wider text-text-muted mb-2">{label}</p>
    {children}
  </div>
)

const SummaryHeader: React.FC<{ summary: GamificationSummary }> = ({ summary }) => {
  const atMax = summary.level >= MAX_LEVEL
  const xpToNext = Math.max(0, summary.xp_for_next_level - summary.xp_into_level)
  const badgePct = summary.badges_total > 0 ? Math.round((summary.badges_earned / summary.badges_total) * 100) : 0

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatTile label="Level" accent="border-t-brand-blue">
        <p className="font-heading font-black text-3xl leading-none mb-3">{summary.level_title}</p>
        <LevelBar
          level={summary.level}
          xpIntoLevel={summary.xp_into_level}
          xpForNextLevel={summary.xp_for_next_level}
          size="md"
          showNumbers
        />
      </StatTile>

      <StatTile label="Total XP" accent="border-t-brand-yellow">
        <p className="font-heading font-black text-3xl leading-none mb-2">{summary.xp_total.toLocaleString()} XP</p>
        <p className="font-mono text-sm text-text-muted">
          {atMax ? 'Top level reached!' : `${xpToNext.toLocaleString()} XP to level ${summary.level + 1}`}
        </p>
      </StatTile>

      <StatTile label="Streak" accent="border-t-brand-orange">
        <StreakFlame
          count={summary.streak.count}
          freezes={summary.streak.freezes}
          atRisk={summary.streak.at_risk}
          active={summary.streak.active_today}
          size="lg"
        />
        <p className="font-mono text-sm text-text-muted mt-2">
          {summary.streak.count > 0 ? 'day streak' : 'No streak yet'} · longest {summary.streak.longest}{' '}
          {summary.streak.longest === 1 ? 'day' : 'days'}
        </p>
      </StatTile>

      <StatTile label="Badges" accent="border-t-brand-green">
        <p className="font-heading font-black text-3xl leading-none mb-3">
          {summary.badges_earned}
          <span className="text-text-muted"> / {summary.badges_total}</span>
        </p>
        <div
          role="progressbar"
          aria-label="Badges earned"
          aria-valuemin={0}
          aria-valuemax={Math.max(summary.badges_total, 1)}
          aria-valuenow={summary.badges_earned}
          aria-valuetext={`${summary.badges_earned} of ${summary.badges_total} badges earned`}
          className="w-full h-3 bg-bg-card border-2 border-border-dark"
          style={{ borderRadius: '2px' }}
        >
          <div className="h-full bg-brand-green transition-all duration-500" style={{ width: `${badgePct}%` }} />
        </div>
      </StatTile>
    </div>
  )
}

const SummarySkeleton: React.FC = () => (
  <div role="status" aria-label="Loading your stats" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    {[0, 1, 2, 3].map((i) => (
      <Skeleton key={i} className="h-28 w-full" />
    ))}
  </div>
)

const EmptyState: React.FC<{ mood: MascotMood; message: string; action?: React.ReactNode }> = ({ mood, message, action }) => (
  <div className="border-2 border-dashed border-border-dark/40 bg-bg-card p-6 flex flex-col items-center gap-4" style={{ borderRadius: '4px' }}>
    <Mascot mood={mood} size={88} message={message} />
    {action}
  </div>
)

const EventRow: React.FC<{ event: RecentEvent }> = ({ event }) => {
  const Icon = eventIcon(event.kind)
  return (
    <li className="flex items-center gap-3 py-2.5 border-b border-border-dark/15 last:border-b-0">
      <span aria-hidden className="w-8 shrink-0 flex items-center justify-center">
        <Icon className="w-5 h-5" strokeWidth={2.25} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-body font-bold text-sm leading-tight truncate">{event.label}</p>
        <p className="font-mono text-xs text-text-muted">{formatWhen(event.created_at)}</p>
      </div>
      <span className="shrink-0 font-mono text-sm font-bold">+{event.amount} XP</span>
    </li>
  )
}

export const AchievementsPage: React.FC = () => {
  const tabsId = useId()
  const panelId = `${tabsId}-panel`
  const alive = useRef(true)
  const tabRefs = useRef<Partial<Record<Tab, HTMLButtonElement | null>>>({})

  const summary = useGamificationStore((s) => s.summary)
  const refresh = useGamificationStore((s) => s.refresh)

  const [summaryTried, setSummaryTried] = useState(false)
  const [badges, setBadges] = useState<BadgeInfo[]>([])
  const [badgesState, setBadgesState] = useState<LoadState>('loading')
  const [tab, setTab] = useState<Tab>('all')
  const [category, setCategory] = useState<CategoryFilter>('all')

  useEffect(() => {
    alive.current = true
    return () => {
      alive.current = false
    }
  }, [])

  const loadSummary = useCallback(() => {
    setSummaryTried(false)
    void refresh().finally(() => {
      if (alive.current) setSummaryTried(true)
    })
  }, [refresh])

  const loadBadges = useCallback(async () => {
    setBadgesState('loading')
    try {
      const res = await getBadges()
      if (!alive.current) return
      setBadges(res.badges)
      setBadgesState('ready')
    } catch {
      if (!alive.current) return
      setBadgesState('error')
    }
  }, [])

  useEffect(() => {
    loadSummary()
    void loadBadges()
  }, [loadSummary, loadBadges])

  // Badges inside the chosen category, before the tab is applied.
  const scoped = useMemo(
    () => badges.filter((b) => category === 'all' || b.category === category),
    [badges, category],
  )
  const counts = useMemo(
    () => ({
      all: scoped.length,
      earned: scoped.filter((b) => b.earned).length,
      locked: scoped.filter((b) => !b.earned).length,
    }),
    [scoped],
  )
  const visible = useMemo(
    () => sortBadges(scoped.filter((b) => tab === 'all' || (tab === 'earned' ? b.earned : !b.earned))),
    [scoped, tab],
  )
  const categoryStats = useMemo(() => {
    const stats: Partial<Record<BadgeCategory, { earned: number; total: number }>> = {}
    for (const b of badges) {
      const s = (stats[b.category] ??= { earned: 0, total: 0 })
      s.total += 1
      if (b.earned) s.earned += 1
    }
    return stats
  }, [badges])

  const categoryLabel = CATEGORIES.find((c) => c.id === category)?.label.toLowerCase()

  const onTabKeyDown = (e: React.KeyboardEvent, index: number) => {
    let next = index
    if (e.key === 'ArrowRight') next = (index + 1) % TABS.length
    else if (e.key === 'ArrowLeft') next = (index - 1 + TABS.length) % TABS.length
    else if (e.key === 'Home') next = 0
    else if (e.key === 'End') next = TABS.length - 1
    else return
    e.preventDefault()
    const id = TABS[next].id
    setTab(id)
    tabRefs.current[id]?.focus()
  }

  const renderEmpty = () => {
    if (tab === 'earned') {
      if (category === 'all') {
        return (
          <EmptyState
            mood="encouraging"
            message="No badges yet, read your first lesson!"
            action={
              <Link to="/dashboard">
                <Button variant="yellow" size="sm">
                  Start learning
                  <ArrowRight aria-hidden className="w-4 h-4 shrink-0" strokeWidth={2.5} />
                </Button>
              </Link>
            }
          />
        )
      }
      return (
        <EmptyState
          mood="encouraging"
          message={`No ${categoryLabel} badges yet. Open the Locked tab to see how to earn them!`}
        />
      )
    }
    if (tab === 'locked') {
      return (
        <EmptyState
          mood="celebrating"
          message={
            category === 'all'
              ? 'You have earned every badge. Amazing work!'
              : `You have earned every ${categoryLabel} badge. Amazing work!`
          }
        />
      )
    }
    return <EmptyState mood="thinking" message="There are no badges to show here yet." />
  }

  return (
    <div className="min-h-screen bg-bg-base">
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="mb-8">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1 font-mono text-sm font-bold underline decoration-2 underline-offset-4 hover:bg-brand-yellow/40 px-1 -ml-1"
          >
            <ArrowLeft aria-hidden className="w-4 h-4 shrink-0" strokeWidth={2.5} />
            Dashboard
          </Link>
          <h1 className="flex items-center gap-4 font-heading font-black text-4xl md:text-5xl text-text-primary mt-4 mb-3">
            <IconTile icon={Trophy} color="yellow" size="lg" />
            Achievements
          </h1>
          <p className="text-text-muted font-mono text-sm max-w-2xl border-l-4 border-brand-yellow pl-4 py-1 bg-brand-yellow/10">
            Earn XP and badges as you learn. Take your time, every step counts.
          </p>
        </div>

        {/* Summary */}
        <section aria-label="Your progress summary" className="mb-10">
          {summary ? (
            <SummaryHeader summary={summary} />
          ) : summaryTried ? (
            <div role="alert" className="border-2 border-border-dark bg-brand-pink/10 p-4 flex flex-wrap items-center gap-3" style={{ borderRadius: '4px' }}>
              <p className="font-body font-bold text-sm flex-1 min-w-[200px]">
                We could not load your level and XP. Your progress is safe.
              </p>
              <Button variant="secondary" size="sm" onClick={loadSummary}>
                Try again
              </Button>
            </div>
          ) : (
            <SummarySkeleton />
          )}
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_360px] gap-8 items-start">
          {/* Badges */}
          <section aria-labelledby={`${tabsId}-badges`}>
            <div className="flex items-center gap-3 mb-5">
              <h2
                id={`${tabsId}-badges`}
                className="font-mono font-bold text-sm text-white bg-brand-pink border border-border-dark px-3 py-1 shadow-neo-sm"
              >
                BADGES
              </h2>
              <div className="flex-1 h-0.5 bg-border-dark" />
            </div>

            {/* Tabs */}
            <div role="tablist" aria-label="Badge filter" className="flex flex-wrap gap-2 mb-4">
              {TABS.map((t, i) => {
                const selected = tab === t.id
                return (
                  <button
                    key={t.id}
                    ref={(el) => {
                      tabRefs.current[t.id] = el
                    }}
                    type="button"
                    role="tab"
                    id={`${tabsId}-tab-${t.id}`}
                    aria-selected={selected}
                    aria-controls={panelId}
                    tabIndex={selected ? 0 : -1}
                    onClick={() => setTab(t.id)}
                    onKeyDown={(e) => onTabKeyDown(e, i)}
                    className={`inline-flex items-center gap-1 px-4 py-2 border-2 border-border-dark font-heading font-bold text-sm transition-all duration-150 ${
                      selected
                        ? 'bg-brand-yellow shadow-neo-sm text-text-primary'
                        : 'bg-bg-card text-text-primary hover:bg-brand-yellow/20'
                    }`}
                    style={{ borderRadius: '4px' }}
                  >
                    {selected && <Check aria-hidden className="w-4 h-4 shrink-0" strokeWidth={3} />}
                    {t.label}
                    {badgesState === 'ready' && (
                      <span className="ml-2 font-mono text-xs font-bold text-text-muted">{counts[t.id]}</span>
                    )}
                  </button>
                )
              })}
            </div>

            {/* Category filter */}
            <div role="group" aria-label="Filter by category" className="flex flex-wrap gap-2 mb-6">
              {[{ id: 'all' as const, label: 'All categories', icon: LayoutGrid }, ...CATEGORIES].map((c) => {
                const Icon = c.icon
                const pressed = category === c.id
                const stat = c.id === 'all' ? null : categoryStats[c.id]
                return (
                  <button
                    key={c.id}
                    type="button"
                    aria-pressed={pressed}
                    onClick={() => setCategory(c.id)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 border-2 border-border-dark font-mono text-xs font-bold transition-all duration-150 ${
                      pressed ? 'bg-border-dark text-white' : 'bg-bg-card text-text-primary hover:bg-brand-yellow/20'
                    }`}
                    style={{ borderRadius: '4px' }}
                  >
                    <Icon aria-hidden className="w-3.5 h-3.5 shrink-0" strokeWidth={2.5} />
                    {c.label}
                    {stat && (
                      <span className={pressed ? 'text-white/80' : 'text-text-muted'}>
                        {stat.earned}/{stat.total}
                      </span>
                    )}
                  </button>
                )
              })}
            </div>

            <div role="tabpanel" id={panelId} aria-labelledby={`${tabsId}-tab-${tab}`} tabIndex={-1}>
              {badgesState === 'loading' && (
                <div
                  role="status"
                  aria-label="Loading badges"
                  className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4"
                >
                  {[0, 1, 2, 3, 4, 5].map((i) => (
                    <Skeleton key={i} className="h-48 w-full" />
                  ))}
                </div>
              )}

              {badgesState === 'error' && (
                <div role="alert" className="border-2 border-border-dark bg-brand-pink/10 p-5" style={{ borderRadius: '4px' }}>
                  <p className="font-body font-bold mb-1">We could not load your badges.</p>
                  <p className="font-body text-sm text-text-muted mb-3">
                    Check your connection and try again. Nothing you earned is lost.
                  </p>
                  <Button variant="secondary" size="sm" onClick={() => void loadBadges()}>
                    Try again
                  </Button>
                </div>
              )}

              {badgesState === 'ready' && (
                <>
                  <p role="status" aria-live="polite" className="sr-only">
                    Showing {visible.length} {visible.length === 1 ? 'badge' : 'badges'}
                  </p>
                  {visible.length === 0 ? (
                    renderEmpty()
                  ) : (
                    <ul className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                      {visible.map((badge) => (
                        <li key={badge.id}>
                          <BadgeCard badge={badge} />
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              )}
            </div>
          </section>

          {/* XP history and leaderboard */}
          <div className="space-y-8">
            <Card accent="blue">
              <section aria-labelledby={`${tabsId}-history`}>
                <div className="flex items-center gap-3 mb-3 border-b-2 border-border-dark pb-3">
                  <IconTile icon={Zap} color="yellow" size="sm" />
                  <h2 id={`${tabsId}-history`} className="font-heading font-bold text-xl">
                    Recent XP
                  </h2>
                </div>

                {!summary && !summaryTried && (
                  <div role="status" aria-label="Loading XP history" className="space-y-2">
                    {[0, 1, 2, 3].map((i) => (
                      <Skeleton key={i} className="h-10 w-full" />
                    ))}
                  </div>
                )}
                {!summary && summaryTried && (
                  <p className="font-body text-sm text-text-muted">Your XP history is not available right now.</p>
                )}
                {summary && summary.recent_events.length === 0 && (
                  <p className="font-body text-sm text-text-muted py-3">
                    No XP yet. Read your first lesson to earn 10 XP!
                  </p>
                )}
                {summary && summary.recent_events.length > 0 && (
                  <ul>
                    {summary.recent_events.map((event, i) => (
                      <EventRow key={`${event.created_at}-${event.kind}-${i}`} event={event} />
                    ))}
                  </ul>
                )}
              </section>
            </Card>

            <LeaderboardCard />
          </div>
        </div>
      </main>
    </div>
  )
}
