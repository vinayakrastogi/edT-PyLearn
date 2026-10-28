import React from 'react'

/** PyLearn logo mark: Pip's face on a yellow neobrutalist tile. Same artwork as public/favicon.svg. */
export const LogoMark: React.FC<{ size?: number; className?: string; title?: string }> = ({ size = 40, className = '', title }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 48 48"
    className={`shrink-0 ${className}`}
    role={title ? 'img' : undefined}
    aria-label={title}
    aria-hidden={title ? undefined : true}
  >
    {/* offset shadow + tile */}
    <rect x="5" y="5" width="41" height="41" rx="8" fill="#1A1A1A" />
    <rect x="2" y="2" width="41" height="41" rx="8" fill="#FFE135" stroke="#1A1A1A" strokeWidth="3" />
    {/* Pip's head */}
    <ellipse cx="22.5" cy="24" rx="14" ry="12.5" fill="#00C875" stroke="#1A1A1A" strokeWidth="2.5" />
    <ellipse cx="22.5" cy="28.5" rx="9" ry="6" fill="#B8F5D5" opacity="0.6" />
    {/* eyes */}
    <circle cx="17.5" cy="21" r="2.6" fill="#1A1A1A" />
    <circle cx="27.5" cy="21" r="2.6" fill="#1A1A1A" />
    <circle cx="18.3" cy="20.2" r="0.9" fill="#FFFFFF" />
    <circle cx="28.3" cy="20.2" r="0.9" fill="#FFFFFF" />
    {/* smile */}
    <path d="M 17.5 27.5 Q 22.5 32 27.5 27.5" fill="none" stroke="#1A1A1A" strokeWidth="2.4" strokeLinecap="round" />
    {/* tongue */}
    <path d="M 22.5 30 l 0 4 M 22.5 34 l -1.6 1.6 M 22.5 34 l 1.6 1.6" stroke="#FF4D6D" strokeWidth="1.6" strokeLinecap="round" />
  </svg>
)

/** Logo mark plus the "PyLearn" word mark. */
export const Logo: React.FC<{ size?: number; showText?: boolean; textClassName?: string }> = ({
  size = 40,
  showText = true,
  textClassName = 'font-heading font-bold text-xl text-text-primary',
}) => (
  <span className="inline-flex items-center gap-3">
    <LogoMark size={size} />
    {showText && <span className={textClassName}>PyLearn</span>}
  </span>
)
