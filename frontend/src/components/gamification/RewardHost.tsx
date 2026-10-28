import React, { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react'
import { useGamificationStore } from '@/store/gamificationStore'
import { useAuthStore } from '@/store/authStore'
import { RewardDialog } from '@/components/gamification/RewardDialog'
import { RewardModalBody } from '@/components/gamification/RewardModalBody'
import { RewardToast, type ToastItem } from '@/components/gamification/RewardToast'
import { buildPlans, toastParts, type ToastParts } from '@/components/gamification/rewardModels'
import { usePrefersReducedMotion } from '@/components/gamification/useReducedMotion'
import type { RewardSummary } from '@/types/gamification'

/** Rewards arriving within this window of the previous one share a toast. */
const MERGE_WINDOW_MS = 1500
const MAX_TOASTS = 3
/** Let the learner see the toast and the page update before a celebration takes over the screen. */
const REVEAL_DELAY_MS = 700
/**
 * Clicks arriving this soon after a dialog appears (or disappears) are ignored: a double-click on
 * "Next" must neither skip the next dialog nor land on the page underneath.
 */
const CLICK_GUARD_MS = 350

/** Pure: fold a new reward into the toast stack (merge into the newest toast when it is "the same moment"). */
function addToast(prev: ToastItem[], parts: ToastParts, now: number, id: number): ToastItem[] {
  const last = prev[prev.length - 1]
  if (last && now - last.at < MERGE_WINDOW_MS) {
    const notes = [...last.notes]
    for (const n of parts.notes) if (!notes.some((x) => x.text === n.text)) notes.push(n)
    const merged: ToastItem = {
      ...last,
      at: now,
      rev: last.rev + 1,
      xp: last.xp + parts.xp,
      events: [...last.events, ...parts.events],
      notes,
    }
    return [...prev.slice(0, -1), merged]
  }
  return [...prev, { id, at: now, rev: 0, xp: parts.xp, events: parts.events, notes: parts.notes }].slice(-MAX_TOASTS)
}

/**
 * Mounted once (inside the router). Drains `rewardQueue` from the gamification store:
 * an XP toast for every reward, then celebration dialogs (level up, badges, streak news) one at a time.
 * A reward leaves the queue (shiftReward) only after it has been fully presented.
 */
export const RewardHost: React.FC = () => {
  const queue = useGamificationStore((s) => s.rewardQueue)
  const shiftReward = useGamificationStore((s) => s.shiftReward)
  const userId = useAuthStore((s) => s.user?.id ?? null)
  const reducedMotion = usePrefersReducedMotion()
  const baseId = useId()

  const [toasts, setToasts] = useState<ToastItem[]>([])
  /** Celebration keys already shown, so a replayed response never celebrates the same thing twice. */
  const [shown, setShown] = useState<ReadonlySet<string>>(() => new Set())
  const [step, setStep] = useState(0)
  /** The reward whose dialogs may be on screen (set after REVEAL_DELAY_MS). */
  const [readyFor, setReadyFor] = useState<RewardSummary | null>(null)

  const toastedRef = useRef(new WeakSet<RewardSummary>())
  const nextToastId = useRef(1)
  const openerRef = useRef<HTMLElement | null>(null)
  /** The queue array we last drained an empty head from, so one queue state is never shifted twice. */
  const emptyShiftedRef = useRef<RewardSummary[] | null>(null)
  const shownAtRef = useRef(0)
  const wasOpenRef = useRef(false)
  const [shield, setShield] = useState(false)

  const plans = useMemo(() => buildPlans(queue, shown), [queue, shown])
  const head = plans[0]
  const total = head?.modals.length ?? 0
  const modal = head && readyFor === head.reward ? head.modals[step] : undefined
  const modalOpen = modal !== undefined

  // A different learner (or a logout) starts from a clean slate.
  const prevUserRef = useRef(userId)
  useEffect(() => {
    if (prevUserRef.current === userId) return
    prevUserRef.current = userId
    setToasts([])
    setShown(new Set())
    setStep(0)
    setReadyFor(null)
  }, [userId])

  // 1. Toasts: every reward in the queue gets exactly one (rapid ones merge).
  useEffect(() => {
    for (const reward of queue) {
      if (toastedRef.current.has(reward)) continue
      toastedRef.current.add(reward)
      const parts = toastParts(reward)
      if (!parts) continue
      const now = Date.now()
      const id = nextToastId.current++
      setToasts((prev) => addToast(prev, parts, now, id))
    }
  }, [queue])

  // 2. A reward with nothing to celebrate is done once its toast exists.
  useEffect(() => {
    if (!head || head.modals.length > 0) return
    if (emptyShiftedRef.current === queue) return
    emptyShiftedRef.current = queue
    shiftReward()
  }, [head, queue, shiftReward])

  // 3. Reveal the dialogs of the head reward after a short pause.
  const headReward = head && head.modals.length > 0 ? head.reward : null
  useEffect(() => {
    if (!headReward) return
    const timer = setTimeout(() => {
      // Remember what had focus so it can be restored when the whole sequence is done.
      if (openerRef.current === null && document.activeElement instanceof HTMLElement) {
        openerRef.current = document.activeElement
      }
      setReadyFor(headReward)
    }, REVEAL_DELAY_MS)
    return () => clearTimeout(timer)
  }, [headReward])

  // 4. While a dialog is open: no page scrolling behind it; afterwards give focus back.
  useEffect(() => {
    if (!modalOpen) return
    const body = document.body
    const prevOverflow = body.style.overflow
    const prevPadding = body.style.paddingRight
    const scrollbar = window.innerWidth - document.documentElement.clientWidth
    body.style.overflow = 'hidden'
    if (scrollbar > 0) body.style.paddingRight = `${scrollbar}px`
    return () => {
      body.style.overflow = prevOverflow
      body.style.paddingRight = prevPadding
      const opener = openerRef.current
      openerRef.current = null
      if (opener && opener.isConnected) opener.focus({ preventScroll: true })
    }
  }, [modalOpen])

  // 5. Click guards around the dialogs (see CLICK_GUARD_MS).
  const modalKey = modal ? `${step}:${modal.keys.join(',')}` : null
  useEffect(() => {
    if (modalKey !== null) shownAtRef.current = Date.now()
  }, [modalKey])
  useEffect(() => {
    if (modalOpen) {
      wasOpenRef.current = true
      return
    }
    if (!wasOpenRef.current) return
    wasOpenRef.current = false
    setShield(true)
    const timer = setTimeout(() => setShield(false), CLICK_GUARD_MS)
    return () => {
      clearTimeout(timer)
      setShield(false)
    }
  }, [modalOpen])

  const dismissToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const finish = useCallback(() => {
    if (!head) return
    const keys = head.modals.flatMap((m) => m.keys)
    // Shift first: if these were ever applied separately, the head must never be re-planned with its own keys marked as shown.
    shiftReward()
    setStep(0)
    setShown((prev) => (keys.every((k) => prev.has(k)) ? prev : new Set([...prev, ...keys])))
  }, [head, shiftReward])

  const advance = useCallback(() => {
    if (!head || Date.now() - shownAtRef.current < CLICK_GUARD_MS) return
    if (step + 1 < head.modals.length) setStep(step + 1)
    else finish()
  }, [head, step, finish])

  /** Esc and the close (x) button leave the whole sequence; only "Next" steps through it. */
  const dismissAll = useCallback(() => {
    if (!head || Date.now() - shownAtRef.current < CLICK_GUARD_MS) return
    finish()
  }, [head, finish])

  const labelId = `${baseId}-title`
  const descId = `${baseId}-desc`

  return (
    <>
      {/* The live region is always mounted so screen readers announce toasts as they are added. */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="false"
        aria-label="XP earned"
        className="pointer-events-none fixed bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:w-[22rem] z-[70] flex flex-col gap-2"
      >
        {toasts.map((t) => (
          <div key={t.id} className="pointer-events-auto">
            <RewardToast toast={t} paused={modalOpen} onDismiss={dismissToast} />
          </div>
        ))}
      </div>

      {shield && <div aria-hidden className="fixed inset-0 z-[80]" />}

      {modal && (
        <RewardDialog key={`${step}:${modal.keys.join(',')}`} labelId={labelId} descId={descId} onClose={dismissAll}>
          <RewardModalBody
            modal={modal}
            step={step}
            total={total}
            labelId={labelId}
            descId={descId}
            reducedMotion={reducedMotion}
            onNext={advance}
            onClose={dismissAll}
            onSkipAll={finish}
          />
        </RewardDialog>
      )}
    </>
  )
}
