import React from 'react'
import { Sparkles } from 'lucide-react'
import { RARITY_LABEL, RARITY_TAG } from '@/components/gamification/rewardModels'
import type { BadgeRarity } from '@/types/gamification'

/** Small rarity label. The rarity is spelled out, colour only adds emphasis. */
export const RarityTag: React.FC<{ rarity: BadgeRarity; className?: string }> = ({ rarity, className = '' }) => (
  <span
    className={`inline-flex items-center gap-0.5 border border-border-dark px-1.5 py-0.5 font-mono font-bold text-[10px] uppercase leading-none align-middle ${RARITY_TAG[rarity]} ${className}`}
  >
    {rarity === 'legendary' && <Sparkles aria-hidden className="w-2.5 h-2.5 shrink-0" strokeWidth={2.75} />}
    {RARITY_LABEL[rarity]}
  </span>
)
