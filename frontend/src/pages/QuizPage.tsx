import React, { useEffect, useState } from 'react'
import { Link, useParams, useOutletContext } from 'react-router-dom'
import { ArrowRight, Brain, Check, ChevronDown, ChevronRight, FlaskConical, Library, Lightbulb, Send, Trophy, X } from 'lucide-react'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'
import { Card } from '@/components/Card'
import { Confetti } from '@/components/Confetti'
import { Mascot } from '@/components/Mascot'
import { moodForScore } from '@/lib/pipReactions'
import { IconTile } from '@/lib/icons'
import { Skeleton } from '@/components/Skeleton'
import { RichText } from '@/components/RichText'
import { XPSummaryPanel } from '@/components/gamification/XPSummary'
import { NO_XP_MODULE_TEXT, moduleEarnsXp } from '@/lib/xp'
import { useGamificationStore } from '@/store/gamificationStore'
import { MCQQuestion } from '@/modules/QuestionTypes/MCQQuestion'
import { TrueFalseQuestion } from '@/modules/QuestionTypes/TrueFalseQuestion'
import { getQuiz, submitQuiz, getQuizAttempts } from '@/api/quiz'
import type { Question, QuizSubmitResponse, QuizAttemptRecord } from '@/types/quiz'
import type { ModuleDetail } from '@/types/module'

type QuizState = 'idle' | 'taking' | 'submitted'

