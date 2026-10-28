import apiClient from './client'

export interface RunResult {
  stdout: string
  stderr: string
  timed_out: boolean
  images: string[]
}

/** Run a snippet in the sandbox (not graded, not stored). */
export const runCode = (code: string, stdin = '') =>
  apiClient.post<RunResult>('/api/run', { code, stdin }).then((r) => r.data)
