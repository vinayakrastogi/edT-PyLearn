import React from 'react'

type Variant = 'primary' | 'secondary' | 'danger' | 'success' | 'ghost' | 'yellow' | 'pink' | 'purple'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  children: React.ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary: 'bg-brand-blue text-white border-border-dark hover:bg-brand-blue/90',
  secondary: 'bg-bg-card text-text-primary border-border-dark hover:bg-brand-yellow/20',
  danger: 'bg-brand-pink text-white border-border-dark hover:bg-brand-pink/90',
  success: 'bg-brand-green text-white border-border-dark hover:bg-brand-green/90',
  ghost: 'bg-transparent text-text-primary border-border-dark hover:bg-bg-dark/5',
  yellow: 'bg-brand-yellow text-text-primary border-border-dark hover:bg-brand-yellow/80',
  pink: 'bg-brand-pink text-white border-border-dark',
  purple: 'bg-brand-purple text-white border-border-dark',
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-5 py-2.5 text-base',
  lg: 'px-7 py-3.5 text-lg',
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  return (
    <button
      className={`neo-btn border-2 ${variantClasses[variant]} ${sizeClasses[size]} ${className} ${
        disabled || loading ? 'opacity-60 cursor-not-allowed pointer-events-none' : ''
      }`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
}
