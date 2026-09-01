"""
Aurelia Cognitive OS V3 - Phase 4: Episodic Memory
================================================
Memory of specific events and experiences.

Episodic memory stores WHAT happened - specific events,
conversations, assessments, and interactions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from aurelia.cognition.contracts import Evidence


class EventType(Enum):
    """Types of episodic events."""
    CONVERSATION = "conversation"
    RESUME_UPLOAD = "resume_upload"
    RESUME_PARSED = "resume_parsed"
    INTERVIEW_COMPLETED = "interview_completed"
    INTERVIEW_SCORED = "interview_scored"
    GOAL_CREATED = "goal_created"
    GOAL_UPDATED = "goal_updated"
    SKILL_ASSESSED = "skill_assessed"
    GAP_ANALYSIS = "gap_analysis"
    SALARY_RESEARCHED = "salary_researched"
    CAREER_PATH_EXPLORED = "career_path_explored"
    USER_CORRECTION = "user_correction"


@dataclass
class EpisodicEvent:
    """
    A single episodic event.
    
    Events are what actually happened - time-stamped, immutable records.
    """
    id: str
    event_type: EventType
    timestamp: datetime
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 1.0
    related_events: List[str] = field(default_factory=list)  # IDs of related events


class EpisodicMemory:
    """
    Memory of specific events and experiences.
    
    Examples:
    - User completed resume review
    - Interview simulation #4 scored 76
    - User previously considered Product Manager
    - A development plan was created in May
    """
    
    def __init__(self):
        self.events: List[EpisodicEvent] = []
        self.event_counter = 0
    
    def add_event(self, event: EpisodicEvent):
        """Add an episodic event."""
        self.events.append(event)
        self.event_counter += 1
    
    def create_event(
        self,
        event_type: EventType,
        description: str,
        data: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[Evidence]] = None,
        confidence: float = 1.0
    ) -> EpisodicEvent:
        """Create and add a new episodic event."""
        event_id = f"event_{self.event_counter}"
        
        event = EpisodicEvent(
            id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            description=description,
            data=data or {},
            evidence=evidence or [],
            confidence=confidence
        )
        
        self.add_event(event)
        return event
    
    def get_events_by_type(self, event_type: EventType) -> List[EpisodicEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_by_time_range(self, start: datetime, end: datetime) -> List[EpisodicEvent]:
        """Get events within a time range."""
        return [e for e in self.events if start <= e.timestamp <= end]
    
    def get_recent_events(self, limit: int = 10) -> List[EpisodicEvent]:
        """Get the most recent events."""
        return sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def get_events_for_entity(self, entity_id: str) -> List[EpisodicEvent]:
        """Get events related to a specific entity."""
        return [e for e in self.events if entity_id in str(e.data)]
    
    def get_conversation_history(self, limit: int = 20) -> List[EpisodicEvent]:
        """Get recent conversation events."""
        conversations = self.get_events_by_type(EventType.CONVERSATION)
        return sorted(conversations, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def get_last_occurrence(self, event_type: EventType) -> Optional[EpisodicEvent]:
        """Get the last occurrence of a specific event type."""
        events = self.get_events_by_type(event_type)
        if events:
            return sorted(events, key=lambda e: e.timestamp, reverse=True)[0]
        return None
    
    def count_events_by_type(self) -> Dict[EventType, int]:
        """Count events by type."""
        counts = {}
        for event in self.events:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts
    
    def find_repeated_patterns(self) -> Dict[str, int]:
        """
        Find repeated patterns in episodic memory.
        
        This feeds into memory consolidation - identifying stable patterns
        that should become semantic knowledge.
        """
        patterns = {}
        
        # Count event types
        for event in self.events:
            pattern = f"{event.event_type.value}"
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        return patterns
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of episodic memory state."""
        return {
            "total_events": len(self.events),
            "event_types": self.count_events_by_type(),
            "recent_events": len(self.get_recent_events(5)),
            "patterns": self.find_repeated_patterns()
        }