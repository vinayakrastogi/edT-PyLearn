import { useSyncExternalStore } from 'react'

const QUERY = '(prefers-reduced-motion: reduce)'

const getMedia = () => (typeof window !== 'undefined' && typeof window.matchMedia === 'function' ? window.matchMedia(QUERY) : null)

const subscribe = (onChange: () => void) => {
  const media = getMedia()
  media?.addEventListener('change', onChange)
  return () => media?.removeEventListener('change', onChange)
}

/** True when the learner asked their system for less motion. Used to skip confetti and flourishes. */
export function usePrefersReducedMotion(): boolean {
  return useSyncExternalStore(subscribe, () => getMedia()?.matches ?? false, () => false)
}
