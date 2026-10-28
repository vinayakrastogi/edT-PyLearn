import React, { useId } from 'react'
import { Check, Diamond, Lock } from 'lucide-react'
import { AppIcon } from '@/lib/icons'
import type { BadgeInfo, BadgeRarity } from '@/types/gamification'

/**
 * Rarity is shown three ways so it never depends on colour alone: the border STYLE (thin solid,
 * thick solid, double, double), a text label, and the number of diamonds in the label.
 */
const RARITY: Record<
  BadgeRarity,
  { label: string; diamonds: number; frame: string; lockedFrame: string; chip: string; iconBg: string; shadow: string }
> = {
  common: {
    label: 'Common',
    diamonds: 1,
    frame: 'border-2 border-solid border-border-dark',
    lockedFrame: 'border-2 border-solid border-gray-400',
    chip: 'bg-bg-card text-text-primary border-border-dark',
    iconBg: 'bg-brand-yellow/40',
    shadow: 'shadow-neo-sm',
  },
  rare: {
    label: 'Rare',
    diamonds: 2,
    frame: 'border-[3px] border-solid border-brand-blue',
    lockedFrame: 'border-[3px] border-solid border-gray-400',
    chip: 'bg-brand-blue text-text-primary border-border-dark',
    iconBg: 'bg-brand-blue/20',
    shadow: 'shadow-neo-sm',
  },
  epic: {
    label: 'Epic',
    diamonds: 3,
    frame: 'border-4 border-double border-brand-purple',
    lockedFrame: 'border-4 border-double border-gray-400',
    chip: 'bg-brand-purple text-white border-border-dark',
    iconBg: 'bg-brand-purple/20',
    shadow: 'shadow-neo',
  },
  legendary: {
    label: 'Legendary',
    diamonds: 4,
    frame: 'border-4 border-double border-brand-orange',
    lockedFrame: 'border-4 border-double border-gray-400',
    chip: 'bg-brand-yellow text-text-primary border-border-dark',
    iconBg: 'bg-brand-orange/25',
    shadow: 'shadow-neo',
  },
}

/** The API sends UTC; a timestamp without a zone designator is treated as UTC rather than local. */
const parseServerDate = (iso: string): Date | null => {
  const hasZone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(iso)
  const d = new Date(hasZone || !iso.includes('T') ? iso : `${iso}Z`)
  return Number.isNaN(d.getTime()) ? null : d
}

const formatEarned = (iso: string | null): string | null => {
  if (!iso) return null
  const d = parseServerDate(iso)
  return d ? d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : null
}

interface BadgeCardProps {
  badge: BadgeInfo
  /** A smaller horizontal layout, used for "recent badges" strips. */
  compact?: boolean
}

export const BadgeCard: React.FC<BadgeCardProps> = ({ badge, compact = false }) => {
  const nameId = useId()
  const rarity = RARITY[badge.rarity] ?? RARITY.common
  const earned = badge.earned
  const earnedOn = earned ? formatEarned(badge.earned_at) : null

  const target = Math.max(0, badge.progress.target)
  const current = Math.min(Math.max(0, badge.progress.current), target)
  const pct = target > 0 ? Math.round((current / target) * 100) : 0

  const frame = earned ? rarity.frame : rarity.lockedFrame
  const chipClass = earned ? rarity.chip : 'bg-bg-base text-text-muted border-gray-400'

  const rarityChip = (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 border font-mono font-bold uppercase tracking-wide ${
        compact ? 'text-[10px]' : 'text-[11px]'
      } ${chipClass}`}
      style={{ borderRadius: '2px' }}
    >
      {rarity.label}
      <span aria-hidden className="inline-flex items-center">
        {Array.from({ length: rarity.diamonds }, (_, i) => (
          <Diamond key={i} className={`${compact ? 'w-2 h-2' : 'w-2.5 h-2.5'} fill-current -mx-px`} strokeWidth={2.5} />
        ))}
      </span>
    </span>
  )

  const icon = (
    <div
      aria-hidden
      className={`relative shrink-0 flex items-center justify-center border-2 ${
        earned ? `border-border-dark ${rarity.iconBg}` : 'border-gray-400 bg-gray-200'
      } ${compact ? 'w-11 h-11' : 'w-16 h-16'}`}
    >
      <AppIcon
        name={badge.icon}
        className={`${compact ? 'w-6 h-6' : 'w-9 h-9'} ${earned ? 'text-text-primary' : 'text-gray-400'}`}
      />
      {!earned && (
        <span className="absolute -bottom-1.5 -right-1.5 bg-bg-card border border-gray-400 p-0.5 text-text-muted">
          <Lock className={compact ? 'w-2.5 h-2.5' : 'w-3 h-3'} strokeWidth={2.5} />
        </span>
      )}
    </div>
  )

  const progress = !earned && target > 0 && (
    <div className={compact ? 'mt-1.5' : 'mt-3'}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-mono text-[11px] font-bold text-text-muted">Progress</span>
        <span className="font-mono text-[11px] font-bold text-text-primary">
          {current} / {target}
        </span>
      </div>
      <div
        role="progressbar"
        aria-label={`${badge.name} progress`}
        aria-valuemin={0}
        aria-valuemax={target}
        aria-valuenow={current}
        aria-valuetext={`${current} of ${target}`}
        className={`w-full bg-bg-card border-2 border-border-dark ${compact ? 'h-2' : 'h-3'}`}
        style={{ borderRadius: '2px' }}
      >
        <div
          className="h-full bg-brand-blue transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )

  const status = earned ? (
    <span className="inline-flex items-center gap-1 font-mono text-[11px] font-bold text-text-primary">
      <Check aria-hidden className="w-3 h-3 shrink-0" strokeWidth={3} />
      {earnedOn ? `Earned ${earnedOn}` : 'Earned'}
    </span>
  ) : (
    <span className="font-mono text-[11px] font-bold text-text-muted">Locked</span>
  )

  if (compact) {
    return (
      <article
        aria-labelledby={nameId}
        className={`flex items-start gap-3 p-2.5 h-full ${earned ? 'bg-bg-card' : 'bg-bg-base'} ${frame} ${
          earned ? rarity.shadow : ''
        }`}
        style={{ borderRadius: '4px' }}
      >
        {icon}
        <div className="min-w-0 flex-1">
          <p id={nameId} className="font-heading font-bold text-sm leading-tight truncate" title={badge.name}>
            {badge.name}
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
            {rarityChip}
            {status}
          </div>
          <p className="mt-1 font-body text-xs text-text-muted leading-snug line-clamp-2">{badge.description}</p>
          {progress}
        </div>
      </article>
    )
  }

  return (
    <article
      aria-labelledby={nameId}
      className={`flex flex-col h-full p-4 ${earned ? 'bg-bg-card' : 'bg-bg-base'} ${frame} ${
        earned ? rarity.shadow : ''
      }`}
      style={{ borderRadius: '4px' }}
    >
      <div className="flex items-start gap-3">
        {icon}
        <div className="min-w-0 flex-1">
          <p id={nameId} className="font-heading font-bold text-base leading-tight">
            {badge.name}
          </p>
          <div className="mt-1.5">{rarityChip}</div>
        </div>
      </div>
      <p className="mt-3 font-body text-sm text-text-muted leading-snug flex-1">{badge.description}</p>
      <div className="mt-3 pt-2 border-t-2 border-border-dark/15">
        {status}
        {progress}
      </div>
    </article>
  )
}
