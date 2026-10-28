import React, { useEffect, useState, useCallback, useRef } from 'react'
import { useParams } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { Check, ChevronDown, ChevronRight, CircleCheck, CircleX, Lightbulb, Play, Send, Terminal, Timer, TriangleAlert, X } from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Mascot, type MascotMood } from '@/components/Mascot'
import { moodForError } from '@/lib/pipReactions'
import { Skeleton } from '@/components/Skeleton'
import { RichText } from '@/components/RichText'
import { LessonMarkdown } from '@/components/lesson/LessonMarkdown'
import { XPLine } from '@/components/gamification/XPSummary'
import { moduleEarnsXp } from '@/lib/xp'
import { useGamificationStore } from '@/store/gamificationStore'
import { getProblem, submitCode, getSubmissions } from '@/api/problems'
import { runCode, type RunResult } from '@/api/run'
import type { ProblemDetail, CodeSubmitResponse, SubmissionRecord, VisibleTest } from '@/types/problem'

const STATUS_CONFIG = {
  PASS: { label: 'All Tests Passed!', icon: CircleCheck, bg: 'bg-brand-green text-white' },
  FAIL: { label: 'Some Tests Failed', icon: CircleX, bg: 'bg-brand-pink text-white' },
  ERROR: { label: 'Runtime Error', icon: TriangleAlert, bg: 'bg-brand-orange text-white' },
  TIMEOUT: { label: 'Time Limit Exceeded', icon: Timer, bg: 'bg-brand-purple text-white' },
}

const DIFFICULTY_COLOR = { easy: 'green', medium: 'orange', hard: 'pink' } as const

const KIND_LABEL = {
  function: 'Write a function',
  program: 'Write a program (reads input, prints output)',
  driver: 'Write the class / functions requested',
} as const

/** How to show one sample test to the learner, depending on the problem kind. */
const TestInput: React.FC<{ test: VisibleTest }> = ({ test }) => {
  if (test.stdin !== undefined) {
    return (
      <div>
        <span className="text-text-muted">Input:</span>
        <pre className="font-bold whitespace-pre-wrap mt-1 mb-0">{test.stdin === '' ? '(empty)' : test.stdin.replace(/\n$/, '')}</pre>
      </div>
    )
  }
  if (test.driver !== undefined) {
    return (
      <div>
        <span className="text-text-muted">Then this code runs:</span>
        <pre className="font-bold whitespace-pre-wrap mt-1 mb-0">{test.driver}</pre>
      </div>
    )
  }
  const args = Array.isArray(test.input) ? test.input.map((v) => JSON.stringify(v)).join(', ') : JSON.stringify(test.input)
  return (
    <div>
      <span className="text-text-muted">Called with: </span>
      <span className="font-bold">{args}</span>
    </div>
  )
}

function reactionFor(result: CodeSubmitResponse): { mood: MascotMood; message: string } {
  switch (result.status) {
    case 'PASS':
      return { mood: 'celebrating', message: 'Brilliant! Every test passed. Onto the next challenge!' }
    case 'FAIL': {
      const ratio = result.passed_count / Math.max(1, result.total_count)
      return ratio >= 0.5
        ? { mood: 'encouraging', message: 'So close! Some tests still fail. Look at the expected and actual values for the visible ones.' }
        : { mood: 'sad', message: 'Not quite yet. Re-read the problem, then try a hint. You can do this!' }
    }
    case 'TIMEOUT':
      return moodForError('', true)
    default:
      return moodForError(result.stderr)
  }
}

