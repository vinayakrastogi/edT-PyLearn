import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, X } from 'lucide-react'
import { Button } from '@/components/Button'
import { Confetti } from '@/components/Confetti'
import { Mascot, type MascotMood } from '@/components/Mascot'
import { LevelBar } from '@/components/gamification/LevelBar'
import { StreakFlame } from '@/components/gamification/StreakFlame'
import { RarityTag } from '@/components/gamification/RarityTag'
import { RARITY_TILE, type RewardModal } from '@/components/gamification/rewardModels'
import { AppIcon } from '@/lib/icons'
import type { BadgeInfo } from '@/types/gamification'

interface RewardModalBodyProps {
  modal: RewardModal
  /** 0-based position of this dialog in the current sequence. */
  step: number
  total: number
  labelId: string
  descId: string
  reducedMotion: boolean
  /** Primary button: go to the next dialog or finish. */
  onNext: () => void
  /** The close (x) button: dismisses every remaining dialog (Esc, handled by the dialog shell, does the same). */
  onClose: () => void
  /** Leave the sequence entirely, e.g. when following a link. */
  onSkipAll: () => void
}

interface Copy {
  title: string
  mood: MascotMood
  message: string
  confetti: boolean
  done: string
}

const plural = (n: number, one: string, many: string) => (n === 1 ? one : many)

function copyFor(modal: RewardModal): Copy {
  switch (modal.type) {
    case 'level_up':
      return {
        title: `Level ${modal.level}: ${modal.title}`,
        mood: 'celebrating',
        message:
          modal.previousLevel < modal.level - 1
            ? `Wow, you jumped from level ${modal.previousLevel} to level ${modal.level}! Your title is ${modal.title}.`
            : `You reached level ${modal.level}! Your title is ${modal.title}. Keep going!`,
        confetti: true,
        done: 'Keep going!',
      }
    case 'badges':
      return {
        title: modal.badges.length === 1 ? 'New badge unlocked!' : `${modal.badges.length} new badges unlocked!`,
        mood: 'proud',
        message:
          modal.badges.length === 1
            ? 'You earned a new badge. I am so proud of you!'
            : 'A whole bunch of badges at once. You are on a roll!',
        confetti: true,
        done: 'Awesome!',
      }
    case 'streak_milestone':
      return {
        title: `${modal.days}-day streak!`,
        mood: 'happy',
        message:
          `${modal.days} days in a row. That is real dedication!` +
          (modal.bonusXp > 0 ? ` Here is a bonus of ${modal.bonusXp} XP.` : ''),
        confetti: true,
        done: 'Keep it up!',
      }
    case 'used_freeze':
      return {
        title: 'Streak saved!',
        mood: 'thinking',
        message:
          `You missed a day, but a streak freeze kept your ${modal.count}-day streak alive. ` +
          (modal.freezes > 0
            ? `You have ${modal.freezes} ${plural(modal.freezes, 'freeze', 'freezes')} left.`
            : 'Keep your streak going to earn more freezes.'),
        confetti: false,
        done: 'Thanks, Pip!',
      }
    case 'comeback':
      return {
        title: 'Welcome back!',
        mood: 'happy',
        message: `It is great to see you again! Taking a break is okay, and coming back is what counts. You earned the ${modal.badge.name} badge.`,
        confetti: false,
        done: "Let's go!",
      }
  }
}

const BadgeTile: React.FC<{ badge: BadgeInfo; big?: boolean }> = ({ badge, big = false }) => (
  <span
    aria-hidden
    className={`badge-pop inline-flex items-center justify-center shrink-0 border-2 border-border-dark shadow-neo-sm text-text-primary ${
      RARITY_TILE[badge.rarity]
    } ${big ? 'w-24 h-24' : 'w-14 h-14'}`}
  >
    <AppIcon name={badge.icon} className={big ? 'w-14 h-14' : 'w-8 h-8'} />
  </span>
)

