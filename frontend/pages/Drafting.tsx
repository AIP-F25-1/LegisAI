import React, { useState } from 'react'
import { FileText, Plus, Edit, Save, Copy, Clock, X, Edit2, Download } from 'lucide-react'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'
import { handleStreamingRequest } from '../utils/streaming'

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
  const [query, setQuery] = useState('')
  const [documentType, setDocumentType] = useState('contract')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<DraftingResult | null>(null)
  const [editingContent, setEditingContent] = useState('')
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
    toast.info('Drafting stopped')
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
        (fullText) => {
          setEditingContent(fullText)
          setResults({
            query: draftQuery,
            draft_content: fullText,
            clauses: [],
            suggestions: [],
            confidence_score: 0.88
          })
          setQuery(draftQuery)
          setEditedQuery('')
          toast.success('Document drafted successfully!')
        },
        controller
      )
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('❌ Drafting error:', error)
        toast.error('Failed to draft document. Please try again.')
      }
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
        <h1 className="text-3xl font-bold text-gray-900">Document Drafting</h1>
        <p className="mt-2 text-gray-600">
          Generate legal documents, contracts, and clauses with AI assistance
        </p>
      </div>

      {/* Drafting Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleDraft} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                Document Description
              </label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Describe the document you want to draft..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isLoading}
              />
            </div>
            <div>
              <label htmlFor="documentType" className="block text-sm font-medium text-gray-700 mb-2">
                Document Type
              </label>
              <select
                id="documentType"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
            <div className="border-t border-gray-200 pt-4">
              <label htmlFor="edit-query" className="block text-sm font-medium text-gray-700 mb-2">
                Edit & Re-draft
              </label>
              <textarea
                id="edit-query"
                value={editedQuery}
                onChange={(e) => setEditedQuery(e.target.value)}
                placeholder={query}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isStreaming || !(editedQuery.trim() || query.trim())}
              className="flex-1 bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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
                className="bg-red-600 text-white py-3 px-4 rounded-md hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 flex items-center justify-center"
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
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Generating Document...</h2>
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

      {results && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Document */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Draft Document</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={handleCopy}
                    className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                  >
                    <Copy className="h-4 w-4 mr-1" />
                    Copy
                  </button>
                  <button
                    onClick={handleSave}
                    className="flex items-center px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    <Save className="h-4 w-4 mr-1" />
                    Save
                  </button>
                  <button
                    onClick={handleDownload}
                    className="flex items-center px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download DOCX
                  </button>
                </div>
              </div>
              {/* Formatted Preview */}
              <div className="bg-gray-50 rounded-lg p-6 max-h-[600px] overflow-y-auto border border-gray-200 mb-4">
                <MarkdownRenderer content={editingContent} />
              </div>
              {/* Editable Version */}
              <details className="border-t border-gray-200 pt-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                  View Raw Markdown (Click to Edit)
                </summary>
                <textarea
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                  className="w-full h-48 p-4 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                  placeholder="Generated document content will appear here..."
                />
              </details>
            </div>

            {/* Suggestions */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Suggestions</h3>
              <div className="space-y-2">
                {results.suggestions.map((suggestion, index) => (
                  <div key={index} className="flex items-start">
                    <Plus className="h-4 w-4 text-green-500 mr-2 mt-1 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{suggestion}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Document Info */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Info</h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-500">Type:</span>
                  <p className="text-sm text-gray-900 capitalize">{documentType}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Confidence:</span>
                  <p className="text-sm text-gray-900">{Math.round(results.confidence_score * 100)}%</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Clauses:</span>
                  <p className="text-sm text-gray-900">{results.clauses.length}</p>
                </div>
              </div>
            </div>

            {/* Clauses */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Generated Clauses</h3>
              <div className="space-y-3">
                {results.clauses.map((clause, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-3">
                    <div className="flex items-center mb-2">
                      <Edit className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {clause.type}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">{clause.content}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Example Prompts */}
      {!results && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Example Drafting Prompts</h3>
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
                className="text-left p-3 bg-white rounded-md border border-gray-200 hover:border-green-300 hover:shadow-sm transition-all"
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

export default Drafting
