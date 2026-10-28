import apiClient from './client'
import type { Quiz, QuizSubmitResponse, QuizAttemptRecord } from '@/types/quiz'

export const getQuiz = (moduleId: string) =>
  apiClient.get<Quiz>(`/api/quiz/${moduleId}`).then((r) => r.data)

export const submitQuiz = (moduleId: string, answers: Record<string, unknown>) =>
  apiClient
    .post<QuizSubmitResponse>(`/api/quiz/${moduleId}/submit`, { answers })
    .then((r) => r.data)

export const getQuizAttempts = (moduleId: string) =>
  apiClient.get<QuizAttemptRecord[]>(`/api/quiz/${moduleId}/attempts`).then((r) => r.data)
