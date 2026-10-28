import { apiUrl } from '@/api/url'
import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, TriangleAlert } from 'lucide-react'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { Logo } from '@/components/Logo'
import { signup } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'

export const SignupPage: React.FC = () => {
  const navigate = useNavigate()
  const setUser = useAuthStore((s) => s.setUser)
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    setLoading(true)
    try {
      const user = await signup(form)
      setUser(user)
      navigate('/dashboard')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(msg || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg-base flex items-center justify-center px-4 py-16">
      <div className="fixed top-16 right-10 w-32 h-32 bg-brand-green border-2 border-border-dark shadow-neo-lg rotate-3 opacity-25 pointer-events-none" />
      <div className="fixed bottom-16 left-10 w-24 h-24 bg-brand-purple border-2 border-border-dark shadow-neo -rotate-12 opacity-20 pointer-events-none" />

      <div className="w-full max-w-md">
        <Link to="/" className="flex items-center mb-8 group">
          <Logo textClassName="font-heading font-bold text-xl text-text-primary group-hover:text-brand-blue transition-colors" />
        </Link>

        <div className="neo-card p-8 animate-slide-up">
          <h1 className="font-heading font-black text-3xl mb-2">Create your account</h1>
          <p className="text-text-muted font-body mb-8">
            Already have one?{' '}
            <Link to="/login" className="inline-flex items-center gap-1 text-brand-blue font-bold hover:underline">
              Log in <ArrowRight aria-hidden className="w-4 h-4" />
            </Link>
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              id="full_name"
              label="Your name"
              type="text"
              placeholder="Alex Johnson"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              required
            />
            <Input
              id="email"
              label="Email address"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
            <Input
              id="password"
              label="Password"
              type="password"
              placeholder="Min. 6 characters"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />

            {error && (
              <div role="alert" className="flex items-start gap-2 bg-brand-pink/10 border-2 border-brand-pink p-3 font-mono text-sm text-brand-pink animate-shake">
                <TriangleAlert aria-hidden className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <Button
              type="submit"
              variant="yellow"
              size="lg"
              loading={loading}
              className="w-full mt-2"
              id="signup-submit-btn"
            >
              Create Account <ArrowRight aria-hidden className="w-5 h-5" />
            </Button>

            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t-2 border-border-dark"></div>
              <span className="flex-shrink-0 mx-4 text-text-muted font-bold text-sm">OR</span>
              <div className="flex-grow border-t-2 border-border-dark"></div>
            </div>

            <a
              href={apiUrl('/api/auth/google/login')}
              className="w-full flex items-center justify-center gap-3 bg-bg-base border-2 border-border-dark shadow-neo hover:-translate-y-1 hover:shadow-neo-sm transition-all py-3 px-4 font-bold rounded-none"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M21.35,11.1H12.18V13.83H18.69C18.36,17.64 15.19,19.27 12.19,19.27C8.36,19.27 5,16.25 5,12C5,7.9 8.2,4.73 12.2,4.73C15.29,4.73 17.1,6.7 17.1,6.7L19,4.72C19,4.72 16.56,2 12.1,2C6.42,2 2.03,6.8 2.03,12C2.03,17.05 6.36,22 12.22,22C17,22 21.97,18.74 21.97,12.22C21.97,11.67 21.82,11.1 21.82,11.1"
                />
              </svg>
              Continue with Google
            </a>
          </form>
        </div>
      </div>
    </div>
  )
}
