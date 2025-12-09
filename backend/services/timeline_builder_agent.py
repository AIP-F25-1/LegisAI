"""
Timeline Builder Agent - Multi-Modal Legal Intelligence
Constructs case chronology from multiple documents and links entities across filings
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class TimelineBuilderAgent:
    """Builds timelines from multiple legal documents with entity linking"""
    
    def __init__(self, ocr_agent=None):
        """Initialize Timeline Builder Agent
        
        Args:
            ocr_agent: Optional OCRAgent instance for processing scanned documents
        """
        self.ocr_agent = ocr_agent
        self.documents = []  # Store processed documents
        self.entities = defaultdict(list)  # Entity -> list of occurrences
        self.events = []  # Chronological events
        logger.info("✅ Timeline Builder Agent initialized")
    
    def add_document(self, document_id: str, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a document to the timeline builder
        
        Args:
            document_id: Unique identifier for the document
            text: Document text content
            metadata: Optional metadata (date, type, etc.)
        
        Returns:
            Processing result with extracted entities and events
        """
        # Extract entities and dates from document
        if self.ocr_agent:
            entity_result = self.ocr_agent.extract_entities(text)
            entities = entity_result.get("entities", {})
        else:
            entities = self._extract_entities_basic(text)
        
        # Extract events (dates with context)
        events = self._extract_events(text, document_id, metadata)
        
        # Store document
        doc_entry = {
            "id": document_id,
            "text": text,
            "metadata": metadata or {},
            "entities": entities,
            "events": events,
            "added_at": datetime.now().isoformat()
        }
        self.documents.append(doc_entry)
        
        # Index entities for linking
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity_text = entity.get("text", "") if isinstance(entity, dict) else str(entity)
                if entity_text:
                    self.entities[entity_text].append({
                        "document_id": document_id,
                        "entity_type": entity_type,
                        "context": entity.get("context", ""),
                        "position": entity.get("start", 0)
                    })
        
        return {
            "success": True,
            "document_id": document_id,
            "entities_extracted": sum(len(v) for v in entities.values()),
            "events_extracted": len(events)
        }
    
    def _extract_entities_basic(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Basic entity extraction without OCR agent"""
        entities = {
            "parties": [],
            "dates": [],
            "monetary_values": [],
            "locations": []
        }
        
        # Date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities["dates"].append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        # Party patterns (common legal terms)
        party_patterns = [
            r'\b(?:Plaintiff|Defendant|Appellant|Appellee|Petitioner|Respondent)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b(?:Party\s+(?:A|B|One|Two)|First\s+Party|Second\s+Party)\b'
        ]
        
        for pattern in party_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities["parties"].append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return entities
    
    def _extract_events(self, text: str, document_id: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Extract chronological events from document text"""
        events = []
        
        # Date patterns with context
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})\b'
        
        # Find dates with surrounding context
        for match in re.finditer(date_pattern, text, re.IGNORECASE):
            date_str = match.group()
            start_pos = max(0, match.start() - 100)
            end_pos = min(len(text), match.end() + 100)
            context = text[start_pos:end_pos]
            
            # Try to parse date
            parsed_date = self._parse_date(date_str)
            
            event = {
                "date_text": date_str,
                "parsed_date": parsed_date,
                "context": context.strip(),
                "document_id": document_id,
                "position": match.start(),
                "event_type": self._classify_event(context)
            }
            events.append(event)
        
        # Use document metadata date if available
        if metadata and metadata.get("date"):
            doc_date = self._parse_date(str(metadata["date"]))
            if doc_date:
                events.append({
                    "date_text": str(metadata["date"]),
                    "parsed_date": doc_date,
                    "context": f"Document: {metadata.get('title', document_id)}",
                    "document_id": document_id,
                    "position": 0,
                    "event_type": "document_filed"
                })
        
        return events
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            formats = [
                "%m/%d/%Y",
                "%m-%d-%Y",
                "%Y-%m-%d",
                "%B %d, %Y",
                "%b %d, %Y",
                "%d %B %Y",
                "%d %b %Y"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat()
                except:
                    continue
        except:
            pass
        return None
    
    def _classify_event(self, context: str) -> str:
        """Classify event type based on context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["filed", "filing", "submitted"]):
            return "filing"
        elif any(word in context_lower for word in ["hearing", "court", "trial"]):
            return "hearing"
        elif any(word in context_lower for word in ["judgment", "ruling", "decision", "order"]):
            return "judgment"
        elif any(word in context_lower for word in ["settlement", "agreement", "resolved"]):
            return "settlement"
        elif any(word in context_lower for word in ["appeal", "appealed"]):
            return "appeal"
        elif any(word in context_lower for word in ["motion", "moved"]):
            return "motion"
        else:
            return "other"
    
    def build_timeline(self, sort_by_date: bool = True) -> Dict[str, Any]:
        """Build chronological timeline from all documents"""
        # Collect all events
        all_events = []
        for doc in self.documents:
            all_events.extend(doc["events"])
        
        # Sort by date
        if sort_by_date:
            all_events.sort(key=lambda e: e.get("parsed_date", ""))
        
        # Build entity links
        entity_links = self._build_entity_links()
        
        return {
            "timeline": {
                "events": all_events,
                "total_events": len(all_events),
                "date_range": self._get_date_range(all_events),
                "event_types": self._count_event_types(all_events)
            },
            "entities": {
                "linked_entities": entity_links,
                "total_unique_entities": len(self.entities),
                "entity_occurrences": {k: len(v) for k, v in self.entities.items()}
            },
            "documents": {
                "total_documents": len(self.documents),
                "document_ids": [doc["id"] for doc in self.documents]
            }
        }
    
    def _build_entity_links(self) -> List[Dict[str, Any]]:
        """Build entity links across documents"""
        links = []
        
        # Find entities that appear in multiple documents
        for entity_name, occurrences in self.entities.items():
            if len(occurrences) > 1:
                # Entity appears in multiple documents - create link
                doc_ids = list(set(occ["document_id"] for occ in occurrences))
                links.append({
                    "entity": entity_name,
                    "documents": doc_ids,
                    "occurrence_count": len(occurrences),
                    "entity_type": occurrences[0].get("entity_type", "unknown")
                })
        
        return links
    
    def _get_date_range(self, events: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """Get date range from events"""
        dates = [e.get("parsed_date") for e in events if e.get("parsed_date")]
        if dates:
            dates.sort()
            return {
                "earliest": dates[0],
                "latest": dates[-1],
                "span_days": (datetime.fromisoformat(dates[-1]) - datetime.fromisoformat(dates[0])).days if len(dates) > 1 else 0
            }
        return {"earliest": None, "latest": None, "span_days": 0}
    
    def _count_event_types(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count events by type"""
        counts = defaultdict(int)
        for event in events:
            event_type = event.get("event_type", "other")
            counts[event_type] += 1
        return dict(counts)
    
    def get_entity_timeline(self, entity_name: str) -> Dict[str, Any]:
        """Get timeline for a specific entity"""
        if entity_name not in self.entities:
            return {
                "success": False,
                "error": f"Entity '{entity_name}' not found"
            }
        
        occurrences = self.entities[entity_name]
        doc_ids = set(occ["document_id"] for occ in occurrences)
        
        # Get events from documents containing this entity
        entity_events = []
        for doc in self.documents:
            if doc["id"] in doc_ids:
                entity_events.extend(doc["events"])
        
        # Sort by date
        entity_events.sort(key=lambda e: e.get("parsed_date", ""))
        
        return {
            "success": True,
            "entity": entity_name,
            "documents": list(doc_ids),
            "occurrences": len(occurrences),
            "events": entity_events,
            "event_count": len(entity_events)
        }
    
    def clear(self):
        """Clear all documents and reset timeline"""
        self.documents = []
        self.entities = defaultdict(list)
        self.events = []
        logger.info("Timeline Builder cleared")

