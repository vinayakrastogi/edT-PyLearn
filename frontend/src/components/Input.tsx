import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  id: string
}

export const Input: React.FC<InputProps> = ({ label, error, id, className = '', ...props }) => {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="font-heading font-bold text-sm text-text-primary">
          {label}
        </label>
      )}
      <input
        id={id}
        className={`neo-input ${error ? 'border-brand-pink shadow-neo-pink' : ''} ${className}`}
        {...props}
      />
      {error && (
        <p className="text-brand-pink text-xs font-mono font-bold">{error}</p>
      )}
    </div>
  )
}
