import React from 'react'

interface DailyGoalRingProps {
  xpToday: number
  goal: number
  /** Outer diameter in px. */
  size?: number
}

const INK = '#1A1A1A'

/**
 * Circular progress towards the daily XP goal. Reaching the goal switches the ring to green AND
 * replaces the numbers with a check mark, so the "done" state is not colour-only.
 */
export const DailyGoalRing: React.FC<DailyGoalRingProps> = ({ xpToday, goal, size = 120 }) => {
  const xp = Math.max(0, Math.round(xpToday))
  const target = Math.max(1, Math.round(goal))
  const done = xp >= target
  const fraction = Math.min(1, xp / target)

  const stroke = Math.max(8, Math.round(size * 0.12))
  const outline = 2 // dark border drawn around the track, neobrutalist style
  const radius = (size - stroke) / 2 - outline
  const circumference = 2 * Math.PI * radius
  const centre = size / 2

  const label = done
    ? `${xp} of ${target} XP today. Daily goal met.`
    : `${xp} of ${target} XP today`

  return (
    <div
      role="img"
      aria-label={label}
      className="relative shrink-0"
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden focusable="false">
        {/* border */}
        <circle cx={centre} cy={centre} r={radius} fill="none" stroke={INK} strokeWidth={stroke + outline * 2} />
        {/* empty track */}
        <circle cx={centre} cy={centre} r={radius} fill="none" stroke="#FFFDF5" strokeWidth={stroke} />
        {/* progress arc, starting at 12 o'clock */}
        <circle
          cx={centre}
          cy={centre}
          r={radius}
          fill="none"
          stroke={done ? '#00C875' : '#FFE135'}
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - fraction)}
          transform={`rotate(-90 ${centre} ${centre})`}
          className="transition-[stroke-dashoffset] duration-700 ease-out"
        />
      </svg>

      <div
        aria-hidden
        className="absolute inset-0 flex flex-col items-center justify-center text-center text-text-primary"
        style={{ padding: stroke + outline * 2 }}
      >
        {done ? (
          <>
            <svg
              width={size * 0.3}
              height={size * 0.3}
              viewBox="0 0 24 24"
              fill="none"
              stroke={INK}
              strokeWidth={4}
              strokeLinecap="square"
              strokeLinejoin="miter"
            >
              <path d="M3 13 L9 19 L21 5" />
            </svg>
            <span className="font-mono font-bold leading-none mt-1" style={{ fontSize: Math.max(10, size * 0.11) }}>
              {xp} XP
            </span>
          </>
        ) : (
          <>
            <span className="font-heading font-black leading-none" style={{ fontSize: size * 0.26 }}>
              {xp}
            </span>
            <span className="font-mono font-bold text-text-muted leading-none mt-1" style={{ fontSize: Math.max(10, size * 0.1) }}>
              / {target} XP
            </span>
          </>
        )}
      </div>
    </div>
  )
}
