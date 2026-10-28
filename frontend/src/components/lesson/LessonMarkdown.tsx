import React from 'react'
import ReactMarkdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CircleAlert, FlaskConical, Info, Lightbulb, PartyPopper, TriangleAlert, type LucideIcon } from 'lucide-react'
import { CodeBlock } from './CodeBlock'
import { Mascot, type MascotMood } from '@/components/Mascot'
import { slugify } from '@/lib/slug'
import { IconTile } from '@/lib/icons'

/* eslint-disable @typescript-eslint/no-explicit-any */

/** Plain text of a hast node (used for headings, callout labels and code blocks). */
const nodeText = (node: any): string => {
  if (!node) return ''
  if (node.type === 'text') return node.value ?? ''
  return (node.children ?? []).map(nodeText).join('')
}

const reactText = (children: React.ReactNode): string =>
  React.Children.toArray(children)
    .map((c) => (typeof c === 'string' ? c : React.isValidElement(c) ? reactText((c.props as any).children) : ''))
    .join('')

type TileColor = NonNullable<React.ComponentProps<typeof IconTile>['color']>

/**
 * Callout styles chosen from the bold label at the start of a blockquote, e.g. "**Tip:**".
 * Detection is text-based only; a callout shows either Pip (mood) or an icon tile.
 */
type Callout = { match: RegExp; label: string; box: string } & (
  | { mood: MascotMood }
  | { icon: LucideIcon; tile: TileColor }
)
const CALLOUTS: Callout[] = [
  { match: /^pip says/i, label: 'Pip says', box: 'bg-brand-green/15 border-brand-green', mood: 'happy' },
  { match: /^tip/i, label: 'Tip', box: 'bg-brand-yellow/30 border-brand-yellow', icon: Lightbulb, tile: 'yellow' },
  { match: /^(warning|caution|danger)/i, label: 'Warning', box: 'bg-brand-orange/15 border-brand-orange', icon: TriangleAlert, tile: 'orange' },
  { match: /^important/i, label: 'Important', box: 'bg-brand-pink/15 border-brand-pink', icon: CircleAlert, tile: 'pink' },
  { match: /^(fun fact|did you know)/i, label: 'Fun fact', box: 'bg-brand-purple/15 border-brand-purple', icon: PartyPopper, tile: 'purple' },
  { match: /^(sandbox|not runnable|setup)/i, label: 'Heads up', box: 'bg-brand-blue/15 border-brand-blue', icon: FlaskConical, tile: 'blue' },
]
const DEFAULT_CALLOUT: Callout = { match: /./, label: '', box: 'bg-brand-blue/10 border-brand-blue', icon: Info, tile: 'blue' }

const components: Components = {
  pre({ node, children }) {
    const codeNode: any = (node as any)?.children?.find((c: any) => c.tagName === 'code')
    if (!codeNode) return <pre>{children}</pre>
    const className: string[] = codeNode.properties?.className ?? []
    const language = (className.find((c) => c.startsWith('language-')) ?? 'language-text').replace('language-', '')
    const meta: string = codeNode.data?.meta ?? ''
    return <CodeBlock code={nodeText(codeNode)} language={language} meta={meta} />
  },

  h2({ children }) {
    const id = slugify(reactText(children))
    return (
      <h2 id={id} className="group">
        {children}
        <a href={`#${id}`} aria-label="Link to this section" className="ml-2 no-underline opacity-0 group-hover:opacity-40 text-text-muted">#</a>
      </h2>
    )
  },
  h3({ children }) {
    return <h3 id={slugify(reactText(children))}>{children}</h3>
  },

  blockquote({ node, children }) {
    const firstPara: any = (node as any)?.children?.find((c: any) => c.tagName === 'p')
    const firstStrong: any = firstPara?.children?.find((c: any) => c.tagName === 'strong')
    const label = firstStrong ? nodeText(firstStrong).replace(/[:.]$/, '') : ''
    const callout = CALLOUTS.find((c) => c.match.test(label)) ?? DEFAULT_CALLOUT
    return (
      <aside className={`lesson-callout not-italic border-2 border-l-8 ${callout.box} px-4 py-3 my-5 flex gap-3 items-start`}>
        {'mood' in callout ? (
          <Mascot mood={callout.mood} size={44} className="shrink-0" />
        ) : (
          <IconTile icon={callout.icon} color={callout.tile} size="sm" className="mt-0.5" />
        )}
        <div className="min-w-0 flex-1 text-text-primary">{children}</div>
      </aside>
    )
  },

  a({ href, children }) {
    const external = !!href && /^https?:\/\//.test(href)
    return (
      <a href={href} {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}>
        {children}
      </a>
    )
  },

  table({ children }) {
    return (
      <div className="overflow-x-auto mb-4">
        <table>{children}</table>
      </div>
    )
  },
}

interface Props {
  markdown: string
  className?: string
}

/**
 * Renders a lesson. Raw HTML in the markdown is NOT rendered (react-markdown escapes it), so
 * lessons, including AI-generated ones, cannot inject scripts.
 */
export const LessonMarkdown: React.FC<Props> = ({ markdown, className = '' }) => (
  <article className={`neo-prose ${className}`}>
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {markdown}
    </ReactMarkdown>
  </article>
)