export const ProblemPage: React.FC = () => {
  const { moduleId, problemId } = useParams<{ moduleId: string; problemId: string }>()
  const [problem, setProblem] = useState<ProblemDetail | null>(null)
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<CodeSubmitResponse | null>(null)
  const [runResult, setRunResult] = useState<RunResult | null>(null)
  const [runError, setRunError] = useState<string | null>(null)
  const [stdin, setStdin] = useState('')
  const [hintsShown, setHintsShown] = useState(0)
  const [submissions, setSubmissions] = useState<SubmissionRecord[]>([])
  const [showHistory, setShowHistory] = useState(false)
  /** Whether the learner had already passed this problem when the shown result was submitted. */
  const [passedBefore, setPassedBefore] = useState(false)
  const [editorReady, setEditorReady] = useState(false)
  const handleRewards = useGamificationStore((s) => s.handleRewards)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const activeKeyRef = useRef('')

  useEffect(() => {
    if (!moduleId || !problemId) return
    activeKeyRef.current = `${moduleId}/${problemId}`
    setSubmitError(null)
    setLoading(true)
    setResult(null)
    setRunResult(null)
    setRunError(null)
    setHintsShown(0)
    Promise.all([getProblem(moduleId, problemId), getSubmissions(moduleId, problemId)])
      .then(([prob, subs]) => {
        setProblem(prob)
        setCode(prob.starter_code)
        setSubmissions(subs)
        setStdin(prob.visible_tests[0]?.stdin ?? '')
        import('@/api/progress').then(({ trackAccess }) => {
          trackAccess(`/modules/${moduleId}/problems/${problemId}`, `Problem: ${prob.title}`).catch(() => {})
        })
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [moduleId, problemId])

  const handleSubmit = useCallback(async () => {
    if (!moduleId || !problemId || !code.trim()) return
    const key = `${moduleId}/${problemId}`
    setSubmitting(true)
    setSubmitError(null)
    setResult(null)
    setRunResult(null)
    setPassedBefore(submissions.some((sub) => sub.status === 'PASS'))
    try {
      const res = await submitCode(moduleId, problemId, code)
      // The XP is real even if the learner has moved to another problem meanwhile ...
      handleRewards(res.rewards)
      // ... but the result and history belong to the problem that was graded.
      if (activeKeyRef.current !== key) return
      setResult(res)
      const subs = await getSubmissions(moduleId, problemId)
      if (activeKeyRef.current === key) setSubmissions(subs)
    } catch (e: unknown) {
      if (activeKeyRef.current !== key) return
      const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      setSubmitError(typeof detail === 'string' ? detail : 'Your code could not be graded. Check your connection and try again.')
    } finally {
      setSubmitting(false)
    }
  }, [moduleId, problemId, code, submissions, handleRewards])

  const handleRun = useCallback(async () => {
    if (!code.trim()) return
    setRunning(true)
    setRunError(null)
    setRunResult(null)
    setResult(null)
    try {
      const input = stdin && !stdin.endsWith('\n') ? stdin + '\n' : stdin
      setRunResult(await runCode(code, input))
    } catch (e: unknown) {
      const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setRunError(detail ?? 'Could not run your code. Is the backend running?')
    } finally {
      setRunning(false)
    }
  }, [code, stdin])

  // Ctrl/Cmd + Enter runs the code from anywhere on the page.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault()
        void handleRun()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [handleRun])

  if (loading) {
    return (
      <div className="p-8 space-y-4" role="status" aria-label="Loading problem">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-10 w-2/3" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!problem) return null

  const statusCfg = result ? STATUS_CONFIG[result.status] : null
  const StatusIcon = statusCfg?.icon
  const reaction = result ? reactionFor(result) : null
  const solved = submissions.some((s) => s.status === 'PASS') || result?.status === 'PASS'
  const needsInput = problem.type === 'program' || /\binput\s*\(/.test(code)

  return (
    <div className="flex flex-col lg:flex-row lg:h-[calc(100vh-var(--nav-h)-3.25rem)] lg:overflow-hidden">
      {/* LEFT: Problem statement */}
      <div className="lg:w-[42%] overflow-y-auto border-r-2 border-border-dark flex flex-col">
        <div className="p-6 flex-1">
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <span className="font-mono font-bold text-sm text-white bg-brand-blue border border-border-dark px-2 py-1">PROBLEM</span>
            <Badge color={DIFFICULTY_COLOR[problem.difficulty] ?? 'green'}>{problem.difficulty}</Badge>
            {solved && (
              <Badge color="green" className="gap-1">
                <Check aria-hidden className="w-3.5 h-3.5" strokeWidth={3} /> Solved
              </Badge>
            )}
            {problem.concepts.map((c) => (
              <Badge key={c} color="purple">{c}</Badge>
            ))}
          </div>
          <h1 className="font-heading font-black text-3xl mb-1">{problem.title}</h1>
          <p className="font-mono text-xs text-text-muted mb-4">{KIND_LABEL[problem.type] ?? KIND_LABEL.function}</p>
          <div className="border-b-4 border-border-dark mb-5" />

          <LessonMarkdown markdown={problem.description} className="mb-6 text-[15px]" />

          {/* Hint ladder */}
          {problem.hints.length > 0 && (
            <div className="mb-6">
              {problem.hints.slice(0, hintsShown).map((hint, i) => (
                <div key={i} className="mb-2 border-2 border-brand-yellow bg-brand-yellow/20 px-4 py-2 font-body text-sm">
                  <span className="font-bold">
                    <Lightbulb aria-hidden className="inline-block w-4 h-4 mr-1 align-[-0.15em] text-brand-orange" />
                    Hint {i + 1}:{' '}
                  </span>
                  <RichText text={hint} />
                </div>
              ))}
              {hintsShown < problem.hints.length && (
                <Button variant="yellow" size="sm" onClick={() => setHintsShown((n) => n + 1)}>
                  <Lightbulb aria-hidden className="w-4 h-4" />
                  {hintsShown === 0 ? 'Need a hint?' : 'Another hint'} ({hintsShown}/{problem.hints.length})
                </Button>
              )}
            </div>
          )}

          <h3 className="font-heading font-bold text-lg mb-3">Sample Test Cases</h3>
          <div className="space-y-3 mb-6">
            {problem.visible_tests.map((test, i) => (
              <div key={i} className="neo-card p-4 bg-bg-base">
                <div className="font-mono text-sm space-y-2">
                  <TestInput test={test} />
                  <div>
                    <span className="text-text-muted">Expected:</span>
                    <pre className="font-bold text-brand-green whitespace-pre-wrap mt-1 mb-0">{test.expected === '' ? '(nothing)' : test.expected}</pre>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Submission history */}
          {submissions.length > 0 && (
            <div>
              <button
                className="font-heading font-bold text-sm text-brand-purple hover:underline mb-3 flex items-center gap-1"
                aria-expanded={showHistory}
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? <ChevronDown aria-hidden className="w-4 h-4" /> : <ChevronRight aria-hidden className="w-4 h-4" />}
                My Submissions ({submissions.length})
              </button>
              {showHistory && (
                <div className="space-y-2">
                  {submissions.map((s) => (
                    <div key={s.id} className="neo-card px-4 py-2 flex items-center justify-between gap-2">
                      <span className="font-mono text-xs text-text-muted">{new Date(s.submitted_at).toLocaleString()}</span>
                      <div className="flex items-center gap-2">
                        <Badge color={s.status === 'PASS' ? 'green' : s.status === 'FAIL' ? 'pink' : 'orange'}>{s.status}</Badge>
                        <button className="font-mono text-xs text-brand-blue hover:underline" onClick={() => setCode(s.code)}>
                          Load
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT: Editor + Results */}
      <div className="lg:w-[58%] flex flex-col min-h-[70vh] lg:min-h-0 lg:h-full">
        <div className="border-b-2 border-border-dark px-4 py-2 bg-bg-dark flex items-center justify-between gap-2 flex-wrap">
          <span className="font-mono text-xs text-white/60 font-bold">Python 3 · Ctrl/Cmd+Enter to run</span>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" loading={running} onClick={() => void handleRun()} disabled={!editorReady} id="run-code-btn">
              <Play aria-hidden className="w-4 h-4" /> Run
            </Button>
            <Button variant="yellow" size="sm" loading={submitting} onClick={() => void handleSubmit()} id="submit-code-btn" disabled={!editorReady}>
              {submitting ? (
                'Grading…'
              ) : (
                <>
                  <Send aria-hidden className="w-4 h-4" /> Submit
                </>
              )}
            </Button>
          </div>
        </div>

        <div className="flex-1 min-h-[280px]">
          <Editor
            height="100%"
            defaultLanguage="python"
            value={code}
            onChange={(v) => setCode(v ?? '')}
            onMount={() => setEditorReady(true)}
            theme="vs-dark"
            options={{
              fontSize: 14,
              fontFamily: '"Space Mono", monospace',
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              lineNumbers: 'on',
              renderLineHighlight: 'all',
              padding: { top: 16, bottom: 16 },
              tabSize: 4,
            }}
          />
        </div>

        {submitError && (
          <p role="alert" className="border-t-2 border-border-dark bg-brand-pink/15 px-4 py-2 font-body text-sm">
            {submitError}
          </p>
        )}

        {/* Input for Run */}
        {needsInput && (
          <div className="border-t-2 border-border-dark bg-bg-dark px-4 py-2">
            <label htmlFor="run-stdin" className="font-mono text-[11px] font-bold text-brand-yellow block mb-1">
              INPUT for Run (one line per input() call)
            </label>
            <textarea
              id="run-stdin"
              value={stdin}
              onChange={(e) => setStdin(e.target.value)}
              rows={Math.min(4, Math.max(1, stdin.split('\n').length))}
              spellCheck={false}
              className="w-full bg-white/10 text-white font-mono text-sm px-2 py-1 border border-white/20 outline-none"
            />
          </div>
        )}

        {/* Quick-run output */}
        {(runResult || runError) && (
          <div className="border-t-2 border-border-dark max-h-64 overflow-y-auto bg-[#0B2A1E] animate-slide-up" role="status">
            <div className="px-4 py-1 font-mono text-[11px] font-bold text-brand-green border-b border-brand-green/30 flex items-center gap-1.5">
              <Terminal aria-hidden className="w-3.5 h-3.5" /> OUTPUT (not graded)
            </div>
            <div className="p-4 space-y-2">
              {runError && <div className="font-mono text-sm text-brand-pink">{runError}</div>}
              {runResult?.timed_out && (
                <div className="font-mono text-sm text-brand-yellow flex items-center gap-1.5">
                  <Timer aria-hidden className="w-4 h-4 shrink-0" /> Stopped: ran for too long.
                </div>
              )}
              {runResult?.stdout && <pre className="font-mono text-sm text-[#B8F5D5] whitespace-pre-wrap m-0">{runResult.stdout}</pre>}
              {runResult?.stderr && <pre className="font-mono text-sm text-brand-pink whitespace-pre-wrap m-0">{runResult.stderr}</pre>}
              {runResult && !runResult.stdout && !runResult.stderr && !runResult.timed_out && (
                <div className="font-mono text-sm text-white/50">(no output. For function problems, use Submit to run the tests)</div>
              )}
              {runResult && runResult.stderr && (
                <Mascot mood={moodForError(runResult.stderr, runResult.timed_out).mood} size={52} message={moodForError(runResult.stderr).message} />
              )}
            </div>
          </div>
        )}

        {/* Graded results */}
        {result && statusCfg && StatusIcon && reaction && (
          <div className="border-t-2 border-border-dark max-h-96 overflow-y-auto animate-slide-up" role="status">
            <div className={`px-5 py-3 flex items-center justify-between gap-2 flex-wrap ${statusCfg.bg}`}>
              <span className="font-heading font-bold text-lg inline-flex items-center gap-2">
                <StatusIcon aria-hidden className="w-5 h-5 shrink-0" strokeWidth={2.5} />
                {statusCfg.label}
              </span>
              <span className="font-mono font-bold">
                {result.passed_count}/{result.total_count} tests passed
              </span>
            </div>

            <div className="p-4 space-y-3 bg-bg-dark text-white">
              <Mascot mood={reaction.mood} size={72} message={reaction.message} />

              {result.rewards && (
                <XPLine
                  rewards={result.rewards}
                  passed={result.status === 'PASS'}
                  alreadySolved={passedBefore}
                  earnsXp={moduleEarnsXp(moduleId)}
                />
              )}

              {result.test_results.map((t) => (
                <div
                  key={t.test_index}
                  className={`px-3 py-2 border ${t.passed ? 'border-brand-green bg-brand-green/10' : 'border-brand-pink bg-brand-pink/10'}`}
                >
                  <span className={`font-mono font-bold text-sm inline-flex items-center gap-1.5 ${t.passed ? 'text-brand-green' : 'text-brand-pink'}`}>
                    {t.passed ? (
                      <Check aria-hidden className="w-4 h-4 shrink-0" strokeWidth={3} />
                    ) : (
                      <X aria-hidden className="w-4 h-4 shrink-0" strokeWidth={3} />
                    )}
                    <span className="sr-only">{t.passed ? 'Passed:' : 'Failed:'}</span>
                    Test {t.test_index + 1}
                    {t.is_hidden ? ' (hidden)' : ''}
                  </span>
                  {!t.passed && !t.is_hidden && (
                    <div className="grid sm:grid-cols-2 gap-2 mt-2 font-mono text-xs">
                      <div>
                        <div className="text-white/50">expected</div>
                        <pre className="text-brand-green whitespace-pre-wrap m-0">{t.expected || '(nothing)'}</pre>
                      </div>
                      <div>
                        <div className="text-white/50">got</div>
                        <pre className="text-brand-pink whitespace-pre-wrap m-0">{t.actual || '(nothing)'}</pre>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {result.stderr && (
                <div className="p-3 border border-brand-pink/40 bg-brand-pink/10">
                  <span className="font-mono text-xs text-brand-pink block mb-1">error</span>
                  <pre className="font-mono text-xs text-brand-pink whitespace-pre-wrap m-0">{result.stderr}</pre>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
