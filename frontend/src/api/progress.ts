import apiClient from './client'
import type { ModuleProgressSummary, DashboardData, LessonProgressRecord } from '@/types/problem'

export const markLessonViewed = (moduleId: string, lessonId: string) =>
  apiClient
    .post<LessonProgressRecord>('/api/progress/lesson-view', { module_id: moduleId, lesson_id: lessonId })
    .then((r) => r.data)

export const getDashboard = () =>
  apiClient
    .get<DashboardData>('/api/progress/dashboard')
    .then((r) => r.data)

export const getModuleProgress = (moduleId: string) =>
  apiClient
    .get<ModuleProgressSummary>(`/api/progress/${moduleId}`)
    .then((r) => r.data)

export const trackAccess = (path: string, title: string) =>
  apiClient
    .post('/api/progress/track-access', { path, title })
    .then((r) => r.data)
