import React, { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Trophy } from 'lucide-react'
import { Skeleton } from '@/components/Skeleton'
import { StreakFlame } from '@/components/gamification/StreakFlame'
import { useGamificationStore } from '@/store/gamificationStore'

/** Fixed height and minimum widths so the navbar does not shift while the summary loads. */
const CHIP_SIZE = 'h-10 min-w-[6.5rem] sm:min-w-[13rem]'

/** Compact navbar element: level, level progress, total XP and streak. Links to /achievements. */
export const XPChip: React.FC = () => {
  const summary = useGamificationStore((s) => s.summary)
  const loading = useGamificationStore((s) => s.loading)
  const refresh = useGamificationStore((s) => s.refresh)
  const { pathname } = useLocation()

  // Tell "still starting" apart from "failed", so a failure does not look like loading forever.
  const [attempted, setAttempted] = useState(false)
  useEffect(() => {
    if (loading) {
      setAttempted(true)
      return
    }
    if (summary) return
    // Idle without data: the request either has not started yet or already failed. Give it a moment.
    const timer = setTimeout(() => setAttempted(true), 1500)
    return () => clearTimeout(timer)
  }, [loading, summary])

  // Pop briefly whenever XP or the level goes up.
  const [bump, setBump] = useState(false)
  const bumpTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const last = useRef<{ xp: number; level: number } | null>(null)
  const xp = summary?.xp_total
  const level = summary?.level
  useEffect(() => {
    if (xp === undefined || level === undefined) {
      last.current = null
      return
    }
    const prev = last.current
    last.current = { xp, level }
    if (!prev || (xp <= prev.xp && level <= prev.level)) return
    setBump(true)
    if (bumpTimer.current) clearTimeout(bumpTimer.current)
    bumpTimer.current = setTimeout(() => setBump(false), 700)
  }, [xp, level])
  useEffect(
    () => () => {
      if (bumpTimer.current) clearTimeout(bumpTimer.current)
    },
    [],
  )

  const current = pathname === '/achievements'
  const base = `neo-btn px-2 ${CHIP_SIZE} ${current ? 'bg-brand-yellow/40' : 'bg-bg-card'}`

  if (!summary) {
    if (loading || !attempted) {
      return (
        <div role="status" aria-label="Loading your level" className={`${CHIP_SIZE} flex items-center`}>
          <Skeleton className="h-10 w-full" />
        </div>
      )
    }
    // The summary could not be loaded: keep a way into the achievements page and retry on click.
    return (
      <Link
        to="/achievements"
        onClick={() => void refresh()}
        aria-label="Achievements. Your level could not be loaded, select to try again."
        aria-current={current ? 'page' : undefined}
        className={base}
      >
        <Trophy aria-hidden className="w-5 h-5 shrink-0" strokeWidth={2.5} />
        <span aria-hidden className="hidden sm:inline font-mono font-bold text-xs text-text-muted">Level unavailable</span>
      </Link>
    )
  }

  const { streak } = summary
  const streakText = streak.count > 0 ? `${streak.count} day streak` : 'no streak yet'
  const risk = streak.at_risk ? ', at risk, do one lesson today to keep it' : ''
  const label = `Level ${summary.level}, ${summary.level_title}. ${summary.xp_total.toLocaleString()} XP total. ${streakText}${risk}. View achievements.`

  const pct =
    summary.xp_for_next_level > 0
      ? Math.min(100, Math.max(0, (summary.xp_into_level / summary.xp_for_next_level) * 100))
      : 100

  return (
    <Link
      to="/achievements"
      aria-label={label}
      aria-current={current ? 'page' : undefined}
      title={`${summary.level_title}: ${summary.xp_into_level.toLocaleString()} / ${summary.xp_for_next_level.toLocaleString()} XP to the next level`}
      className={`${base} gap-2 ${bump ? 'animate-pop' : ''}`}
    >
      <span
        aria-hidden
        className="font-mono font-black text-xs leading-none bg-brand-purple text-white border border-border-dark px-1.5 py-1 whitespace-nowrap"
      >
        Lv {summary.level}
      </span>

      {/* Level progress and total XP: wider screens only */}
      <span aria-hidden className="hidden sm:flex flex-col justify-center gap-1 flex-1 min-w-[5.5rem]">
        <span className="font-mono font-bold text-[11px] leading-none tabular-nums text-text-primary whitespace-nowrap">
          {summary.xp_total.toLocaleString()} XP
        </span>
        <span className="block h-1.5 w-full bg-bg-card border border-border-dark overflow-hidden">
          <span
            className="block h-full bg-brand-green transition-[width] duration-700 ease-out"
            style={{ width: `${pct}%` }}
          />
        </span>
      </span>

      {/* Freezes only fit on wider screens */}
      <StreakFlame count={streak.count} atRisk={streak.at_risk} active={streak.active_today} size="sm" className="shrink-0 sm:hidden" />
      <StreakFlame
        count={streak.count}
        freezes={streak.freezes}
        atRisk={streak.at_risk}
        active={streak.active_today}
        size="sm"
        className="shrink-0 hidden sm:inline-flex"
      />
    </Link>
  )
}
