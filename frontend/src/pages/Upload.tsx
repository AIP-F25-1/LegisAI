import React, { useCallback } from 'react'
import { Upload, FileText, Download, Trash2, Eye } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'
import { useTimeline } from '../contexts/TimelineContext'
import { useUpload } from '../contexts/UploadContext'

interface UploadedFile {
  file_id: string
  filename: string
  file_type: string
  size: number
  status: string
  processing_results?: {
    pages_extracted: number
    text_length: number
    language_detected: string
    document_type: string
  }
}

interface DocumentAnalysis {
  file_id: string
  filename: string
  document_type: string
  analysis: string
  key_findings: string[]
  recommendations: string[]
  confidence_score: number
  risk_level: string
  compliance_status: string
  processing_time: string
  text_extraction_status: string
  enhanced_analysis: boolean
  ai_generated: boolean
  version: string
  extracted_entities?: {
    dates: Array<{ text: string; parsed?: string }>
    monetary_values: Array<{ text: string; parsed?: number }>
    parties: Array<{ text: string }>
    locations: Array<{ text: string }>
  }
  entity_summary?: {
    dates: number
    monetary_values: number
    parties: number
    locations: number
  }
}

interface TimelineData {
  timeline: {
    events: Array<{
      date_text: string
      parsed_date: string
      context: string
      document_id: string
      event_type: string
    }>
    total_events: number
    date_range: {
      earliest: string
      latest: string
      span_days: number
    }
    event_types: Record<string, number>
  }
  entities: {
    linked_entities: Array<{
      entity: string
      documents: string[]
      occurrence_count: number
    }>
    total_unique_entities: number
  }
  documents: {
    total_documents: number
    document_ids: string[]
  }
}

