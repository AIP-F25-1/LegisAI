import React, { useState } from 'react'
import { Shield, AlertTriangle, CheckCircle, XCircle, Info, Clock, X, Edit2, BarChart3, History, Trash2 } from 'lucide-react'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'
import { handleStreamingRequest } from '../utils/streaming'
import RiskHeatmap from '../components/RiskHeatmap'
import { useTimeline } from '../contexts/TimelineContext'
import { useCompliance } from '../contexts/ComplianceContext'
import HITLPanel from '../components/HITLPanel'

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
  const { addToTimeline, cacheResponse } = useTimeline()
  const {
    results,
    setResults,
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
  } = useCompliance()
  const [isLoading, setIsLoading] = useState(false)
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [editedContent, setEditedContent] = useState('')
  const [clauseAnalysis, setClauseAnalysis] = useState<any>(null)
  const [showHeatmap, setShowHeatmap] = useState(false)
  const [isAnalyzingClauses, setIsAnalyzingClauses] = useState(false)
  const [showHistory, setShowHistory] = useState(false)

  const stopStreaming = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
    }
    setIsStreaming(false)
    toast('Compliance check stopped')
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
        async (fullText) => {
          // After streaming completes, fetch the full compliance results
          try {
            setIsLoading(true)
            const response = await apiClient.post('/compliance/check', {
              content: checkContent,
              jurisdiction: jurisdiction,
              check_gdpr: checkGdpr,
              check_us_code: checkUsCode,
              check_eu_lex: false
            })
            
            const complianceData = response.data
            
            // Parse recommendations from response
            let recommendations: string[] = []
            if (complianceData.recommendations && Array.isArray(complianceData.recommendations)) {
              recommendations = complianceData.recommendations
            } else if (typeof complianceData.recommendations === 'string') {
              // Parse string recommendations
              const lines = complianceData.recommendations.split('\n')
              for (const line of lines) {
                const trimmed = line.trim()
                if (trimmed && (trimmed[0].match(/[\d•\-]/) || trimmed.startsWith('•'))) {
                  recommendations.push(trimmed.replace(/^[\d•\-\.]\s*/, ''))
                }
              }
            }
            
            // Parse issues from response
            let issues: Array<{type: string, severity: string, description: string}> = []
            if (complianceData.issues && Array.isArray(complianceData.issues)) {
              // If it's an array of objects, use as-is
              if (complianceData.issues.length > 0 && typeof complianceData.issues[0] === 'object') {
                issues = complianceData.issues
              } else {
                // If it's an array of strings, convert to objects
                issues = complianceData.issues.map((issue: string) => ({
                  type: 'COMPLIANCE',
                  severity: 'medium',
                  description: issue
                }))
              }
            } else if (typeof complianceData.issues === 'string') {
              const lines = complianceData.issues.split('\n')
              for (const line of lines) {
                const trimmed = line.trim()
                if (trimmed && (trimmed[0].match(/[\d•\-]/) || trimmed.startsWith('•'))) {
                  issues.push({
                    type: 'COMPLIANCE',
                    severity: 'medium',
                    description: trimmed.replace(/^[\d•\-\.]\s*/, '')
                  })
                }
              }
            }
            
            // Determine compliance status based on risk score and issues
            let complianceStatus = 'compliant'
            const riskScore = complianceData.risk_score || 0.5
            if (riskScore >= 0.7 || issues.length > 5) {
              complianceStatus = 'high_risk'
            } else if (riskScore >= 0.4 || issues.length > 0) {
              complianceStatus = 'needs_review'
            }
            
            const resultData = {
              content: checkContent,
              risk_score: riskScore,
              issues: issues,
              recommendations: recommendations,
              compliance_status: complianceStatus,
              analysis: fullText || complianceData.analysis || '',
              ai_generated: complianceData.ai_generated !== false
            }
            setResults(resultData)
            setContent(checkContent)
            setEditedContent('')
            
            // Cache response and add to timeline
            cacheResponse('compliance', resultData, checkContent.substring(0, 50), {
              jurisdiction: jurisdiction,
              risk_score: riskScore,
              timestamp: new Date().toISOString()
            })
            
            if (fullText.length > 50) {
              await addToTimeline(`compliance_${Date.now()}`, fullText, {
                title: `Compliance Check: ${jurisdiction}`,
                type: 'compliance',
                jurisdiction: jurisdiction,
                risk_score: riskScore,
                timestamp: new Date().toISOString()
              }, resultData)
            }
            
            toast.success(`Compliance check completed! Found ${issues.length} issues`)
          } catch (error: any) {
            console.error('Error fetching compliance results:', error)
            // Fallback to streamed content with default values
            const resultData = {
              content: checkContent,
              risk_score: 0.5,
              issues: [],
              recommendations: [],
              compliance_status: 'compliant',
              analysis: fullText,
              ai_generated: true
            }
            setResults(resultData)
            setContent(checkContent)
            setEditedContent('')
            toast.error('Could not fetch detailed compliance results, but analysis is available')
          } finally {
            setIsLoading(false)
          }
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
        return 'liquid-glass-card glass-content border-red-500/30 text-white'
      case 'medium':
        return 'liquid-glass-card glass-content border-yellow-500/30 text-white'
      case 'low':
        return 'liquid-glass-card glass-content border-green-500/30 text-white'
      default:
        return 'liquid-glass-card glass-content border-white/30 text-white'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return <XCircle className="h-5 w-5 text-red-400" />
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />
      case 'low':
        return <Info className="h-5 w-5 text-blue-400" />
      default:
        return <Info className="h-5 w-5 text-white/60" />
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

  const handleClauseAnalysis = async () => {
    const checkContent = editedContent.trim() || content.trim()
    if (!checkContent) {
      toast.error('Please provide content to analyze')
      return
    }

    setIsAnalyzingClauses(true)
    setClauseAnalysis(null)
    setShowHeatmap(false)

    try {
      const response = await apiClient.post('/clauses/analyze', {
        content: checkContent,
        jurisdiction: jurisdiction,
        analyze_full_document: true
      })

      setClauseAnalysis(response.data)
      setShowHeatmap(true)
      toast.success('Clause analysis completed!')
    } catch (error: any) {
      console.error('❌ Clause analysis error:', error)
      toast.error('Failed to analyze clauses. Please try again.')
    } finally {
      setIsAnalyzingClauses(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white">Compliance Check</h1>
        <p className="mt-2 text-white/80">
          Automated compliance checking against GDPR, US Code, and other regulations
        </p>
      </div>

      {/* Compliance Check Form */}
      <div className="liquid-glass-card glass-content p-8 md:p-12">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl md:text-3xl font-semibold text-white">Compliance Check</h2>
          <div className="flex gap-2">
            {complianceHistory.length > 0 && (
              <>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="glass-button flex items-center px-3 py-1 text-sm"
                >
                  <History className="h-4 w-4 mr-1" />
                  History ({complianceHistory.length})
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
        {showHistory && complianceHistory.length > 0 && (
          <div className="mb-4 p-4 glass-panel max-h-60 overflow-y-auto">
            <h3 className="text-sm font-medium text-white mb-2">Previous Checks</h3>
            <div className="space-y-2">
              {complianceHistory.map((item, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setResults(item)
                    setContent(item.content)
                    setShowHistory(false)
                  }}
                  className="w-full text-left p-2 liquid-glass-card glass-content hover:scale-[1.02] transition-all"
                >
                  <p className="text-sm font-medium text-white">
                    {item.compliance_status.charAt(0).toUpperCase() + item.compliance_status.slice(1)} - Risk: {Math.round(item.risk_score * 100)}%
                  </p>
                  <p className="text-xs text-white/70 mt-1 line-clamp-2">{item.content.substring(0, 100)}...</p>
                </button>
              ))}
            </div>
          </div>
        )}

        <form onSubmit={handleCheck} className="space-y-4">
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-white mb-2">
              Legal Content to Check
            </label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste your legal document content here..."
              rows={8}
              className="glass-textarea w-full"
              disabled={isLoading}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="jurisdiction" className="block text-sm font-medium text-white mb-2">
                Jurisdiction
              </label>
              <select
                id="jurisdiction"
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
                className="glass-input w-full"
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
                  className="rounded border-white/30 text-blue-400 focus:ring-blue-400"
                  disabled={isLoading}
                />
                <span className="ml-2 text-sm text-white">Check GDPR</span>
              </label>
            </div>
            
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={checkUsCode}
                  onChange={(e) => setCheckUsCode(e.target.checked)}
                  className="rounded border-white/30 text-blue-400 focus:ring-blue-400"
                  disabled={isLoading}
                />
                <span className="ml-2 text-sm text-white">Check US Code</span>
              </label>
            </div>
          </div>
          
          {/* Edit Content */}
          {!isStreaming && results && (
            <div className="border-t border-white/20 pt-4">
              <label htmlFor="edit-content" className="block text-sm font-medium text-white mb-2">
                Edit & Re-check
              </label>
              <textarea
                id="edit-content"
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                placeholder={content}
                rows={6}
                className="glass-textarea w-full text-sm"
              />
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isStreaming || !(editedContent.trim() || content.trim())}
              className="glass-button flex-1 py-3 px-4 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
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
            
            <button
              type="button"
              onClick={handleClauseAnalysis}
              disabled={isAnalyzingClauses || !(editedContent.trim() || content.trim())}
              className="glass-button py-3 px-4 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzingClauses ? (
                <>
                  <Clock className="h-5 w-5 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Analyze Clauses
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
            <h2 className="text-xl font-semibold text-white">Analyzing Compliance...</h2>
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

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Compliance Status */}
          <div className="glass-panel p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-white">Compliance Status</h2>
              <div className={`px-3 py-1 rounded-full border ${getStatusColor(results.compliance_status)}`}>
                <span className="text-sm font-medium capitalize text-white">{results.compliance_status}</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {Math.round(results.risk_score * 100)}%
                </div>
                <div className="text-sm text-white/80">Risk Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {results.issues.length}
                </div>
                <div className="text-sm text-white/80">Issues Found</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-white">
                  {results.recommendations.length}
                </div>
                <div className="text-sm text-white/80">Recommendations</div>
              </div>
            </div>
          </div>

          {/* AI Analysis */}
          {results.analysis && (
            <div className="liquid-glass-card glass-content p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">AI Compliance Analysis</h3>
                {results.ai_generated && (
                  <span className="text-xs px-2 py-1 bg-green-500/20 text-white rounded backdrop-blur-sm">
                    AI Generated
                  </span>
                )}
              </div>
              <div className="liquid-glass-card glass-content p-6 max-h-[600px] overflow-y-auto">
                <div className="text-white prose prose-invert max-w-none">
                  <MarkdownRenderer content={results.analysis} />
                </div>
              </div>
              
              {/* HITL Panel */}
              <HITLPanel
                featureType="compliance"
                originalOutput={results}
                onAccept={() => {
                  toast.success('Compliance output accepted')
                }}
                onReject={() => {
                  toast.success('Compliance output rejected - feedback recorded')
                }}
                onEdit={(editedContent) => {
                  setResults({
                    ...results,
                    analysis: editedContent
                  })
                  toast.success('Compliance output edited')
                }}
              />
            </div>
          )}

          {/* Issues */}
          {results.issues.length > 0 && (
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Compliance Issues</h3>
              <div className="space-y-4">
                {results.issues.map((issue, index) => (
                  <div
                    key={index}
                    className={`p-4 ${getSeverityColor(issue.severity)}`}
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 mr-3">
                        {getSeverityIcon(issue.severity)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-white">{issue.type}</h4>
                          <span className="text-sm font-medium capitalize text-white/80">
                            {issue.severity} Severity
                          </span>
                        </div>
                        <p className="text-sm text-white/90">{issue.description}</p>
                        {issue.position && (
                          <p className="text-xs mt-2 text-white/70">
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
            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Recommendations</h3>
              <div className="space-y-3">
                {results.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start">
                    <CheckCircle className="h-5 w-5 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-white/90">{recommendation}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Assessment */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Risk Assessment</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Risk Level</span>
                <span className="font-medium">
                  {(() => {
                    // Use clause analysis document risk level if available (more accurate)
                    if (clauseAnalysis?.document_risk_level || clauseAnalysis?.summary?.document_risk_level) {
                      const docRiskLevel = clauseAnalysis.document_risk_level || clauseAnalysis.summary?.document_risk_level;
                      return docRiskLevel.charAt(0).toUpperCase() + docRiskLevel.slice(1);
                    }
                    // Fallback to compliance check risk score
                    if (results.risk_score < 0.3) return 'Low';
                    if (results.risk_score < 0.6) return 'Medium';
                    return 'High';
                  })()}
                </span>
              </div>
              <div className="w-full bg-gray-200/30 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    (() => {
                      // Use clause analysis if available
                      if (clauseAnalysis?.document_risk_level || clauseAnalysis?.summary?.document_risk_level) {
                        const docRiskLevel = (clauseAnalysis.document_risk_level || clauseAnalysis.summary?.document_risk_level).toLowerCase();
                        if (docRiskLevel === 'critical') return 'bg-red-600';
                        if (docRiskLevel === 'high') return 'bg-red-500';
                        if (docRiskLevel === 'medium') return 'bg-yellow-500';
                        return 'bg-green-500';
                      }
                      // Fallback to compliance check
                      if (results.risk_score < 0.3) return 'bg-green-500';
                      if (results.risk_score < 0.6) return 'bg-yellow-500';
                      return 'bg-red-500';
                    })()
                  }`}
                  style={{ 
                    width: `${(() => {
                      // Use clause analysis if available
                      if (clauseAnalysis?.document_risk_level || clauseAnalysis?.summary?.document_risk_level) {
                        const docRiskLevel = (clauseAnalysis.document_risk_level || clauseAnalysis.summary?.document_risk_level).toLowerCase();
                        // For Critical, always fill 100%
                        if (docRiskLevel === 'critical') return 100;
                        // For High, fill 80-100% based on average score
                        if (docRiskLevel === 'high') {
                          const avgScore = clauseAnalysis.average_risk_score ?? clauseAnalysis.summary?.average_risk_score ?? 0;
                          return Math.max(80, Math.min(avgScore * 100, 100));
                        }
                        // For Medium, fill 40-70% based on average score
                        if (docRiskLevel === 'medium') {
                          const avgScore = clauseAnalysis.average_risk_score ?? clauseAnalysis.summary?.average_risk_score ?? 0;
                          return Math.max(40, Math.min(avgScore * 100, 70));
                        }
                        // For Low, fill 0-30% based on average score
                        const avgScore = clauseAnalysis.average_risk_score ?? clauseAnalysis.summary?.average_risk_score ?? 0;
                        return Math.min(avgScore * 100, 30);
                      }
                      // Fallback to compliance check
                      return Math.min(results.risk_score * 100, 100);
                    })()}%` 
                  }}
                ></div>
              </div>
              {/* Show which source is being used */}
              {(clauseAnalysis?.document_risk_level || clauseAnalysis?.summary?.document_risk_level) && (
                <p className="text-xs text-white/70 mt-2">
                  Based on clause-level analysis ({clauseAnalysis.clause_risks?.length || 0} clauses analyzed)
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Clause Analysis & Risk Heatmap */}
      {clauseAnalysis && showHeatmap && (
        <div className="liquid-glass-card glass-content p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">Clause Risk Analysis</h2>
            <button
              onClick={() => setShowHeatmap(false)}
              className="text-white/80 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <RiskHeatmap
            clauseRisks={clauseAnalysis.clause_risks || []}
            documentRiskLevel={clauseAnalysis.document_risk_level || clauseAnalysis.summary?.document_risk_level}
            averageRiskScore={clauseAnalysis.average_risk_score || clauseAnalysis.summary?.average_risk_score}
            onClauseClick={(clause) => {
              toast(`Selected clause: ${clause.clause_id}`)
            }}
          />
        </div>
      )}

    </div>
  )
}

export default Compliance
