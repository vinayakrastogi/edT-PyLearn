import React from 'react'

/** A pulsing placeholder block used instead of bare spinners while content loads. */
export const Skeleton: React.FC<{ className?: string }> = ({ className = 'h-4 w-full' }) => (
  <div className={`skeleton ${className}`} aria-hidden />
)

export const LessonSkeleton: React.FC = () => (
  <div className="max-w-3xl mx-auto px-6 sm:px-8 py-10 space-y-4" role="status" aria-label="Loading lesson">
    <Skeleton className="h-6 w-32" />
    <Skeleton className="h-12 w-3/4" />
    <div className="border-b-4 border-border-dark/20 my-6" />
    {[95, 88, 92, 70, 96, 84].map((w, i) => (
      <Skeleton key={i} className="h-4" />
    ))}
    <Skeleton className="h-40 w-full" />
    <Skeleton className="h-4 w-2/3" />
  </div>
)
