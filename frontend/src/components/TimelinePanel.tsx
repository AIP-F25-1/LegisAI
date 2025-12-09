import React, { useState } from 'react'
import { Clock, TrendingUp, FileText, X, ChevronDown, ChevronUp } from 'lucide-react'
import { useTimeline } from '../contexts/TimelineContext'

const TimelinePanel: React.FC = () => {
  const { timelineData, sessionStartTime, isBuildingTimeline } = useTimeline()
  const [isExpanded, setIsExpanded] = useState(true)

  if (!timelineData || timelineData.timeline.total_events === 0) {
    return null
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    } catch {
      return dateString
    }
  }

  const getEventTypeColor = (eventType: string) => {
    const colors: Record<string, string> = {
      filing: 'bg-blue-100 text-blue-800',
      hearing: 'bg-purple-100 text-purple-800',
      judgment: 'bg-green-100 text-green-800',
      settlement: 'bg-yellow-100 text-yellow-800',
      appeal: 'bg-red-100 text-red-800',
      motion: 'bg-indigo-100 text-indigo-800',
      document_filed: 'bg-gray-100 text-gray-800',
      research: 'bg-cyan-100 text-cyan-800',
      drafting: 'bg-pink-100 text-pink-800',
      compliance: 'bg-orange-100 text-orange-800',
      other: 'bg-gray-100 text-gray-800'
    }
    return colors[eventType] || colors.other
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center">
          <Clock className="h-5 w-5 mr-2 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Case Timeline (Active Session)
          </h3>
          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
            {timelineData.timeline.total_events} events
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {isBuildingTimeline && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
          {isExpanded ? (
            <ChevronUp className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          )}
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t">
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="flex items-center">
                <Clock className="h-4 w-4 text-blue-600 mr-2" />
                <div>
                  <p className="text-xs text-gray-600">Events</p>
                  <p className="text-lg font-bold text-blue-600">{timelineData.timeline.total_events}</p>
                </div>
              </div>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <div className="flex items-center">
                <FileText className="h-4 w-4 text-green-600 mr-2" />
                <div>
                  <p className="text-xs text-gray-600">Documents</p>
                  <p className="text-lg font-bold text-green-600">{timelineData.documents.total_documents}</p>
                </div>
              </div>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <div className="flex items-center">
                <TrendingUp className="h-4 w-4 text-purple-600 mr-2" />
                <div>
                  <p className="text-xs text-gray-600">Entities</p>
                  <p className="text-lg font-bold text-purple-600">{timelineData.entities.linked_entities.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-orange-50 rounded-lg p-3">
              <div className="flex items-center">
                <Clock className="h-4 w-4 text-orange-600 mr-2" />
                <div>
                  <p className="text-xs text-gray-600">Span</p>
                  <p className="text-lg font-bold text-orange-600">{timelineData.timeline.date_range.span_days}d</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Events */}
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Events</h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {timelineData.timeline.events.slice(0, 5).map((event, index) => (
                <div key={index} className="flex items-start space-x-2 p-2 bg-gray-50 rounded text-xs">
                  <span className={`px-2 py-1 rounded ${getEventTypeColor(event.event_type)}`}>
                    {event.event_type}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-700 truncate">{event.context.substring(0, 60)}...</p>
                    <p className="text-gray-500">{formatDate(event.parsed_date)}</p>
                  </div>
                </div>
              ))}
            </div>
            {timelineData.timeline.events.length > 5 && (
              <p className="text-xs text-gray-500 text-center mt-2">
                +{timelineData.timeline.events.length - 5} more events
              </p>
            )}
          </div>

          {/* Entity Links Preview */}
          {timelineData.entities.linked_entities.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Linked Entities</h4>
              <div className="flex flex-wrap gap-2">
                {timelineData.entities.linked_entities.slice(0, 5).map((link, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs"
                    title={`Appears in ${link.documents.length} document(s)`}
                  >
                    {link.entity} ({link.occurrence_count})
                  </span>
                ))}
                {timelineData.entities.linked_entities.length > 5 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                    +{timelineData.entities.linked_entities.length - 5} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default TimelinePanel

