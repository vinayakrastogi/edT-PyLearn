import React, { useEffect, useRef, useState } from 'react'
import { PartyPopper, X } from 'lucide-react'
import { XpIcon } from '@/lib/icons'
import type { RewardEvent } from '@/types/gamification'
import { eventIcon, type ToastNote } from '@/components/gamification/rewardModels'

export interface ToastItem {
  id: number
  /** When the newest reward was merged in (ms since epoch). Used to merge rapid rewards into one toast. */
  at: number
  /** Bumped on every merge so the auto-dismiss timer restarts. */
  rev: number
  xp: number
  events: RewardEvent[]
  notes: ToastNote[]
}

const DISMISS_AFTER_MS = 4000
/** After the pointer or focus leaves, never dismiss in under this long. */
const MIN_REMAINING_MS = 1200

interface RewardToastProps {
  toast: ToastItem
  /** Hold the timer, e.g. while a celebration dialog is open on top. */
  paused: boolean
  onDismiss: (id: number) => void
}

/** One XP toast: itemised events, auto-dismisses, pauses on hover/focus, closable. */
export const RewardToast: React.FC<RewardToastProps> = ({ toast, paused, onDismiss }) => {
  const [hovered, setHovered] = useState(false)
  const [focused, setFocused] = useState(false)
  const halted = paused || hovered || focused
  const remaining = useRef(DISMISS_AFTER_MS)
  const { id, rev } = toast

  // A merged-in reward gives the toast a fresh lease of life. Declared before the timer so it runs first.
  useEffect(() => {
    remaining.current = DISMISS_AFTER_MS
  }, [rev])

  useEffect(() => {
    if (halted) return
    const started = Date.now()
    const timer = setTimeout(() => onDismiss(id), remaining.current)
    return () => {
      clearTimeout(timer)
      remaining.current = Math.max(MIN_REMAINING_MS, remaining.current - (Date.now() - started))
    }
  }, [halted, rev, id, onDismiss])

  const itemised = toast.events.length > 1
  const single = toast.events.length === 1 ? toast.events[0] : null

  return (
    <div
      className="toast-in neo-card relative p-3 pr-11 bg-bg-card"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onFocus={() => setFocused(true)}
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setFocused(false)
      }}
    >
      <div className="flex items-start gap-3">
        {toast.xp > 0 ? (
          <XpIcon className="w-6 h-6 mt-0.5" />
        ) : (
          <PartyPopper aria-hidden className="w-6 h-6 shrink-0 mt-0.5 text-brand-purple" strokeWidth={2.25} />
        )}
        <div className="min-w-0 flex-1">
          {toast.xp > 0 && (
            <p className="font-heading font-black text-lg leading-tight text-text-primary m-0">
              +{toast.xp} XP
              {single && <span className="font-body font-medium text-sm text-text-muted"> · {single.label}</span>}
            </p>
          )}
          {itemised && (
            <ul className="mt-1 space-y-0.5 list-none p-0 m-0">
              {toast.events.map((e, i) => {
                const Icon = eventIcon(e.kind)
                return (
                  <li key={`${e.kind}-${i}`} className="flex items-center gap-1.5 font-body text-sm text-text-primary">
                    <Icon aria-hidden className="w-4 h-4 shrink-0" strokeWidth={2.25} />
                    <span className="font-mono font-bold tabular-nums">+{e.amount} XP</span>
                    <span className="text-text-muted truncate">{e.label}</span>
                  </li>
                )
              })}
            </ul>
          )}
          {toast.notes.map((n, i) => {
            const NoteIcon = n.icon
            return (
              <p key={i} className="flex items-start gap-1.5 font-body text-sm text-text-primary mt-1 mb-0">
                <NoteIcon aria-hidden className="w-4 h-4 shrink-0 mt-0.5" strokeWidth={2.25} />
                <span>{n.text}</span>
              </p>
            )
          })}
        </div>
      </div>
      <button
        type="button"
        onClick={() => onDismiss(id)}
        aria-label="Dismiss notification"
        className="absolute top-1.5 right-1.5 w-8 h-8 flex items-center justify-center border-2 border-border-dark bg-bg-card font-heading font-black text-sm leading-none hover:bg-brand-yellow/40"
      >
        <X aria-hidden className="w-4 h-4" strokeWidth={3} />
      </button>
    </div>
  )
}
