import React from 'react'
import { Flame, Snowflake } from 'lucide-react'

interface StreakFlameProps {
  /** Current streak in days. */
  count: number
  /** Banked streak freezes (shown with a snowflake when provided). */
  freezes?: number
  /** The streak will end unless the learner is active today. Adds a text cue, not just a colour. */
  atRisk?: boolean
  /** Whether the learner has already been active today. When false the flame is greyed out. */
  active?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const SIZES = {
  sm: { flame: 'w-4 h-4', count: 'text-sm', freeze: 'text-xs', snow: 'w-3.5 h-3.5', gap: 'gap-1' },
  md: { flame: 'w-6 h-6', count: 'text-xl', freeze: 'text-sm', snow: 'w-4 h-4', gap: 'gap-1.5' },
  lg: { flame: 'w-9 h-9', count: 'text-3xl', freeze: 'text-base', snow: 'w-5 h-5', gap: 'gap-2' },
} as const

/** Flame + day count (+ snowflake count for freezes). Greyed out until the learner is active today. */
export const StreakFlame: React.FC<StreakFlameProps> = ({
  count,
  freezes,
  atRisk = false,
  active = true,
  size = 'md',
  className = '',
}) => {
  const cfg = SIZES[size]
  const dim = !active || count <= 0

  const parts = [count > 0 ? `${count} day streak` : 'No streak yet']
  if (freezes !== undefined) parts.push(`${freezes} streak ${freezes === 1 ? 'freeze' : 'freezes'}`)
  if (atRisk) parts.push('at risk, do one lesson, quiz or problem today to keep it')
  else if (!active && count > 0) parts.push('no activity yet today')
  const label = parts.join(', ')

  return (
    <span role="img" aria-label={label} title={label} className={`inline-flex items-center ${cfg.gap} ${className}`}>
      <Flame
        aria-hidden
        className={`${cfg.flame} shrink-0 inline-block ${
          dim ? 'text-text-muted opacity-60' : 'text-brand-orange fill-brand-yellow flame-flicker'
        }`}
        strokeWidth={2.25}
      />
      <span
        aria-hidden
        className={`font-heading font-black tabular-nums leading-none ${cfg.count} ${dim ? 'text-text-muted' : 'text-text-primary'}`}
      >
        {count}
      </span>
      {freezes !== undefined && (freezes > 0 || size !== 'sm') && (
        <span
          aria-hidden
          className={`inline-flex items-center gap-0.5 font-mono font-bold leading-none ${cfg.freeze} ${
            freezes > 0 ? 'text-text-primary' : 'text-text-muted opacity-60'
          }`}
        >
          <Snowflake className={`${cfg.snow} shrink-0 ${freezes > 0 ? 'text-brand-blue' : ''}`} strokeWidth={2.5} />
          <span className="tabular-nums">{freezes}</span>
        </span>
      )}
      {atRisk && (
        <span
          aria-hidden
          className="risk-pulse inline-flex items-center border-2 border-border-dark bg-brand-yellow text-text-primary font-mono font-black leading-none px-1 py-0.5 text-[10px]"
        >
          {size === 'sm' ? '!' : 'AT RISK'}
        </span>
      )}
    </span>
  )
}
