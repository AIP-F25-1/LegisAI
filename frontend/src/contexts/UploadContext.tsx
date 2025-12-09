import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface UploadedFile {
  file_id: string
  filename: string
  size: number
  file_type: string
  processing_results?: any
}

interface DocumentAnalysis {
  filename: string
  text_content?: string
  document_preview?: string
  analysis?: string
  extracted_entities?: any
  entity_summary?: any
}

interface UploadContextType {
  uploadedFiles: UploadedFile[]
  setUploadedFiles: (files: UploadedFile[]) => void
  analyzedDocuments: DocumentAnalysis[]
  setAnalyzedDocuments: (docs: DocumentAnalysis[]) => void
  isUploading: boolean
  setIsUploading: (isUploading: boolean) => void
  isAnalyzing: string | null
  setIsAnalyzing: (fileId: string | null) => void
  clearAll: () => void
}

const UploadContext = createContext<UploadContextType | undefined>(undefined)

export const useUpload = () => {
  const context = useContext(UploadContext)
  if (!context) {
    throw new Error('useUpload must be used within UploadProvider')
  }
  return context
}

interface UploadProviderProps {
  children: ReactNode
}

export const UploadProvider: React.FC<UploadProviderProps> = ({ children }) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [analyzedDocuments, setAnalyzedDocuments] = useState<DocumentAnalysis[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState<string | null>(null)

  // Load cached data on mount
  useEffect(() => {
    const cached = sessionStorage.getItem('legisai_upload_cache')
    if (cached) {
      try {
        const cacheData = JSON.parse(cached)
        if (cacheData.uploadedFiles) {
          setUploadedFiles(cacheData.uploadedFiles)
        }
        if (cacheData.analyzedDocuments) {
          setAnalyzedDocuments(cacheData.analyzedDocuments)
        }
      } catch (e) {
        console.warn('Failed to load cached upload data:', e)
      }
    }
  }, [])

  // Save to cache whenever data changes
  useEffect(() => {
    if (uploadedFiles.length > 0 || analyzedDocuments.length > 0) {
      const cacheData = {
        uploadedFiles: uploadedFiles,
        analyzedDocuments: analyzedDocuments,
        timestamp: new Date().toISOString()
      }
      sessionStorage.setItem('legisai_upload_cache', JSON.stringify(cacheData))
    }
  }, [uploadedFiles, analyzedDocuments])

  const clearAll = () => {
    setUploadedFiles([])
    setAnalyzedDocuments([])
    sessionStorage.removeItem('legisai_upload_cache')
  }

  return (
    <UploadContext.Provider
      value={{
        uploadedFiles,
        setUploadedFiles,
        analyzedDocuments,
        setAnalyzedDocuments,
        isUploading,
        setIsUploading,
        isAnalyzing,
        setIsAnalyzing,
        clearAll
      }}
    >
      {children}
    </UploadContext.Provider>
  )
}

