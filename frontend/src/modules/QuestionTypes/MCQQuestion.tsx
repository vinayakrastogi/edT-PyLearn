import React from 'react'
import { Check, X } from 'lucide-react'
import type { MCQQuestion as MCQQuestionType } from '@/types/quiz'
import { RichText } from '@/components/RichText'

interface Props {
  question: MCQQuestionType
  answer: number | null
  onAnswer: (idx: number) => void
  disabled?: boolean
  result?: { correct: boolean; correct_answer: unknown } | null
}

export const MCQQuestion: React.FC<Props> = ({
  question,
  answer,
  onAnswer,
  disabled,
  result,
}) => {
  return (
    <div className="space-y-3">
      {question.options.map((option, idx) => {
        const isSelected = answer === idx
        const isCorrectAnswer = result && result.correct_answer === idx
        const isWrongAnswer = result && isSelected && !result.correct

        let optionStyle =
          'neo-card px-5 py-3 cursor-pointer flex items-center gap-4 transition-all duration-150 group'

        if (result) {
          if (isCorrectAnswer) {
            optionStyle += ' bg-brand-green/20 border-brand-green shadow-neo-green'
          } else if (isWrongAnswer) {
            optionStyle += ' bg-brand-pink/20 border-brand-pink shadow-neo-pink animate-shake'
          } else {
            optionStyle += ' opacity-60'
          }
        } else if (isSelected) {
          optionStyle += ' bg-brand-yellow border-border-dark shadow-neo-yellow'
        } else {
          optionStyle += ' hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-neo-sm hover:bg-brand-yellow/20'
        }

        return (
          <button
            key={idx}
            className={`w-full text-left ${optionStyle}`}
            onClick={() => !disabled && onAnswer(idx)}
            disabled={disabled}
          >
            <span
              className={`w-8 h-8 flex items-center justify-center border-2 border-border-dark font-mono font-bold text-sm shrink-0 transition-colors ${
                isSelected && !result ? 'bg-border-dark text-white' : 'bg-bg-base'
              } ${isCorrectAnswer ? 'bg-brand-green text-white border-brand-green' : ''}
              ${isWrongAnswer ? 'bg-brand-pink text-white border-brand-pink' : ''}`}
            >
              {String.fromCharCode(65 + idx)}
            </span>
            <span className="font-body text-text-primary"><RichText text={option} /></span>
            {result && isCorrectAnswer && (
              <span className="ml-auto shrink-0 text-brand-green">
                <Check aria-hidden className="w-5 h-5" strokeWidth={3} />
                <span className="sr-only">Correct answer</span>
              </span>
            )}
            {result && isWrongAnswer && (
              <span className="ml-auto shrink-0 text-brand-pink">
                <X aria-hidden className="w-5 h-5" strokeWidth={3} />
                <span className="sr-only">Your answer, incorrect</span>
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
