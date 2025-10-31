import React, { useState } from 'react'
import { Search, FileText, Clock, CheckCircle, X, Edit2 } from 'lucide-react'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'
import { handleStreamingRequest } from '../utils/streaming'

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
            <h3 className="text-lg font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-2 bg-gray-50 px-3 py-2 rounded-md">
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
            <span className="text-blue-600 mr-2 mt-1">•</span>
            <span className="text-gray-700">{trimmedLine.substring(1).trim()}</span>
          </div>
        )
      }
      
      // Numbered lists
      if (trimmedLine.match(/^\d+\./)) {
        return (
          <div key={index} className="flex items-start mb-2">
            <span className="text-blue-600 mr-2 mt-1 font-medium">{trimmedLine.split('.')[0]}.</span>
            <span className="text-gray-700">{trimmedLine.substring(trimmedLine.indexOf('.') + 1).trim()}</span>
          </div>
        )
      }
      
      // Regular paragraphs
      if (trimmedLine) {
        return (
          <p key={index} className="text-gray-700 mb-3 leading-relaxed">
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
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ResearchResult | null>(null)
  const [streamingText, setStreamingText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [editedQuery, setEditedQuery] = useState('')

  const stopStreaming = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
    setIsStreaming(false)
    toast.info('Streaming stopped')
  }

  const handleSearchStreaming = async (e: React.FormEvent) => {
    e.preventDefault()
    const searchQuery = editedQuery.trim() || query.trim()
    if (!searchQuery) return

    // Create new abort controller
    const controller = new AbortController()
    setAbortController(controller)
    setResults(null)

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
        (fullText) => {
          setResults({
            query: searchQuery,
            documents: [],
            summary: fullText,
            confidence_score: 0.88,
            ai_generated: true
          })
          setQuery(searchQuery)
          setEditedQuery('')
          toast.success('Research completed!')
        },
        controller
      )
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('❌ Streaming error:', error)
        toast.error('Research failed. Please try again.')
      }
    } finally {
      setAbortController(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Legal Research</h1>
        <p className="mt-2 text-gray-600">
          AI-powered legal research with precedent analysis and case law retrieval
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearchStreaming} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Research Query
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your legal research query..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isStreaming}
              />
            </div>
          </div>
          
          {/* Edit Query */}
          {!isStreaming && results && (
            <div className="border-t border-gray-200 pt-4">
              <label htmlFor="edit-query" className="block text-sm font-medium text-gray-700 mb-2">
                Edit & Re-search
              </label>
              <div className="relative">
                <Edit2 className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  id="edit-query"
                  value={editedQuery}
                  onChange={(e) => setEditedQuery(e.target.value)}
                  placeholder={query}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isStreaming || !(editedQuery.trim() || query.trim())}
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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
                className="bg-red-600 text-white py-3 px-4 rounded-md hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 flex items-center justify-center"
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
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Generating Research...</h2>
            <div className="ml-auto flex items-center text-sm text-gray-500">
              <span className="h-2 w-2 bg-green-500 rounded-full animate-pulse mr-2"></span>
              Live
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-6 max-h-[600px] overflow-y-auto border border-gray-200">
            <MarkdownRenderer content={streamingText} />
            <span className="inline-block w-2 h-5 bg-blue-600 animate-pulse ml-1">▋</span>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && !results && !isStreaming && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex flex-col items-center justify-center py-12">
            <Clock className="h-12 w-12 text-blue-600 animate-spin mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Generating Research Results...</h3>
            <p className="text-sm text-gray-500 text-center max-w-md">
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
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center mb-4">
              <CheckCircle className="h-6 w-6 text-green-500 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">Research Summary</h2>
              <span className="ml-auto text-sm text-gray-500">
                Confidence: {Math.round(results.confidence_score * 100)}%
              </span>
            </div>
            <div className="bg-gray-50 rounded-lg p-6 max-h-[600px] overflow-y-auto border border-gray-200">
              <MarkdownRenderer content={results.summary} />
            </div>
          </div>

          {/* Documents */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Relevant Documents ({results.documents.length})
            </h2>
            <div className="space-y-4">
              {results.documents.map((doc, index) => (
                <div
                  key={doc.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">
                        Document {doc.id}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      Relevance: {Math.round(doc.score * 100)}%
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {doc.content}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Query Info */}
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">Research Query</h3>
            <p className="text-blue-800">{results.query}</p>
          </div>
        </div>
      )}

      {/* Example Queries */}
      {!results && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Example Research Queries</h3>
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
                className="text-left p-3 bg-white rounded-md border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all"
              >
                <span className="text-sm text-gray-700">{example}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Research
