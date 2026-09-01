"""
Aurelia Cognitive OS V3 - Phase 12: Event Bus
============================================
Event-driven communication system for autonomous operation.

The event bus enables components to communicate asynchronously
through events, supporting the autonomous cognitive runtime.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from datetime import datetime
from collections import defaultdict


class EventType(Enum):
    """Types of events in the system."""
    USER_MESSAGE = "user_message"
    SYSTEM_RESPONSE = "system_response"
    MEMORY_UPDATE = "memory_update"
    GOAL_PROGRESS = "goal_progress"
    STATE_CHANGE = "state_change"
    ERROR_OCCURRED = "error_occurred"
    INSIGHT_GENERATED = "insight_generated"
    HEALTH_ALERT = "health_alert"


@dataclass
class Event:
    """
    An event in the system.
    
    Represents a notification or message between components.
    """
    id: str
    event_type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 0  # Higher = more important
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """
    Event-driven communication system for autonomous operation.
    
    The event bus:
    - Publishes events to subscribers
    - Subscribes components to specific event types
    - Handles event routing and delivery
    - Maintains event history for debugging
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.event_counter = 0
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe a handler to an event type."""
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe a handler from an event type."""
        if handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
    
    def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        
        Delivers the event to all handlers subscribed to its type.
        """
        # Add to history
        self.event_history.append(event)
        
        # Notify subscribers
        for handler in self.subscribers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                # Log error but continue notifying other handlers
                print(f"Error in event handler: {e}")
    
    def create_event(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """Create and return a new event."""
        event_id = f"event_{self.event_counter}"
        
        event = Event(
            id=event_id,
            event_type=event_type,
            source=source,
            data=data,
            timestamp=datetime.now(),
            priority=priority,
            metadata=metadata or {}
        )
        
        self.event_counter += 1
        return event
    
    def publish_event(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create and publish an event in one step."""
        event = self.create_event(event_type, source, data, priority, metadata)
        self.publish(event)
    
    def get_event_history(self, limit: int = 100) -> List[Event]:
        """Get recent event history."""
        return self.event_history[-limit:]
    
    def get_events_by_type(self, event_type: EventType, limit: int = 50) -> List[Event]:
        """Get recent events of a specific type."""
        type_events = [e for e in self.event_history if e.event_type == event_type]
        return type_events[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of event bus state."""
        return {
            "total_events": len(self.event_history),
            "subscriber_count": sum(len(handlers) for handlers in self.subscribers.values()),
            "by_type": {
                et.value: len(self.get_events_by_type(et))
                for et in EventType
            }
        }