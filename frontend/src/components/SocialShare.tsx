import React from 'react'
import { Link2 } from 'lucide-react'

interface SocialShareProps {
  title: string
  text: string
  url?: string
}

export const SocialShare: React.FC<SocialShareProps> = ({ title, text, url }) => {
  const shareUrl = url || window.location.href

  const shareOnTwitter = () => {
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl)}`
    window.open(twitterUrl, '_blank', 'width=600,height=400')
  }

  const shareOnLinkedIn = () => {
    const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`
    window.open(linkedInUrl, '_blank', 'width=600,height=600')
  }

  const shareOnFacebook = () => {
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`
    window.open(facebookUrl, '_blank', 'width=600,height=400')
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl)
    alert('Link copied to clipboard!')
  }

  return (
    <div className="flex gap-2 items-center">
      <span className="font-mono text-xs text-text-muted mr-2">Share:</span>
      
      <button
        onClick={shareOnTwitter}
        className="w-9 h-9 inline-flex items-center justify-center font-bold border-2 border-border-dark bg-brand-blue hover:bg-brand-blue/80 text-white"
        title="Share on Twitter"
        aria-label="Share on Twitter"
      >
        𝕏
      </button>

      <button
        onClick={shareOnLinkedIn}
        className="w-9 h-9 inline-flex items-center justify-center font-bold border-2 border-border-dark bg-[#0077b5] hover:bg-[#0077b5]/80 text-white"
        title="Share on LinkedIn"
        aria-label="Share on LinkedIn"
      >
        in
      </button>

      <button
        onClick={shareOnFacebook}
        className="w-9 h-9 inline-flex items-center justify-center font-bold border-2 border-border-dark bg-[#1877f2] hover:bg-[#1877f2]/80 text-white"
        title="Share on Facebook"
        aria-label="Share on Facebook"
      >
        f
      </button>

      <button
        onClick={copyToClipboard}
        className="w-9 h-9 inline-flex items-center justify-center font-bold border-2 border-border-dark bg-bg-base text-text-primary hover:bg-brand-yellow/20"
        title="Copy link"
        aria-label="Copy link"
      >
        <Link2 aria-hidden className="w-4 h-4" strokeWidth={2.5} />
      </button>
    </div>
  )
}
