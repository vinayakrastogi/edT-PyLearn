import { create } from 'zustand'

interface GeneratedModule {
  module: {
    id: string
    title: string
    description: string
    order: number
    icon: string // icon key from ICONS in @/lib/icons
  }
  docs: any[]
  quiz_json: any
  problems: any[]
}

interface GeneratedModuleStore {
  generatedModule: GeneratedModule | null
  setGeneratedModule: (module: GeneratedModule | null) => void
  clearGeneratedModule: () => void
}

export const useGeneratedModuleStore = create<GeneratedModuleStore>((set) => ({
  generatedModule: null,
  setGeneratedModule: (module) => set({ generatedModule: module }),
  clearGeneratedModule: () => set({ generatedModule: null })
}))
