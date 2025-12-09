import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface DraftingResult {
  query: string
  draft_content: string
  clauses: Array<{
    type: string
    content: string
  }>
  suggestions: string[]
  confidence_score: number
}

interface DraftingContextType {
  results: DraftingResult | null
  setResults: (results: DraftingResult | null) => void
  query: string
  setQuery: (query: string) => void
  documentType: string
  setDocumentType: (type: string) => void
  editingContent: string
  setEditingContent: (content: string) => void
  streamingText: string
  setStreamingText: (text: string) => void
  isStreaming: boolean
  setIsStreaming: (isStreaming: boolean) => void
  draftingHistory: DraftingResult[]
  clearHistory: () => void
}

const DraftingContext = createContext<DraftingContextType | undefined>(undefined)

export const useDrafting = () => {
  const context = useContext(DraftingContext)
  if (!context) {
    throw new Error('useDrafting must be used within DraftingProvider')
  }
  return context
}

interface DraftingProviderProps {
  children: ReactNode
}

export const DraftingProvider: React.FC<DraftingProviderProps> = ({ children }) => {
  const [results, setResults] = useState<DraftingResult | null>(null)
  const [query, setQuery] = useState('')
  const [documentType, setDocumentType] = useState('contract')
  const [editingContent, setEditingContent] = useState('')
  const [streamingText, setStreamingText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [draftingHistory, setDraftingHistory] = useState<DraftingResult[]>([])

  // Load cached results on mount
  useEffect(() => {
    const cached = sessionStorage.getItem('legisai_drafting_cache')
    if (cached) {
      try {
        const cacheData = JSON.parse(cached)
        if (cacheData.results) {
          setResults(cacheData.results)
          setQuery(cacheData.query || '')
          setDocumentType(cacheData.documentType || 'contract')
          setEditingContent(cacheData.editingContent || cacheData.results.draft_content || '')
        }
        if (cacheData.history) {
          setDraftingHistory(cacheData.history)
        }
      } catch (e) {
        console.warn('Failed to load cached drafting:', e)
      }
    }
  }, [])

  // Save results to cache whenever they change
  useEffect(() => {
    if (results || editingContent) {
      const cacheData = {
        results: results,
        query: query,
        documentType: documentType,
        editingContent: editingContent,
        history: draftingHistory,
        timestamp: new Date().toISOString()
      }
      sessionStorage.setItem('legisai_drafting_cache', JSON.stringify(cacheData))
    }
  }, [results, query, documentType, editingContent, draftingHistory])

  const handleSetResults = (newResults: DraftingResult | null) => {
    setResults(newResults)
    if (newResults) {
      setEditingContent(newResults.draft_content)
      setDraftingHistory(prev => {
        const exists = prev.some(r => r.query === newResults.query && r.draft_content === newResults.draft_content)
        if (!exists) {
          return [...prev, newResults]
        }
        return prev
      })
    }
  }

  const clearHistory = () => {
    setDraftingHistory([])
    setResults(null)
    setQuery('')
    setEditingContent('')
    sessionStorage.removeItem('legisai_drafting_cache')
  }

  return (
    <DraftingContext.Provider
      value={{
        results,
        setResults: handleSetResults,
        query,
        setQuery,
        documentType,
        setDocumentType,
        editingContent,
        setEditingContent,
        streamingText,
        setStreamingText,
        isStreaming,
        setIsStreaming,
        draftingHistory,
        clearHistory
      }}
    >
      {children}
    </DraftingContext.Provider>
  )
}

