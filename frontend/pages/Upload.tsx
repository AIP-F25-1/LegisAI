import React, { useState, useCallback } from 'react'
import { Upload, FileText, Download, Trash2, Eye } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'
import { MarkdownRenderer } from '../utils/markdown'

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
}

const UploadPage: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [analyzedDocuments, setAnalyzedDocuments] = useState<DocumentAnalysis[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState<string | null>(null)

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
      
      // Use the backend response directly
      setAnalyzedDocuments(prev => [...prev, response.data])
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
        <h1 className="text-3xl font-bold text-gray-900">Document Upload & Analysis</h1>
        <p className="mt-2 text-gray-600">
          Upload and analyze legal documents with AI-powered insights
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} disabled={isUploading} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          {isUploading ? (
            <div>
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
              <p className="text-lg font-medium text-gray-900">Uploading...</p>
            </div>
          ) : isDragActive ? (
            <div>
              <p className="text-lg font-medium text-blue-600">Drop the files here...</p>
              <p className="text-sm text-gray-500">Release to upload</p>
            </div>
          ) : (
            <div>
              <p className="text-lg font-medium text-gray-900">Drag & drop files here</p>
              <p className="text-sm text-gray-500">or click to select files</p>
              <p className="text-xs text-gray-400 mt-2">
                Supports PDF, DOC, DOCX, TXT files
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Uploaded Files</h2>
          <div className="space-y-4">
            {uploadedFiles.map((file) => (
              <div key={file.file_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FileText className="h-8 w-8 text-gray-400 mr-3" />
                    <div>
                      <h3 className="font-medium text-gray-900">{file.filename}</h3>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(file.size)} • {file.file_type}
                      </p>
                      {file.processing_results && (
                        <p className="text-xs text-gray-400">
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
                      className="flex items-center px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
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
                      className="flex items-center px-3 py-1 text-sm text-red-600 hover:text-red-800"
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
            <div key={doc.file_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Document Analysis</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Confidence: {Math.round(doc.confidence_score * 100)}%</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    doc.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                    doc.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {doc.risk_level} risk
                  </span>
                </div>
              </div>
              
              {/* Document Info */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">Document</h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p className="font-medium">{doc.filename}</p>
                    <p className="capitalize">{doc.document_type}</p>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">Status</h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p className="capitalize">{doc.compliance_status}</p>
                    <p>{doc.text_extraction_status}</p>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">Processing</h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>{doc.processing_time}</p>
                    <p className="capitalize">{doc.version}</p>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">AI Generated</h3>
                  <div className="space-y-1 text-sm">
                    {doc.ai_generated ? (
                      <span className="text-green-600 font-medium">Yes</span>
                    ) : (
                      <span className="text-gray-400">No</span>
                    )}
                  </div>
                </div>
              </div>

              {/* AI Analysis */}
              <div className="mb-6">
                <h3 className="font-medium text-gray-900 mb-3">AI Legal Analysis</h3>
                <div className="bg-blue-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <MarkdownRenderer content={doc.analysis} />
                </div>
              </div>

              {/* Key Findings */}
              {doc.key_findings && doc.key_findings.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-medium text-gray-900 mb-3">Key Findings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {doc.key_findings.map((finding, index) => (
                      <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-start">
                          <div className="flex-shrink-0">
                            <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                          </div>
                          <div className="ml-3">
                            <p className="text-sm text-green-800">{finding}</p>
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
                  <h3 className="font-medium text-gray-900 mb-3">Recommendations</h3>
                  <div className="space-y-2">
                    {doc.recommendations.map((recommendation, index) => (
                      <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                        <div className="flex items-start">
                          <div className="flex-shrink-0">
                            <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                          </div>
                          <div className="ml-3">
                            <p className="text-sm text-yellow-800">{recommendation}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Instructions */}
      {uploadedFiles.length === 0 && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">How Document Analysis Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">1. Upload</h4>
              <p className="text-sm text-gray-600">Upload your legal documents in PDF, DOC, or TXT format</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                <Eye className="h-6 w-6 text-green-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">2. Analyze</h4>
              <p className="text-sm text-gray-600">AI extracts text and identifies legal entities and clauses</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full p-3 w-12 h-12 mx-auto mb-2 flex items-center justify-center">
                <FileText className="h-6 w-6 text-purple-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">3. Review</h4>
              <p className="text-sm text-gray-600">Review extracted content and use for further legal analysis</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadPage
