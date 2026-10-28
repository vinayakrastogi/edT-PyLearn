import { apiUrl } from '@/api/url'
import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Save, Settings, Trophy } from 'lucide-react'
import { Button } from '@/components/Button'
import { LogoMark } from '@/components/Logo'
import { XPChip } from '@/components/gamification/XPChip'
import { useAuthStore } from '@/store/authStore'
import { useGeneratedModuleStore } from '@/store/generatedModuleStore'

export const Navbar: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { generatedModule } = useGeneratedModuleStore()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const handleSaveModule = async () => {
    if (!generatedModule) return
    
    try {
      const response = await fetch(apiUrl('/api/generate/save-local'), {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(generatedModule)
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Failed to save module')
      }

      // Clear generated module and navigate to dashboard
      useGeneratedModuleStore.getState().clearGeneratedModule()
      navigate('/dashboard')
    } catch (err: any) {
      alert(`Failed to save: ${err.message}`)
    }
  }

  // Don't show navbar on landing/login pages
  if (location.pathname === '/' || location.pathname === '/login') {
    return null
  }

  return (
    <header className="sticky top-0 z-50 border-b-4 border-border-dark bg-bg-card shadow-neo">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 py-4 flex items-center justify-between gap-2">
        {/* Left: Logo & Brand (icon only on phones when signed in, to make room for the XP chip) */}
        <Link to="/dashboard" aria-label="PyLearn dashboard" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <LogoMark size={36} />
          <span className={`font-heading font-bold text-xl text-text-primary ${user ? 'hidden sm:inline' : ''}`}>PyLearn</span>
        </Link>
        
        {/* Center: Navigation Links */}
        <nav className="hidden lg:flex items-center gap-4 xl:gap-6 min-w-0">
          <NavLink to="/dashboard">Dashboard</NavLink>
          {user?.role === 'faculty' && (
            <>
              <NavLink to="/create">Create Content</NavLink>
              <NavLink to="/my-classrooms">My Classrooms</NavLink>
            </>
          )}
          {user?.role === 'student' && (
            <NavLink to="/my-courses">My Courses</NavLink>
          )}
          <NavLink to="/achievements">
            <span className="inline-flex items-center gap-1.5">
              <Trophy aria-hidden className="w-4 h-4" strokeWidth={2.5} />
              Achievements
            </span>
          </NavLink>
        </nav>
        
        {/* Right: Actions */}
        <div className="flex items-center gap-1.5 sm:gap-3">
          {/* Level, XP and streak (also the way to Achievements on phones) */}
          {user && <XPChip />}

          {/* Save Module Button (if preview mode) */}
          {generatedModule && (
            <Button 
              color="green" 
              size="sm"
              className="animate-pulse shadow-neo-lg"
              onClick={handleSaveModule}
            >
              <Save aria-hidden className="w-4 h-4" strokeWidth={2.5} />
              Save to Disk
            </Button>
          )}

          {/* Settings */}
          <Button 
            variant="ghost" 
            size="sm"
            aria-label="Settings"
            onClick={() => navigate('/settings')}
          >
            <Settings aria-hidden className="w-5 h-5" strokeWidth={2.5} />
          </Button>
          
          {/* User Avatar & Logout */}
          <div className="flex items-center gap-2">
            <div className="hidden xl:block text-right">
              <div className="font-body font-bold text-sm text-text-primary">
                {user?.full_name}
              </div>
              <div className="font-mono text-xs text-text-muted">
                {user?.role || 'student'}
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleLogout}
              title={user?.full_name ? `Signed in as ${user.full_name}` : undefined}
              className="border-2 border-border-dark"
            >
              Log out
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

// NavLink helper component
const NavLink: React.FC<{ to: string; children: React.ReactNode }> = ({ to, children }) => {
  const location = useLocation()
  const isActive = location.pathname === to

  return (
    <Link
      to={to}
      aria-current={isActive ? 'page' : undefined}
      className={`font-body font-bold text-sm whitespace-nowrap ${
        isActive
          ? 'text-brand-blue border-b-2 border-brand-blue pb-1'
          : 'text-text-muted hover:text-text-primary'
      }`}
    >
      {children}
    </Link>
  )
}
