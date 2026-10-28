import React, { lazy, Suspense, useEffect, useRef } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useGamificationStore } from '@/store/gamificationStore'
import { initializeReminders } from '@/store/progressRemindersStore'
import { Navbar } from '@/components/Navbar'
import { RewardHost } from '@/components/gamification/RewardHost'
import { LandingPage } from '@/pages/LandingPage'
import { LoginPage } from '@/pages/LoginPage'
import { SignupPage } from '@/pages/SignupPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ModulePage } from '@/pages/ModulePage'
import { DocPage } from '@/pages/DocPage'
import { QuizPage } from '@/pages/QuizPage'
// The code editor (Monaco) is large, so the problem page is loaded on demand.
const ProblemPage = lazy(() => import('@/pages/ProblemPage').then((m) => ({ default: m.ProblemPage })))
import { SettingsPage } from '@/pages/SettingsPage'
import { AchievementsPage } from '@/pages/AchievementsPage'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, initialized } = useAuthStore()
  if (!initialized) {
    return (
      <div className="min-h-screen bg-bg-base flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-border-dark border-t-brand-yellow rounded-full animate-spin" />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

const App: React.FC = () => {
  const initAuth = useAuthStore((s) => s.initAuth)
  const userId = useAuthStore((s) => s.user?.id)

  useEffect(() => {
    initAuth()
    // Initialize progress reminders
    initializeReminders()
  }, [initAuth])

  // Load XP, level and streak once signed in. Signing out (or in as someone else) starts clean.
  // The store starts empty, so nothing is reset on the first sign-in: a page that mounted in the same
  // commit has already started its own refresh(), and a reset would orphan it (its result discarded,
  // the page briefly showing its error state while a second request is in flight).
  const previousUserId = useRef<typeof userId>(undefined)
  useEffect(() => {
    const gamification = useGamificationStore.getState()
    if (previousUserId.current !== undefined) gamification.reset()
    previousUserId.current = userId
    if (userId !== undefined) void gamification.refresh()
  }, [userId])

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-courses"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/achievements"
          element={
            <ProtectedRoute>
              <AchievementsPage />
            </ProtectedRoute>
          }
        />

        
        {/* Module routes (nested layout) */}
        <Route
          path="/modules/:moduleId"
          element={
            <ProtectedRoute>
              <ModulePage />
            </ProtectedRoute>
          }
        >
          <Route path="docs/:docId" element={<DocPage />} />
          <Route path="quiz" element={<QuizPage />} />
          <Route
            path="problems/:problemId"
            element={
              <Suspense fallback={<div className="p-8 font-mono text-sm text-text-muted">Loading editor…</div>}>
                <ProblemPage />
              </Suspense>
            }
          />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <RewardHost />
    </BrowserRouter>
  )
}

export default App
