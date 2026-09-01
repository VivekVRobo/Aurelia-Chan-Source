"""
Aurelia Cognitive OS V6 - Observation Deduplicator & Session Engine
====================================================================
Prevents duplicate observations within sliding time windows and manages
explicit perception capture sessions with modality gating.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from aurelia.contracts.v6_contracts import (
    Observation,
    ObservationSession,
    SessionMode,
    Modality
)


class ObservationSessionManager:
    """
    Manages active perception capture sessions and enforces consent boundaries.
    """

    def __init__(self):
        self.active_session: Optional[ObservationSession] = None

    def start_session(
        self,
        session_id: str,
        mode: SessionMode,
        allowed_modalities: Set[Modality]
    ) -> ObservationSession:
        """Starts a bounded perception session."""
        session = ObservationSession(
            session_id=session_id,
            mode=mode,
            allowed_modalities=allowed_modalities,
            started_at=datetime.now(timezone.utc),
            retention_policy="DISCARD_RAW_IMMEDIATELY"
        )
        self.active_session = session
        return session

    def end_session(self) -> Optional[ObservationSession]:
        """Terminates active session."""
        if not self.active_session:
            return None
        ended = ObservationSession(
            session_id=self.active_session.session_id,
            mode=self.active_session.mode,
            allowed_modalities=self.active_session.allowed_modalities,
            started_at=self.active_session.started_at,
            retention_policy=self.active_session.retention_policy,
            ended_at=datetime.now(timezone.utc)
        )
        self.active_session = None
        return ended

    def is_modality_allowed(self, modality: Modality) -> bool:
        """Checks if modality is permitted in current session."""
        if not self.active_session:
            return False
        if self.active_session.mode == SessionMode.OFF:
            return False
        return modality in self.active_session.allowed_modalities


class ObservationDeduplicator:
    """
    Deduplicates repeated identical environmental observations within a sliding window.
    """

    def __init__(self, window_seconds: float = 60.0):
        self.window_seconds = window_seconds
        # Key: (source, entity_type, normalized_value_str) -> last_observed_at
        self.recent_observations: Dict[Tuple[str, str, str], datetime] = {}

    def should_record(
        self,
        source_name: str,
        entity_type: str,
        normalized_val: Any,
        observed_at: Optional[datetime] = None
    ) -> bool:
        """
        Returns True if observation is novel or occurred after the deduplication window.
        """
        now = observed_at or datetime.now(timezone.utc)
        key = (source_name, entity_type, str(normalized_val))

        last_time = self.recent_observations.get(key)
        if last_time:
            elapsed = (now - last_time).total_seconds()
            if elapsed < self.window_seconds:
                return False # Duplicate within window

        self.recent_observations[key] = now
        return True
