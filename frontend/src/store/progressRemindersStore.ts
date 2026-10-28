import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ReminderSettings {
  enabled: boolean
  emailReminders: boolean
  pushReminders: boolean
  reminderTime: string // HH:MM format
  reminderDays: number[] // 0-6 (Sunday-Saturday)
}

interface ProgressRemindersStore extends ReminderSettings {
  setReminderSettings: (settings: Partial<ReminderSettings>) => void
  checkAndNotify: () => void
}

export const useProgressReminders = create<ProgressRemindersStore>()(
  persist(
    (set, get) => ({
      enabled: true,
      emailReminders: false,
      pushReminders: true,
      reminderTime: '18:00', // 6 PM default
      reminderDays: [1, 2, 3, 4, 5], // Weekdays

      setReminderSettings: (settings) => set((state) => ({ ...state, ...settings })),

      checkAndNotify: () => {
        const state = get()
        if (!state.enabled || !state.pushReminders) return

        const now = new Date()
        const dayOfWeek = now.getDay()
        const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

        // Check if today is a reminder day and time matches
        if (state.reminderDays.includes(dayOfWeek) && currentTime === state.reminderTime) {
          // Check last activity
          const lastActivity = localStorage.getItem('last_activity_date')
          const today = now.toDateString()

          if (lastActivity !== today) {
            showProgressReminder()
          }
        }
      }
    }),
    {
      name: 'progress-reminders'
    }
  )
)

function showProgressReminder() {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('PyLearn Reminder', {
      body: 'Keep your learning streak alive! Complete a lesson today.',
      icon: '/favicon.svg'
    })
  } else if ('Notification' in window && Notification.permission !== 'denied') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        showProgressReminder()
      }
    })
  }
}

// Track user activity
export function trackActivity() {
  const now = new Date()
  localStorage.setItem('last_activity_date', now.toDateString())
}

// Initialize reminder checker (call this in App.tsx)
export function initializeReminders() {
  const store = useProgressReminders.getState()
  
  // Check every minute
  setInterval(() => {
    store.checkAndNotify()
  }, 60000)

  // Request notification permission
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
}
