import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeStore {
  isDark: boolean
  toggleTheme: () => void
  setTheme: (dark: boolean) => void
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      isDark: false,
      toggleTheme: () => set((state) => {
        const newIsDark = !state.isDark
        document.documentElement.classList.toggle('dark', newIsDark)
        return { isDark: newIsDark }
      }),
      setTheme: (dark: boolean) => set(() => {
        document.documentElement.classList.toggle('dark', dark)
        return { isDark: dark }
      })
    }),
    {
      name: 'pylearn-theme',
      onRehydrateStorage: () => (state) => {
        // Apply theme on rehydration
        if (state?.isDark) {
          document.documentElement.classList.add('dark')
        }
      }
    }
  )
)
