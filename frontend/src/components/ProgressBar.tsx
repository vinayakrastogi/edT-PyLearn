import React from 'react'

interface ProgressBarProps {
  value: number   // 0–100
  color?: 'yellow' | 'blue' | 'green' | 'pink' | 'purple' | 'orange'
  label?: string
  showPercent?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const colorClasses = {
  yellow: 'bg-brand-yellow',
  blue: 'bg-brand-blue',
  green: 'bg-brand-green',
  pink: 'bg-brand-pink',
  purple: 'bg-brand-purple',
  orange: 'bg-brand-orange',
}

const heightClasses = {
  sm: 'h-2',
  md: 'h-3',
  lg: 'h-4',
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  color = 'yellow',
  label,
  showPercent = true,
  size = 'md',
}) => {
  const clamped = Math.min(100, Math.max(0, value))

  return (
    <div className="w-full">
      {(label || showPercent) && (
        <div className="flex justify-between items-center mb-1.5">
          {label && <span className="text-sm font-heading font-bold text-text-primary">{label}</span>}
          {showPercent && (
            <span className="text-sm font-mono font-bold text-text-muted">{clamped}%</span>
          )}
        </div>
      )}
      <div
        className={`w-full ${heightClasses[size]} bg-bg-card border-2 border-border-dark`}
        style={{ borderRadius: '2px' }}
      >
        <div
          className={`${heightClasses[size]} ${colorClasses[color]} transition-all duration-500`}
          style={{ width: `${clamped}%`, borderRadius: '0px' }}
        />
      </div>
    </div>
  )
}
