import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Check, ChevronRight, Copy, Eye, LoaderCircle, Pencil, Play, RotateCcw, Timer } from 'lucide-react'
import { runCode, type RunResult } from '@/api/run'
import { highlightPython } from '@/lib/pythonHighlight'

interface Props {
  code: string
  language: string
  /** The text after the language on the fence line, e.g. `stdin="Asha|7" no-run`. */
  meta?: string
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    return false
  }
}

const TOOL_BTN = 'inline-flex items-center gap-1 font-mono text-[11px] text-white/60 hover:text-white'
const TOOL_ICON = 'w-3.5 h-3.5'

/** Toolbar "Copy" button that briefly shows "Copied" after a successful copy. */
const CopyButton: React.FC<{ text: string }> = ({ text }) => {
  const [copied, setCopied] = useState(false)
  return (
    <button
      type="button"
      onClick={async () => {
        if (await copyToClipboard(text)) {
          setCopied(true)
          setTimeout(() => setCopied(false), 1500)
        }
      }}
      className={TOOL_BTN}
    >
      {copied ? <Check aria-hidden className={`${TOOL_ICON} text-brand-green`} strokeWidth={3} /> : <Copy aria-hidden className={TOOL_ICON} />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

/** Static "Output" panel that follows a runnable example. */
const OutputPanel: React.FC<{ code: string }> = ({ code }) => (
  <div className="lesson-output border-2 border-t-0 border-border-dark bg-[#0B2A1E] mb-6">
    <div className="px-3 py-1 font-mono text-[11px] font-bold text-brand-green border-b border-brand-green/30 flex items-center gap-2">
      <ChevronRight aria-hidden className={TOOL_ICON} strokeWidth={3} /> OUTPUT
    </div>
    <pre className="px-4 py-3 font-mono text-sm text-[#B8F5D5] overflow-x-auto whitespace-pre-wrap m-0">{code || '(nothing is printed)'}</pre>
  </div>
)

const StaticBlock: React.FC<{ code: string; language: string }> = ({ code, language }) => {
  const label = language === 'bash' || language === 'shell' || language === 'console' ? 'TERMINAL' : language.toUpperCase()
  return (
    <div className="lesson-code border-2 border-border-dark shadow-neo mb-6 bg-bg-dark text-white">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-white/15">
        <span className="font-mono text-[11px] font-bold text-white/60">{label}</span>
        <CopyButton text={code} />
      </div>
      <pre className="p-4 font-mono text-sm overflow-x-auto m-0 whitespace-pre">{code}</pre>
    </div>
  )
}

export const CodeBlock: React.FC<Props> = ({ code, language, meta = '' }) => {
  const original = useMemo(() => code.replace(/\n$/, ''), [code])
  const isTry = language === 'python-try'
  const isPython = language === 'python' || isTry

  const flags = useMemo(
    () => ({
      noRun: /\bno-run\b/.test(meta),
      expectError: /\bexpect-error\b/.test(meta),
      stdin: (/stdin="([^"]*)"/.exec(meta)?.[1] ?? '').split('|').join('\n'),
    }),
    [meta],
  )

  const [text, setText] = useState(original)
  const [editing, setEditing] = useState(isTry)
  const [stdin, setStdin] = useState(flags.stdin)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<RunResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const areaRef = useRef<HTMLTextAreaElement>(null)

  // Reset when navigating to a different lesson.
  useEffect(() => {
    setText(original)
    setStdin(flags.stdin)
    setResult(null)
    setError(null)
    setEditing(isTry)
  }, [original, flags.stdin, isTry])

  if (language === 'output') return <OutputPanel code={original} />
  if (!isPython) return <StaticBlock code={original} language={language || 'text'} />

  const needsInput = /\binput\s*\(/.test(text)
  const canRun = !flags.noRun
  const dirty = text !== original

  const run = async () => {
    if (!canRun || running) return
    setRunning(true)
    setError(null)
    setResult(null)
    try {
      setResult(await runCode(text, needsInput ? (stdin.endsWith('\n') || stdin === '' ? stdin : stdin + '\n') : ''))
    } catch (e: unknown) {
      const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(detail ?? 'Could not reach the code runner. Is the backend running?')
    } finally {
      setRunning(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault()
      void run()
      return
    }
    if (e.key === 'Tab' && !e.shiftKey) {
      e.preventDefault()
      const el = e.currentTarget
      const { selectionStart, selectionEnd } = el
      const next = text.slice(0, selectionStart) + '    ' + text.slice(selectionEnd)
      setText(next)
      requestAnimationFrame(() => {
        el.selectionStart = el.selectionEnd = selectionStart + 4
      })
    }
  }

  const rows = Math.max(3, text.split('\n').length)

  return (
    <div className="lesson-code mb-6">
      <div className="border-2 border-border-dark shadow-neo bg-bg-dark text-white">
        {/* Toolbar */}
        <div className="flex flex-wrap items-center gap-2 px-3 py-1.5 border-b border-white/15">
          <span className="font-mono text-[11px] font-bold text-white/60">PYTHON</span>
          {isTry && <span className="font-mono text-[11px] font-bold bg-brand-yellow text-text-primary px-1.5">TRY IT YOURSELF</span>}
          {flags.expectError && <span className="font-mono text-[11px] font-bold bg-brand-pink text-white px-1.5">RAISES AN ERROR</span>}
          <span className="flex-1" />
          {dirty && (
            <button type="button" onClick={() => { setText(original); setResult(null) }} className={TOOL_BTN}>
              <RotateCcw aria-hidden className={TOOL_ICON} />
              Reset
            </button>
          )}
          {!isTry && canRun && (
            <button type="button" onClick={() => setEditing((v) => !v)} className={TOOL_BTN}>
              {editing ? <Eye aria-hidden className={TOOL_ICON} /> : <Pencil aria-hidden className={TOOL_ICON} />}
              {editing ? 'View' : 'Edit'}
            </button>
          )}
          <CopyButton text={text} />
          {canRun ? (
            <button
              type="button"
              onClick={() => void run()}
              disabled={running}
              title="Run (Ctrl/Cmd + Enter)"
              className="inline-flex items-center gap-1.5 font-mono text-xs font-bold bg-brand-green text-text-primary border-2 border-border-dark px-3 py-0.5 hover:bg-brand-green/80 disabled:opacity-60"
            >
              {running ? (
                <LoaderCircle aria-hidden className={`${TOOL_ICON} animate-spin`} strokeWidth={2.5} />
              ) : (
                <Play aria-hidden className={`${TOOL_ICON} fill-current`} strokeWidth={2.5} />
              )}
              {running ? 'Running…' : 'Run'}
            </button>
          ) : (
            <span className="font-mono text-[11px] text-white/40" title="Needs your own computer (network or a window)">
              not runnable here
            </span>
          )}
        </div>

        {/* Code area */}
        {editing ? (
          <textarea
            ref={areaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKeyDown}
            spellCheck={false}
            rows={rows}
            aria-label="Editable Python code"
            className="block w-full bg-transparent text-white font-mono text-sm p-4 resize-y outline-none focus-visible:bg-white/5 leading-relaxed"
          />
        ) : (
          <pre className="p-4 font-mono text-sm overflow-x-auto m-0 leading-relaxed whitespace-pre">
            <code>{highlightPython(text)}</code>
          </pre>
        )}

        {/* Optional stdin */}
        {canRun && needsInput && (
          <div className="border-t border-white/15 px-3 py-2">
            <label className="font-mono text-[11px] font-bold text-brand-yellow block mb-1">
              INPUT (one line for each input() call)
            </label>
            <textarea
              value={stdin}
              onChange={(e) => setStdin(e.target.value)}
              rows={Math.min(5, Math.max(1, stdin.split('\n').length))}
              spellCheck={false}
              aria-label="Program input"
              className="w-full bg-white/10 text-white font-mono text-sm px-2 py-1 border border-white/20 outline-none"
            />
          </div>
        )}
      </div>

      {/* Run results */}
      {(result || error) && (
        <div className="border-2 border-t-0 border-border-dark bg-[#0B2A1E]" role="status">
          <div className="px-3 py-1 font-mono text-[11px] font-bold text-brand-green border-b border-brand-green/30 flex items-center gap-2">
            <ChevronRight aria-hidden className={TOOL_ICON} strokeWidth={3} /> RESULT
          </div>
          <div className="p-3 space-y-2">
            {error && <div className="font-mono text-sm text-brand-pink">{error}</div>}
            {result?.timed_out && (
              <div className="font-mono text-sm text-brand-yellow flex items-start gap-1.5">
                <Timer aria-hidden className="w-4 h-4 shrink-0 mt-0.5" />
                Stopped: the program ran for too long (maybe an endless loop?).
              </div>
            )}
            {result && result.stdout && <pre className="font-mono text-sm text-[#B8F5D5] whitespace-pre-wrap m-0 overflow-x-auto">{result.stdout}</pre>}
            {result && result.stderr && <pre className="font-mono text-sm text-brand-pink whitespace-pre-wrap m-0 overflow-x-auto">{result.stderr}</pre>}
            {result && !result.stdout && !result.stderr && !result.timed_out && (
              <div className="font-mono text-sm text-white/50">(the program ran and printed nothing)</div>
            )}
            {result?.images.map((src, i) => (
              <img key={i} src={src} alt={`Chart produced by the program (${i + 1})`} className="bg-white border-2 border-border-dark max-w-full" />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
