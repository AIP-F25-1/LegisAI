import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { apiClient } from '../utils/api'

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

interface CachedResponse {
  id: string
  type: 'research' | 'drafting' | 'compliance' | 'upload'
  timestamp: string
  query?: string
  response: any
  metadata?: any
}

interface TimelineContextType {
  timelineData: TimelineData | null
  isBuildingTimeline: boolean
  sessionStartTime: string
  cachedResponses: CachedResponse[]
  addToTimeline: (documentId: string, text: string, metadata?: any, responseData?: any) => Promise<void>
  cacheResponse: (type: 'research' | 'drafting' | 'compliance' | 'upload', response: any, query?: string, metadata?: any) => void
  getCachedResponses: (type?: string) => CachedResponse[]
  buildTimeline: () => Promise<void>
  clearTimeline: () => Promise<void>
}

const TimelineContext = createContext<TimelineContextType | undefined>(undefined)

export const useTimeline = () => {
  const context = useContext(TimelineContext)
  if (!context) {
    throw new Error('useTimeline must be used within TimelineProvider')
  }
  return context
}

interface TimelineProviderProps {
  children: ReactNode
}

export const TimelineProvider: React.FC<TimelineProviderProps> = ({ children }) => {
  const [timelineData, setTimelineData] = useState<TimelineData | null>(null)
  const [isBuildingTimeline, setIsBuildingTimeline] = useState(false)
  const [sessionStartTime] = useState<string>(new Date().toISOString())
  const [cachedResponses, setCachedResponses] = useState<CachedResponse[]>([])

  // Load cached data on mount
  useEffect(() => {
    // Load timeline cache
    const cached = sessionStorage.getItem('legisai_timeline_cache')
    if (cached) {
      try {
        const cacheData = JSON.parse(cached)
        if (cacheData.session_start === sessionStartTime) {
          setTimelineData(cacheData.timeline)
        }
      } catch (e) {
        console.warn('Failed to load cached timeline:', e)
      }
    }
    
    // Load responses cache
    const responsesCache = sessionStorage.getItem('legisai_responses_cache')
    if (responsesCache) {
      try {
        const cacheData = JSON.parse(responsesCache)
        if (cacheData.session_start === sessionStartTime) {
          setCachedResponses(cacheData.responses || [])
        }
      } catch (e) {
        console.warn('Failed to load cached responses:', e)
      }
    }
  }, [sessionStartTime])

  const cacheResponse = (type: 'research' | 'drafting' | 'compliance' | 'upload', response: any, query?: string, metadata?: any) => {
    const cachedResponse: CachedResponse = {
      id: `${type}_${Date.now()}`,
      type: type,
      timestamp: new Date().toISOString(),
      query: query,
      response: response,
      metadata: metadata
    }
    
    const updated = [...cachedResponses, cachedResponse]
    setCachedResponses(updated)
    
    // Save to sessionStorage
    const cacheData = {
      responses: updated,
      session_start: sessionStartTime,
      timestamp: new Date().toISOString()
    }
    sessionStorage.setItem('legisai_responses_cache', JSON.stringify(cacheData))
  }

  const getCachedResponses = (type?: string): CachedResponse[] => {
    if (type) {
      return cachedResponses.filter(r => r.type === type)
    }
    return cachedResponses
  }

  const addToTimeline = async (documentId: string, text: string, metadata?: any, responseData?: any) => {
    try {
      if (text.length > 50) {
        // Cache the response if provided
        if (responseData && metadata?.type) {
          cacheResponse(metadata.type as 'research' | 'drafting' | 'compliance' | 'upload', responseData, metadata.query || metadata.title, metadata)
        }
        
        await apiClient.post('/timeline/add-document', {
          document_id: documentId,
          text: text,
          metadata: {
            ...metadata,
            added_at: new Date().toISOString()
          }
        })
        // Auto-build timeline after adding
        await buildTimeline()
      }
    } catch (error: any) {
      console.warn('⚠️ Timeline update failed (optional):', error)
    }
  }

  const buildTimeline = async () => {
    setIsBuildingTimeline(true)
    try {
      const response = await apiClient.post('/timeline/build', {
        sort_by_date: true
      })
      setTimelineData(response.data)
      
      // Cache timeline in sessionStorage with timestamp
      const cacheData = {
        timeline: response.data,
        timestamp: new Date().toISOString(),
        session_start: sessionStartTime
      }
      sessionStorage.setItem('legisai_timeline_cache', JSON.stringify(cacheData))
    } catch (error: any) {
      console.warn('Timeline build failed (optional):', error)
    } finally {
      setIsBuildingTimeline(false)
    }
  }

  const clearTimeline = async () => {
    try {
      await apiClient.post('/timeline/clear')
      setTimelineData(null)
      setCachedResponses([])
      sessionStorage.removeItem('legisai_timeline_cache')
      sessionStorage.removeItem('legisai_responses_cache')
    } catch (error: any) {
      console.warn('Timeline clear failed:', error)
    }
  }

  return (
    <TimelineContext.Provider
      value={{
        timelineData,
        isBuildingTimeline,
        sessionStartTime,
        cachedResponses,
        addToTimeline,
        cacheResponse,
        getCachedResponses,
        buildTimeline,
        clearTimeline
      }}
    >
      {children}
    </TimelineContext.Provider>
  )
}

