import { apiUrl } from '@/api/url'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlarmClock, ArrowLeft, ChartColumn, Globe, Library, Lock, Plus, School, Settings, UserRound, Users } from 'lucide-react'
import { Button } from '@/components/Button'
import { Card } from '@/components/Card'
import { GamificationSettings } from '@/components/gamification/GamificationSettings'
import { useAuthStore } from '@/store/authStore'
import { useProgressReminders } from '@/store/progressRemindersStore'

interface Enrollment {
  id: number
  classroom_module_id: number
  classroom_title: string
  classroom_code: string
  module_id: string
  enrolled_at: string
  score: number | null
  completed_at: string | null
}

interface Classroom {
  id: number
  code: string
  module_id: string
  title: string
  description: string | null
  is_public: boolean
  enrollment_count: number
  created_at: string
}

export const SettingsPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const reminderSettings = useProgressReminders()
  
  const [enrollments, setEnrollments] = useState<Enrollment[]>([])
  const [classrooms, setClassrooms] = useState<Classroom[]>([])
  const [enrollCode, setEnrollCode] = useState('')
  const [isEnrolling, setIsEnrolling] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    
    try {
      if (user?.role === 'student') {
        const res = await fetch(apiUrl('/api/classrooms/my-enrollments'), {
          credentials: 'include'
        })
        if (res.ok) {
          const data = await res.json()
          setEnrollments(data)
        }
      } else if (user?.role === 'faculty') {
        const res = await fetch(apiUrl('/api/classrooms/my-classrooms'), {
          credentials: 'include'
        })
        if (res.ok) {
          const data = await res.json()
          setClassrooms(data)
        }
      }
    } catch (err) {
      console.error('Failed to load data:', err)
    }
  }

  const handleEnroll = async () => {
    if (!enrollCode.trim()) {
      setError('Please enter a classroom code')
      return
    }
    
    setIsEnrolling(true)
    setError(null)
    setSuccess(null)
    
    
    try {
      const res = await fetch(apiUrl('/api/classrooms/enroll'), {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: enrollCode.toUpperCase() })
      })
      
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Failed to enroll')
      }
      
      setSuccess('Successfully enrolled in classroom!')
      setEnrollCode('')
      loadData()
      
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsEnrolling(false)
    }
  }

  const handleUnenroll = async (classroomId: number) => {
    if (!window.confirm('Are you sure you want to unenroll from this classroom?')) return
    
    
    try {
      const res = await fetch(apiUrl(`/api/classrooms/${classroomId}/unenroll`), {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (!res.ok) throw new Error('Failed to unenroll')
      
      setSuccess('Successfully unenrolled from classroom')
      loadData()
      
    } catch (err: any) {
      setError(err.message)
    }
  }

  const handleDeleteClassroom = async (classroomId: number) => {
    if (!window.confirm('Are you sure you want to delete this classroom? All enrollments will be removed.')) return
    
    
    try {
      const res = await fetch(apiUrl(`/api/classrooms/${classroomId}`), {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (!res.ok) throw new Error('Failed to delete classroom')
      
      setSuccess('Classroom deleted successfully')
      loadData()
      
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div className="min-h-screen bg-bg-base py-10 px-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="font-heading font-black text-4xl mb-8 flex items-center gap-3">
          <Settings aria-hidden className="w-9 h-9 shrink-0" strokeWidth={2.5} />
          Settings
        </h1>

        {error && (
          <div className="bg-brand-pink text-white font-bold p-4 border-2 border-border-dark mb-6 animate-shake">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-brand-green text-white font-bold p-4 border-2 border-border-dark mb-6 animate-bounce-in">
            {success}
          </div>
        )}

        {/* Profile Section */}
        <Card accent="blue" className="mb-8">
          <h2 className="font-heading font-bold text-2xl mb-4 flex items-center gap-2">
            <UserRound aria-hidden className="w-6 h-6 shrink-0" strokeWidth={2.5} />
            Profile
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between border-b border-border-dark pb-2">
              <span className="font-mono text-sm text-text-muted">Name:</span>
              <span className="font-body font-bold">{user?.full_name}</span>
            </div>
            <div className="flex justify-between border-b border-border-dark pb-2">
              <span className="font-mono text-sm text-text-muted">Email:</span>
              <span className="font-body font-bold">{user?.email}</span>
            </div>
            <div className="flex justify-between border-b border-border-dark pb-2">
              <span className="font-mono text-sm text-text-muted">Role:</span>
              <span className="font-body font-bold uppercase">{user?.role}</span>
            </div>
          </div>
        </Card>
        
        {/* Progress Reminders */}
        <Card accent="orange" className="mb-8">
          <h2 className="font-heading font-bold text-2xl mb-4 flex items-center gap-2">
            <AlarmClock aria-hidden className="w-6 h-6 shrink-0" strokeWidth={2.5} />
            Progress Reminders
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-border-dark pb-3">
              <div>
                <div className="font-body font-bold">Enable Reminders</div>
                <div className="text-sm text-text-muted">Get notifications to keep learning</div>
              </div>
              <Button 
                color={reminderSettings.enabled ? 'green' : 'pink'}
                size="sm"
                onClick={() => reminderSettings.setReminderSettings({ enabled: !reminderSettings.enabled })}
              >
                {reminderSettings.enabled ? 'ON' : 'OFF'}
              </Button>
            </div>
            
            {reminderSettings.enabled && (
              <>
                <div className="flex items-center justify-between border-b border-border-dark pb-3">
                  <div>
                    <div className="font-body font-bold">Push Notifications</div>
                    <div className="text-sm text-text-muted">Browser push notifications</div>
                  </div>
                  <Button 
                    color={reminderSettings.pushReminders ? 'green' : 'pink'}
                    size="sm"
                    onClick={() => reminderSettings.setReminderSettings({ pushReminders: !reminderSettings.pushReminders })}
                  >
                    {reminderSettings.pushReminders ? 'ON' : 'OFF'}
                  </Button>
                </div>

                <div>
                  <label className="font-body font-bold block mb-2">Reminder Time</label>
                  <input 
                    type="time"
                    value={reminderSettings.reminderTime}
                    onChange={(e) => reminderSettings.setReminderSettings({ reminderTime: e.target.value })}
                    className="neo-input w-full"
                  />
                </div>

                <div>
                  <label className="font-body font-bold block mb-2">Reminder Days</label>
                  <div className="flex gap-2 flex-wrap">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, idx) => (
                      <button
                        key={day}
                        onClick={() => {
                          const days = reminderSettings.reminderDays.includes(idx)
                            ? reminderSettings.reminderDays.filter(d => d !== idx)
                            : [...reminderSettings.reminderDays, idx]
                          reminderSettings.setReminderSettings({ reminderDays: days })
                        }}
                        className={`px-3 py-2 border-2 border-border-dark font-mono text-xs font-bold transition-all duration-300 ${
                          reminderSettings.reminderDays.includes(idx)
                            ? 'bg-brand-green text-white'
                            : 'bg-bg-base text-text-primary hover:bg-brand-yellow/20'
                        }`}
                      >
                        {day}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </Card>

        {/* Daily XP goal and leaderboard */}
        <GamificationSettings />

        {/* 
        {/* Student Settings */}
        {user?.role === 'student' && (
          <>
            <Card accent="green" className="mb-8">
              <h2 className="font-heading font-bold text-2xl mb-4 flex items-center gap-2">
                <Plus aria-hidden className="w-6 h-6 shrink-0" strokeWidth={2.5} />
                Add Classroom
              </h2>
              <p className="text-sm text-text-muted mb-4">
                Enter the 6-digit code provided by your instructor
              </p>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={enrollCode}
                  onChange={(e) => setEnrollCode(e.target.value.toUpperCase())}
                  placeholder="ABC123"
                  maxLength={6}
                  className="neo-input flex-1 uppercase font-mono"
                />
                <Button 
                  color="green" 
                  onClick={handleEnroll}
                  disabled={isEnrolling || !enrollCode.trim()}
                >
                  {isEnrolling ? 'Enrolling...' : 'Enroll'}
                </Button>
              </div>
            </Card>

            <Card accent="orange" className="mb-8">
              <h2 className="font-heading font-bold text-2xl mb-4 flex items-center gap-2">
                <Library aria-hidden className="w-6 h-6 shrink-0" strokeWidth={2.5} />
                My Classrooms
              </h2>
              {enrollments.length === 0 ? (
                <p className="text-text-muted">No enrollments yet. Add a classroom using the code above!</p>
              ) : (
                <div className="space-y-4">
                  {enrollments.map(enrollment => (
                    <div key={enrollment.id} className="border-2 border-border-dark p-4 bg-bg-base">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-heading font-bold text-lg">{enrollment.classroom_title}</h3>
                          <p className="font-mono text-xs text-text-muted">Code: {enrollment.classroom_code}</p>
                        </div>
                        {enrollment.score !== null && (
                          <div className="bg-brand-green text-white font-bold px-3 py-1 text-sm">
                            Score: {enrollment.score}%
                          </div>
                        )}
                      </div>
                      <div className="flex justify-between items-center mt-3">
                        <span className="text-xs text-text-muted">
                          Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                        </span>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-brand-pink border-brand-pink hover:bg-brand-pink hover:text-white"
                          onClick={() => handleUnenroll(enrollment.classroom_module_id)}
                        >
                          Unenroll
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </>
        )}

        {/* Faculty Settings */}
        {user?.role === 'faculty' && (
          <Card accent="pink" className="mb-8">
            <h2 className="font-heading font-bold text-2xl mb-4 flex items-center gap-2">
              <School aria-hidden className="w-6 h-6 shrink-0" strokeWidth={2.5} />
              My Classrooms
            </h2>
            <Button 
              color="blue" 
              className="mb-6"
              onClick={() => navigate('/create')}
            >
              <Plus aria-hidden className="w-5 h-5" /> Create New Classroom
            </Button>
            
            {classrooms.length === 0 ? (
              <p className="text-text-muted">No classrooms created yet.</p>
            ) : (
              <div className="space-y-4">
                {classrooms.map(classroom => (
                  <div key={classroom.id} className="border-2 border-border-dark p-4 bg-bg-base">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-heading font-bold text-lg">{classroom.title}</h3>
                        <p className="text-sm text-text-muted">{classroom.description}</p>
                      </div>
                      <div className="bg-brand-yellow text-text-primary font-bold px-3 py-1 text-sm font-mono">
                        {classroom.code}
                      </div>
                    </div>
                    <div className="flex justify-between items-center mt-3">
                      <div className="flex gap-4 text-xs">
                        <span className="text-text-muted inline-flex items-center gap-1">
                          <Users aria-hidden className="w-3.5 h-3.5 shrink-0" /> {classroom.enrollment_count} students
                        </span>
                        <span className="text-text-muted inline-flex items-center gap-1">
                          {classroom.is_public ? (
                            <>
                              <Globe aria-hidden className="w-3.5 h-3.5 shrink-0" /> Public
                            </>
                          ) : (
                            <>
                              <Lock aria-hidden className="w-3.5 h-3.5 shrink-0" /> Private (Max 80)
                            </>
                          )}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => navigate(`/classrooms/${classroom.id}/analytics`)}
                        >
                          <ChartColumn aria-hidden className="w-4 h-4" /> Analytics
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          className="text-brand-pink border-brand-pink hover:bg-brand-pink hover:text-white"
                          onClick={() => handleDeleteClassroom(classroom.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        <Button 
          variant="ghost" 
          onClick={() => navigate('/dashboard')}
          className="w-full"
        >
          <ArrowLeft aria-hidden className="w-5 h-5" /> Back to Dashboard
        </Button>
      </div>
    </div>
  )
}
