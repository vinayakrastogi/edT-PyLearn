import React, { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BadgeCheck, ChartColumn, Check, Dumbbell, Flame, Inbox, Rocket, Sparkles, Trash } from 'lucide-react'
import { Button } from '@/components/Button'
import { IconTile } from '@/lib/icons'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'
import { ProgressBar } from '@/components/ProgressBar'
import { Skeleton } from '@/components/Skeleton'
import { SocialShare } from '@/components/SocialShare'
import { JourneyCard } from '@/components/gamification/JourneyCard'
import { LeaderboardCard } from '@/components/gamification/LeaderboardCard'
import { useAuthStore } from '@/store/authStore'
import { useGamificationStore } from '@/store/gamificationStore'
import { trackActivity } from '@/store/progressRemindersStore'
import { listModules, deleteModule } from '@/api/modules'
import { getDashboard } from '@/api/progress'
import type { ModuleMeta } from '@/types/module'
import type { ModuleProgressSummary, DashboardData } from '@/types/problem'

const ACCENT_CYCLE = ['yellow', 'blue', 'pink', 'green', 'purple', 'orange'] as const

const QUOTES = [
  "“The beautiful thing about learning is that no one can take it away from you.” — B.B. King",
  "“First, solve the problem. Then, write the code.” — John Johnson",
  "“Experience is the name everyone gives to their mistakes.” — Oscar Wilde",
  "“Code is like humor. When you have to explain it, it’s bad.” — Cory House",
  "“Make it work, make it right, make it fast.” — Kent Beck",
  "“Anyone who has never made a mistake has never tried anything new.” — Albert Einstein",
]

