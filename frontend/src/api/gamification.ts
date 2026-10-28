import apiClient from './client'
import type {
  BadgeListResponse,
  GamificationSummary,
  LeaderboardResponse,
  SettingsUpdate,
} from '@/types/gamification'

export const getGamificationSummary = () =>
  apiClient.get<GamificationSummary>('/api/gamification/me').then((r) => r.data)

export const getBadges = () =>
  apiClient.get<BadgeListResponse>('/api/gamification/badges').then((r) => r.data)

export const getLeaderboard = () =>
  apiClient.get<LeaderboardResponse>('/api/gamification/leaderboard').then((r) => r.data)

export const updateGamificationSettings = (body: SettingsUpdate) =>
  apiClient.patch<GamificationSummary>('/api/gamification/settings', body).then((r) => r.data)
