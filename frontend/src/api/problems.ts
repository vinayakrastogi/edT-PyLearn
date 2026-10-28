import apiClient from './client'
import type { ProblemDetail, CodeSubmitResponse, SubmissionRecord } from '@/types/problem'

export const getProblem = (moduleId: string, problemId: string) =>
  apiClient
    .get<ProblemDetail>(`/api/problems/${moduleId}/${problemId}`)
    .then((r) => r.data)

export const submitCode = (moduleId: string, problemId: string, code: string) =>
  apiClient
    .post<CodeSubmitResponse>(`/api/problems/${moduleId}/${problemId}/submit`, { code })
    .then((r) => r.data)

export const getSubmissions = (moduleId: string, problemId: string) =>
  apiClient
    .get<SubmissionRecord[]>(`/api/problems/${moduleId}/${problemId}/submissions`)
    .then((r) => r.data)
