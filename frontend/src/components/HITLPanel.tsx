import React, { useState } from 'react'
import { CheckCircle, XCircle, Edit2, Save, X, MessageSquare, TrendingUp } from 'lucide-react'
import { apiClient } from '../utils/api'
import toast from 'react-hot-toast'

interface HITLPanelProps {
  featureType: string
  originalOutput: any
  onAccept?: () => void
  onReject?: () => void
  onEdit?: (editedContent: string) => void
}

const HITLPanel: React.FC<HITLPanelProps> = ({
  featureType,
  originalOutput,
  onAccept,
  onReject,
  onEdit
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState('')
  const [feedbackReason, setFeedbackReason] = useState('')
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [submittedAction, setSubmittedAction] = useState<string | null>(null)

  const handleAccept = async () => {
    // Close any open forms first
    if (showFeedbackForm) {
      setShowFeedbackForm(false)
      setFeedbackReason('')
    }
    if (isEditing) {
      setIsEditing(false)
      setEditedContent('')
    }

    setIsSubmitting(true)
    try {
      await apiClient.post('/hitl/feedback', {
        feature_type: featureType,
        action: 'accept',
        original_output: originalOutput,
        metadata: {
          timestamp: new Date().toISOString()
        }
      })
      toast.success('✅ Output accepted - feedback recorded')
      setFeedbackSubmitted(true)
      setSubmittedAction('accept')
      if (onAccept) onAccept()
    } catch (error: any) {
      toast.error(`Error submitting feedback: ${error.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReject = async () => {
    // Close edit form if open
    if (isEditing) {
      setIsEditing(false)
      setEditedContent('')
    }

    if (!showFeedbackForm) {
      setShowFeedbackForm(true)
      return
    }

    if (!feedbackReason.trim()) {
      toast.error('Please provide a reason for rejection')
      return
    }

    setIsSubmitting(true)
    try {
      await apiClient.post('/hitl/feedback', {
        feature_type: featureType,
        action: 'reject',
        original_output: originalOutput,
        feedback_reason: feedbackReason,
        metadata: {
          timestamp: new Date().toISOString()
        }
      })
      toast.success('❌ Output rejected - feedback recorded')
      setShowFeedbackForm(false)
      setFeedbackReason('')
      setFeedbackSubmitted(true)
      setSubmittedAction('reject')
      if (onReject) onReject()
    } catch (error: any) {
      toast.error(`Error submitting feedback: ${error.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEdit = () => {
    // Close feedback form if open
    if (showFeedbackForm) {
      setShowFeedbackForm(false)
      setFeedbackReason('')
    }

    if (!isEditing) {
      // Extract text content from output
      const content = typeof originalOutput === 'string'
        ? originalOutput
        : originalOutput?.content || originalOutput?.summary || originalOutput?.draft_content || JSON.stringify(originalOutput, null, 2)
      setEditedContent(content)
      setIsEditing(true)
    }
  }

  const handleSaveEdit = async () => {
    if (!editedContent.trim()) {
      toast.error('Edited content cannot be empty')
      return
    }

    setIsSubmitting(true)
    try {
      await apiClient.post('/hitl/feedback', {
        feature_type: featureType,
        action: 'edit',
        original_output: originalOutput,
        user_edit: editedContent,
        metadata: {
          timestamp: new Date().toISOString()
        }
      })
      toast.success('✏️ Edit saved - feedback recorded')
      setIsEditing(false)
      setFeedbackSubmitted(true)
      setSubmittedAction('edit')
      if (onEdit) onEdit(editedContent)
    } catch (error: any) {
      toast.error(`Error submitting feedback: ${error.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditedContent('')
  }

  // Show success state after feedback is submitted
  if (feedbackSubmitted) {
    return (
      <div className="mt-4 liquid-glass-card glass-content px-4 pt-4 pb-2 border-green-500/30" style={{ height: 'fit-content', width: 'fit-content', maxWidth: '100%' }}>
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 flex-shrink-0">
            <CheckCircle className="w-5 h-5 text-green-300 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-white">
                Feedback Submitted Successfully
              </h3>
              <p className="text-xs text-white/90 mt-1">
                {submittedAction === 'accept' && 'Output accepted - thank you for your feedback!'}
                {submittedAction === 'reject' && 'Output rejected - your feedback helps improve the system!'}
                {submittedAction === 'edit' && 'Edit saved - your feedback helps improve the system!'}
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              setFeedbackSubmitted(false)
              setSubmittedAction(null)
            }}
            className="text-xs text-green-300 hover:text-green-200 underline flex-shrink-0"
          >
            Reset
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="mt-4 liquid-glass-card glass-content px-4 pt-4 pb-2" style={{ height: 'fit-content' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-blue-300" />
          <h3 className="text-sm font-semibold text-white">Human-in-the-Loop Feedback</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleAccept}
            disabled={isSubmitting || (isEditing && !showFeedbackForm)}
            className="glass-button flex items-center gap-1 px-3 py-1.5 bg-green-500/20 border-green-500/30 hover:bg-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            <CheckCircle className="w-4 h-4" />
            Accept
          </button>
          <button
            onClick={handleReject}
            disabled={isSubmitting || isEditing}
            className="glass-button flex items-center gap-1 px-3 py-1.5 bg-red-500/20 border-red-500/30 hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            <XCircle className="w-4 h-4" />
            Reject
          </button>
          <button
            onClick={handleEdit}
            disabled={isSubmitting || showFeedbackForm}
            className="glass-button flex items-center gap-1 px-3 py-1.5 bg-yellow-500/20 border-yellow-500/30 hover:bg-yellow-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            <Edit2 className="w-4 h-4" />
            Edit
          </button>
        </div>
      </div>

      {showFeedbackForm && (
        <div className="mt-3 p-3 liquid-glass-card glass-content mb-2">
          <label className="block text-sm font-medium text-white mb-2">
            Reason for rejection:
          </label>
          <textarea
            value={feedbackReason}
            onChange={(e) => setFeedbackReason(e.target.value)}
            placeholder="Please explain why this output is not acceptable..."
            className="glass-textarea w-full px-3 py-2 text-sm"
            rows={3}
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleReject}
              disabled={isSubmitting || !feedbackReason.trim()}
              className="glass-button px-3 py-1.5 bg-red-500/20 border-red-500/30 hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              Submit Rejection
            </button>
            <button
              onClick={() => {
                setShowFeedbackForm(false)
                setFeedbackReason('')
              }}
              className="glass-button px-3 py-1.5 text-sm font-medium"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {isEditing && (
        <div className="mt-3 p-3 liquid-glass-card glass-content mb-2">
          <label className="block text-sm font-medium text-white mb-2">
            Edit output:
          </label>
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className="glass-textarea w-full px-3 py-2 text-sm font-mono"
            rows={8}
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleSaveEdit}
              disabled={isSubmitting || !editedContent.trim()}
              className="glass-button flex items-center gap-1 px-3 py-1.5 bg-green-500/20 border-green-500/30 hover:bg-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              <Save className="w-4 h-4" />
              Save Edit
            </button>
            <button
              onClick={handleCancelEdit}
              className="glass-button flex items-center gap-1 px-3 py-1.5 text-sm font-medium"
            >
              <X className="w-4 h-4" />
              Cancel
            </button>
          </div>
        </div>
      )}

      {!showFeedbackForm && !isEditing && (
        <div className="mt-2 mb-0 text-xs text-white/70">
          <TrendingUp className="w-3 h-3 inline mr-1" />
          Your feedback helps improve AI model reasoning
        </div>
      )}
    </div>
  )
}

export default HITLPanel

