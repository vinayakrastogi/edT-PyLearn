import React from 'react'

/**
 * Pip the python: PLACEHOLDER mascot.
 *
 * A deliberately simple SVG so the mood system can be wired into the whole app now and the
 * artwork replaced later. To upgrade Pip, only the `MOODS` table and the drawing below need
 * to change; every caller just passes a `mood` and an optional `message`.
 */
export type MascotMood =
  | 'happy'
  | 'celebrating'
  | 'proud'
  | 'thinking'
  | 'encouraging'
  | 'sad'
  | 'sleepy'
  | 'confused'

type Eyes = 'open' | 'happy' | 'sad' | 'closed' | 'wide' | 'sideways'

interface MoodConfig {
  eyes: Eyes
  mouth: string // SVG path (drawn relative to the 120x120 viewBox)
  mouthFill?: string
  extras?: Array<'sparkles' | 'tear' | 'sweat' | 'zzz' | 'question' | 'blush' | 'tongue' | 'thumb'>
  animation: string
  label: string
}

const MOODS: Record<MascotMood, MoodConfig> = {
  happy: { eyes: 'open', mouth: 'M 44 74 Q 60 88 76 74', extras: ['blush', 'tongue'], animation: 'pip-sway', label: 'smiling' },
  celebrating: { eyes: 'happy', mouth: 'M 40 70 Q 60 96 80 70 Z', mouthFill: '#FF4D6D', extras: ['sparkles', 'blush'], animation: 'pip-bounce', label: 'celebrating' },
  proud: { eyes: 'happy', mouth: 'M 44 74 Q 60 86 76 74', extras: ['sparkles', 'blush'], animation: 'pip-sway', label: 'proud' },
  thinking: { eyes: 'sideways', mouth: 'M 48 78 L 72 78', extras: ['question'], animation: 'pip-sway', label: 'thinking' },
  encouraging: { eyes: 'open', mouth: 'M 46 76 Q 60 82 74 76', extras: ['sweat'], animation: 'pip-sway', label: 'encouraging' },
  sad: { eyes: 'sad', mouth: 'M 46 82 Q 60 70 74 82', extras: ['tear'], animation: 'pip-droop', label: 'sad' },
  sleepy: { eyes: 'closed', mouth: 'M 50 78 Q 60 82 70 78', extras: ['zzz'], animation: 'pip-sway', label: 'sleepy' },
  confused: { eyes: 'wide', mouth: 'M 46 80 Q 53 74 60 80 T 74 80', extras: ['question'], animation: 'pip-shake', label: 'confused' },
}

const STROKE = '#1A1A1A'

const renderEyes = (eyes: Eyes) => {
  const left = 46
  const right = 74
  const y = 52
  switch (eyes) {
    case 'happy':
      return (
        <g fill="none" stroke={STROKE} strokeWidth={4} strokeLinecap="round">
          <path d={`M ${left - 7} ${y + 3} Q ${left} ${y - 8} ${left + 7} ${y + 3}`} />
          <path d={`M ${right - 7} ${y + 3} Q ${right} ${y - 8} ${right + 7} ${y + 3}`} />
        </g>
      )
    case 'sad':
      return (
        <g>
          <circle cx={left} cy={y} r={6} fill={STROKE} />
          <circle cx={right} cy={y} r={6} fill={STROKE} />
          <path d={`M ${left - 9} ${y - 8} L ${left + 7} ${y - 14}`} stroke={STROKE} strokeWidth={3.5} strokeLinecap="round" />
          <path d={`M ${right + 9} ${y - 8} L ${right - 7} ${y - 14}`} stroke={STROKE} strokeWidth={3.5} strokeLinecap="round" />
        </g>
      )
    case 'closed':
      return (
        <g fill="none" stroke={STROKE} strokeWidth={4} strokeLinecap="round">
          <path d={`M ${left - 7} ${y} L ${left + 7} ${y}`} />
          <path d={`M ${right - 7} ${y} L ${right + 7} ${y}`} />
        </g>
      )
    case 'wide':
      return (
        <g>
          <circle cx={left} cy={y} r={10} fill="white" stroke={STROKE} strokeWidth={3} />
          <circle cx={right} cy={y} r={10} fill="white" stroke={STROKE} strokeWidth={3} />
          <circle cx={left} cy={y} r={3.5} fill={STROKE} />
          <circle cx={right} cy={y} r={3.5} fill={STROKE} />
        </g>
      )
    case 'sideways':
      return (
        <g>
          <circle cx={left} cy={y} r={9} fill="white" stroke={STROKE} strokeWidth={3} />
          <circle cx={right} cy={y} r={9} fill="white" stroke={STROKE} strokeWidth={3} />
          <circle cx={left + 4} cy={y - 3} r={4} fill={STROKE} />
          <circle cx={right + 4} cy={y - 3} r={4} fill={STROKE} />
        </g>
      )
    default:
      return (
        <g>
          <circle cx={left} cy={y} r={9} fill="white" stroke={STROKE} strokeWidth={3} />
          <circle cx={right} cy={y} r={9} fill="white" stroke={STROKE} strokeWidth={3} />
          <circle cx={left + 1} cy={y + 1} r={4.5} fill={STROKE} />
          <circle cx={right + 1} cy={y + 1} r={4.5} fill={STROKE} />
        </g>
      )
  }
}

