import React from 'react'
import type { WeeklyPoint } from '@/types/gamification'

interface WeeklyXpChartProps {
  /** Oldest first; the last point is today. */
  points: WeeklyPoint[]
  /** Optional daily goal, drawn as a dashed line. */
  goal?: number
}

/** `YYYY-MM-DD` as a local calendar date (new Date('YYYY-MM-DD') would be parsed as UTC and can land on the wrong day). */
const parseLocalDate = (s: string): Date | null => {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s)
  if (!m) return null
  const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]))
  return Number.isNaN(d.getTime()) ? null : d
}

/** Share of the plot height the tallest bar may use, leaving room for its value above it. */
const USABLE = 0.8

export const WeeklyXpChart: React.FC<WeeklyXpChartProps> = ({ points, goal }) => {
  const days = points.map((p, i) => {
    const d = parseLocalDate(p.date)
    const xp = Math.max(0, p.xp)
    const long = d ? d.toLocaleDateString(undefined, { weekday: 'long' }) : p.date
    const initial = d ? d.toLocaleDateString(undefined, { weekday: 'narrow' }) : '?'
    const isToday = i === points.length - 1
    return { key: p.date, xp, long, initial, isToday }
  })

  const total = days.reduce((sum, d) => sum + d.xp, 0)
  const hasGoal = typeof goal === 'number' && goal > 0
  const max = Math.max(1, ...days.map((d) => d.xp), hasGoal ? (goal as number) : 0)
  const heightPct = (xp: number) => (xp / max) * USABLE * 100

  const summary =
    total === 0
      ? 'XP over the last 7 days: none earned yet.'
      : `XP over the last 7 days: ${days
          .map((d) => `${d.isToday ? 'today' : d.long} ${d.xp}`)
          .join(', ')}. Total ${total} XP.`

  if (days.length === 0) {
    return <p className="font-mono text-xs text-text-muted">No XP history yet.</p>
  }

  return (
    <figure role="img" aria-label={summary} className="m-0 w-full">
      <div className="relative h-24 border-b-2 border-border-dark">
        {total === 0 && (
          <p className="absolute inset-x-0 top-1/3 text-center font-mono text-[11px] font-bold text-text-muted">
            No XP yet this week
          </p>
        )}

        {hasGoal && (
          <div
            className="absolute left-0 right-0 border-t-2 border-dashed border-brand-pink pointer-events-none"
            style={{ bottom: `${heightPct(goal as number)}%` }}
          >
            <span className="absolute right-0 bottom-full bg-bg-card px-1 font-mono text-[10px] font-bold text-text-muted leading-tight">
              Goal {goal}
            </span>
          </div>
        )}

        <div className="absolute inset-0 flex items-end gap-1.5 px-1">
          {days.map((d) => (
            <div
              key={d.key}
              title={`${d.long}: ${d.xp} XP`}
              className="flex-1 min-w-0 h-full flex flex-col items-center justify-end"
            >
              {d.xp > 0 && (
                <span className="font-mono text-[10px] font-bold leading-none mb-0.5 text-text-primary">{d.xp}</span>
              )}
              {d.xp > 0 ? (
                <div
                  className={`w-full max-w-[32px] border-2 border-border-dark ${
                    d.isToday ? 'bg-brand-yellow shadow-neo-sm' : 'bg-brand-blue'
                  }`}
                  style={{ height: `max(6px, ${heightPct(d.xp)}%)` }}
                />
              ) : (
                <div className="w-full max-w-[32px] h-[3px] bg-border-dark/30" />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-1.5 px-1 pt-1.5">
        {days.map((d) => (
          <div key={d.key} className="flex-1 min-w-0 flex justify-center">
            <span
              className={`font-mono text-[11px] font-bold leading-none px-1.5 py-1 ${
                d.isToday ? 'bg-border-dark text-white' : 'text-text-muted'
              }`}
              style={{ borderRadius: '2px' }}
            >
              {d.initial}
            </span>
          </div>
        ))}
      </div>
    </figure>
  )
}
