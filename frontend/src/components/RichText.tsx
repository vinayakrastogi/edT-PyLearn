import React from 'react'

/** Renders `code` spans inside plain text (used for quiz questions, options and explanations). */
export const RichText: React.FC<{ text: string }> = ({ text }) => {
  const parts = text.split(/`([^`]+)`/g)
  return (
    <>
      {parts.map((part, i) =>
        i % 2 === 1 ? (
          <code key={i} className="font-mono text-[0.9em] bg-brand-yellow/30 border border-border-dark/60 px-1 py-px rounded-sm">
            {part}
          </code>
        ) : (
          <React.Fragment key={i}>{part}</React.Fragment>
        ),
      )}
    </>
  )
}
