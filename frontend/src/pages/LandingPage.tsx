import React, { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import type { LucideIcon } from 'lucide-react'
import { ArrowRight, BookOpen, Brain, ChartColumn, CodeXml, Sparkles, Target, Zap } from 'lucide-react'
import { Button } from '@/components/Button'
import { Logo } from '@/components/Logo'
import { IconTile } from '@/lib/icons'
import { useAuthStore } from '@/store/authStore'

export const LandingPage: React.FC = () => {
  const { user, initialized } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (initialized && user) {
      navigate('/dashboard')
    }
  }, [user, initialized, navigate])

  return (
    <div className="min-h-screen bg-bg-base overflow-hidden">
      {/* Nav */}
      <nav className="border-b-2 border-border-dark bg-bg-card px-8 py-4 flex items-center justify-between sticky top-0 z-10 shadow-neo-sm">
        <Logo />
        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm">Log in</Button>
          </Link>
          <Link to="/signup">
            <Button variant="yellow" size="sm">Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative px-8 pt-20 pb-16 max-w-6xl mx-auto">
        {/* Decorative blocks */}
        <div className="absolute top-8 right-12 w-40 h-40 bg-brand-yellow border-2 border-border-dark shadow-neo-lg rotate-6 opacity-40 hidden lg:block" />
        <div className="absolute top-24 right-32 w-24 h-24 bg-brand-blue border-2 border-border-dark shadow-neo -rotate-3 opacity-30 hidden lg:block" />
        <div className="absolute bottom-4 left-8 w-32 h-32 bg-brand-pink border-2 border-border-dark shadow-neo rotate-12 opacity-20 hidden lg:block" />

        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 bg-brand-yellow border-2 border-border-dark shadow-neo px-4 py-2 mb-8">
            <Sparkles aria-hidden className="w-4 h-4" />
            <span className="font-mono font-bold text-sm">FREE FOR STUDENTS</span>
          </div>
          <h1 className="font-heading font-black text-5xl md:text-7xl leading-none mb-6 text-text-primary">
            Learn Python.<br />
            <span className="bg-brand-yellow px-2">Have Fun.</span><br />
            Actually Learn.
          </h1>
          <p className="font-body text-xl text-text-muted mb-10 max-w-xl leading-relaxed">
            Interactive lessons, instant quiz feedback, and a real Python editor — 
            all in one place. No boring lectures, just hands-on learning.
          </p>
          <div className="flex flex-wrap items-center gap-4">
            <Link to="/signup">
              <Button variant="yellow" size="lg" className="text-lg">
                Start Learning Free <ArrowRight aria-hidden className="w-5 h-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="secondary" size="lg">
                I already have an account
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="px-8 py-16 max-w-6xl mx-auto">
        <h2 className="font-heading font-black text-4xl mb-12 text-center">
          Everything you need to master Python
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <div
              key={i}
              className="neo-card p-6 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-neo-sm transition-all duration-150"
            >
              <IconTile icon={f.icon} color={f.color} size="lg" className="mb-4" />
              <h3 className="font-heading font-bold text-xl mb-2">{f.title}</h3>
              <p className="text-text-muted font-body">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Strip */}
      <section className="mx-8 mb-16 bg-brand-blue border-2 border-border-dark shadow-neo-lg p-10 flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <h2 className="font-heading font-black text-3xl text-white mb-2">Ready to start?</h2>
          <p className="font-body text-blue-100">Join and complete your first lesson in under 10 minutes.</p>
        </div>
        <Link to="/signup">
          <Button variant="yellow" size="lg">
            Create Free Account <ArrowRight aria-hidden className="w-5 h-5" />
          </Button>
        </Link>
      </section>

      {/* Footer */}
      <footer className="border-t-2 border-border-dark px-8 py-6 text-center text-text-muted font-mono text-sm">
        <span>PyLearn — EdTech MVP © 2024</span>
      </footer>
    </div>
  )
}

const features: {
  icon: LucideIcon
  title: string
  desc: string
  color: 'yellow' | 'pink' | 'blue' | 'green' | 'purple' | 'orange'
}[] = [
  {
    icon: BookOpen,
    title: 'Interactive Lessons',
    desc: 'Rich markdown-rendered lessons with code examples. Learn at your own pace.',
    color: 'yellow',
  },
  {
    icon: Brain,
    title: 'Smart Quizzes',
    desc: 'MCQ and True/False questions with instant grading and attempt history.',
    color: 'pink',
  },
  {
    icon: CodeXml,
    title: 'Real Code Editor',
    desc: 'Write Python code in a Monaco editor and run it against test cases — on the server!',
    color: 'blue',
  },
  {
    icon: ChartColumn,
    title: 'Progress Dashboard',
    desc: 'Track your completion across lessons, quizzes, and coding problems.',
    color: 'green',
  },
  {
    icon: Target,
    title: 'Concept Tagging',
    desc: 'Every question and problem is tagged. See exactly which concepts you need to work on.',
    color: 'purple',
  },
  {
    icon: Zap,
    title: 'Instant Feedback',
    desc: 'Know right away what you got right and wrong. No waiting, no guessing.',
    color: 'orange',
  },
]
