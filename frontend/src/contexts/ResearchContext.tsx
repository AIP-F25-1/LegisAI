import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface ResearchResult {
  query: string
  documents: Array<{
    id: number | string
    score: number
    content: string
  }>
  summary: string
  confidence_score: number
  ai_generated?: boolean
}

interface ResearchContextType {
  results: ResearchResult | null
  setResults: (results: ResearchResult | null) => void
  query: string
  setQuery: (query: string) => void
  streamingText: string
  setStreamingText: (text: string) => void
  isStreaming: boolean
  setIsStreaming: (isStreaming: boolean) => void
  isLoading: boolean
  setIsLoading: (isLoading: boolean) => void
  researchHistory: ResearchResult[]
  clearHistory: () => void
}

const ResearchContext = createContext<ResearchContextType | undefined>(undefined)

export const useResearch = () => {
  const context = useContext(ResearchContext)
  if (!context) {
    throw new Error('useResearch must be used within ResearchProvider')
  }
  return context
}

interface ResearchProviderProps {
  children: ReactNode
}

export const ResearchProvider: React.FC<ResearchProviderProps> = ({ children }) => {
  const [results, setResults] = useState<ResearchResult | null>(null)
  const [query, setQuery] = useState('')
  const [streamingText, setStreamingText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [researchHistory, setResearchHistory] = useState<ResearchResult[]>([])

  // Load cached results on mount
  useEffect(() => {
    const cached = sessionStorage.getItem('legisai_research_cache')
    if (cached) {
      try {
        const cacheData = JSON.parse(cached)
        if (cacheData.results) {
          setResults(cacheData.results)
          setQuery(cacheData.query || '')
        }
        if (cacheData.history) {
          setResearchHistory(cacheData.history)
        }
      } catch (e) {
        console.warn('Failed to load cached research:', e)
      }
    }
  }, [])

  // Save results to cache whenever they change
  useEffect(() => {
    if (results) {
      const cacheData = {
        results: results,
        query: query,
        history: researchHistory,
        timestamp: new Date().toISOString()
      }
      sessionStorage.setItem('legisai_research_cache', JSON.stringify(cacheData))
    }
  }, [results, query, researchHistory])

  const handleSetResults = (newResults: ResearchResult | null) => {
    setResults(newResults)
    if (newResults) {
      setResearchHistory(prev => {
        // Avoid duplicates
        const exists = prev.some(r => r.query === newResults.query && r.summary === newResults.summary)
        if (!exists) {
          return [...prev, newResults]
        }
        return prev
      })
    }
  }

  const clearHistory = () => {
    setResearchHistory([])
    setResults(null)
    setQuery('')
    sessionStorage.removeItem('legisai_research_cache')
  }

  return (
    <ResearchContext.Provider
      value={{
        results,
        setResults: handleSetResults,
        query,
        setQuery,
        streamingText,
        setStreamingText,
        isStreaming,
        setIsStreaming,
        isLoading,
        setIsLoading,
        researchHistory,
        clearHistory
      }}
    >
      {children}
    </ResearchContext.Provider>
  )
}

