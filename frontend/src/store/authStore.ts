import { create } from 'zustand'
import type { User } from '@/types/module'
import { getMe, logout as apiLogout } from '@/api/auth'
import { useGamificationStore } from '@/store/gamificationStore'

interface AuthState {
  user: User | null
  loading: boolean
  initialized: boolean
  setUser: (user: User | null) => void
  initAuth: () => Promise<void>
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  initialized: false,

  setUser: (user) => set({ user }),

  initAuth: async () => {
    set({ loading: true })
    try {
      const user = await getMe()
      set({ user, loading: false, initialized: true })
    } catch {
      set({ user: null, loading: false, initialized: true })
      useGamificationStore.getState().reset()
    }
  },

  logout: async () => {
    try {
      await apiLogout()
    } finally {
      set({ user: null })
      // Never leave the previous learner's XP, streak or pending celebrations behind.
      useGamificationStore.getState().reset()
    }
  },
}))
