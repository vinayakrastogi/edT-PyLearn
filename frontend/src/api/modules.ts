import apiClient from './client'
import type { ModuleMeta, ModuleDetail, DocPage } from '@/types/module'

export const listModules = () =>
  apiClient.get<ModuleMeta[]>('/api/modules').then((r) => r.data)

export const getModule = (moduleId: string) =>
  apiClient.get<ModuleDetail>(`/api/modules/${moduleId}`).then((r) => r.data)

export const getDoc = (moduleId: string, docId: string) =>
  apiClient.get<DocPage>(`/api/modules/${moduleId}/docs/${docId}`).then((r) => r.data)

export const deleteModule = (moduleId: string) =>
  apiClient.delete(`/api/modules/${moduleId}`).then((r) => r.data)
