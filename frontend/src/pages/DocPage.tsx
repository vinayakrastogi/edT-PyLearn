import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useParams, useNavigate, useOutletContext } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Check, Clock, TriangleAlert } from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Mascot } from '@/components/Mascot'
import { LessonSkeleton } from '@/components/Skeleton'
import { LessonMarkdown } from '@/components/lesson/LessonMarkdown'
import { TableOfContents } from '@/components/lesson/TableOfContents'
import { LessonNotes } from '@/components/lesson/LessonNotes'
import { getDoc } from '@/api/modules'
import { markLessonViewed, getModuleProgress, trackAccess } from '@/api/progress'
import { XpIcon } from '@/lib/icons'
import { extractHeadings } from '@/lib/slug'
import { useGamificationStore } from '@/store/gamificationStore'
import type { DocPage as DocPageType, ModuleDetail } from '@/types/module'
import type { ModuleProgressSummary } from '@/types/problem'

/** A lesson counts as read once the learner has scrolled through most of it. */
const READ_THRESHOLD = 0.85
/** After a failed save, wait this long (doubling per failure, up to the maximum) before trying again. */
const RETRY_BASE_MS = 5000
const RETRY_MAX_MS = 30000

export const DocPage: React.FC = () => {
  const { moduleId, docId } = useParams<{ moduleId: string; docId: string }>()
  const navigate = useNavigate()
  const { module, setProgress } = useOutletContext<{
    module: ModuleDetail
    setProgress: React.Dispatch<React.SetStateAction<ModuleProgressSummary | null>>
  }>()
  const [doc, setDoc] = useState<DocPageType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [marked, setMarked] = useState(false)
  /** XP this visit earned for the lesson (0 when it was already read or earns no XP). */
  const [earnedXp, setEarnedXp] = useState(0)
  const [scrollPct, setScrollPct] = useState(0)
  /** Consecutive failed attempts to record the lesson as read (0 = none, or it succeeded since). */
  const [saveFailures, setSaveFailures] = useState(0)
  const markingRef = useRef(false)
  /** The lesson-view call already succeeded for the lesson on screen (only the progress refresh may need a retry). */
  const recordedRef = useRef(false)
  /** The lesson currently on screen, to ignore late answers about a lesson the learner has left. */
  const lessonKeyRef = useRef('')
  /** Scroll-driven saves are skipped until this time after a failure, so a failing server is not hit on every scroll tick. */
  const retryAtRef = useRef(0)
  const failuresRef = useRef(0)
  const handleRewards = useGamificationStore((s) => s.handleRewards)

  /** Record the lesson as read. `manual` (Next button, Retry button) ignores the retry backoff. */
  const markRead = useCallback(
    async (manual = false) => {
      if (!moduleId || !docId || markingRef.current) return
      if (!manual && Date.now() < retryAtRef.current) return
      markingRef.current = true
      const key = `${moduleId}/${docId}`
      const failed = (lessonSaved: boolean) => {
        if (lessonKeyRef.current !== key) return
        failuresRef.current += 1
        retryAtRef.current = Date.now() + Math.min(RETRY_MAX_MS, RETRY_BASE_MS * 2 ** (failuresRef.current - 1))
        markingRef.current = false
        // A failed progress refresh is not worth a warning: the lesson itself is already recorded.
        if (!lessonSaved) setSaveFailures(failuresRef.current)
      }
      if (!recordedRef.current) {
        let record
        try {
          record = await markLessonViewed(moduleId, docId)
        } catch {
          failed(false)
          return
        }
        // The XP is real even if the learner has already moved on, so always hand it to the store.
        handleRewards(record.rewards)
        if (lessonKeyRef.current === key) {
          recordedRef.current = true
          failuresRef.current = 0
          retryAtRef.current = 0
          setSaveFailures(0)
          setMarked(true)
          setEarnedXp(record.rewards?.xp_gained ?? 0)
        }
      }
      try {
        setProgress(await getModuleProgress(moduleId))
      } catch {
        failed(true)
      }
    },
    [moduleId, docId, setProgress, handleRewards],
  )

  // The scroll listener always calls the latest markRead without being re-attached (and re-measured) whenever its identity changes.
  const markReadRef = useRef(markRead)
  useEffect(() => {
    markReadRef.current = markRead
  })

  useEffect(() => {
    if (!moduleId || !docId) return
    let cancelled = false
    // Drop the previous lesson at once: its DOM and scroll position must never be measured as the new lesson's.
    setDoc(null)
    setLoading(true)
    setError(false)
    setMarked(false)
    setEarnedXp(0)
    setScrollPct(0)
    setSaveFailures(0)
    markingRef.current = false
    recordedRef.current = false
    failuresRef.current = 0
    retryAtRef.current = 0
    lessonKeyRef.current = `${moduleId}/${docId}`
    getDoc(moduleId, docId)
      .then((d) => {
        if (cancelled) return
        setDoc(d)
        trackAccess(`/modules/${moduleId}/docs/${d.id}`, d.title).catch(() => {})
      })
      .catch(() => {
        if (!cancelled) setError(true)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [moduleId, docId])

  // Reading progress from the page scroll position. Runs only once the lesson itself is on screen.
  useEffect(() => {
    if (!doc) return
    // `instant` beats the global smooth scrolling, so the first measurement below really is at the top.
    window.scrollTo({ top: 0, behavior: 'instant' })
    const onScroll = () => {
      const de = document.documentElement
      const max = de.scrollHeight - window.innerHeight
      const pct = max <= 8 ? 1 : Math.min(1, window.scrollY / max)
      setScrollPct(pct)
      if (pct >= READ_THRESHOLD) void markReadRef.current()
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [doc])

  // After a failed save, try again on a timer (scrolling alone may never happen again at the bottom of the page).
  useEffect(() => {
    if (saveFailures === 0) return
    const timer = setTimeout(() => void markReadRef.current(), Math.max(0, retryAtRef.current - Date.now()) + 50)
    return () => clearTimeout(timer)
  }, [saveFailures])

  // The page header already shows the title, so drop the lesson's own leading "# Title" line.
  const body = useMemo(() => (doc ? doc.content_md.replace(/^\s*#\s+[^\n]*\n+/, '') : ''), [doc])
  const headings = useMemo(() => extractHeadings(body), [body])

  if (loading) return <LessonSkeleton />

  if (error || !doc) {
    return (
      <div className="max-w-xl mx-auto px-8 py-16">
        <Mascot mood="confused" message="I could not load this lesson. Check that the backend is running, then refresh the page." />
      </div>
    )
  }

  const currentIndex = module.docs.findIndex((d) => d.id === docId)
  const prevDoc = currentIndex > 0 ? module.docs[currentIndex - 1] : null
  const nextDoc = currentIndex !== -1 && currentIndex < module.docs.length - 1 ? module.docs[currentIndex + 1] : null

  const goNext = async () => {
    await markRead(true)
    // If saving failed, stay here: the hint above the buttons explains it and the learner can retry,
    // instead of silently leaving a lesson that was never recorded.
    if (!recordedRef.current) return
    if (nextDoc) navigate(`/modules/${moduleId}/docs/${nextDoc.id}`)
    else if (module.quiz_id) navigate(`/modules/${moduleId}/quiz`)
    else if (module.problems.length > 0) navigate(`/modules/${moduleId}/problems/${module.problems[0].id}`)
    else navigate('/dashboard')
  }
  const goPrev = () => navigate(prevDoc ? `/modules/${moduleId}/docs/${prevDoc.id}` : '/dashboard')

  return (
    <div>
      {/* Reading progress */}
      <div className="fixed top-0 left-0 right-0 z-[60] h-1.5 bg-transparent" role="progressbar" aria-valuenow={Math.round(scrollPct * 100)} aria-valuemin={0} aria-valuemax={100} aria-label="Reading progress">
        <div className="h-full bg-brand-pink transition-[width] duration-150" style={{ width: `${scrollPct * 100}%` }} />
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-8 py-10 flex gap-8">
        <div className="min-w-0 flex-1 max-w-3xl">
          {/* Header */}
          <header className="mb-8">
            <div className="flex items-center gap-2 mb-3 flex-wrap">
              <span className="font-mono font-bold text-sm text-text-muted bg-brand-yellow/30 px-2 py-1 border border-border-dark">
                Lesson {doc.order} of {module.docs.length}
              </span>
              <Badge color="blue" className="gap-1">
                <Clock aria-hidden className="w-3.5 h-3.5" /> {doc.read_minutes} min read
              </Badge>
              {marked && (
                <Badge color="green" className="gap-1">
                  <Check aria-hidden className="w-3.5 h-3.5" strokeWidth={3} /> Read
                </Badge>
              )}
              {marked && earnedXp > 0 && (
                <Badge color="yellow" className="gap-1">
                  <XpIcon className="w-3.5 h-3.5" /> +{earnedXp} XP
                </Badge>
              )}
              {doc.concepts.map((c) => (
                <Badge key={c} color="purple">{c}</Badge>
              ))}
            </div>
            <h1 className="font-heading font-black text-3xl sm:text-4xl text-text-primary leading-tight">{doc.title}</h1>
          </header>

          <div className="border-b-4 border-border-dark mb-8" />

          <LessonMarkdown markdown={body} />
          {moduleId && docId && <LessonNotes key={`${moduleId}/${docId}`} moduleId={moduleId} docId={docId} />}

          {/* Completion + navigation */}
          <footer className="mt-14 pt-8 border-t-2 border-border-dark">
            <div className="neo-card p-5 mb-6 bg-brand-green/10">
              <Mascot
                mood={marked ? 'proud' : 'encouraging'}
                message={
                  marked ? (
                    <>
                      {nextDoc ? 'Lesson complete! ' : 'You finished the last lesson. '}
                      {earnedXp > 0 && (
                        <strong>
                          <XpIcon className="w-4 h-4 mr-1 align-[-0.15em]" />+{earnedXp} XP earned!{' '}
                        </strong>
                      )}
                      {nextDoc ? `Next up: "${nextDoc.title}".` : 'Time to test yourself with the quiz!'}
                    </>
                  ) : (
                    'Scroll to the end of the lesson and I will mark it as read for you.'
                  )
                }
              />
            </div>
            {saveFailures > 0 && !marked && (
              <div role="status" className="mb-6 flex items-center justify-between gap-3 flex-wrap border-2 border-border-dark bg-brand-yellow/20 px-4 py-3">
                <p className="font-body text-sm font-bold m-0 inline-flex items-center gap-2">
                  <TriangleAlert aria-hidden className="w-4 h-4 shrink-0 text-brand-orange" />
                  Could not save your progress. Retrying...
                </p>
                <Button variant="secondary" size="sm" onClick={() => void markRead(true)}>
                  Retry now
                </Button>
              </div>
            )}
            <div className="flex justify-between items-center gap-3 flex-wrap">
              <button onClick={goPrev} className="inline-flex items-center gap-1.5 font-heading font-bold text-sm text-text-muted hover:text-brand-blue transition-colors">
                <ArrowLeft aria-hidden className="w-4 h-4 shrink-0" /> {prevDoc ? prevDoc.title : 'Dashboard'}
              </button>
              <Button variant="yellow" size="md" onClick={() => void goNext()} id="next-lesson-btn">
                {nextDoc ? `Next: ${nextDoc.title}` : module.quiz_id ? 'Take the quiz' : 'Continue'}
                <ArrowRight aria-hidden className="w-4 h-4 shrink-0" />
              </Button>
            </div>
          </footer>
        </div>

        {/* Table of contents (wide screens) */}
        <aside className="hidden xl:block w-60 shrink-0">
          <div className="sticky top-[calc(var(--nav-h)+4rem)]">
            <TableOfContents headings={headings} />
          </div>
        </aside>
      </div>
    </div>
  )
}
