import React, { useState } from 'react'
import { Search, FileText, Clock, CheckCircle, X, Edit2, History, Trash2 } from 'lucide-react'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'
import { handleStreamingRequest } from '../utils/streaming'
import { useTimeline } from '../contexts/TimelineContext'
import { useResearch } from '../contexts/ResearchContext'
import HITLPanel from '../components/HITLPanel'

// Component to format research summary with proper structure
const FormattedResearchSummary: React.FC<{ summary: string }> = ({ summary }) => {
  const formatSummary = (text: string) => {
    // Split by major sections (look for ALL CAPS headers)
    const sections = text.split(/(?=^[A-Z][A-Z\s]+:)/m).filter(section => section.trim())
    
    return sections.map((section, index) => {
      const lines = section.trim().split('\n')
      const title = lines[0]
      const content = lines.slice(1).join('\n').trim()
      
      // Check if this is a main section header (ALL CAPS)
      if (title.match(/^[A-Z][A-Z\s]+:$/)) {
        return (
          <div key={index} className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3 border-b border-white/20 pb-2 bg-white/10 px-3 py-2">
              {title.replace(':', '')}
            </h3>
            <div className="ml-4">
              {formatContent(content)}
            </div>
          </div>
        )
      }
      
      // Regular content
      return (
        <div key={index} className="mb-4">
          {formatContent(section)}
        </div>
      )
    })
  }
  
  const formatContent = (content: string) => {
    const lines = content.split('\n').filter(line => line.trim())
    
    return lines.map((line, index) => {
      const trimmedLine = line.trim()
      
      // Bullet points
      if (trimmedLine.startsWith('•') || trimmedLine.startsWith('-')) {
        return (
          <div key={index} className="flex items-start mb-2">
            <span className="text-white/80 mr-2 mt-1">•</span>
            <span className="text-white/90">{trimmedLine.substring(1).trim()}</span>
          </div>
        )
      }
      
      // Numbered lists
      if (trimmedLine.match(/^\d+\./)) {
        return (
          <div key={index} className="flex items-start mb-2">
            <span className="text-white/80 mr-2 mt-1 font-medium">{trimmedLine.split('.')[0]}.</span>
            <span className="text-white/90">{trimmedLine.substring(trimmedLine.indexOf('.') + 1).trim()}</span>
          </div>
        )
      }
      
      // Regular paragraphs
      if (trimmedLine) {
        return (
          <p key={index} className="text-white/90 mb-3 leading-relaxed">
            {trimmedLine}
          </p>
        )
      }
      
      return null
    })
  }
  
  return (
    <div className="space-y-4">
      {formatSummary(summary)}
    </div>
  )
}

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

