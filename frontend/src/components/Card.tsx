import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  accent?: 'yellow' | 'blue' | 'pink' | 'green' | 'purple' | 'orange' | 'none'
  onClick?: () => void
  hoverable?: boolean
}

const accentClasses = {
  yellow: 'border-t-4 border-t-brand-yellow',
  blue: 'border-t-4 border-t-brand-blue',
  pink: 'border-t-4 border-t-brand-pink',
  green: 'border-t-4 border-t-brand-green',
  purple: 'border-t-4 border-t-brand-purple',
  orange: 'border-t-4 border-t-brand-orange',
  none: '',
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  accent = 'none',
  onClick,
  hoverable = false,
}) => {
  return (
    <div
      className={`neo-card p-6 ${accentClasses[accent]} ${className} ${
        hoverable
          ? 'cursor-pointer transition-all duration-150 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-neo-sm active:translate-x-[4px] active:translate-y-[4px] active:shadow-none'
          : ''
      }`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
