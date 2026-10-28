import type { RewardSummary } from '@/types/gamification'

export interface VisibleTest {
  /** function problems: the arguments passed to the learner's function */
  input?: unknown
  /** program problems: text fed to stdin */
  stdin?: string
  /** driver problems: a script appended after the learner's code */
  driver?: string
  expected: string
}

export type ProblemKind = 'function' | 'program' | 'driver'
export type Difficulty = 'easy' | 'medium' | 'hard'

export interface ProblemDetail {
  id: string
  title: string
  description: string
  starter_code: string
  concepts: string[]
  visible_tests: VisibleTest[]
  type: ProblemKind
  difficulty: Difficulty
  hints: string[]
}

export interface TestResult {
  test_index: number
  passed: boolean
  expected: string
  actual: string
  is_hidden: boolean
}

export interface CodeSubmitResponse {
  status: 'PASS' | 'FAIL' | 'ERROR' | 'TIMEOUT'
  passed_count: number
  total_count: number
  test_results: TestResult[]
  stdout: string
  stderr: string
  /** XP, level and badge news for this submission. Null/absent when gamification failed or is off. */
  rewards?: RewardSummary | null
}

export interface SubmissionRecord {
  id: number
  problem_id: string
  code: string
  status: string
  test_results: TestResult[] | null
  stdout: string | null
  stderr: string | null
  submitted_at: string
}

export interface ConceptMastery {
  concept: string
  correct: number
  total: number
  percentage: number
}

export interface DashboardData {
  modules: ModuleProgressSummary[]
  streak_count: number
  mastery_stats: ConceptMastery[]
}

/** Response of POST /api/progress/lesson-view. */
export interface LessonProgressRecord {
  lesson_id: string
  viewed_at: string
  is_complete: boolean
  /** XP, level and badge news for this lesson. Null/absent when gamification failed or is off. */
  rewards?: RewardSummary | null
}

export interface ModuleProgressSummary {
  module_id: string
  total_docs: number
  docs_read: number
  quiz_attempts: number
  best_quiz_score: number | null
  total_problems: number
  problems_solved: number
  completion_percentage: number
  viewed_docs: string[]
  passed_problems: string[]
}