const UploadPage: React.FC = () => {
  const { addToTimeline, cacheResponse } = useTimeline()
  const {
    uploadedFiles,
    setUploadedFiles,
    analyzedDocuments,
    setAnalyzedDocuments,
    isUploading,
    setIsUploading,
    isAnalyzing,
    setIsAnalyzing,
    clearAll
  } = useUpload()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true)
    
    for (const file of acceptedFiles) {
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await apiClient.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        
        setUploadedFiles(prev => [...prev, response.data])
        toast.success(`${file.name} uploaded successfully!`)
      } catch (error) {
        console.error('Upload error:', error)
        toast.error(`Failed to upload ${file.name}`)
      }
    }
    
    setIsUploading(false)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: true
  })

  const analyzeDocument = async (fileId: string) => {
    setIsAnalyzing(fileId)
    try {
      console.log('🔍 Analyzing document:', fileId)
      const response = await apiClient.get(`/analyze/${fileId}`)
      console.log('✅ Analysis response received:', response.data)
      
      // Extract entities using OCR Agent
      let analysisData = response.data
      if (analysisData.text_content || analysisData.document_preview) {
        try {
          const textToExtract = analysisData.text_content || analysisData.document_preview || ''
          if (textToExtract.length > 50) {
            // API expects JSON string (text wrapped in quotes)
            const entityResponse = await apiClient.post('/ocr/extract-entities', JSON.stringify(textToExtract), {
              headers: { 'Content-Type': 'application/json' }
            })
            analysisData.extracted_entities = entityResponse.data.entities
            analysisData.entity_summary = {
              dates: entityResponse.data.date_count,
              monetary_values: entityResponse.data.monetary_count,
              parties: entityResponse.data.party_count,
              locations: entityResponse.data.location_count
            }
            console.log('✅ Entities extracted:', analysisData.entity_summary)
          }
        } catch (entityError: any) {
          console.warn('⚠️ Entity extraction failed (optional):', entityError)
          // Continue without entities - this is optional functionality
          if (entityError.response?.status !== 503) {
            // Only log if it's not a "service unavailable" error
            console.warn('Entity extraction error details:', entityError.response?.data || entityError.message)
          }
        }
      }
      
      // Use the backend response directly
      setAnalyzedDocuments(prev => [...prev, analysisData])
      
      // Cache response and add to timeline
      cacheResponse('upload', analysisData, analysisData.filename || fileId, {
        file_id: fileId,
        analyzed_at: new Date().toISOString()
      })
      
      // Automatically add document to timeline
      const textToAdd = analysisData.text_content || analysisData.document_preview || analysisData.analysis || ''
      if (textToAdd.length > 50) {
        await addToTimeline(fileId, textToAdd, {
          title: analysisData.filename || fileId,
          date: new Date().toISOString().split('T')[0],
          type: 'filing',
          analyzed_at: new Date().toISOString()
        }, analysisData)
      }
      
      toast.success('Document analyzed successfully!')
    } catch (error) {
      console.error('❌ Analysis error:', error)
      toast.error('Failed to analyze document')
    } finally {
      setIsAnalyzing(null)
    }
  }

  const deleteFile = async (fileId: string) => {
    try {
      await apiClient.delete(`/files/${fileId}`)
      setUploadedFiles(prev => prev.filter(file => file.file_id !== fileId))
      setAnalyzedDocuments(prev => prev.filter(doc => doc.file_id !== fileId))
      toast.success('File deleted successfully!')
    } catch (error) {
      console.error('Delete error:', error)
      toast.error('Failed to delete file')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white">Document Upload & Analysis</h1>
        <p className="mt-2 text-white/80">
          Upload and analyze legal documents with AI-powered insights
        </p>
      </div>

      {/* Upload Area */}
      <div className="liquid-glass-card glass-content p-8 md:p-12">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-blue-400/60 bg-blue-500/20'
              : 'border-white/30 hover:border-white/50'
          } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} disabled={isUploading} />
          <Upload className="mx-auto h-16 w-16 text-white/70 mb-6" />
          {isUploading ? (
            <div>
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-white mx-auto mb-3"></div>
              <p className="text-xl font-medium text-white">Uploading...</p>
            </div>
          ) : isDragActive ? (
            <div>
              <p className="text-xl font-medium text-white">Drop the files here...</p>
              <p className="text-base text-white/80 mt-2">Release to upload</p>
            </div>
          ) : (
            <div>
              <p className="text-xl font-medium text-white">Drag & drop files here</p>
              <p className="text-base text-white/80 mt-2">or click to select files</p>
              <p className="text-sm text-white/70 mt-3">
                Supports PDF, DOC, DOCX, TXT files
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Uploaded Files</h2>
          <div className="space-y-4">
            {uploadedFiles.map((file) => (
              <div key={file.file_id} className="liquid-glass-card glass-content p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="h-8 w-8 text-white/60 mr-3" />
                    <div>
                      <h3 className="font-medium text-white">{file.filename}</h3>
                      <p className="text-sm text-white/70">
                        {formatFileSize(file.size)} • {file.file_type}
                      </p>
                      {file.processing_results && (
                        <p className="text-xs text-white/60">
                          {file.processing_results.pages_extracted} pages • 
                          {file.processing_results.language_detected} • 
                          {file.processing_results.document_type}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => analyzeDocument(file.file_id)}
                      disabled={isAnalyzing === file.file_id}
                      className="glass-button flex items-center px-3 py-1 text-sm disabled:opacity-50"
                    >
                      {isAnalyzing === file.file_id ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Eye className="h-4 w-4 mr-1" />
                          Analyze
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => deleteFile(file.file_id)}
                      className="glass-button flex items-center px-3 py-1 text-sm bg-red-500/20 border-red-500/30 hover:bg-red-500/30"
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analyzed Documents */}
      {analyzedDocuments.length > 0 && (
        <div className="space-y-6">
          {analyzedDocuments.map((doc) => (
            <div key={doc.file_id} className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Document Analysis</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-white/80">Confidence: {Math.round(doc.confidence_score * 100)}%</span>
                  <span className={`text-xs px-2 py-1 rounded backdrop-blur-sm ${
                    doc.risk_level === 'low' ? 'bg-green-500/20 text-green-300' :
                    doc.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-red-500/20 text-red-300'
                  }`}>
                    {doc.risk_level} risk
                  </span>
                </div>
              </div>
              
              {/* Document Info */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="liquid-glass-card glass-content p-4">
                  <h3 className="font-medium text-white mb-2">Document</h3>
                  <div className="space-y-1 text-sm text-white/80">
                    <p className="font-medium">{doc.filename}</p>
                    <p className="capitalize">{doc.document_type}</p>
                  </div>
                </div>
                
                <div className="liquid-glass-card glass-content p-4">
                  <h3 className="font-medium text-white mb-2">Status</h3>
                  <div className="space-y-1 text-sm text-white/80">
                    <p className="capitalize">{doc.compliance_status}</p>
                    <p>{doc.text_extraction_status}</p>
                  </div>
                </div>
                
                <div className="liquid-glass-card glass-content p-4">
                  <h3 className="font-medium text-white mb-2">Processing</h3>
                  <div className="space-y-1 text-sm text-white/80">
                    <p>{doc.processing_time}</p>
                    <p className="capitalize">{doc.version}</p>
                  </div>
                </div>

                <div className="liquid-glass-card glass-content p-4">
                  <h3 className="font-medium text-white mb-2">AI Generated</h3>
                  <div className="space-y-1 text-sm">
                    {doc.ai_generated ? (
                      <span className="text-green-300 font-medium">Yes</span>
                    ) : (
                      <span className="text-white/60">No</span>
                    )}
                  </div>
                </div>
              </div>

              {/* AI Analysis */}
              <div className="mb-6">
                <h3 className="font-medium text-white mb-3">AI Legal Analysis</h3>
                <div className="liquid-glass-card glass-content relative" style={{ minHeight: '200px' }}>
                  <div className="p-4 max-h-96 overflow-y-auto relative" style={{ 
                    background: 'transparent',
                    zIndex: 1
                  }}>
                    <div className="text-white prose prose-invert max-w-none">
                      <MarkdownRenderer content={doc.analysis} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Key Findings */}
              {doc.key_findings && doc.key_findings.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-medium text-white mb-3">Key Findings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {doc.key_findings.map((finding, index) => (
                      <div key={index} className="liquid-glass-card glass-content p-3 border-green-500/30">
                        <div className="flex items-start">
                          <div className="flex-shrink-0">
                            <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                          </div>
                          <div className="ml-3">
                            <p className="text-sm text-white/90">{finding}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {doc.recommendations && doc.recommendations.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-medium text-white mb-3">Recommendations</h3>
                  <div className="space-y-2">
                    {doc.recommendations.map((recommendation, index) => (
                      <div key={index} className="liquid-glass-card glass-content p-3 border-yellow-500/30">
                        <div className="flex items-start">
                          <div className="flex-shrink-0">
                            <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                          </div>
                          <div className="ml-3">
                            <p className="text-sm text-white/90">{recommendation}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Extracted Entities (OCR Agent) */}
              {doc.extracted_entities && doc.entity_summary && (
                <div className="mt-6 border-t border-white/20 pt-6">
                  <h3 className="font-medium text-white mb-4 flex items-center">
                    <span className="bg-blue-500/20 text-blue-300 px-2 py-1 text-xs mr-2 backdrop-blur-sm">OCR</span>
                    Extracted Entities
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {/* Dates */}
                    {doc.entity_summary.dates > 0 && (
                      <div className="liquid-glass-card glass-content p-4 border-blue-500/30">
                        <h4 className="font-medium text-white mb-2">📅 Dates ({doc.entity_summary.dates})</h4>
                        <div className="space-y-1">
                          {doc.extracted_entities.dates.slice(0, 3).map((date: any, idx: number) => (
                            <p key={idx} className="text-sm text-white/90">
                              {date.text}
                              {date.parsed && <span className="text-xs text-blue-300 ml-1">({new Date(date.parsed).toLocaleDateString()})</span>}
                            </p>
                          ))}
                          {doc.entity_summary.dates > 3 && (
                            <p className="text-xs text-blue-300">+{doc.entity_summary.dates - 3} more</p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Monetary Values */}
                    {doc.entity_summary.monetary_values > 0 && (
                      <div className="liquid-glass-card glass-content p-4 border-green-500/30">
                        <h4 className="font-medium text-white mb-2">💰 Monetary ({doc.entity_summary.monetary_values})</h4>
                        <div className="space-y-1">
                          {doc.extracted_entities.monetary_values.slice(0, 3).map((money: any, idx: number) => (
                            <p key={idx} className="text-sm text-white/90">
                              {money.text}
                              {money.parsed && <span className="text-xs text-green-300 ml-1">(${money.parsed.toLocaleString()})</span>}
                            </p>
                          ))}
                          {doc.entity_summary.monetary_values > 3 && (
                            <p className="text-xs text-green-300">+{doc.entity_summary.monetary_values - 3} more</p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Parties */}
                    {doc.entity_summary.parties > 0 && (
                      <div className="liquid-glass-card glass-content p-4 border-purple-500/30">
                        <h4 className="font-medium text-white mb-2">👥 Parties ({doc.entity_summary.parties})</h4>
                        <div className="space-y-1">
                          {doc.extracted_entities.parties.slice(0, 3).map((party: any, idx: number) => (
                            <p key={idx} className="text-sm text-white/90">{party.text}</p>
                          ))}
                          {doc.entity_summary.parties > 3 && (
                            <p className="text-xs text-purple-300">+{doc.entity_summary.parties - 3} more</p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Locations */}
                    {doc.entity_summary.locations > 0 && (
                      <div className="liquid-glass-card glass-content p-4 border-orange-500/30">
                        <h4 className="font-medium text-white mb-2">📍 Locations ({doc.entity_summary.locations})</h4>
                        <div className="space-y-1">
                          {doc.extracted_entities.locations.slice(0, 3).map((loc: any, idx: number) => (
                            <p key={idx} className="text-sm text-white/90">{loc.text}</p>
                          ))}
                          {doc.entity_summary.locations > 3 && (
                            <p className="text-xs text-orange-300">+{doc.entity_summary.locations - 3} more</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  {doc.entity_summary.dates === 0 && doc.entity_summary.monetary_values === 0 && 
                   doc.entity_summary.parties === 0 && doc.entity_summary.locations === 0 && (
                    <p className="text-sm text-white/70 mt-2">No entities extracted from this document.</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}


      {/* Instructions */}
      {uploadedFiles.length === 0 && (
        <div className="p-6">
          <h3 className="text-lg font-medium text-white mb-4">How Document Analysis Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="bg-blue-500/20 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center backdrop-blur-sm">
                <Upload className="h-6 w-6 text-white" />
              </div>
              <h4 className="font-medium text-white mb-1">1. Upload</h4>
              <p className="text-sm text-white/80">Upload your legal documents in PDF, DOC, or TXT format</p>
            </div>
            <div className="text-center">
              <div className="bg-green-500/20 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center backdrop-blur-sm">
                <Eye className="h-6 w-6 text-white" />
              </div>
              <h4 className="font-medium text-white mb-1">2. Analyze</h4>
              <p className="text-sm text-white/80">AI extracts text and identifies legal entities and clauses</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-500/20 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center backdrop-blur-sm">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <h4 className="font-medium text-white mb-1">3. Review</h4>
              <p className="text-sm text-white/80">Review extracted content and use for further legal analysis</p>
            </div>
          </div>
          <div className="mt-6 p-4 liquid-glass-card glass-content">
            <p className="text-sm text-white/90">
              <strong className="text-white">💡 Timeline Feature:</strong> As you analyze documents, a case timeline is automatically built with entity linking across all documents in your active session.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadPage
