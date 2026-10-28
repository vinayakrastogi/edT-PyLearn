import apiClient from './client'
import type { User } from '@/types/module'

export const signup = (data: { email: string; password: string; full_name: string }) =>
  apiClient.post<User>('/api/auth/signup', data).then((r) => r.data)

export const login = (data: { email: string; password: string }) =>
  apiClient.post<User>('/api/auth/login', data).then((r) => r.data)

export const logout = () =>
  apiClient.post('/api/auth/logout').then((r) => r.data)

export const getMe = () =>
  apiClient.get<User>('/api/auth/me').then((r) => r.data)