const renderExtras = (extras: MoodConfig['extras'] = []) => (
  <>
    {extras.includes('blush') && (
      <g fill="#FF4D6D" opacity={0.35}>
        <ellipse cx={33} cy={68} rx={7} ry={4} />
        <ellipse cx={87} cy={68} rx={7} ry={4} />
      </g>
    )}
    {extras.includes('tongue') && <path d="M 58 83 L 58 94 Q 60 98 62 94 L 62 83" fill="#FF4D6D" stroke={STROKE} strokeWidth={2} />}
    {extras.includes('sparkles') && (
      <g fill="#FFE135" stroke={STROKE} strokeWidth={1.5}>
        <path d="M 14 22 l 3 7 7 3 -7 3 -3 7 -3 -7 -7 -3 7 -3 z" />
        <path d="M 100 12 l 2.5 6 6 2.5 -6 2.5 -2.5 6 -2.5 -6 -6 -2.5 6 -2.5 z" />
        <path d="M 104 50 l 2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 5 -2 z" />
      </g>
    )}
    {extras.includes('tear') && <path d="M 40 66 Q 36 76 40 80 Q 44 76 40 66 Z" fill="#7EC8FF" stroke={STROKE} strokeWidth={1.5} />}
    {extras.includes('sweat') && <path d="M 92 36 Q 87 46 92 50 Q 97 46 92 36 Z" fill="#7EC8FF" stroke={STROKE} strokeWidth={1.5} />}
    {extras.includes('zzz') && (
      <g fill={STROKE} fontFamily="Space Grotesk, sans-serif" fontWeight={800}>
        <text x="86" y="30" fontSize="16">Z</text>
        <text x="98" y="18" fontSize="12">z</text>
      </g>
    )}
    {extras.includes('question') && (
      <text x="88" y="28" fontSize="26" fontWeight={800} fontFamily="Space Grotesk, sans-serif" fill={STROKE}>?</text>
    )}
  </>
)

interface MascotProps {
  mood?: MascotMood
  /** Optional speech bubble shown next to Pip. */
  message?: React.ReactNode
  size?: number
  className?: string
  /** Put the speech bubble below instead of beside Pip (good for narrow spaces). */
  stacked?: boolean
}

export const Mascot: React.FC<MascotProps> = ({ mood = 'happy', message, size = 96, className = '', stacked = false }) => {
  const cfg = MOODS[mood]
  return (
    <div className={`flex ${stacked ? 'flex-col items-center text-center' : 'items-center'} gap-4 ${className}`}>
      <svg
        role="img"
        aria-label={`Pip the python is ${cfg.label}`}
        width={size}
        height={size}
        viewBox="0 0 120 120"
        className={`shrink-0 ${cfg.animation}`}
      >
        {/* tail curl */}
        <path d="M 22 104 Q 6 108 10 92 Q 14 84 24 90" fill="none" stroke={STROKE} strokeWidth={9} strokeLinecap="round" />
        <path d="M 22 104 Q 6 108 10 92 Q 14 84 24 90" fill="none" stroke="#00C875" strokeWidth={4.5} strokeLinecap="round" />
        {/* body */}
        <rect x="18" y="86" width="84" height="22" rx="11" fill="#00C875" stroke={STROKE} strokeWidth={3} />
        <path d="M 30 97 h 8 M 46 97 h 8 M 62 97 h 8 M 78 97 h 8" stroke={STROKE} strokeWidth={3} strokeLinecap="round" opacity={0.35} />
        {/* head */}
        <ellipse cx="60" cy="58" rx="42" ry="38" fill="#00C875" stroke={STROKE} strokeWidth={3.5} />
        <ellipse cx="60" cy="72" rx="28" ry="20" fill="#B8F5D5" opacity={0.55} />
        {/* face */}
        {renderEyes(cfg.eyes)}
        <path d={cfg.mouth} fill={cfg.mouthFill ?? 'none'} stroke={STROKE} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
        {renderExtras(cfg.extras)}
      </svg>
      {message && (
        <div className="relative neo-card bg-bg-card text-text-primary px-4 py-3 font-body text-sm leading-relaxed max-w-md">
          {!stacked && (
            <span
              aria-hidden
              className="absolute -left-2 top-1/2 -translate-y-1/2 w-3 h-3 rotate-45 bg-bg-card border-l-2 border-b-2 border-border-dark"
            />
          )}
          {message}
        </div>
      )}
    </div>
  )
}
