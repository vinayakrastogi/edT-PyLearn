import React from 'react'
import { Check, X, type LucideIcon } from 'lucide-react'
import type { TrueFalseQuestion as TrueFalseType } from '@/types/quiz'
import { IconTile } from '@/lib/icons'

interface Props {
  question: TrueFalseType
  answer: boolean | null
  onAnswer: (val: boolean) => void
  disabled?: boolean
  result?: { correct: boolean; correct_answer: unknown } | null
}

export const TrueFalseQuestion: React.FC<Props> = ({
  answer,
  onAnswer,
  disabled,
  result,
}) => {
  const options: { label: string; value: boolean; icon: LucideIcon; tile: 'green' | 'pink' }[] = [
    { label: 'True', value: true, icon: Check, tile: 'green' },
    { label: 'False', value: false, icon: X, tile: 'pink' },
  ]

  return (
    <div className="flex gap-4">
      {options.map(({ label, value, icon, tile }) => {
        const isSelected = answer === value
        const isCorrectAnswer = result && result.correct_answer === value
        const isWrongAnswer = result && isSelected && !result.correct

        let style =
          'flex-1 neo-card flex flex-col items-center gap-2 py-6 cursor-pointer transition-all duration-150 font-heading font-bold text-lg'

        if (result) {
          if (isCorrectAnswer) style += ' bg-brand-green/20 border-brand-green shadow-neo-green'
          else if (isWrongAnswer) style += ' bg-brand-pink/20 border-brand-pink shadow-neo-pink animate-shake'
          else style += ' opacity-60'
        } else if (isSelected) {
          style += ' bg-brand-yellow shadow-neo-yellow border-border-dark'
        } else {
          style += ' hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-neo-sm hover:bg-brand-yellow/20'
        }

        return (
          <button
            key={label}
            className={`${style}`}
            onClick={() => !disabled && onAnswer(value)}
            disabled={disabled}
          >
            <IconTile icon={icon} color={tile} />
            <span>{label}</span>
            {result && isCorrectAnswer && (
              <span className="text-brand-green text-sm font-mono">Correct!</span>
            )}
            {result && isWrongAnswer && (
              <span className="text-brand-pink text-sm font-mono">Your answer</span>
            )}
          </button>
        )
      })}
    </div>
  )
}
