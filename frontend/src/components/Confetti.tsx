import React, { useMemo } from 'react'

const COLOURS = ['#FFE135', '#FF4D6D', '#00C875', '#3A86FF', '#8338EC', '#FB5607']

/** A one-off burst of confetti; place inside a `relative overflow-hidden` container. */
export const Confetti: React.FC<{ pieces?: number }> = ({ pieces = 36 }) => {
  const items = useMemo(
    () =>
      Array.from({ length: pieces }, (_, i) => ({
        left: Math.random() * 100,
        delay: Math.random() * 0.8,
        colour: COLOURS[i % COLOURS.length],
        rotate: Math.random() * 360,
      })),
    [pieces],
  )
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {items.map((p, i) => (
        <span
          key={i}
          className="confetti-piece"
          style={{ left: `${p.left}%`, background: p.colour, animationDelay: `${p.delay}s`, transform: `rotate(${p.rotate}deg)` }}
        />
      ))}
    </div>
  )
}