export const QuizPage: React.FC = () => {
  const { moduleId } = useParams<{ moduleId: string }>()
  const { module } = useOutletContext<{ module: ModuleDetail }>()
  const [questions, setQuestions] = useState<Question[]>([])
  const [quizTitle, setQuizTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const [state, setState] = useState<QuizState>('idle')
  const [answers, setAnswers] = useState<Record<string, unknown>>({})
  const [result, setResult] = useState<QuizSubmitResponse | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [attempts, setAttempts] = useState<QuizAttemptRecord[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [previousBest, setPreviousBest] = useState<number | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const handleRewards = useGamificationStore((s) => s.handleRewards)

  useEffect(() => {
    if (!moduleId) return
    Promise.all([getQuiz(moduleId), getQuizAttempts(moduleId)])
      .then(([quiz, att]) => {
        setQuestions(quiz.questions)
        setQuizTitle(quiz.title)
        setAttempts(att)
        // Track last accessed
        import('@/api/progress').then(({ trackAccess }) => {
          trackAccess(`/modules/${moduleId}/quiz`, `Quiz: ${quiz.title}`).catch(() => {})
        })
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [moduleId])

  const handleAnswer = (qid: string, val: unknown) => {
    setAnswers((prev) => ({ ...prev, [qid]: val }))
  }

  const handleSubmit = async () => {
    if (!moduleId) return
    setSubmitting(true)
    setSubmitError(null)
    setPreviousBest(attempts.length ? Math.max(...attempts.map((a) => a.percentage)) : null)
    try {
      const res = await submitQuiz(moduleId, answers)
      setResult(res)
      setState('submitted')
      handleRewards(res.rewards)
      window.scrollTo({ top: 0, behavior: 'smooth' })
      // Refresh attempt history
      const att = await getQuizAttempts(moduleId)
      setAttempts(att)
    } catch (e: unknown) {
      const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      setSubmitError(typeof detail === 'string' ? detail : 'Your answers could not be submitted. Check your connection and try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleRetake = () => {
    setAnswers({})
    setResult(null)
    setState('taking')
  }

  const answeredCount = Object.keys(answers).length
  const allAnswered = answeredCount === questions.length

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-6 sm:px-8 py-10 space-y-4" role="status" aria-label="Loading quiz">
        <Skeleton className="h-6 w-28" />
        <Skeleton className="h-12 w-2/3" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  /** Lessons in this module that teach any of the given concepts. */
  const lessonsFor = (concepts: string[]) =>
    module.docs.filter((d) => d.concepts.some((c) => concepts.includes(c)))

  return (
    <div className="max-w-3xl mx-auto px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <span className="font-mono font-bold text-sm text-white bg-brand-pink border border-border-dark px-2 py-1">
            QUIZ
          </span>
          <Badge color="dark">{questions.length} questions</Badge>
          {attempts.length > 0 && (
            <Badge color="purple">{attempts.length} previous attempts</Badge>
          )}
        </div>
        <h1 className="font-heading font-black text-4xl text-text-primary">{quizTitle}</h1>
      </div>
      <div className="border-b-4 border-border-dark mb-8" />

      {/* IDLE STATE */}
      {state === 'idle' && (
        <div className="space-y-6">
          <Card accent="pink">
            <div className="text-center py-4">
              <IconTile icon={Brain} color="pink" size="lg" className="mb-4" />
              <h2 className="font-heading font-bold text-2xl mb-2">Ready to test yourself?</h2>
              <p className="text-text-muted font-body mb-6">
                {questions.length} questions · Mix of MCQ and True/False · All attempts are saved
              </p>
              <Button variant="pink" size="lg" onClick={() => setState('taking')} id="start-quiz-btn">
                Start Quiz <ArrowRight aria-hidden className="w-5 h-5" />
              </Button>
            </div>
          </Card>

          {attempts.length > 0 && (
            <div>
              <button
                className="font-heading font-bold text-sm text-brand-purple hover:underline mb-3 flex items-center gap-1"
                aria-expanded={showHistory}
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? <ChevronDown aria-hidden className="w-4 h-4" /> : <ChevronRight aria-hidden className="w-4 h-4" />}
                Past Attempts ({attempts.length})
              </button>
              {showHistory && (
                <div className="space-y-2">
                  {attempts.map((a) => (
                    <div key={a.id} className="neo-card px-4 py-3 flex items-center justify-between">
                      <span className="font-mono text-sm text-text-muted">
                        {new Date(a.attempted_at).toLocaleString()}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="font-heading font-bold">{a.score}/{a.max_score}</span>
                        <Badge color={a.percentage >= 80 ? 'green' : a.percentage >= 50 ? 'yellow' : 'pink'}>
                          {a.percentage}%
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAKING STATE */}
      {state === 'taking' && (
        <div className="space-y-8">
          {/* Progress */}
          <div className="flex items-center gap-3 p-3 bg-brand-yellow/20 border-2 border-border-dark">
            <span className="font-mono font-bold text-sm">{answeredCount}/{questions.length} answered</span>
            <div className="flex-1 h-2 bg-bg-card border border-border-dark overflow-hidden">
              <div
                className="h-full bg-brand-pink transition-all duration-300"
                style={{ width: `${(answeredCount / questions.length) * 100}%` }}
              />
            </div>
          </div>

          {questions.map((q, i) => (
            <div key={q.id} className="neo-card p-6 animate-slide-up">
              <div className="flex items-start gap-4 mb-5">
                <span className="font-mono font-bold text-lg bg-brand-pink text-white px-3 py-1 border-2 border-border-dark shrink-0">
                  Q{i + 1}
                </span>
                <p className="font-body text-text-primary text-base leading-relaxed whitespace-pre-line">
                  <RichText text={q.question} />
                </p>
              </div>

              {q.type === 'mcq' && (
                <MCQQuestion
                  question={q}
                  answer={answers[q.id] as number | null ?? null}
                  onAnswer={(idx) => handleAnswer(q.id, idx)}
                />
              )}
              {q.type === 'true_false' && (
                <TrueFalseQuestion
                  question={q}
                  answer={answers[q.id] as boolean | null ?? null}
                  onAnswer={(val) => handleAnswer(q.id, val)}
                />
              )}
            </div>
          ))}

          {submitError && (
            <p role="alert" className="border-2 border-border-dark bg-brand-pink/15 px-4 py-3 font-body text-sm">
              {submitError}
            </p>
          )}
          <div className="sticky bottom-4">
            <Button
              variant="pink"
              size="lg"
              className="w-full"
              disabled={!allAnswered}
              loading={submitting}
              onClick={handleSubmit}
              id="submit-quiz-btn"
            >
              {allAnswered ? (
                <>
                  <Send aria-hidden className="w-5 h-5" /> Submit Quiz
                </>
              ) : (
                `Answer all questions (${answeredCount}/${questions.length})`
              )}
            </Button>
          </div>
        </div>
      )}

      {/* SUBMITTED STATE */}
      {state === 'submitted' && result && (() => {
        const pip = moodForScore(result.percentage)
        const wrong = result.per_question_results.filter((r) => !r.correct)
        const weakConcepts = Array.from(new Set(wrong.flatMap((r) => r.concepts)))
        const reviewLessons = lessonsFor(weakConcepts)
        const newBest = previousBest !== null && result.percentage > previousBest
        return (
          <div className="space-y-8 animate-bounce-in">
            {/* Score banner with Pip */}
            <div
              className={`relative overflow-hidden border-4 border-border-dark shadow-neo-lg p-6 sm:p-8 ${
                result.percentage >= 80
                  ? 'bg-brand-green text-white'
                  : result.percentage >= 50
                  ? 'bg-brand-yellow text-text-primary'
                  : 'bg-brand-pink text-white'
              }`}
            >
              {result.percentage >= 80 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches && <Confetti />}
              <div className="relative flex flex-col sm:flex-row items-center gap-6">
                <Mascot mood={pip.mood} size={128} className="shrink-0" />
                <div className="text-center sm:text-left">
                  <div className="font-heading font-black text-5xl mb-1">
                    {result.score}/{result.max_score}
                  </div>
                  <div className="font-mono font-bold text-2xl">{result.percentage}%</div>
                  {newBest && (
                    <div className="mt-2 inline-flex items-center gap-1.5 bg-bg-card text-text-primary border-2 border-border-dark px-2 py-0.5 font-mono text-xs font-bold">
                      <Trophy aria-hidden className="w-3.5 h-3.5 shrink-0" /> NEW PERSONAL BEST (was {previousBest}%)
                    </div>
                  )}
                </div>
              </div>
              <div className="relative mt-5 neo-card bg-bg-card text-text-primary p-4 font-body" role="status">
                <span className="font-bold">Pip says: </span>
                {pip.message}
              </div>
            </div>

            {/* XP earned for this attempt */}
            {result.rewards && !moduleEarnsXp(moduleId) && (
              <p className="neo-card p-4 font-body text-sm m-0 flex items-start gap-2">
                <FlaskConical aria-hidden className="w-4 h-4 shrink-0 mt-0.5 text-brand-purple" />
                {NO_XP_MODULE_TEXT}
              </p>
            )}
            {result.rewards && moduleEarnsXp(moduleId) && (
              <XPSummaryPanel
                rewards={result.rewards}
                emptyText={
                  previousBest !== null
                    ? `No new XP this time. Quiz XP is paid for your first attempt, then at most once every 12 hours, and only for beating your best score (${previousBest}%). Retakes are still great practice!`
                    : 'No XP was earned for this attempt.'
                }
              />
            )}

            {/* What to review */}
            {reviewLessons.length > 0 && (
              <Card accent="yellow">
                <h2 className="font-heading font-bold text-xl mb-1 flex items-center gap-2">
                  <Library aria-hidden className="w-6 h-6 shrink-0" /> Lessons worth another look
                </h2>
                <p className="font-body text-sm text-text-muted mb-3">
                  You missed questions about: {weakConcepts.join(', ')}.
                </p>
                <div className="flex flex-wrap gap-2">
                  {reviewLessons.map((d) => (
                    <Link
                      key={d.id}
                      to={`/modules/${moduleId}/docs/${d.id}`}
                      className="neo-btn bg-bg-card px-3 py-1.5 text-sm hover:bg-brand-yellow/30"
                    >
                      Lesson {d.order}: {d.title} <ArrowRight aria-hidden className="w-4 h-4 shrink-0" />
                    </Link>
                  ))}
                </div>
              </Card>
            )}

            {/* Per-question review */}
            <h2 className="font-heading font-bold text-2xl">Question Review</h2>
            {result.per_question_results.map((qr, i) => {
              const q = questions.find((x) => x.id === qr.question_id)
              if (!q) return null
              const lessons = qr.correct ? [] : lessonsFor(qr.concepts)
              return (
                <div
                  key={qr.question_id}
                  className={`neo-card p-5 border-l-8 ${qr.correct ? 'border-l-brand-green' : 'border-l-brand-pink'}`}
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <span className="font-mono font-bold text-sm">Q{i + 1}</span>
                    <Badge color={qr.correct ? 'green' : 'pink'} className="gap-1">
                      {qr.correct ? (
                        <Check aria-hidden className="w-3.5 h-3.5" strokeWidth={3} />
                      ) : (
                        <X aria-hidden className="w-3.5 h-3.5" strokeWidth={3} />
                      )}
                      {qr.correct ? 'Correct' : 'Incorrect'}
                    </Badge>
                  </div>
                  <p className="font-body text-text-primary mb-4 whitespace-pre-line"><RichText text={q.question} /></p>

                  {q.type === 'mcq' && (
                    <MCQQuestion
                      question={q}
                      answer={(qr.user_answer as number | null) ?? null}
                      onAnswer={() => {}}
                      disabled
                      result={{ correct: qr.correct, correct_answer: qr.correct_answer }}
                    />
                  )}
                  {q.type === 'true_false' && (
                    <TrueFalseQuestion
                      question={q}
                      answer={(qr.user_answer as boolean | null) ?? null}
                      onAnswer={() => {}}
                      disabled
                      result={{ correct: qr.correct, correct_answer: qr.correct_answer }}
                    />
                  )}

                  {qr.explanation && (
                    <div className="mt-4 border-2 border-border-dark bg-brand-blue/10 px-4 py-3 font-body text-sm">
                      <span className="font-bold">
                        <Lightbulb aria-hidden className="inline-block w-4 h-4 mr-1 align-[-0.15em]" />
                        Why:{' '}
                      </span>
                      <RichText text={qr.explanation} />
                    </div>
                  )}

                  {lessons.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2 items-center">
                      <span className="font-mono text-xs text-text-muted">Review:</span>
                      {lessons.map((d) => (
                        <Link key={d.id} to={`/modules/${moduleId}/docs/${d.id}`} className="font-heading font-bold text-sm text-brand-blue hover:underline">
                          Lesson {d.order}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}

            <div className="flex gap-4 flex-wrap">
              <Button variant="pink" size="lg" onClick={handleRetake} className="flex-1" id="retake-quiz-btn">
                Retake Quiz
              </Button>
              {module.problems.length > 0 && (
                <Link to={`/modules/${moduleId}/problems/${module.problems[0].id}`} className="flex-1">
                  <Button variant="primary" size="lg" className="w-full">
                    Practice coding <ArrowRight aria-hidden className="w-5 h-5" />
                  </Button>
                </Link>
              )}
            </div>
          </div>
        )
      })()}
    </div>
  )
}
