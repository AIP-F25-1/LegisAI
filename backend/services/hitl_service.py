"""
Human-in-the-Loop (HITL) Service
Manages user feedback, accept/reject/edit actions, and continuous learning
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FeedbackEntry:
    """Single feedback entry"""
    id: str
    timestamp: str
    feature_type: str  # "research", "drafting", "compliance", "clause_analysis", etc.
    action: str  # "accept", "reject", "edit"
    original_output: Dict[str, Any]
    user_edit: Optional[str] = None
    feedback_reason: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class LearningPattern:
    """Pattern learned from feedback"""
    pattern_type: str  # "rejection_reason", "edit_pattern", "preference"
    feature_type: str
    pattern: str
    frequency: int
    last_updated: str

class HITLService:
    """Service for managing human-in-the-loop feedback and learning"""
    
    def __init__(self, feedback_file: str = "feedback_data.json", learning_file: str = "learning_patterns.json"):
        """
        Initialize HITL service
        
        Args:
            feedback_file: Path to feedback storage file
            learning_file: Path to learning patterns file
        """
        self.feedback_file = Path(feedback_file)
        self.learning_file = Path(learning_file)
        self.feedback_entries: List[FeedbackEntry] = []
        self.learning_patterns: List[LearningPattern] = []
        
        # Load existing data
        self._load_feedback()
        self._load_learning_patterns()
    
    def _load_feedback(self):
        """Load feedback entries from file"""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
                    self.feedback_entries = [
                        FeedbackEntry(**entry) for entry in data
                    ]
                logger.info(f"✅ Loaded {len(self.feedback_entries)} feedback entries")
            except Exception as e:
                logger.error(f"❌ Error loading feedback: {e}")
                self.feedback_entries = []
        else:
            self.feedback_entries = []
    
    def _save_feedback(self):
        """Save feedback entries to file"""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(
                    [asdict(entry) for entry in self.feedback_entries],
                    f,
                    indent=2
                )
            logger.info(f"✅ Saved {len(self.feedback_entries)} feedback entries")
        except Exception as e:
            logger.error(f"❌ Error saving feedback: {e}")
    
    def _load_learning_patterns(self):
        """Load learning patterns from file"""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r') as f:
                    data = json.load(f)
                    self.learning_patterns = [
                        LearningPattern(**pattern) for pattern in data
                    ]
                logger.info(f"✅ Loaded {len(self.learning_patterns)} learning patterns")
            except Exception as e:
                logger.error(f"❌ Error loading learning patterns: {e}")
                self.learning_patterns = []
        else:
            self.learning_patterns = []
    
    def _save_learning_patterns(self):
        """Save learning patterns to file"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(
                    [asdict(pattern) for pattern in self.learning_patterns],
                    f,
                    indent=2
                )
            logger.info(f"✅ Saved {len(self.learning_patterns)} learning patterns")
        except Exception as e:
            logger.error(f"❌ Error saving learning patterns: {e}")
    
    def submit_feedback(
        self,
        feature_type: str,
        action: str,
        original_output: Dict[str, Any],
        user_edit: Optional[str] = None,
        feedback_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit user feedback
        
        Args:
            feature_type: Type of feature (research, drafting, etc.)
            action: Action taken (accept, reject, edit)
            original_output: Original agent output
            user_edit: User's edited version (if action is "edit")
            feedback_reason: Reason for feedback
            metadata: Additional metadata
            
        Returns:
            Feedback entry ID
        """
        entry_id = f"{feature_type}_{datetime.now().isoformat()}_{len(self.feedback_entries)}"
        
        entry = FeedbackEntry(
            id=entry_id,
            timestamp=datetime.now().isoformat(),
            feature_type=feature_type,
            action=action,
            original_output=original_output,
            user_edit=user_edit,
            feedback_reason=feedback_reason,
            metadata=metadata or {}
        )
        
        self.feedback_entries.append(entry)
        self._save_feedback()
        
        # Update learning patterns
        self._update_learning_patterns(entry)
        
        logger.info(f"✅ Feedback submitted: {entry_id} ({action})")
        return entry_id
    
    def _update_learning_patterns(self, entry: FeedbackEntry):
        """Update learning patterns based on feedback"""
        # Extract patterns from feedback
        if entry.action == "reject" and entry.feedback_reason:
            # Learn rejection reasons
            pattern_key = f"rejection_{entry.feature_type}"
            pattern = self._find_or_create_pattern(
                "rejection_reason",
                entry.feature_type,
                pattern_key
            )
            pattern.frequency += 1
            pattern.last_updated = entry.timestamp
        
        elif entry.action == "edit" and entry.user_edit:
            # Learn edit patterns
            pattern_key = f"edit_{entry.feature_type}"
            pattern = self._find_or_create_pattern(
                "edit_pattern",
                entry.feature_type,
                pattern_key
            )
            pattern.frequency += 1
            pattern.last_updated = entry.timestamp
        
        self._save_learning_patterns()
    
    def _find_or_create_pattern(
        self,
        pattern_type: str,
        feature_type: str,
        pattern_key: str
    ) -> LearningPattern:
        """Find or create a learning pattern"""
        for pattern in self.learning_patterns:
            if (pattern.pattern_type == pattern_type and
                pattern.feature_type == feature_type and
                pattern.pattern == pattern_key):
                return pattern
        
        # Create new pattern
        new_pattern = LearningPattern(
            pattern_type=pattern_type,
            feature_type=feature_type,
            pattern=pattern_key,
            frequency=0,
            last_updated=datetime.now().isoformat()
        )
        self.learning_patterns.append(new_pattern)
        return new_pattern
    
    def get_feedback_stats(self, feature_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback statistics
        
        Args:
            feature_type: Optional filter by feature type
            
        Returns:
            Statistics dictionary
        """
        entries = (
            [e for e in self.feedback_entries if e.feature_type == feature_type]
            if feature_type
            else self.feedback_entries
        )
        
        total = len(entries)
        accepts = sum(1 for e in entries if e.action == "accept")
        rejects = sum(1 for e in entries if e.action == "reject")
        edits = sum(1 for e in entries if e.action == "edit")
        
        return {
            "total_feedback": total,
            "accepts": accepts,
            "rejects": rejects,
            "edits": edits,
            "accept_rate": accepts / total if total > 0 else 0.0,
            "reject_rate": rejects / total if total > 0 else 0.0,
            "edit_rate": edits / total if total > 0 else 0.0,
            "learning_patterns": len(self.learning_patterns)
        }
    
    def get_learning_insights(self, feature_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get learning insights for improving model reasoning
        
        Args:
            feature_type: Optional filter by feature type
            
        Returns:
            Insights dictionary
        """
        patterns = (
            [p for p in self.learning_patterns if p.feature_type == feature_type]
            if feature_type
            else self.learning_patterns
        )
        
        rejection_patterns = [p for p in patterns if p.pattern_type == "rejection_reason"]
        edit_patterns = [p for p in patterns if p.pattern_type == "edit_pattern"]
        
        return {
            "rejection_patterns": [
                {
                    "pattern": p.pattern,
                    "frequency": p.frequency,
                    "last_updated": p.last_updated
                }
                for p in sorted(rejection_patterns, key=lambda x: x.frequency, reverse=True)
            ],
            "edit_patterns": [
                {
                    "pattern": p.pattern,
                    "frequency": p.frequency,
                    "last_updated": p.last_updated
                }
                for p in sorted(edit_patterns, key=lambda x: x.frequency, reverse=True)
            ],
            "recommendations": self._generate_recommendations(patterns)
        }
    
    def _generate_recommendations(self, patterns: List[LearningPattern]) -> List[str]:
        """Generate recommendations based on learning patterns"""
        recommendations = []
        
        # Find most common rejection reasons
        rejection_patterns = [p for p in patterns if p.pattern_type == "rejection_reason"]
        if rejection_patterns:
            top_rejection = max(rejection_patterns, key=lambda x: x.frequency)
            if top_rejection.frequency > 3:
                recommendations.append(
                    f"High rejection rate for {top_rejection.feature_type}. "
                    f"Consider improving output quality for this feature."
                )
        
        # Find most common edit patterns
        edit_patterns = [p for p in patterns if p.pattern_type == "edit_pattern"]
        if edit_patterns:
            top_edit = max(edit_patterns, key=lambda x: x.frequency)
            if top_edit.frequency > 5:
                recommendations.append(
                    f"Frequent edits for {top_edit.feature_type}. "
                    f"Consider adjusting default output format."
                )
        
        return recommendations
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent feedback entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of feedback entries
        """
        sorted_entries = sorted(
            self.feedback_entries,
            key=lambda x: x.timestamp,
            reverse=True
        )
        
        return [
            asdict(entry) for entry in sorted_entries[:limit]
        ]

