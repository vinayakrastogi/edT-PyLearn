import apiClient from './client'

export interface LessonNote {
  id: string
  title: string
  content: string
  resource_id: string
  created_at: string
}

const path = (moduleId: string, docId: string) =>
  `/api/notes/${encodeURIComponent(moduleId)}/${encodeURIComponent(docId)}`

export const listLessonNotes = async (moduleId: string, docId: string) =>
  (await apiClient.get<{ notes: LessonNote[] }>(path(moduleId, docId))).data.notes

export const createLessonNote = async (moduleId: string, docId: string, content: string, requestId: string) =>
  (await apiClient.post<LessonNote>(path(moduleId, docId), { content, request_id: requestId })).data

export const deleteLessonNote = async (noteId: string) =>
  apiClient.delete(`/api/notes/${encodeURIComponent(noteId)}`)
