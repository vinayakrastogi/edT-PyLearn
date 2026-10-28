import React, { useEffect, useState } from 'react'
import { Link, useParams, useNavigate, useLocation, Outlet } from 'react-router-dom'
import { ArrowLeft, BookOpen, Brain, CodeXml, Menu } from 'lucide-react'
import { Badge } from '@/components/Badge'
import { ProgressBar } from '@/components/ProgressBar'
import { getModule } from '@/api/modules'
import { getModuleProgress } from '@/api/progress'
import type { ModuleDetail } from '@/types/module'
import type { ModuleProgressSummary } from '@/types/problem'
import { Skeleton } from '@/components/Skeleton'
import { Mascot } from '@/components/Mascot'
import { useAuthStore } from '@/store/authStore'
import { IconTile } from '@/lib/icons'
import { GenerativeUploadUI } from './GenerativeUploadUI'

export const ModulePage: React.FC = () => {
  const { moduleId } = useParams<{ moduleId: string }>()
  const navigate = useNavigate()
  const [module, setModule] = useState<ModuleDetail | null>(null)
  const [progress, setProgress] = useState<ModuleProgressSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const user = useAuthStore((st) => st.user)

  // Close the mobile lesson list after navigating, and keep the active item visible.
  useEffect(() => {
    setSidebarOpen(false)
    requestAnimationFrame(() => {
      document.querySelector('[aria-current="page"]')?.scrollIntoView({ block: 'nearest' })
    })
  }, [location.pathname])

  useEffect(() => {
    if (!moduleId) return
    Promise.all([getModule(moduleId), getModuleProgress(moduleId)])
      .then(([mod, prog]) => {
        setModule(mod)
        setProgress(prog)
        // Auto-navigate to first doc if just entering module root
        if (window.location.pathname === `/modules/${moduleId}` && mod.docs.length > 0 && !mod.is_generative) {
          navigate(`/modules/${moduleId}/docs/${mod.docs[0].id}`, { replace: true })
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [moduleId, navigate])

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-base px-8 py-10 space-y-4" role="status" aria-label="Loading module">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (!module) return null

  const currentPath = location.pathname

  if (module.is_generative) {
    return (
      <div className="min-h-screen bg-bg-base flex flex-col">
        {/* Top bar */}
        <header className="border-b-2 border-border-dark bg-bg-card px-6 py-3 flex items-center justify-between sticky top-[var(--nav-h)] z-20 shadow-neo-sm">
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="inline-flex items-center gap-1.5 font-heading font-bold text-sm hover:text-brand-blue transition-colors">
              <ArrowLeft aria-hidden className="w-4 h-4" /> Dashboard
            </Link>
            <span className="text-text-muted">|</span>
            <span className="font-heading font-bold text-sm">{module.title}</span>
          </div>
        </header>
        {user?.role === 'faculty' ? (
          <GenerativeUploadUI />
        ) : (
          <div className="max-w-xl mx-auto px-6 py-16">
            <Mascot
              mood="thinking"
              message="The AI module generator is for teachers (faculty accounts). Ask your teacher to create a module for your class!"
            />
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-bg-base flex flex-col">
      {/* Top bar */}
      <header className="border-b-2 border-border-dark bg-bg-card px-6 py-3 flex items-center justify-between sticky top-[var(--nav-h)] z-20 shadow-neo-sm">
        <div className="flex items-center gap-4">
          <button
            type="button"
            className="lg:hidden neo-btn bg-bg-card px-2 py-1 text-sm"
            aria-expanded={sidebarOpen}
            aria-controls="module-sidebar"
            onClick={() => setSidebarOpen((v) => !v)}
          >
            <Menu aria-hidden className="w-4 h-4" /> Contents
          </button>
          <Link to="/dashboard" className="inline-flex items-center gap-1.5 font-heading font-bold text-sm hover:text-brand-blue transition-colors">
            <ArrowLeft aria-hidden className="w-4 h-4" /> Dashboard
          </Link>
          <span className="text-text-muted">|</span>
          <span className="font-heading font-bold text-sm">{module.title}</span>
        </div>
        {progress && (
          <div className="hidden sm:block min-w-[200px]">
            <ProgressBar value={progress.completion_percentage} color="green" size="sm" label="Module Progress" />
          </div>
        )}
      </header>

      <div className="flex flex-1 items-start">
        {/* Sidebar: slides over the content on small screens, sticks beside it on large ones */}
        <aside
          id="module-sidebar"
          className={`${sidebarOpen ? 'flex' : 'hidden'} lg:flex w-72 border-r-2 border-border-dark bg-bg-card flex-col overflow-y-auto shrink-0
                      fixed lg:sticky left-0 z-30 shadow-neo-lg lg:shadow-none
                      top-[calc(var(--nav-h)+3.25rem)] lg:top-[calc(var(--nav-h)+3.25rem)]
                      h-[calc(100vh-var(--nav-h)-3.25rem)]`}
        >
          {/* Module title block */}
          <div className="p-5 border-b-2 border-border-dark">
            <IconTile name={module.icon} size="md" className="mb-3" />
            <h2 className="font-heading font-bold text-base leading-tight">{module.title}</h2>
          </div>

          {/* Docs */}
          {module.docs.length > 0 && (
            <div>
              <div className="px-4 py-2 bg-brand-yellow border-b-2 border-border-dark">
                <span className="inline-flex items-center gap-1.5 font-mono font-bold text-xs">
                  <BookOpen aria-hidden className="w-3.5 h-3.5" /> LESSONS
                </span>
              </div>
              {module.docs.map((doc) => {
                const active = currentPath.includes(`/docs/${doc.id}`)
                const completed = progress?.viewed_docs?.includes(doc.id)
                return (
                  <Link
                    key={doc.id}
                    to={`/modules/${moduleId}/docs/${doc.id}`}
                    aria-current={active ? 'page' : undefined}
                    className={`relative flex items-center gap-3 px-4 py-3 border-b border-border-dark/20 font-body text-sm transition-colors ${
                      active
                        ? 'bg-brand-yellow border-l-4 border-l-border-dark font-bold'
                        : 'hover:bg-brand-yellow/20'
                    }`}
                  >
                    {completed && !active && (
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-green border-r border-border-dark" />
                    )}
                    {completed && active && (
                      <div className="absolute left-1 top-1 bottom-1 w-1 bg-brand-green" />
                    )}
                    <span className={`font-mono text-xs text-text-muted ${completed && !active ? 'ml-1' : ''}`}>
                      {String(doc.order).padStart(2, '0')}
                    </span>
                    <span className="flex-1">{doc.title}</span>
                  </Link>
                )
              })}
            </div>
          )}

          {/* Quiz */}
          {module.quiz_id && (
            <div>
              <div className="px-4 py-2 bg-brand-pink border-b-2 border-border-dark">
                <span className="inline-flex items-center gap-1.5 font-mono font-bold text-xs text-white">
                  <Brain aria-hidden className="w-3.5 h-3.5" /> QUIZ
                </span>
              </div>
              <Link
                to={`/modules/${moduleId}/quiz`}
                className={`relative flex items-center gap-3 px-4 py-3 border-b border-border-dark/20 font-body text-sm transition-colors ${
                  currentPath.includes('/quiz')
                    ? 'bg-brand-pink/20 border-l-4 border-l-border-dark font-bold'
                    : 'hover:bg-brand-pink/10'
                }`}
              >
                {progress && progress.quiz_attempts > 0 && !currentPath.includes('/quiz') && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-green border-r border-border-dark" />
                )}
                {progress && progress.quiz_attempts > 0 && currentPath.includes('/quiz') && (
                  <div className="absolute left-1 top-1 bottom-1 w-1 bg-brand-green" />
                )}
                <span className={`flex-1 ${progress && progress.quiz_attempts > 0 && !currentPath.includes('/quiz') ? 'ml-1' : ''}`}>Module Quiz</span>
                {progress && progress.quiz_attempts > 0 && (
                  <Badge color="green" className="text-xs">
                    {progress.quiz_attempts}x
                  </Badge>
                )}
              </Link>
            </div>
          )}

          {/* Problems */}
          {module.problems.length > 0 && (
            <div>
              <div className="px-4 py-2 bg-brand-blue border-b-2 border-border-dark">
                <span className="inline-flex items-center gap-1.5 font-mono font-bold text-xs text-white">
                  <CodeXml aria-hidden className="w-3.5 h-3.5" /> CODING
                </span>
              </div>
              {module.problems.map((prob) => {
                const active = currentPath.includes(`/problems/${prob.id}`)
                const completed = progress?.passed_problems?.includes(prob.id)
                return (
                  <Link
                    key={prob.id}
                    to={`/modules/${moduleId}/problems/${prob.id}`}
                    aria-current={active ? 'page' : undefined}
                    className={`relative flex items-center gap-3 px-4 py-3 border-b border-border-dark/20 font-body text-sm transition-colors ${
                      active
                        ? 'bg-brand-blue/10 border-l-4 border-l-border-dark font-bold'
                        : 'hover:bg-brand-blue/10'
                    }`}
                  >
                    {completed && !active && (
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-brand-green border-r border-border-dark" />
                    )}
                    {completed && active && (
                      <div className="absolute left-1 top-1 bottom-1 w-1 bg-brand-green" />
                    )}
                    <span className={`flex-1 ${completed && !active ? 'ml-1' : ''}`}>{prob.title}</span>
                  </Link>
                )
              })}
            </div>
          )}

          {/* Bottom padding */}
          <div className="flex-1" />
        </aside>

        {/* Main content area */}
        <main className="flex-1 min-w-0">
          <Outlet context={{ module, progress, setProgress }} />
        </main>
      </div>
    </div>
  )
}
