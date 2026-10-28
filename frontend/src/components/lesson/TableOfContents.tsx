import React, { useEffect, useState } from 'react'
import type { Heading } from '@/lib/slug'

interface Props {
  headings: Heading[]
}

/** Sticky "On this page" list that highlights the section currently being read. */
export const TableOfContents: React.FC<Props> = ({ headings }) => {
  const [active, setActive] = useState<string>(headings[0]?.id ?? '')

  useEffect(() => {
    const elements = headings.map((h) => document.getElementById(h.id)).filter((el): el is HTMLElement => !!el)
    if (elements.length === 0) return
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible.length > 0) setActive(visible[0].target.id)
      },
      { rootMargin: '-80px 0px -65% 0px', threshold: 0 },
    )
    elements.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [headings])

  if (headings.length < 3) return null

  return (
    <nav aria-label="On this page" className="neo-card p-4 text-sm">
      <div className="font-mono font-bold text-xs mb-3 text-text-muted">ON THIS PAGE</div>
      <ul className="space-y-1.5">
        {headings.map((h) => (
          <li key={h.id} className={h.level === 3 ? 'ml-3' : ''}>
            <a
              href={`#${h.id}`}
              onClick={(e) => {
                e.preventDefault()
                document.getElementById(h.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                setActive(h.id)
              }}
              className={`block leading-snug py-0.5 border-l-4 pl-2 transition-colors ${
                active === h.id
                  ? 'border-brand-pink font-bold text-text-primary'
                  : 'border-transparent text-text-muted hover:text-text-primary hover:border-border-dark/30'
              }`}
            >
              {h.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}
