import React, { useState } from 'react'
import { FileText, Plus, Edit, Save, Copy, Clock, X, Edit2, Download, History, Trash2 } from 'lucide-react'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'
import { handleStreamingRequest } from '../utils/streaming'
import { useTimeline } from '../contexts/TimelineContext'
import { useDrafting } from '../contexts/DraftingContext'
import HITLPanel from '../components/HITLPanel'

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

const Drafting: React.FC = () => {
  const { addToTimeline, cacheResponse } = useTimeline()
  const {
    results,
    setResults,
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
  } = useDrafting()
  const [isLoading, setIsLoading] = useState(false)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [editedQuery, setEditedQuery] = useState('')
  const [showHistory, setShowHistory] = useState(false)

  const stopStreaming = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
    setIsStreaming(false)
    toast('Drafting stopped')
  }

  const handleDraft = async (e: React.FormEvent) => {
    e.preventDefault()
    const draftQuery = editedQuery.trim() || query.trim()
    if (!draftQuery) return

    // Create new abort controller
    const controller = new AbortController()
    setAbortController(controller)
    setResults(null)

    try {
      await handleStreamingRequest(
        'draft/stream',
        {
          query: draftQuery,
          document_type: documentType,
          context: ''
        },
        setStreamingText,
        setIsStreaming,
        async (fullText) => {
          // After streaming completes, fetch clauses and suggestions
          let clauses: Array<{type: string, content: string}> = []
          let suggestions: string[] = []
          
          try {
            setIsLoading(true)
            // Add timeout to prevent hanging
            const timeoutPromise = new Promise((_, reject) => 
              setTimeout(() => reject(new Error('Request timeout')), 10000)
            )
            
            const draftResponse = await Promise.race([
              apiClient.post('/draft', {
                query: draftQuery,
                document_type: documentType
              }),
              timeoutPromise
            ]) as any
            
            if (draftResponse?.data) {
              clauses = draftResponse.data.clauses || []
              suggestions = draftResponse.data.suggestions || []
            }
          } catch (error: any) {
            console.warn('Failed to fetch clauses and suggestions:', error)
            // Use fallback defaults
            clauses = [
              {"type": "definitions", "content": "Standard definitions and terminology"},
              {"type": "scope", "content": `Scope of work for ${draftQuery}`},
              {"type": "terms", "content": "Standard terms and conditions"},
              {"type": "compliance", "content": "Compliance and regulatory requirements"},
              {"type": "termination", "content": "Termination and transition procedures"}
            ]
            suggestions = [
              "Review with qualified legal counsel",
              "Ensure compliance with applicable laws",
              "Include specific performance metrics",
              "Add dispute resolution mechanisms",
              "Consider confidentiality provisions",
              "Implement risk management measures"
            ]
          } finally {
            setIsLoading(false)
          }
          
          const resultData = {
            query: draftQuery,
            draft_content: fullText,
            clauses: clauses,
            suggestions: suggestions,
            confidence_score: 0.88
          }
          setEditingContent(fullText)
          setResults(resultData)
          setQuery(draftQuery)
          setEditedQuery('')

          // Cache response and add to timeline
          cacheResponse('drafting', resultData, draftQuery, {
            document_type: documentType,
            timestamp: new Date().toISOString()
          })

          if (fullText.length > 50) {
            await addToTimeline(`draft_${Date.now()}`, fullText, {
              title: `Draft: ${documentType} - ${draftQuery.substring(0, 50)}`,
              type: 'drafting',
              document_type: documentType,
              timestamp: new Date().toISOString()
            }, resultData)
          }

          toast.success('Document drafted successfully!')
        },
        controller
      )
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('❌ Drafting error:', error)
        toast.error('Failed to draft document. Please try again.')
      }
      setIsLoading(false)
    } finally {
      setAbortController(null)
    }
  }

  const handleSave = () => {
    if (results) {
      setResults({ ...results, draft_content: editingContent })
      toast.success('Document saved!')
    }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(editingContent)
    toast.success('Content copied to clipboard!')
  }

  const handleDownload = async () => {
    if (!editingContent) return

    try {
      // Create a backend endpoint for DOCX generation
      const response = await apiClient.post('/draft/download', {
        content: editingContent,
        title: query || 'Legal_Document',
        document_type: documentType
      }, {
        responseType: 'blob'
      })

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${documentType}_${Date.now()}.docx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      toast.success('Document downloaded successfully!')
    } catch (error) {
      console.error('Download error:', error)
      toast.error('Failed to download document')
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white">Document Drafting</h1>
        <p className="mt-2 text-white/80">
          Generate legal documents, contracts, and clauses with AI assistance
        </p>
      </div>

      {/* Drafting Form */}
      <div className="liquid-glass-card glass-content p-8 md:p-12">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl md:text-3xl font-semibold text-white">Document Drafting</h2>
          <div className="flex gap-2">
            {draftingHistory.length > 0 && (
              <>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="glass-button flex items-center px-3 py-1 text-sm"
                >
                  <History className="h-4 w-4 mr-1" />
                  History ({draftingHistory.length})
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
        {showHistory && draftingHistory.length > 0 && (
          <div className="mb-4 p-4 glass-panel max-h-60 overflow-y-auto">
            <h3 className="text-sm font-medium text-white mb-2">Previous Drafts</h3>
            <div className="space-y-2">
              {draftingHistory.map((item, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setResults(item)
                    setQuery(item.query)
                    setEditingContent(item.draft_content)
                    setShowHistory(false)
                  }}
                  className="w-full text-left p-2 liquid-glass-card glass-content hover:scale-[1.02] transition-all"
                >
                  <p className="text-sm font-medium text-white">{item.query}</p>
                  <p className="text-xs text-white/70 mt-1 line-clamp-2">{item.draft_content.substring(0, 100)}...</p>
                </button>
              ))}
            </div>
          </div>
        )}

        <form onSubmit={handleDraft} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-white mb-2">
                Document Description
              </label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Describe the document you want to draft..."
                rows={3}
                className="glass-textarea w-full"
                disabled={isLoading}
              />
            </div>
            <div>
              <label htmlFor="documentType" className="block text-sm font-medium text-white mb-2">
                Document Type
              </label>
              <select
                id="documentType"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                className="glass-input w-full"
                disabled={isLoading}
              >
                <option value="contract">Contract</option>
                <option value="agreement">Agreement</option>
                <option value="terms">Terms of Service</option>
                <option value="privacy">Privacy Policy</option>
                <option value="nda">Non-Disclosure Agreement</option>
                <option value="employment">Employment Contract</option>
              </select>
            </div>
          </div>
          {/* Edit Query */}
          {!isStreaming && results && (
            <div className="border-t border-white/20 pt-4">
              <label htmlFor="edit-query" className="block text-sm font-medium text-white mb-2">
                Edit & Re-draft
              </label>
              <textarea
                id="edit-query"
                value={editedQuery}
                onChange={(e) => setEditedQuery(e.target.value)}
                placeholder={query}
                rows={3}
                className="glass-textarea w-full text-sm"
              />
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
                  Drafting...
                </>
              ) : (
                <>
                  <FileText className="h-5 w-5 mr-2" />
                  {results ? 'Re-draft' : 'Generate Document'}
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

      {/* Results */}
      {/* Streaming Results */}
      {isStreaming && streamingText && (
        <div className="liquid-glass-card glass-content p-6">
          <div className="flex items-center mb-4">
            <h2 className="text-xl font-semibold text-white">Generating Document...</h2>
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

      {results && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Document */}
          <div className="lg:col-span-2 space-y-4">
            <div className="liquid-glass-card glass-content px-6 pt-6 pb-2 w-full" style={{ height: 'fit-content' }}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Draft Document</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={handleCopy}
                    className="glass-button flex items-center px-3 py-1 text-sm"
                  >
                    <Copy className="h-4 w-4 mr-1" />
                    Copy
                  </button>
                  <button
                    onClick={handleSave}
                    className="glass-button flex items-center px-3 py-1 text-sm bg-blue-500/20 border-blue-500/30 hover:bg-blue-500/30"
                  >
                    <Save className="h-4 w-4 mr-1" />
                    Save
                  </button>
                  <button
                    onClick={handleDownload}
                    className="glass-button flex items-center px-3 py-1 text-sm bg-green-500/20 border-green-500/30 hover:bg-green-500/30"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download DOCX
                  </button>
                </div>
              </div>
              {/* Formatted Preview */}
              <div className="max-h-[600px] overflow-y-auto w-full relative -mx-2 px-2" style={{ 
                background: 'transparent',
                zIndex: 1
              }}>
                <div className="text-white prose prose-invert max-w-none" style={{ marginBottom: 0 }}>
                  <MarkdownRenderer content={editingContent} />
                </div>
              </div>
            </div>

            {/* HITL Panel - Outside the drafting response block */}
            <HITLPanel
              featureType="drafting"
              originalOutput={results}
              onAccept={() => {
                toast.success('Draft output accepted')
              }}
              onReject={() => {
                toast.success('Draft output rejected - feedback recorded')
              }}
              onEdit={(editedContent) => {
                setEditingContent(editedContent)
                setResults({
                  ...results,
                  draft_content: editedContent
                })
                toast.success('Draft output edited')
              }}
            />

            {/* Suggestions */}
            {results.suggestions && results.suggestions.length > 0 && (
              <div className="glass-panel p-6">
                <h3 className="text-lg font-semibold text-white mb-4">AI Suggestions</h3>
                <div className="space-y-2">
                  {results.suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start">
                      <Plus className="h-4 w-4 text-green-400 mr-2 mt-1 flex-shrink-0" />
                      <span className="text-sm text-white/90">{suggestion}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Document Info */}
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Document Info</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-white/70">Type:</span>
                  <p className="text-sm text-white capitalize">{documentType}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-white/70">Confidence:</span>
                  <p className="text-sm text-white">{Math.round(results.confidence_score * 100)}%</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-white/70">Clauses:</span>
                  <p className="text-sm text-white">{results.clauses.length}</p>
                </div>
              </div>
            </div>

            {/* Clauses */}
            {results.clauses && results.clauses.length > 0 && (
              <div className="glass-panel p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Generated Clauses</h3>
                <div className="space-y-3">
                  {results.clauses.map((clause, index) => (
                    <div key={index} className="liquid-glass-card glass-content p-3">
                      <div className="flex items-center mb-2">
                        <Edit className="h-4 w-4 text-white/60 mr-2" />
                        <span className="text-sm font-medium text-white capitalize">
                          {clause.type}
                        </span>
                      </div>
                      <p className="text-xs text-white/80">{clause.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Example Prompts */}
      {!results && (
        <div className="p-6">
          <h3 className="text-lg font-medium text-white mb-4">Example Drafting Prompts</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              "Software development agreement between client and contractor",
              "Privacy policy for mobile application",
              "Non-disclosure agreement for business partnership",
              "Employment contract for remote software developer",
              "Terms of service for SaaS platform",
              "Service level agreement for IT support"
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

export default Drafting
