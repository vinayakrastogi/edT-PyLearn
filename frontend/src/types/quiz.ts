import type { RewardSummary } from '@/types/gamification'

export type QuestionType = 'mcq' | 'true_false'

export interface BaseQuestion {
  id: string
  type: QuestionType
  question: string
  concepts: string[]
}

export interface MCQQuestion extends BaseQuestion {
  type: 'mcq'
  options: string[]
}

export interface TrueFalseQuestion extends BaseQuestion {
  type: 'true_false'
}

export type Question = MCQQuestion | TrueFalseQuestion

export interface Quiz {
  id: string
  module_id: string
  title: string
  questions: Question[]
}

export interface QuestionResult {
  question_id: string
  correct: boolean
  concepts: string[]
  user_answer: unknown
  correct_answer: unknown
  explanation?: string | null
}

export interface QuizSubmitResponse {
  score: number
  max_score: number
  percentage: number
  per_question_results: QuestionResult[]
  /** XP, level and badge news for this attempt. Null/absent when gamification failed or is off. */
  rewards?: RewardSummary | null
}

export interface QuizAttemptRecord {
  id: number
  quiz_id: string
  score: number
  max_score: number
  percentage: number
  per_question_results: QuestionResult[]
  attempted_at: string
}