const Visual: React.FC<{ modal: RewardModal }> = ({ modal }) => {
  switch (modal.type) {
    case 'level_up':
      return (
        <div className="space-y-3">
          <div className="badge-pop mx-auto inline-block bg-brand-purple text-white border-2 border-border-dark shadow-neo px-6 py-2">
            <span className="block font-mono font-bold text-xs tracking-widest">LEVEL</span>
            <span className="block font-heading font-black text-5xl leading-none tabular-nums">{modal.level}</span>
          </div>
          <LevelBar level={modal.level} title={modal.title} xpIntoLevel={modal.xpIntoLevel} xpForNextLevel={modal.xpForNextLevel} />
        </div>
      )
    case 'badges':
      if (modal.badges.length === 1) {
        const badge = modal.badges[0]
        return (
          <div className="space-y-2">
            <BadgeTile badge={badge} big />
            <div>
              <p className="font-heading font-black text-2xl leading-tight m-0">{badge.name}</p>
              <div className="mt-1">
                <RarityTag rarity={badge.rarity} />
              </div>
              <p className="font-body text-sm text-text-muted mt-2 mb-0">{badge.description}</p>
            </div>
          </div>
        )
      }
      return (
        <ul className="list-none p-0 m-0 space-y-2 text-left">
          {modal.badges.map((badge) => (
            <li key={badge.id} className="flex items-center gap-3 border-2 border-border-dark bg-bg-base p-2">
              <BadgeTile badge={badge} />
              <div className="min-w-0">
                <p className="font-heading font-bold leading-tight m-0">
                  {badge.name} <RarityTag rarity={badge.rarity} />
                </p>
                <p className="font-body text-sm text-text-muted mt-0.5 mb-0">{badge.description}</p>
              </div>
            </li>
          ))}
        </ul>
      )
    case 'streak_milestone':
      return (
        <div className="inline-block border-2 border-border-dark bg-brand-yellow/40 shadow-neo-sm px-6 py-3">
          <StreakFlame count={modal.days} size="lg" />
        </div>
      )
    case 'used_freeze':
      return (
        <div className="inline-block border-2 border-border-dark bg-brand-blue/15 shadow-neo-sm px-6 py-3">
          <StreakFlame count={modal.count} freezes={modal.freezes} size="lg" />
        </div>
      )
    case 'comeback':
      return (
        <div className="space-y-1">
          <BadgeTile badge={modal.badge} big />
          <p className="font-heading font-black text-xl leading-tight m-0">{modal.badge.name}</p>
          <RarityTag rarity={modal.badge.rarity} />
        </div>
      )
  }
}

/** Content of one celebration dialog. The shell (focus trap, Esc) lives in <RewardDialog/>. */
export const RewardModalBody: React.FC<RewardModalBodyProps> = ({
  modal,
  step,
  total,
  labelId,
  descId,
  reducedMotion,
  onNext,
  onClose,
  onSkipAll,
}) => {
  const copy = copyFor(modal)
  const more = step + 1 < total
  const showsBadges = modal.type === 'badges' || modal.type === 'comeback'

  return (
    <div className="relative p-6 pt-8 text-center">
      {copy.confetti && !reducedMotion && <Confetti pieces={48} />}

      <button
        type="button"
        onClick={onClose}
        aria-label={more ? 'Close and skip the remaining celebrations' : 'Close'}
        title={more ? 'Skip the remaining celebrations' : 'Close'}
        className="absolute top-2 right-2 z-10 w-9 h-9 flex items-center justify-center border-2 border-border-dark bg-bg-card font-heading font-black leading-none hover:bg-brand-yellow/40"
      >
        <X aria-hidden className="w-5 h-5" strokeWidth={3} />
      </button>

      <div className="relative space-y-4">
        {total > 1 && (
          <p className="font-mono text-xs font-bold text-text-muted m-0">
            Celebration {step + 1} of {total}
          </p>
        )}
        <h2 id={labelId} className="font-heading font-black text-3xl leading-tight m-0 px-8">
          {copy.title}
        </h2>

        <Visual modal={modal} />

        <Mascot mood={copy.mood} size={104} stacked className="mx-auto" message={<span id={descId}>{copy.message}</span>} />

        <div className="flex flex-col items-center gap-3 pt-1">
          <Button variant="yellow" size="lg" onClick={onNext} data-autofocus className="w-full sm:w-auto">
            {more ? 'Next' : copy.done}
          </Button>
          {showsBadges && (
            <Link
              to="/achievements"
              onClick={onSkipAll}
              className="inline-flex items-center gap-1 font-heading font-bold text-sm text-text-primary underline decoration-2 decoration-brand-blue underline-offset-2 hover:bg-brand-yellow/40"
            >
              See all my badges
              <ArrowRight aria-hidden className="w-4 h-4 shrink-0" strokeWidth={2.5} />
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
