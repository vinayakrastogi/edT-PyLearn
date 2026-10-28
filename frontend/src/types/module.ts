export interface User {
  id: number
  email: string
  full_name: string
  role?: 'student' | 'faculty'
  last_accessed_path: string | null
  last_accessed_title: string | null
  created_at: string
}

export interface ModuleMeta {
  id: string
  title: string
  description: string
  order: number
  icon: string // icon key from ICONS in @/lib/icons (e.g. "terminal"), never an emoji
  doc_count: number
  problem_count: number
  is_generative: boolean
}

export interface DocMeta {
  id: string
  title: string
  order: number
  concepts: string[]
}

export interface ProblemMeta {
  id: string
  title: string
  concepts: string[]
}

export interface ModuleDetail {
  id: string
  title: string
  description: string
  order: number
  icon: string // icon key from ICONS in @/lib/icons
  docs: DocMeta[]
  quiz_id: string | null
  problems: ProblemMeta[]
  is_generative: boolean
}

export interface DocPage {
  id: string
  title: string
  order: number
  concepts: string[]
  content_md: string
  read_minutes: number
}
