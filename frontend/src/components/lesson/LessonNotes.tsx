import { useEffect, useState } from 'react'
import axios from 'axios'
import { NotebookPen, Trash2 } from 'lucide-react'
import { Button } from '@/components/Button'
import { createLessonNote, deleteLessonNote, listLessonNotes } from '@/api/notes'
import type { LessonNote } from '@/api/notes'

function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error) && typeof error.response?.data?.detail === 'string') {
    return error.response.data.detail
  }
  return 'Could not reach your notes. Check your connection and try again.'
}

// crypto.randomUUID is unavailable on plain HTTP LAN addresses in many browsers.
function requestId(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  bytes[6] = (bytes[6] & 15) | 64
  bytes[8] = (bytes[8] & 63) | 128
  const hex = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
}

export function LessonNotes({ moduleId, docId }: { moduleId: string; docId: string }) {
  const [notes, setNotes] = useState<LessonNote[]>([])
  const [draft, setDraft] = useState('')
  const [pendingId, setPendingId] = useState(requestId)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  useEffect(() => {
    let active = true
    listLessonNotes(moduleId, docId)
      .then((items) => { if (active) setNotes(items) })
      .catch((err) => { if (active) setError(errorMessage(err)) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [moduleId, docId])

  const refresh = async () => {
    setLoading(true)
    setError('')
    try { setNotes(await listLessonNotes(moduleId, docId)) }
    catch (err) { setError(errorMessage(err)) }
    finally { setLoading(false) }
  }

  const save = async () => {
    if (!draft.trim() || busy) return
    setBusy(true)
    setError('')
    setNotice('')
    try {
      const note = await createLessonNote(moduleId, docId, draft.trim(), pendingId)
      setNotes((items) => [note, ...items.filter((item) => item.id !== note.id)].slice(0, 100))
      setDraft('')
      setPendingId(requestId())
      setNotice('Saved to LifeAdmin.')
    } catch (err) { setError(errorMessage(err)) }
    finally { setBusy(false) }
  }

  const remove = async (noteId: string) => {
    setBusy(true)
    setError('')
    setNotice('')
    try {
      await deleteLessonNote(noteId)
      setNotes((items) => items.filter((item) => item.id !== noteId))
      setNotice('Note deleted.')
    } catch (err) { setError(errorMessage(err)) }
    finally { setBusy(false) }
  }

  return (
    <section aria-labelledby="lesson-notes-title" className="neo-card p-5 mt-10 bg-brand-yellow/10">
      <h2 id="lesson-notes-title" className="font-heading font-bold text-xl flex items-center gap-2">
        <NotebookPen aria-hidden className="w-5 h-5" /> My lesson notes
      </h2>
      <p className="text-sm text-text-muted my-3">Write down what you learned. Your notes are saved in LifeAdmin.</p>
      <form onSubmit={(event) => { event.preventDefault(); void save() }}>
        <label htmlFor="lesson-note" className="font-bold text-sm">New note</label>
        <textarea id="lesson-note" value={draft} maxLength={20000} rows={4} disabled={busy}
          onChange={(event) => { setDraft(event.target.value); setPendingId(requestId()); setNotice('') }}
          placeholder="What would you like to remember?"
          className="block w-full border-2 border-border-dark bg-bg-card p-3 my-2 font-body" />
        <div className="flex gap-3 flex-wrap">
          <Button type="submit" size="sm" loading={busy} disabled={!draft.trim() || loading}>Save note</Button>
          <Button type="button" variant="secondary" size="sm" disabled={busy || loading} onClick={() => void refresh()}>Refresh notes</Button>
        </div>
      </form>
      {error && <p role="alert" className="text-sm font-bold mt-3">{error}</p>}
      {notice && <p role="status" className="text-sm font-bold mt-3">{notice}</p>}
      {loading ? <p role="status" className="text-sm mt-4">Loading notes...</p> : (
        <div className="space-y-3 mt-5">
          {notes.length === 0 && !error && <p className="text-sm text-text-muted">No notes for this lesson yet.</p>}
          {notes.map((note) => (
            <article key={note.id} className="border-2 border-border-dark bg-bg-card p-3">
              <p className="whitespace-pre-wrap break-words text-sm">{note.content}</p>
              <div className="flex items-center justify-between gap-3 mt-3">
                <time dateTime={note.created_at} className="text-xs text-text-muted">{new Date(note.created_at).toLocaleString()}</time>
                <Button type="button" size="sm" variant="ghost" disabled={busy} aria-label="Delete note" onClick={() => void remove(note.id)}>
                  <Trash2 aria-hidden className="w-4 h-4" /> Delete
                </Button>
              </div>
            </article>
          ))}
          {notes.length === 100 && <p className="text-xs text-text-muted">Showing the latest 100 notes for this lesson.</p>}
        </div>
      )}
    </section>
  )
}
