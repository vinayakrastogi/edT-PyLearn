import React from 'react'

type BadgeColor = 'yellow' | 'blue' | 'pink' | 'green' | 'purple' | 'orange' | 'dark'

interface BadgeProps {
  children: React.ReactNode
  color?: BadgeColor
  className?: string
}

const colorClasses: Record<BadgeColor, string> = {
  yellow: 'bg-brand-yellow text-text-primary',
  blue: 'bg-brand-blue text-white',
  pink: 'bg-brand-pink text-white',
  green: 'bg-brand-green text-white',
  purple: 'bg-brand-purple text-white',
  orange: 'bg-brand-orange text-white',
  dark: 'bg-bg-dark text-white',
}

export const Badge: React.FC<BadgeProps> = ({ children, color = 'yellow', className = '' }) => {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 text-xs font-mono font-bold
                  border border-border-dark shadow-neo-sm ${colorClasses[color]} ${className}`}
      style={{ borderRadius: '2px' }}
    >
      {children}
    </span>
  )
}
