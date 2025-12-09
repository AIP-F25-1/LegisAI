import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface ComplianceResult {
  content: string
  risk_score: number
  issues: Array<{
    type: string
    severity: string
    description: string
    position?: number
  }>
  recommendations: string[]
  compliance_status: string
  analysis?: string
  ai_generated?: boolean
}

interface ComplianceContextType {
  results: ComplianceResult | null
  setResults: (results: ComplianceResult | null) => void
  content: string
  setContent: (content: string) => void
  jurisdiction: string
  setJurisdiction: (jurisdiction: string) => void
  checkGdpr: boolean
  setCheckGdpr: (check: boolean) => void
  checkUsCode: boolean
  setCheckUsCode: (check: boolean) => void
  streamingText: string
  setStreamingText: (text: string) => void
  isStreaming: boolean
  setIsStreaming: (isStreaming: boolean) => void
  complianceHistory: ComplianceResult[]
  clearHistory: () => void
}

const ComplianceContext = createContext<ComplianceContextType | undefined>(undefined)

export const useCompliance = () => {
  const context = useContext(ComplianceContext)
  if (!context) {
    throw new Error('useCompliance must be used within ComplianceProvider')
  }
  return context
}

interface ComplianceProviderProps {
  children: ReactNode
}

export const ComplianceProvider: React.FC<ComplianceProviderProps> = ({ children }) => {
  const [results, setResults] = useState<ComplianceResult | null>(null)
  const [content, setContent] = useState('')
  const [jurisdiction, setJurisdiction] = useState('US')
  const [checkGdpr, setCheckGdpr] = useState(true)
  const [checkUsCode, setCheckUsCode] = useState(true)
  const [streamingText, setStreamingText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [complianceHistory, setComplianceHistory] = useState<ComplianceResult[]>([])

  // Load cached results on mount
  useEffect(() => {
    const cached = sessionStorage.getItem('legisai_compliance_cache')
    if (cached) {
      try {
        const cacheData = JSON.parse(cached)
        if (cacheData.results) {
          setResults(cacheData.results)
          setContent(cacheData.content || '')
          setJurisdiction(cacheData.jurisdiction || 'US')
          setCheckGdpr(cacheData.checkGdpr !== undefined ? cacheData.checkGdpr : true)
          setCheckUsCode(cacheData.checkUsCode !== undefined ? cacheData.checkUsCode : true)
        }
        if (cacheData.history) {
          setComplianceHistory(cacheData.history)
        }
      } catch (e) {
        console.warn('Failed to load cached compliance:', e)
      }
    }
  }, [])

  // Save results to cache whenever they change
  useEffect(() => {
    if (results || content) {
      const cacheData = {
        results: results,
        content: content,
        jurisdiction: jurisdiction,
        checkGdpr: checkGdpr,
        checkUsCode: checkUsCode,
        history: complianceHistory,
        timestamp: new Date().toISOString()
      }
      sessionStorage.setItem('legisai_compliance_cache', JSON.stringify(cacheData))
    }
  }, [results, content, jurisdiction, checkGdpr, checkUsCode, complianceHistory])

  const handleSetResults = (newResults: ComplianceResult | null) => {
    setResults(newResults)
    if (newResults) {
      setComplianceHistory(prev => {
        const exists = prev.some(r => r.content === newResults.content && r.analysis === newResults.analysis)
        if (!exists) {
          return [...prev, newResults]
        }
        return prev
      })
    }
  }

  const clearHistory = () => {
    setComplianceHistory([])
    setResults(null)
    setContent('')
    sessionStorage.removeItem('legisai_compliance_cache')
  }

  return (
    <ComplianceContext.Provider
      value={{
        results,
        setResults: handleSetResults,
        content,
        setContent,
        jurisdiction,
        setJurisdiction,
        checkGdpr,
        setCheckGdpr,
        checkUsCode,
        setCheckUsCode,
        streamingText,
        setStreamingText,
        isStreaming,
        setIsStreaming,
        complianceHistory,
        clearHistory
      }}
    >
      {children}
    </ComplianceContext.Provider>
  )
}

