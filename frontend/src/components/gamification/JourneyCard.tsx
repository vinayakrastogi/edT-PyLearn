import React, { useId } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Check, Compass, Snowflake } from 'lucide-react'
import { Card } from '@/components/Card'
import { Mascot } from '@/components/Mascot'
import type { MascotMood } from '@/components/Mascot'
import { BadgeCard } from '@/components/gamification/BadgeCard'
import { DailyGoalRing } from '@/components/gamification/DailyGoalRing'
import { LevelBar } from '@/components/gamification/LevelBar'
import { StreakFlame } from '@/components/gamification/StreakFlame'
import { WeeklyXpChart } from '@/components/gamification/WeeklyXpChart'
import { IconTile } from '@/lib/icons'
import type { GamificationSummary } from '@/types/gamification'

const MAX_LEVEL = 99

/** Pip's nudge for the learner's current situation. Always kind, never shaming. */
function nudgeFor(summary: GamificationSummary): { mood: MascotMood; message: string } {
  const { streak, daily } = summary

  if (streak.at_risk && streak.count >= 1) {
    const streakText = streak.count > 1 ? `your ${streak.count}-day streak` : 'your streak'
    const base = `Do one lesson today to keep ${streakText}!`
    return {
      mood: 'encouraging',
      message: streak.freezes > 0 ? `${base} If today gets busy, a streak freeze has your back.` : base,
    }
  }

  if (daily.goal_met) {
    return {
      mood: 'proud',
      message: `Daily goal complete! You earned ${daily.xp_today} XP today. Anything extra is a bonus.`,
    }
  }

  if (summary.xp_total === 0 && streak.count === 0 && summary.recent_events.length === 0) {
    return {
      mood: 'encouraging',
      message: 'Welcome! Read your first lesson to earn 10 XP and start your journey.',
    }
  }

  if (daily.xp_today > 0) {
    const left = Math.max(0, daily.goal - daily.xp_today)
    return { mood: 'happy', message: `Nice work today! Just ${left} more XP to reach your daily goal.` }
  }

  if (streak.count === 0) {
    return { mood: 'happy', message: 'Every day is a fresh start. Read a lesson to begin a new streak!' }
  }

  return { mood: 'happy', message: 'Ready for today? One lesson is worth 10 XP.' }
}

interface JourneyCardProps {
  summary: GamificationSummary
}

/** The dashboard hero for progress: level, daily goal, streak, weekly XP, recent badges and a Pip nudge. */
export const JourneyCard: React.FC<JourneyCardProps> = ({ summary }) => {
  const headingId = useId()
  const badgesHeadingId = useId()
  const { streak, daily } = summary

  const atMaxLevel = summary.level >= MAX_LEVEL
  const xpToNext = Math.max(0, summary.xp_for_next_level - summary.xp_into_level)
  const weekTotal = summary.weekly.reduce((sum, p) => sum + Math.max(0, p.xp), 0)
  const goalLeft = Math.max(0, daily.goal - daily.xp_today)
  const nudge = nudgeFor(summary)
  const recent = summary.recent_badges.slice(0, 4)

  return (
    <Card accent="yellow">
      <section aria-labelledby={headingId}>
        <div className="flex items-center gap-3 mb-5 border-b-2 border-border-dark pb-3">
          <IconTile icon={Compass} color="blue" size="sm" />
          <h2 id={headingId} className="font-heading font-bold text-2xl">
            Your Journey
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-6">
          {/* Level and XP */}
          <div className="md:col-span-2 lg:col-span-5 flex flex-col justify-center">
            <p className="font-mono text-xs font-bold uppercase tracking-wider text-text-muted">Your title</p>
            <p className="font-heading font-black text-3xl leading-tight mb-3">{summary.level_title}</p>
            <LevelBar
              level={summary.level}
              xpIntoLevel={summary.xp_into_level}
              xpForNextLevel={summary.xp_for_next_level}
              size="lg"
              showNumbers
            />
            <p className="mt-2 font-mono text-sm text-text-muted">
              <span className="font-bold text-text-primary">{summary.xp_total.toLocaleString()} XP</span> total
              {' · '}
              {atMaxLevel ? 'Top level reached!' : `${xpToNext.toLocaleString()} XP to level ${summary.level + 1}`}
            </p>
          </div>

          {/* Daily goal and streak */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            <div className="flex items-center gap-4">
              <DailyGoalRing xpToday={daily.xp_today} goal={daily.goal} size={104} />
              <div className="min-w-0">
                <p className="font-heading font-bold text-lg leading-tight">Daily goal</p>
                <p className="font-mono text-xs text-text-muted">{daily.goal} XP a day</p>
                <p className="mt-1 font-body text-sm font-bold">
                  {daily.goal_met ? (
                    <span className="inline-flex items-center gap-1">
                      <Check aria-hidden className="w-4 h-4 shrink-0" strokeWidth={3} />
                      Goal met!
                    </span>
                  ) : (
                    `${goalLeft} XP to go`
                  )}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 border-t-2 border-border-dark/15 pt-4">
              <StreakFlame
                count={streak.count}
                freezes={streak.freezes}
                atRisk={streak.at_risk}
                active={streak.active_today}
                size="lg"
              />
              <div className="min-w-0">
                <p className="font-heading font-bold text-lg leading-tight">
                  {streak.count > 0 ? 'Day streak' : 'No streak yet'}
                </p>
                <p className="font-mono text-xs text-text-muted">Longest: {streak.longest} {streak.longest === 1 ? 'day' : 'days'}</p>
                <p className="font-body text-xs text-text-muted leading-snug mt-0.5">
                  <Snowflake aria-hidden className="inline-block w-3.5 h-3.5 mr-1 align-[-0.15em] text-brand-blue" strokeWidth={2.5} />
                  A streak freeze saves your streak if you miss a day.
                </p>
              </div>
            </div>
          </div>

          {/* Last 7 days */}
          <div className="lg:col-span-3 flex flex-col">
            <div className="flex items-baseline justify-between gap-2 mb-2">
              <p className="font-heading font-bold text-lg leading-tight">This week</p>
              <p className="font-mono text-xs font-bold text-text-muted">{weekTotal.toLocaleString()} XP</p>
            </div>
            <WeeklyXpChart points={summary.weekly} goal={daily.goal} />
          </div>
        </div>

        {/* Pip */}
        <div className="mt-6 pt-5 border-t-2 border-border-dark/15">
          <Mascot mood={nudge.mood} size={72} message={nudge.message} />
        </div>

        {/* Recent badges */}
        <div className="mt-6 pt-5 border-t-2 border-border-dark/15">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <h3 id={badgesHeadingId} className="font-heading font-bold text-lg">
              Recent badges
              <span className="ml-2 font-mono text-xs font-normal text-text-muted">
                {summary.badges_earned} of {summary.badges_total} earned
              </span>
            </h3>
            <Link
              to="/achievements"
              className="inline-flex items-center gap-1 font-mono text-sm font-bold underline decoration-2 underline-offset-4 hover:bg-brand-yellow/40 px-1"
            >
              View all
              <ArrowRight aria-hidden className="w-4 h-4 shrink-0" strokeWidth={2.5} />
            </Link>
          </div>

          {recent.length === 0 ? (
            <p className="font-body text-sm text-text-muted border-2 border-dashed border-border-dark/30 p-4">
              No badges yet, read your first lesson to earn one!
            </p>
          ) : (
            <ul aria-labelledby={badgesHeadingId} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {recent.map((badge) => (
                <li key={badge.id}>
                  <BadgeCard badge={badge} compact />
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </Card>
  )
}