/** Placeholder with the same footprint as the JourneyCard while the gamification summary loads. */
const JourneySkeleton: React.FC = () => (
  <div role="status" aria-label="Loading your progress" className="neo-card p-6 border-t-4 border-t-brand-yellow">
    <Skeleton className="h-8 w-48 mb-5" />
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <Skeleton className="lg:col-span-5 h-28" />
      <Skeleton className="lg:col-span-4 h-28" />
      <Skeleton className="lg:col-span-3 h-28" />
    </div>
    <Skeleton className="h-20 w-full mt-6" />
  </div>
)

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore()
  const gamification = useGamificationStore((s) => s.summary)
  const refreshGamification = useGamificationStore((s) => s.refresh)
  const [modules, setModules] = useState<ModuleMeta[]>([])
  const [progress, setProgress] = useState<Record<string, ModuleProgressSummary>>({})
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  // True once the first gamification request has settled (so a failure can fall back to the old streak chip).
  const [gamificationTried, setGamificationTried] = useState(gamification !== null)

  const randomQuote = useMemo(() => QUOTES[Math.floor(Math.random() * QUOTES.length)], [])

  useEffect(() => {
    // Track activity for reminders
    trackActivity()
    
    // Load modules and dashboard separately - don't let dashboard errors block modules
    const loadData = async () => {
      try {
        const mods = await listModules()
        setModules(mods)
      } catch (error) {
        console.error('Failed to load modules:', error)
      }
      
      try {
        const dash = await getDashboard()
        setDashboardData(dash)
        const prog: Record<string, ModuleProgressSummary> = {}
        for (const p of dash.modules) prog[p.module_id] = p
        setProgress(prog)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      }
      
      setLoading(false)
    }
    
    loadData()
  }, [])

  useEffect(() => {
    let alive = true
    void refreshGamification().finally(() => {
      if (alive) setGamificationTried(true)
    })
    return () => {
      alive = false
    }
  }, [refreshGamification])

  const streakCount = gamification?.streak.count ?? dashboardData?.streak_count ?? 0
  const hasMastery = !!dashboardData && dashboardData.mastery_stats.length > 0

  const handleDeleteModule = async (moduleId: string) => {
    if (!window.confirm("Are you sure you want to delete this AI-generated module?")) return
    try {
      await deleteModule(moduleId)
      setModules(modules.filter((m) => m.id !== moduleId))
    } catch (error) {
      console.error("Failed to delete module:", error)
      alert("Failed to delete module.")
    }
  }

  return (
    <div className="min-h-screen bg-bg-base">
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="mb-10">
          <div>
            <h1 className="font-heading font-black text-4xl md:text-5xl text-text-primary mb-3">
              Hello, <span className="text-brand-blue">{user?.full_name}</span>
            </h1>
            <p className="text-text-muted font-mono text-sm max-w-2xl border-l-4 border-brand-yellow pl-4 py-1 italic bg-brand-yellow/10">
              {randomQuote}
            </p>
          </div>

          {gamification ? (
            <div className="mt-6">
              <JourneyCard summary={gamification} />
              {streakCount > 0 && (
                <div className="mt-4">
                  <SocialShare
                    title="My PyLearn Streak"
                    text={`I'm on a ${streakCount}-day learning streak on PyLearn!`}
                  />
                </div>
              )}
            </div>
          ) : !gamificationTried ? (
            <div className="mt-6">
              <JourneySkeleton />
            </div>
          ) : (
            /* The gamification service did not answer: keep the plain streak chip from the dashboard data. */
            dashboardData && dashboardData.streak_count > 0 && (
              <div className="flex flex-col md:flex-row items-center gap-3 mt-6">
                <div className="bg-brand-orange text-white px-4 py-2 border-2 border-border-dark shadow-neo-sm flex items-center gap-2 transform rotate-1">
                  <Flame aria-hidden className="w-7 h-7" strokeWidth={2.25} />
                  <div>
                    <div className="font-heading font-black text-xl leading-none">{dashboardData.streak_count} Day</div>
                    <div className="font-mono text-xs uppercase tracking-wider opacity-90">Learning Streak</div>
                  </div>
                </div>
                <SocialShare
                  title="My PyLearn Streak"
                  text={`I'm on a ${dashboardData.streak_count}-day learning streak on PyLearn!`}
                />
              </div>
            )
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-16 h-16 border-4 border-border-dark border-t-brand-yellow rounded-full animate-spin" />
          </div>
        ) : (
          <div className="space-y-8 animate-bounce-in">
            {/* Top Cards: Progress & Continue Learning */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Progress Card */}
              <Card accent="purple" className="flex flex-col h-full">
                <div className="flex items-center gap-3 mb-6 border-b-2 border-border-dark pb-3">
                  <IconTile icon={ChartColumn} color="purple" size="sm" />
                  <h2 className="font-heading font-bold text-2xl">Overall Progress</h2>
                </div>
                
                {modules.length === 0 ? (
                  <div className="text-text-muted font-mono text-sm">No modules available.</div>
                ) : (
                  <div className="space-y-5 overflow-y-auto max-h-[300px] pr-2 custom-scrollbar flex-1">
                    {modules.map((mod) => {
                      const pct = progress[mod.id]?.completion_percentage ?? 0
                      return (
                        <div key={mod.id}>
                          <div className="flex justify-between items-center mb-1">
                            <span className="font-body text-sm font-bold truncate pr-4">{mod.title}</span>
                            <span className="font-mono text-xs text-text-muted">{pct}%</span>
                          </div>
                          <ProgressBar value={pct} color={pct === 100 ? 'green' : 'blue'} size="sm" showPercent={false} />
                        </div>
                      )
                    })}
                  </div>
                )}
              </Card>

              {/* Continue Learning Card */}
              <Card accent="green" className="flex flex-col h-full justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-6 border-b-2 border-border-dark pb-3">
                    <IconTile icon={Rocket} color="green" size="sm" />
                    <h2 className="font-heading font-bold text-2xl">Continue Learning</h2>
                  </div>
                  
                  {user?.last_accessed_path ? (
                    <div className="mb-6">
                      <p className="text-text-muted font-mono text-sm mb-2">Last visited:</p>
                      <h3 className="font-heading font-bold text-xl mb-4 bg-brand-green/10 border-l-4 border-brand-green pl-3 py-2">
                        {user.last_accessed_title || "Your last lesson"}
                      </h3>
                    </div>
                  ) : (
                    <div className="mb-6">
                      <p className="text-text-muted font-body">
                        You haven't started any lessons yet. Dive into your first module to begin tracking your progress!
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-auto">
                  {user?.last_accessed_path ? (
                    <Link to={user.last_accessed_path}>
                      <Button variant="success" size="lg" className="w-full text-lg shadow-neo-sm hover:-translate-y-1 hover:shadow-neo transition-all" id="continue-learning-btn">
                        Jump Back In <ArrowRight aria-hidden className="w-5 h-5" />
                      </Button>
                    </Link>
                  ) : modules.length > 0 ? (
                    <Link to={`/modules/${modules[0].id}`}>
                      <Button variant="yellow" size="lg" className="w-full text-lg shadow-neo-sm hover:-translate-y-1 hover:shadow-neo transition-all">
                        Start First Module <ArrowRight aria-hidden className="w-5 h-5" />
                      </Button>
                    </Link>
                  ) : null}
                </div>
              </Card>
            </div>

            {/* Modules Section */}
            <div>
              <div className="flex items-center gap-3 mb-6 mt-4">
                <span className="font-mono font-bold text-sm text-white bg-brand-pink border border-border-dark px-3 py-1 shadow-neo-sm">
                  COURSE CONTENT
                </span>
                <div className="flex-1 h-0.5 bg-border-dark"></div>
              </div>

              {modules.length === 0 ? (
                <div className="neo-card p-16 text-center bg-bg-card">
                  <Inbox aria-hidden className="w-12 h-12 mx-auto mb-4 text-text-muted" />
                  <p className="font-heading font-bold text-xl">No modules yet.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {modules.map((mod, i) => {
                    const p = progress[mod.id]
                    const pct = p?.completion_percentage ?? 0
                    const accent = ACCENT_CYCLE[i % ACCENT_CYCLE.length]

                    return (
                      <Card key={mod.id} accent={accent} hoverable className="flex flex-col h-full">
                        <div className="flex items-start justify-between mb-4">
                          <IconTile name={mod.icon} color={accent} size="lg" />
                          {pct === 100 ? (
                            <Badge color="green" className="gap-1">
                              <Check aria-hidden className="w-3.5 h-3.5" strokeWidth={3} /> DONE
                            </Badge>
                          ) : pct > 0 ? (
                            <Badge color="blue">IN PROGRESS</Badge>
                          ) : null}
                        </div>

                        <h3 className="font-heading font-bold text-lg mb-2 line-clamp-1">{mod.title}</h3>
                        <p className="text-text-muted font-body text-xs mb-4 line-clamp-2 flex-1">
                          {mod.description}
                        </p>

                        {/* Delete button for generated modules */}
                        {mod.id.startsWith("generated-") && user?.role === "faculty" && (
                          <div className="mb-4">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="text-brand-pink border-2 border-brand-pink hover:bg-brand-pink hover:text-white w-full"
                              onClick={() => handleDeleteModule(mod.id)}
                            >
                              <Trash aria-hidden className="w-4 h-4" /> Delete
                            </Button>
                          </div>
                        )}
                        
                        {/* Progress Bar - Only show for non-generative modules */}
                        {!mod.is_generative && (
                          <>
                            <ProgressBar value={pct} color={accent} size="sm" showPercent={false} />
                            <div className="mt-1 mb-5 flex justify-between">
                              <span className="font-mono text-xs text-text-muted">{pct}% Complete</span>
                              <span className="font-mono text-xs text-text-muted">{p?.docs_read ?? 0}/{mod.doc_count} Lessons</span>
                            </div>
                          </>
                        )}

                        {/* Generative module indicator */}
                        {mod.is_generative && (
                          <div className="mb-5">
                            <div className="bg-brand-purple/20 border-2 border-brand-purple px-3 py-2 text-center">
                              <span className="inline-flex items-center gap-1.5 font-mono text-xs font-bold text-brand-purple">
                                <Sparkles aria-hidden className="w-3.5 h-3.5" /> AI Content Generator
                              </span>
                            </div>
                          </div>
                        )}
                        
                        <Link to={`/modules/${mod.id}`} className="flex-1">
                          <Button variant="primary" size="sm" className="w-full" id={`enter-module-${mod.id}`}>
                            {pct > 0 ? 'Continue' : 'Start'} <ArrowRight aria-hidden className="w-4 h-4" />
                          </Button>
                        </Link>
                      </Card>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Concept Mastery Section, with the weekly leaderboard next to it */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
              {hasMastery && dashboardData && (
                <div className="lg:col-span-2">
                  <div className="flex items-center gap-3 mb-6 mt-8">
                    <span className="font-mono font-bold text-sm text-white bg-brand-orange border border-border-dark px-3 py-1 shadow-neo-sm">
                      CONCEPT MASTERY
                    </span>
                    <div className="flex-1 h-0.5 bg-border-dark"></div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Well Known Concepts */}
                    <Card accent="green">
                      <div className="flex items-center gap-2 mb-4">
                        <BadgeCheck aria-hidden className="w-6 h-6 text-brand-green" strokeWidth={2.25} />
                        <h3 className="font-heading font-bold text-lg">Well Known Concepts</h3>
                      </div>
                      <div className="space-y-4">
                        {dashboardData.mastery_stats.slice(0, 3).map((stat) => (
                          <div key={stat.concept}>
                            <div className="flex justify-between items-center mb-1">
                              <span className="font-body text-sm font-bold capitalize">{stat.concept.replace('-', ' ')}</span>
                              <span className="font-mono text-xs font-bold text-brand-green">{stat.percentage}%</span>
                            </div>
                            <ProgressBar value={stat.percentage} color="green" size="sm" showPercent={false} />
                          </div>
                        ))}
                      </div>
                    </Card>

                    {/* Weak Concepts */}
                    <Card accent="pink">
                      <div className="flex items-center gap-2 mb-4">
                        <Dumbbell aria-hidden className="w-6 h-6 text-brand-pink" strokeWidth={2.25} />
                        <h3 className="font-heading font-bold text-lg">Concepts to Review</h3>
                      </div>
                      <div className="space-y-4">
                        {(() => {
                          const weak = [...dashboardData.mastery_stats].reverse().slice(0, 3)
                          if (weak.every(s => s.percentage === 100)) {
                            return (
                              <p className="text-text-muted font-mono text-sm py-4">You're doing great! No weak concepts right now.</p>
                            )
                          }
                          return weak.map((stat) => (
                            <div key={stat.concept}>
                              <div className="flex justify-between items-center mb-1">
                                <span className="font-body text-sm font-bold capitalize">{stat.concept.replace('-', ' ')}</span>
                                <span className="font-mono text-xs font-bold text-brand-pink">{stat.percentage}%</span>
                              </div>
                              <ProgressBar value={stat.percentage} color={stat.percentage < 50 ? 'pink' : 'yellow'} size="sm" showPercent={false} />
                            </div>
                          ))
                        })()}
                      </div>
                    </Card>
                  </div>
                </div>
              )}

              <div className={hasMastery ? '' : 'lg:col-span-3 max-w-2xl'}>
                <div className="flex items-center gap-3 mb-6 mt-8">
                  <span className="font-mono font-bold text-sm text-white bg-brand-purple border border-border-dark px-3 py-1 shadow-neo-sm">
                    LEADERBOARD
                  </span>
                  <div className="flex-1 h-0.5 bg-border-dark"></div>
                </div>
                <LeaderboardCard />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
