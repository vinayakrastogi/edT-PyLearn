import React, { useId } from 'react'
import { ArrowUp, Flame } from 'lucide-react'
import { LevelBar } from '@/components/gamification/LevelBar'
import { RarityTag } from '@/components/gamification/RarityTag'
import { RARITY_TILE, eventIcon } from '@/components/gamification/rewardModels'
import { AppIcon, XpIcon } from '@/lib/icons'
import { NO_XP_MODULE_TEXT } from '@/lib/xp'
import type { RewardSummary } from '@/types/gamification'

interface XPSummaryPanelProps {
  rewards: RewardSummary
  /** Explains why nothing was earned (shown only when xp_gained is 0). */
  emptyText?: string
  className?: string
}

/** Quiz result panel: itemised XP, level progress and the badges just earned. */
export const XPSummaryPanel: React.FC<XPSummaryPanelProps> = ({
  rewards,
  emptyText = 'No new XP this time.',
  className = '',
}) => {
  const headingId = useId()
  const earned = rewards.xp_gained > 0
  const { streak } = rewards

  return (
    <section aria-labelledby={headingId} className={`neo-card p-5 border-t-4 border-t-brand-green space-y-4 ${className}`}>
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 id={headingId} className="flex items-center gap-2 font-heading font-bold text-xl m-0">
          <XpIcon className="w-6 h-6" />
          XP earned
        </h2>
        <p className="font-heading font-black text-3xl leading-none m-0 tabular-nums">
          {earned ? `+${rewards.xp_gained} XP` : '+0 XP'}
        </p>
      </div>

      {rewards.events.length > 0 ? (
        <ul className="list-none p-0 m-0 space-y-1">
          {rewards.events.map((e, i) => {
            const Icon = eventIcon(e.kind)
            return (
              <li key={`${e.kind}-${i}`} className="flex items-center gap-2 font-body text-sm">
                <Icon aria-hidden className="w-4 h-4 shrink-0" strokeWidth={2.25} />
                <span className="font-mono font-bold tabular-nums">+{e.amount} XP</span>
                <span className="text-text-muted">{e.label}</span>
              </li>
            )
          })}
        </ul>
      ) : (
        !earned && <p className="font-body text-sm text-text-muted m-0">{emptyText}</p>
      )}

      {rewards.level_up && (
        <p className="flex items-center gap-2 font-heading font-bold text-base m-0 border-2 border-border-dark bg-brand-purple text-white px-3 py-2">
          <ArrowUp aria-hidden className="w-5 h-5 shrink-0" strokeWidth={3} />
          Level up! You reached level {rewards.level}: {rewards.level_title}
        </p>
      )}

      <LevelBar
        level={rewards.level}
        title={rewards.level_title}
        xpIntoLevel={rewards.xp_into_level}
        xpForNextLevel={rewards.xp_for_next_level}
      />

      {streak.extended && streak.count > 1 && (
        <p className="flex items-center gap-1.5 font-body text-sm m-0">
          <Flame aria-hidden className="w-4 h-4 shrink-0 text-brand-orange fill-brand-yellow" strokeWidth={2.25} />
          Streak extended: {streak.count} days in a row.
        </p>
      )}

      {rewards.new_badges.length > 0 && (
        <div>
          <h3 className="font-heading font-bold text-sm m-0 mb-2">
            New {rewards.new_badges.length === 1 ? 'badge' : 'badges'}
          </h3>
          <ul className="list-none p-0 m-0 flex flex-wrap gap-2">
            {rewards.new_badges.map((b) => (
              <li
                key={b.id}
                title={b.description}
                className={`inline-flex items-center gap-1.5 border-2 border-border-dark shadow-neo-sm px-2 py-1 ${RARITY_TILE[b.rarity]}`}
              >
                <AppIcon name={b.icon} className="w-5 h-5 shrink-0 text-text-primary" />
                <span className="font-heading font-bold text-sm">{b.name}</span>
                <RarityTag rarity={b.rarity} />
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}

interface XPLineProps {
  rewards: RewardSummary
  /** Whether the submission passed; decides if "no new XP" is worth explaining. */
  passed: boolean
  /** The learner had already passed this problem before this submission (only then is "solved before" true). */
  alreadySolved: boolean
  /** False for modules that never award XP (AI or faculty made). */
  earnsXp: boolean
  className?: string
}

/** One compact line for the dark problem results panel. Renders nothing when there is nothing useful to say. */
export const XPLine: React.FC<XPLineProps> = ({ rewards, passed, alreadySolved, earnsXp, className = '' }) => {
  if (rewards.xp_gained <= 0) {
    if (!passed) return null
    return (
      <p className={`flex items-start gap-1.5 font-mono text-xs text-white/70 m-0 ${className}`}>
        <XpIcon className="w-3.5 h-3.5 mt-px" />
        {!earnsXp
          ? NO_XP_MODULE_TEXT
          : alreadySolved
            ? 'No new XP: you have solved this one before. XP is awarded the first time.'
            : 'No new XP this time.'}
      </p>
    )
  }

  return (
    <div
      className={`flex flex-wrap items-center gap-x-3 gap-y-1 border-2 border-brand-yellow bg-brand-yellow/10 px-3 py-2 font-mono text-sm text-brand-yellow ${className}`}
    >
      <span className="inline-flex items-center gap-1.5 font-bold">
        <XpIcon className="w-4 h-4" />+{rewards.xp_gained} XP
      </span>
      {rewards.events.length > 0 && (
        <span className="text-white/80">
          {rewards.events.map((e) => `+${e.amount} ${e.label}`).join(' · ')}
        </span>
      )}
      {rewards.level_up && (
        <span className="inline-flex items-center gap-1 font-bold text-white">
          <ArrowUp aria-hidden className="w-4 h-4 shrink-0" strokeWidth={3} />
          Level {rewards.level}!
        </span>
      )}
      {rewards.new_badges.length > 0 && (
        <span className="text-white">
          {rewards.new_badges.length === 1 ? 'New badge: ' : 'New badges: '}
          {rewards.new_badges.map((b) => b.name).join(', ')}
        </span>
      )}
    </div>
  )
}
