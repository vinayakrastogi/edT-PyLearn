import React, { useEffect, useRef } from 'react'

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

interface RewardDialogProps {
  /** id of the element holding the dialog title. */
  labelId: string
  /** id of the element holding the dialog description. */
  descId: string
  onClose: () => void
  children: React.ReactNode
}

/**
 * Modal shell for celebrations: backdrop, role="dialog", focus moves in and is trapped,
 * Esc dismisses it (via onClose). Returning focus to where it was is handled by <RewardHost/>.
 */
export const RewardDialog: React.FC<RewardDialogProps> = ({ labelId, descId, onClose, children }) => {
  const panelRef = useRef<HTMLDivElement>(null)
  const onCloseRef = useRef(onClose)
  useEffect(() => {
    onCloseRef.current = onClose
  })

  useEffect(() => {
    const panel = panelRef.current
    if (!panel) return

    const focusables = () => Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE))
    const focusFirst = () => {
      const target = panel.querySelector<HTMLElement>('[data-autofocus]') ?? focusables()[0] ?? panel
      target.focus({ preventScroll: true })
    }
    focusFirst()

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        e.stopPropagation()
        onCloseRef.current()
        return
      }
      if (e.key !== 'Tab') return
      const items = focusables()
      if (items.length === 0) {
        e.preventDefault()
        panel.focus()
        return
      }
      const first = items[0]
      const last = items[items.length - 1]
      const active = document.activeElement
      const inside = active !== null && panel.contains(active)
      if (e.shiftKey && (!inside || active === first || active === panel)) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && (!inside || active === last)) {
        e.preventDefault()
        first.focus()
      }
    }
    // Anything that grabs focus from outside (e.g. the code editor) is pulled back in.
    const onFocusIn = (e: FocusEvent) => {
      if (e.target instanceof Node && !panel.contains(e.target)) focusFirst()
    }

    document.addEventListener('keydown', onKeyDown, true)
    document.addEventListener('focusin', onFocusIn)
    return () => {
      document.removeEventListener('keydown', onKeyDown, true)
      document.removeEventListener('focusin', onFocusIn)
    }
  }, [])

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center p-4">
      <div aria-hidden className="reward-backdrop absolute inset-0 bg-black/55" />
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelId}
        aria-describedby={descId}
        tabIndex={-1}
        className="neo-card relative w-full max-w-md max-h-[calc(100dvh-2rem)] overflow-y-auto border-4 shadow-neo-lg animate-bounce-in outline-none"
      >
        {children}
      </div>
    </div>
  )
}
