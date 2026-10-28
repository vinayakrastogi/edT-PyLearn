import { apiUrl } from '@/api/url'
import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Lightbulb, Link2, NotebookPen, Sparkles, Upload } from 'lucide-react'
import { Button } from '@/components/Button'
import { useGeneratedModuleStore } from '@/store/generatedModuleStore'

type InputMethod = 'pdf' | 'topic' | 'url' | 'text'

export const GenerativeUploadUI: React.FC = () => {
  const [inputMethod, setInputMethod] = useState<InputMethod>('pdf')
  const [file, setFile] = useState<File | null>(null)
  const [topicInput, setTopicInput] = useState('')
  const [urlInput, setUrlInput] = useState('')
  const [textInput, setTextInput] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const setGeneratedModule = useGeneratedModuleStore(s => s.setGeneratedModule)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0]
      if (selected.type !== 'application/pdf') {
        setError('Please upload a valid PDF file.')
        setFile(null)
      } else {
        setError(null)
        setFile(selected)
      }
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const selected = e.dataTransfer.files[0]
      if (selected.type !== 'application/pdf') {
        setError('Please upload a valid PDF file.')
        setFile(null)
      } else {
        setError(null)
        setFile(selected)
      }
    }
  }

  const canGenerate = () => {
    if (inputMethod === 'pdf') return !!file
    if (inputMethod === 'topic') return topicInput.trim().length > 0
    if (inputMethod === 'url') return urlInput.trim().length > 0
    if (inputMethod === 'text') return textInput.trim().length > 0
    return false
  }

  const handleGenerate = async () => {
    let endpoint = ''
    let body: any = null
    
    setIsGenerating(true)
    setError(null)

    try {
      if (inputMethod === 'pdf') {
        if (!file) return
        endpoint = apiUrl('/api/generate/from-pdf')
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await fetch(endpoint, {
          method: 'POST',
          credentials: 'include',
          body: formData,
        })
        
        if (!response.ok) {
          const errData = await response.json()
          throw new Error(errData.detail || 'Failed to generate content')
        }
        
        const data = await response.json()
        setGeneratedModule(data)
        navigate(`/modules/preview-${Date.now()}`)
        
      } else if (inputMethod === 'topic') {
        if (!topicInput.trim()) {
          setError('Please enter a topic')
          setIsGenerating(false)
          return
        }
        endpoint = apiUrl('/api/generate/from-topic')
        body = { topic: topicInput }
        
      } else if (inputMethod === 'url') {
        if (!urlInput.trim()) {
          setError('Please enter a URL')
          setIsGenerating(false)
          return
        }
        endpoint = apiUrl('/api/generate/from-url')
        body = { url: urlInput }
        
      } else if (inputMethod === 'text') {
        if (!textInput.trim()) {
          setError('Please enter some text')
          setIsGenerating(false)
          return
        }
        endpoint = apiUrl('/api/generate/from-text')
        body = { text: textInput }
      }
      
      // For non-PDF methods
      if (body) {
        const response = await fetch(endpoint, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(body)
        })

        if (!response.ok) {
          const errData = await response.json()
          throw new Error(errData.detail || 'Failed to generate content')
        }

        const data = await response.json()
        setGeneratedModule(data)
        navigate(`/modules/preview-${Date.now()}`)
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg-base eyecandy:bg-gradient-to-br eyecandy:from-white eyecandy:to-green-50 flex items-center justify-center px-6 py-12">
      <div className="max-w-3xl w-full">
        <div className="bg-bg-card eyecandy:bg-white border-4 eyecandy:border-2 border-border-dark eyecandy:border-green-200 p-8 shadow-neo eyecandy:shadow-2xl eyecandy:rounded-3xl text-center">
          
          <h1 className="font-heading font-black text-3xl mb-4 eyecandy:text-candy-green-700 flex items-center justify-center gap-3">
            <Sparkles aria-hidden className="w-7 h-7 shrink-0" strokeWidth={2.25} />
            AI Module Generator
          </h1>
          <p className="text-text-muted eyecandy:text-gray-700 mb-8 font-body">
            Choose your input method and let AI create a complete learning module with docs, quizzes, and coding challenges!
          </p>

          {error && (
            <div className="bg-brand-pink text-white font-bold p-4 border-2 border-border-dark mb-6 animate-shake">
              Error: {error}
            </div>
          )}

          {/* Input Method Tabs */}
          <div className="flex gap-2 mb-6 border-b-2 eyecandy:border-b eyecandy:border-green-200 border-border-dark pb-2">
            {[
              { id: 'pdf' as InputMethod, label: 'PDF Upload', icon: FileText },
              { id: 'topic' as InputMethod, label: 'Topic Input', icon: Lightbulb },
              { id: 'url' as InputMethod, label: 'URL Import', icon: Link2 },
              { id: 'text' as InputMethod, label: 'Text Paste', icon: NotebookPen }
            ].map(method => (
              <button
                key={method.id}
                onClick={() => setInputMethod(method.id)}
                aria-label={method.label}
                aria-pressed={inputMethod === method.id}
                className={`flex-1 inline-flex items-center justify-center gap-1.5 py-3 px-4 font-heading font-bold text-sm border-2 eyecandy:border eyecandy:rounded-xl border-border-dark eyecandy:border-green-300 transition-all duration-300 ${
                  inputMethod === method.id
                    ? 'bg-brand-yellow eyecandy:bg-gradient-to-br eyecandy:from-candy-green-400 eyecandy:to-emerald-500 text-text-primary eyecandy:text-white shadow-neo-sm eyecandy:shadow-lg translate-y-[-2px] eyecandy:scale-105'
                    : 'bg-bg-base eyecandy:bg-white text-text-muted eyecandy:text-gray-700 hover:bg-brand-yellow/20 eyecandy:hover:bg-green-50 eyecandy:hover:scale-105'
                }`}
              >
                <method.icon aria-hidden className="w-4 h-4 shrink-0" />
                {method.label.split(' ')[1]}
              </button>
            ))}
          </div>

          {/* PDF Upload */}
          {inputMethod === 'pdf' && (
            <div className="flex flex-col items-center gap-6">
              <input
                type="file"
                accept="application/pdf"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileChange}
              />
              
              <div 
                className={`w-full border-4 eyecandy:border-2 border-dashed eyecandy:border-solid border-border-dark eyecandy:border-green-300 eyecandy:rounded-2xl p-12 cursor-pointer transition-all duration-300 ${
                  isDragging 
                    ? 'bg-brand-yellow/40 eyecandy:bg-green-100 eyecandy:scale-105' 
                    : 'bg-brand-yellow/10 eyecandy:bg-gradient-to-br eyecandy:from-green-50 eyecandy:to-emerald-50 hover:bg-brand-yellow/20 eyecandy:hover:shadow-xl eyecandy:hover:scale-105'
                }`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {file ? (
                  <div>
                    <FileText aria-hidden className="w-10 h-10 mx-auto mb-2" />
                    <div className="font-bold text-xl eyecandy:text-candy-green-800">{file.name}</div>
                    <div className="text-sm text-text-muted eyecandy:text-gray-600 mt-1">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>
                ) : (
                  <div>
                    <Upload aria-hidden className="w-10 h-10 mx-auto mb-2 text-text-muted" />
                    <div className="font-bold text-xl text-text-muted eyecandy:text-gray-700">
                      Click or Drag PDF here to upload
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Topic Input */}
          {inputMethod === 'topic' && (
            <div className="text-left">
              <label className="block font-heading font-bold mb-2 eyecandy:text-candy-green-700">
                What topic would you like to learn?
              </label>
              <input
                type="text"
                placeholder="e.g., Machine Learning Basics, Web Scraping, Django REST APIs"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                className="neo-input mb-4"
              />
              <p className="flex items-start gap-1.5 text-xs text-text-muted eyecandy:text-gray-600 font-mono">
                <Lightbulb aria-hidden className="w-3.5 h-3.5 shrink-0 mt-px" />
                Tip: Be specific! Include skill level (beginner/intermediate/advanced) for better results.
              </p>
            </div>
          )}

          {/* URL Import */}
          {inputMethod === 'url' && (
            <div className="text-left">
              <label className="block font-heading font-bold mb-2 eyecandy:text-candy-green-700">
                Enter URL to documentation or tutorial
              </label>
              <input
                type="url"
                placeholder="https://docs.python.org/3/tutorial/..."
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="neo-input mb-4"
              />
              <p className="flex items-start gap-1.5 text-xs text-text-muted eyecandy:text-gray-600 font-mono">
                <Link2 aria-hidden className="w-3.5 h-3.5 shrink-0 mt-px" />
                Supported: Public documentation, tutorials, blog posts
              </p>
            </div>
          )}

          {/* Text Paste */}
          {inputMethod === 'text' && (
            <div className="text-left">
              <label className="block font-heading font-bold mb-2 eyecandy:text-candy-green-700">
                Paste your content (Markdown supported)
              </label>
              <textarea
                placeholder="Paste your learning material here..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                rows={12}
                className="neo-input mb-4 font-mono text-sm resize-none"
              />
              <p className="flex items-start gap-1.5 text-xs text-text-muted eyecandy:text-gray-600 font-mono">
                <NotebookPen aria-hidden className="w-3.5 h-3.5 shrink-0 mt-px" />
                Supports: Markdown, plain text, code snippets
              </p>
            </div>
          )}

          {/* Generate Button */}
          <Button 
            color="blue" 
            size="lg" 
            className="w-full mt-6"
            disabled={!canGenerate() || isGenerating}
            onClick={handleGenerate}
          >
            {isGenerating ? (
              <span className="flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generating module... (this may take a minute)
              </span>
            ) : (
              <>
                <Sparkles aria-hidden className="w-5 h-5" /> Generate Module
              </>
            )}
          </Button>
          
        </div>
      </div>
    </div>
  )
}