const Research: React.FC = () => {
  const { addToTimeline, cacheResponse } = useTimeline()
  const {
    results,
    setResults,
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
  } = useResearch()
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [editedQuery, setEditedQuery] = useState('')
  const [showHistory, setShowHistory] = useState(false)

  const stopStreaming = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
    setIsStreaming(false)
    toast('Streaming stopped')
  }

  const handleSearchStreaming = async (e: React.FormEvent) => {
    e.preventDefault()
    const searchQuery = editedQuery.trim() || query.trim()
    if (!searchQuery) return

    // Create new abort controller
    const controller = new AbortController()
    setAbortController(controller)
    setResults(null)
    setIsLoading(true)

    try {
      await handleStreamingRequest(
        'research/stream',
        {
          query: searchQuery,
          max_results: 10,
          similarity_threshold: 0.7
        },
        setStreamingText,
        setIsStreaming,
        async (fullText) => {
          // After streaming completes, fetch the full results with documents
          try {
            setIsLoading(true)
            const response = await apiClient.post('/research', {
              query: searchQuery,
              max_results: 10,
              similarity_threshold: 0.3
            })
            
            const researchData = response.data
            
            const researchSummary = (fullText && fullText.length > 100) ? fullText : (researchData.summary || fullText)
            const resultData = {
              query: searchQuery,
              documents: researchData.documents || [],
              summary: researchSummary,
              confidence_score: researchData.confidence_score || 0.88,
              ai_generated: researchData.ai_generated !== false
            }
            setResults(resultData)
            setQuery(searchQuery)
            setEditedQuery('')
            
            // Cache response and add to timeline
            cacheResponse('research', resultData, searchQuery, {
              timestamp: new Date().toISOString(),
              confidence_score: resultData.confidence_score
            })
            
            if (researchSummary.length > 50) {
              await addToTimeline(`research_${Date.now()}`, researchSummary, {
                title: `Research: ${searchQuery.substring(0, 50)}`,
                type: 'research',
                query: searchQuery,
                timestamp: new Date().toISOString()
              }, resultData)
            }
            
            const docCount = researchData.documents?.length || 0
            const apiCount = researchData.api_results_count || 0
            const vectorCount = researchData.vector_store_results_count || 0
            
            if (docCount > 0) {
              toast.success(`Research completed! Found ${docCount} relevant documents${apiCount > 0 ? ` (${apiCount} from CourtListener API)` : ''}`)
            } else {
              toast.success('Research completed!')
            }
          } catch (error: any) {
            // If fetching documents fails, at least show the streamed summary
            console.error('Error fetching documents:', error)
            console.error('Error details:', error.response?.data || error.message)
            
            // Try to parse error response
            let errorMessage = 'Failed to fetch documents'
            if (error.response?.data?.detail) {
              errorMessage = error.response.data.detail
            } else if (error.message) {
              errorMessage = error.message
            }
            
            toast.error(`Error: ${errorMessage}`)
            
          setResults({
            query: searchQuery,
            documents: [],
            summary: fullText,
            confidence_score: 0.88,
            ai_generated: true
          })
          setQuery(searchQuery)
          setEditedQuery('')
            
            // Show error but still display summary
            toast.error('Could not fetch documents, but summary is available')
          } finally {
            setIsLoading(false)
          }
        },
        controller
      )
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('❌ Streaming error:', error)
        toast.error('Research failed. Please try again.')
      }
      setIsLoading(false)
    } finally {
      setAbortController(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white">Legal Research</h1>
        <p className="mt-2 text-white/80">
          AI-powered legal research with precedent analysis and case law retrieval
        </p>
      </div>

      {/* Search Form */}
      <div className="liquid-glass-card glass-content p-8 md:p-12">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl md:text-3xl font-semibold text-white">Research Query</h2>
          <div className="flex gap-2">
            {researchHistory.length > 0 && (
              <>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="glass-button flex items-center px-3 py-1 text-sm"
                >
                  <History className="h-4 w-4 mr-1" />
                  History ({researchHistory.length})
                </button>
                <button
                  onClick={clearHistory}
                  className="glass-button flex items-center px-3 py-1 text-sm bg-red-500/20 border-red-500/30 hover:bg-red-500/30"
                >
                  <Trash2 className="h-4 w-4 mr-1" />
                  Clear
                </button>
              </>
            )}
          </div>
        </div>

        {/* History Panel */}
        {showHistory && researchHistory.length > 0 && (
          <div className="mb-4 p-4 glass-panel max-h-60 overflow-y-auto">
            <h3 className="text-sm font-medium text-white mb-2">Previous Research</h3>
            <div className="space-y-2">
              {researchHistory.map((item, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setResults(item)
                    setQuery(item.query)
                    setShowHistory(false)
                  }}
                  className="w-full text-left p-2 liquid-glass-card glass-content hover:scale-[1.02] transition-all"
                >
                  <p className="text-sm font-medium text-white">{item.query}</p>
                  <p className="text-xs text-white/70 mt-1 line-clamp-2">{item.summary.substring(0, 100)}...</p>
                </button>
              ))}
            </div>
          </div>
        )}

        <form onSubmit={handleSearchStreaming} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-white mb-2">
              Research Query
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-white/60" />
              <input
                type="text"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your legal research query..."
                className="glass-input w-full pl-10 pr-4 py-3"
                disabled={isStreaming}
              />
            </div>
          </div>
          
          {/* Edit Query */}
          {!isStreaming && results && (
            <div className="border-t border-white/20 pt-4">
              <label htmlFor="edit-query" className="block text-sm font-medium text-white mb-2">
                Edit & Re-search
              </label>
              <div className="relative">
                <Edit2 className="absolute left-3 top-3 h-5 w-5 text-white/60" />
                <input
                  type="text"
                  id="edit-query"
                  value={editedQuery}
                  onChange={(e) => setEditedQuery(e.target.value)}
                  placeholder={query}
                  className="glass-input w-full pl-10 pr-4 py-2 text-sm"
                />
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isStreaming || !(editedQuery.trim() || query.trim())}
              className="glass-button flex-1 py-3 px-4 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isStreaming ? (
                <>
                  <Clock className="h-5 w-5 mr-2 animate-spin" />
                  Researching...
                </>
              ) : (
                <>
                  <Search className="h-5 w-5 mr-2" />
                  {results ? 'Re-search' : 'Search Legal Database'}
                </>
              )}
            </button>
            
            {isStreaming && (
              <button
                type="button"
                onClick={stopStreaming}
                className="glass-button py-3 px-4 bg-red-500/20 border-red-500/30 hover:bg-red-500/30 flex items-center justify-center"
              >
                <X className="h-5 w-5 mr-2" />
                Stop
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Streaming Results */}
      {isStreaming && streamingText && (
        <div className="glass-panel p-6">
          <div className="flex items-center mb-4">
            <h2 className="text-xl font-semibold text-white">Generating Research...</h2>
            <div className="ml-auto flex items-center text-sm text-white/80">
              <span className="h-2 w-2 bg-green-400 rounded-full animate-pulse mr-2"></span>
              Live
            </div>
          </div>
          <div className="liquid-glass-card glass-content p-6 max-h-[600px] overflow-y-auto">
            <div className="text-white prose prose-invert max-w-none">
              <MarkdownRenderer content={streamingText} />
            </div>
            <span className="inline-block w-2 h-5 bg-white animate-pulse ml-1">▋</span>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && !results && !isStreaming && (
        <div className="glass-panel p-6">
          <div className="flex flex-col items-center justify-center py-12">
            <Clock className="h-12 w-12 text-white animate-spin mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">Generating Research Results...</h3>
            <p className="text-sm text-white/80 text-center max-w-md">
              Our AI is analyzing your query and conducting comprehensive legal research. 
              This may take up to 10 minutes depending on the complexity of your query.
            </p>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="p-6">
            <div className="flex items-center mb-4">
              <CheckCircle className="h-6 w-6 text-green-400 mr-2" />
              <h2 className="text-xl font-semibold text-white">Research Summary</h2>
              <span className="ml-auto text-sm text-white/80">
                Confidence: {Math.round(results.confidence_score * 100)}%
              </span>
            </div>
            <div className="liquid-glass-card glass-content p-8 md:p-12">
              <div className="max-h-[600px] overflow-y-auto relative">
                <div className="text-white prose prose-invert max-w-none p-4">
                  <MarkdownRenderer content={results.summary} />
                </div>
              </div>
            </div>
            
            {/* HITL Panel */}
            <HITLPanel
              featureType="research"
              originalOutput={results}
              onAccept={() => {
                toast.success('Research output accepted')
              }}
              onReject={() => {
                toast.success('Research output rejected - feedback recorded')
              }}
              onEdit={(editedContent) => {
                setResults({
                  ...results,
                  summary: editedContent
                })
                toast.success('Research output edited')
              }}
            />
          </div>

          {/* Documents */}
          <div className="liquid-glass-card glass-content p-8 md:p-12">
            <h2 className="text-xl font-semibold text-white mb-4">
              Relevant Documents ({results.documents.length})
            </h2>
            <div className="space-y-4">
              {results.documents.map((doc, index) => (
                <div
                  key={doc.id}
                  className="p-4 hover:scale-[1.01] transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-white/60 mr-2" />
                      <span className="text-sm font-medium text-white">
                        Document {doc.id}
                      </span>
                    </div>
                    <span className="text-sm text-white/80">
                      Relevance: {Math.round(doc.score * 100)}%
                    </span>
                  </div>
                  <p className="text-white/90 text-sm leading-relaxed">
                    {doc.content}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Query Info */}
          <div className="glass-panel p-4">
            <h3 className="text-sm font-medium text-white mb-2">Research Query</h3>
            <p className="text-white/90">{results.query}</p>
          </div>
        </div>
      )}

      {/* Example Queries */}
      {!results && (
        <div className="liquid-glass-card glass-content p-8 md:p-12">
          <h3 className="text-2xl md:text-3xl font-medium text-white mb-6">Example Research Queries</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              "What are the requirements for a valid contract?",
              "GDPR compliance requirements for data processing",
              "Employment law regarding termination procedures",
              "Intellectual property rights in software development",
              "Liability limitations in service agreements",
              "Dispute resolution mechanisms in commercial contracts"
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setQuery(example)}
                className="text-left p-3 liquid-glass-card glass-content hover:scale-[1.02] transition-all"
              >
                <span className="text-sm text-white">{example}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Research
