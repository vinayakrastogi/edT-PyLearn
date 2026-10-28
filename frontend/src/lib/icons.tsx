import React from 'react'
import type { LucideIcon, LucideProps } from 'lucide-react'
import {
  Award,
  Blocks,
  BookOpen,
  Bot,
  Brain,
  Bug,
  CalendarCheck,
  ChartColumn,
  Cookie,
  Crosshair,
  Crown,
  Flame,
  FolderOpen,
  FolderSearch,
  Gem,
  GitBranch,
  GraduationCap,
  Hammer,
  Hand,
  Landmark,
  Library,
  Medal,
  Mountain,
  Package,
  Puzzle,
  Repeat,
  Rocket,
  Sparkles,
  SquareFunction,
  Star,
  Sunrise,
  Swords,
  Target,
  Terminal,
  Trophy,
  Wrench,
  Zap,
} from 'lucide-react'

/**
 * Icons whose name comes from the server (badge `icon`, module `icon` in module.yaml).
 * Keys are kebab-case strings; the backend must only send keys listed here.
 * Icons used directly in a component should be imported from lucide-react instead.
 * Not exported (this file exports only components, for fast refresh): render keys with <AppIcon>/<IconTile>.
 * backend/tests/test_icon_keys.py reads this table, so keep it a plain `const ICONS ... = {` ... `}` literal.
 */
const ICONS: Record<string, LucideIcon> = {
  award: Award,
  blocks: Blocks,
  'book-open': BookOpen,
  bot: Bot,
  brain: Brain,
  bug: Bug,
  'calendar-check': CalendarCheck,
  'chart-column': ChartColumn,
  cookie: Cookie,
  crosshair: Crosshair,
  crown: Crown,
  flame: Flame,
  'folder-open': FolderOpen,
  'folder-search': FolderSearch,
  gem: Gem,
  'git-branch': GitBranch,
  'graduation-cap': GraduationCap,
  hammer: Hammer,
  hand: Hand,
  landmark: Landmark,
  library: Library,
  medal: Medal,
  mountain: Mountain,
  package: Package,
  puzzle: Puzzle,
  repeat: Repeat,
  rocket: Rocket,
  sparkles: Sparkles,
  'square-function': SquareFunction,
  sunrise: Sunrise,
  swords: Swords,
  target: Target,
  terminal: Terminal,
  trophy: Trophy,
  wrench: Wrench,
  zap: Zap,
}

export type IconName = keyof typeof ICONS

interface AppIconProps extends Omit<LucideProps, 'name'> {
  /** A key of ICONS. Unknown names (e.g. old data) fall back to a book, never to raw text. */
  name: string | null | undefined
}

/** Render a server-named icon. Decorative by default; pass `aria-label` to make it meaningful. */
export const AppIcon: React.FC<AppIconProps> = ({ name, ...props }) => {
  const Icon = (name && ICONS[name]) || BookOpen
  const labelled = props['aria-label'] !== undefined
  return <Icon aria-hidden={labelled ? undefined : true} strokeWidth={2.25} {...props} />
}

/** The XP symbol used everywhere XP is shown: a filled yellow star with a dark outline. */
export const XpIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4' }) => (
  <Star aria-hidden className={`inline-block shrink-0 fill-brand-yellow text-border-dark ${className}`} strokeWidth={2.25} />
)

const TILE_COLORS = {
  yellow: 'bg-brand-yellow',
  pink: 'bg-brand-pink',
  green: 'bg-brand-green',
  blue: 'bg-brand-blue',
  purple: 'bg-brand-purple',
  orange: 'bg-brand-orange',
  white: 'bg-bg-card',
} as const

/**
 * A neobrutalist square holding an icon (replaces the big decorative emoji on cards and headers).
 * Pass a lucide component as `icon`, or a server icon key as `name`.
 */
export const IconTile: React.FC<{
  icon?: LucideIcon
  name?: string
  color?: keyof typeof TILE_COLORS
  size?: 'sm' | 'md' | 'lg'
  className?: string
}> = ({ icon, name, color = 'yellow', size = 'md', className = '' }) => {
  const box = { sm: 'w-8 h-8', md: 'w-11 h-11', lg: 'w-14 h-14' }[size]
  const glyph = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' }[size]
  const Icon = icon ?? ((name && ICONS[name]) || BookOpen)
  return (
    <span
      aria-hidden
      className={`inline-flex shrink-0 items-center justify-center border-2 border-border-dark shadow-neo text-border-dark ${TILE_COLORS[color]} ${box} ${className}`}
    >
      <Icon className={glyph} strokeWidth={2.25} />
    </span>
  )
}
