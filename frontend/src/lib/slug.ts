/** Turn heading text into a stable anchor id (shared by the headings and the table of contents). */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[`*_]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
}

export interface Heading {
  level: 2 | 3
  text: string
  id: string
}

/** Extract ## / ### headings from markdown, ignoring anything inside code fences. */
export function extractHeadings(markdown: string): Heading[] {
  const headings: Heading[] = []
  let inFence = false
  for (const line of markdown.split('\n')) {
    if (line.startsWith('```')) {
      inFence = !inFence
      continue
    }
    if (inFence) continue
    const m = /^(#{2,3})\s+(.*)$/.exec(line)
    if (m) {
      const text = m[2].replace(/[`*_]/g, '').trim()
      headings.push({ level: m[1].length as 2 | 3, text, id: slugify(text) })
    }
  }
  return headings
}
