import React, { useId } from 'react'

/** Levels stop here (see GAMIFICATION.md). The bar is shown full at the cap. */
const MAX_LEVEL = 99

interface LevelBarProps {
  level: number
  /** Level title such as "Loop Rider". */
  title?: string
  /** XP earned since the current level started. */
  xpIntoLevel: number
  /** Total XP needed to cross from this level to the next one. */
  xpForNextLevel: number
  size?: 'sm' | 'md' | 'lg'
  /** Show "120 / 400 XP" beside the label. The numbers are always in the accessible value text. */
  showNumbers?: boolean
  className?: string
}

const SIZES = {
  sm: { bar: 'h-2.5', text: 'text-xs', gap: 'gap-1', stripes: false },
  md: { bar: 'h-3.5', text: 'text-sm', gap: 'gap-1.5', stripes: true },
  lg: { bar: 'h-5', text: 'text-base', gap: 'gap-2', stripes: true },
} as const

const fmt = (n: number) => Math.round(n).toLocaleString()

/** Labelled XP progress bar for the current level. */
export const LevelBar: React.FC<LevelBarProps> = ({
  level,
  title,
  xpIntoLevel,
  xpForNextLevel,
  size = 'md',
  showNumbers = true,
  className = '',
}) => {
  const labelId = useId()
  const cfg = SIZES[size]

  const isMax = level >= MAX_LEVEL
  const target = Math.max(0, xpForNextLevel)
  const into = Math.min(Math.max(0, xpIntoLevel), target)
  const fraction = isMax || target === 0 ? 1 : into / target
  // A sliver of progress should still be visible.
  const widthPct = fraction > 0 ? Math.max(3, fraction * 100) : 0
  const toNext = Math.max(0, target - into)

  const heading = title ? `Level ${level}: ${title}` : `Level ${level}`
  const valueText = isMax
    ? `${heading}. Maximum level reached.`
    : `${heading}. ${fmt(into)} of ${fmt(target)} XP, ${fmt(toNext)} XP to reach level ${level + 1}.`

  return (
    <div className={`w-full ${className}`}>
      <div className={`flex items-baseline justify-between ${cfg.gap} mb-1 ${cfg.text}`}>
        <span id={labelId} className="font-heading font-bold text-text-primary truncate">
          Level {level}
          {title && <span className="font-body font-medium text-text-muted"> · {title}</span>}
        </span>
        {showNumbers && (
          <span aria-hidden className="font-mono font-bold text-text-muted tabular-nums shrink-0">
            {isMax ? 'MAX' : `${fmt(into)} / ${fmt(target)} XP`}
          </span>
        )}
      </div>
      <div
        role="progressbar"
        aria-labelledby={labelId}
        aria-valuemin={0}
        aria-valuemax={Math.max(target, 1)}
        aria-valuenow={target > 0 && !isMax ? into : Math.max(target, 1)}
        aria-valuetext={valueText}
        className={`w-full ${cfg.bar} bg-bg-card border-2 border-border-dark overflow-hidden`}
        style={{ borderRadius: '2px' }}
      >
        <div
          className={`h-full bg-brand-green transition-[width] duration-700 ease-out ${
            widthPct > 0 && widthPct < 100 ? 'border-r-2 border-border-dark' : ''
          }`}
          style={{
            width: `${widthPct}%`,
            backgroundImage: cfg.stripes
              ? 'repeating-linear-gradient(45deg, rgba(255,255,255,0.28) 0 6px, transparent 6px 12px)'
              : undefined,
          }}
        />
      </div>
    </div>
  )
}
