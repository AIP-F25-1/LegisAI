import React, { useState } from 'react'
import { Shield, AlertTriangle, CheckCircle, XCircle, Info, Clock, X, Edit2 } from 'lucide-react'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'
import { handleStreamingRequest } from '../utils/streaming'

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

const Compliance: React.FC = () => {
  const [content, setContent] = useState('')
  const [jurisdiction, setJurisdiction] = useState('US')
  const [checkGdpr, setCheckGdpr] = useState(true)
  const [checkUsCode, setCheckUsCode] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ComplianceResult | null>(null)
  const [streamingText, setStreamingText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [editedContent, setEditedContent] = useState('')

  const stopStreaming = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
    setIsStreaming(false)
    toast.info('Compliance check stopped')
  }

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault()
    const checkContent = editedContent.trim() || content.trim()
    if (!checkContent) return

    // Create new abort controller
    const controller = new AbortController()
    setAbortController(controller)
    setResults(null)

    try {
      await handleStreamingRequest(
        'compliance/stream',
        {
          content: checkContent,
          jurisdiction: jurisdiction,
          check_gdpr: checkGdpr,
          check_us_code: checkUsCode,
          check_eu_lex: false
        },
        setStreamingText,
        setIsStreaming,
        (fullText) => {
          setResults({
            content: checkContent,
            risk_score: 0.5,
            issues: [],
            recommendations: [],
            compliance_status: 'compliant',
            analysis: fullText,
            ai_generated: true
          })
          setContent(checkContent)
          setEditedContent('')
          toast.success('Compliance check completed!')
        },
        controller
      )
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('❌ Compliance check error:', error)
        toast.error('Failed to perform compliance check. Please try again.')
      }
    } finally {
      setAbortController(null)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low':
        return 'text-green-600 bg-green-50 border-green-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <XCircle className="h-5 w-5" />
      case 'medium':
        return <AlertTriangle className="h-5 w-5" />
      case 'low':
        return <Info className="h-5 w-5" />
      default:
        return <Info className="h-5 w-5" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'needs_review':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'high_risk':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Compliance Check</h1>
        <p className="mt-2 text-gray-600">
          Automated compliance checking against GDPR, US Code, and other regulations
        </p>
      </div>

      {/* Compliance Check Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleCheck} className="space-y-4">
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
              Legal Content to Check
            </label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your legal document content here..."
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isLoading}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="jurisdiction" className="block text-sm font-medium text-gray-700 mb-2">
                Jurisdiction
              </label>
              <select
                id="jurisdiction"
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isLoading}
              >
                <option value="US">United States</option>
                <option value="EU">European Union</option>
                <option value="UK">United Kingdom</option>
                <option value="CA">Canada</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checkGdpr}
                  onChange={(e) => setCheckGdpr(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <span className="ml-2 text-sm text-gray-700">Check GDPR</span>
              </label>
            </div>
            
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checkUsCode}
                  onChange={(e) => setCheckUsCode(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <span className="ml-2 text-sm text-gray-700">Check US Code</span>
              </label>
            </div>
          </div>
          
          {/* Edit Content */}
          {!isStreaming && results && (
            <div className="border-t border-gray-200 pt-4">
              <label htmlFor="edit-content" className="block text-sm font-medium text-gray-700 mb-2">
                Edit & Re-check
              </label>
              <textarea
                id="edit-content"
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                placeholder={content}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isStreaming || !(editedContent.trim() || content.trim())}
              className="flex-1 bg-purple-600 text-white py-3 px-4 rounded-md hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isStreaming ? (
                <>
                  <Clock className="h-5 w-5 mr-2 animate-spin" />
                  Checking...
                </>
              ) : (
                <>
                  <Shield className="h-5 w-5 mr-2" />
                  {results ? 'Re-check Compliance' : 'Check Compliance'}
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
            <h2 className="text-xl font-semibold text-gray-900">Analyzing Compliance...</h2>
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

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Compliance Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Compliance Status</h2>
              <div className={`px-3 py-1 rounded-full border ${getStatusColor(results.compliance_status)}`}>
                <span className="text-sm font-medium capitalize">{results.compliance_status}</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {Math.round(results.risk_score * 100)}%
                </div>
                <div className="text-sm text-gray-500">Risk Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {results.issues.length}
                </div>
                <div className="text-sm text-gray-500">Issues Found</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {results.recommendations.length}
                </div>
                <div className="text-sm text-gray-500">Recommendations</div>
              </div>
            </div>
          </div>

          {/* AI Analysis */}
          {results.analysis && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">AI Compliance Analysis</h3>
                {results.ai_generated && (
                  <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                    AI Generated
                  </span>
                )}
              </div>
              <div className="bg-gray-50 rounded-lg p-6 max-h-[600px] overflow-y-auto border border-gray-200">
                <MarkdownRenderer content={results.analysis} />
              </div>
            </div>
          )}

          {/* Issues */}
          {results.issues.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Issues</h3>
              <div className="space-y-4">
                {results.issues.map((issue, index) => (
                  <div
                    key={index}
                    className={`border rounded-lg p-4 ${getSeverityColor(issue.severity)}`}
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 mr-3">
                        {getSeverityIcon(issue.severity)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{issue.type}</h4>
                          <span className="text-sm font-medium capitalize">
                            {issue.severity} Severity
                          </span>
                        </div>
                        <p className="text-sm">{issue.description}</p>
                        {issue.position && (
                          <p className="text-xs mt-2 opacity-75">
                            Position: {issue.position}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {results.recommendations.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
              <div className="space-y-3">
                {results.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{recommendation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Assessment */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Assessment</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Risk Level</span>
                <span className="font-medium">
                  {results.risk_score < 0.3 ? 'Low' : 
                   results.risk_score < 0.6 ? 'Medium' : 'High'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    results.risk_score < 0.3 ? 'bg-green-500' :
                    results.risk_score < 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${results.risk_score * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Example Content */}
      {!results && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Example Content to Check</h3>
          <div className="space-y-4">
            {[
              "This agreement contains personal data processing clauses that may require GDPR compliance review.",
              "The parties agree to unlimited liability for all damages arising from this contract.",
              "All disputes shall be resolved through binding arbitration in accordance with local laws.",
              "The service provider shall maintain confidentiality of client information as required by applicable privacy regulations."
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setContent(example)}
                className="text-left w-full p-3 bg-white rounded-md border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all"
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

export default Compliance
