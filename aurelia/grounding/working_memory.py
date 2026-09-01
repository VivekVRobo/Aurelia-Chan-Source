"""
Aurelia Cognitive OS V6 - Perceptual Working Memory & Session Manager
=====================================================================
Manages ephemeral environmental observations, enforces explicit TTL expiration,
and handles active perception capture sessions.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from aurelia.contracts.v6_contracts import (
    Observation,
    ObservationSession,
    ObservationPromotionStage,
    ObservedEntityState,
    EntityVisibility,
    EntityExistence,
    Modality,
    SessionMode
)


class PerceptualWorkingMemory:
    """
    In-memory store of active environmental observations with explicit TTL expiration.
    """

    def __init__(self):
        self.observations: Dict[str, Observation] = {}
        self.entity_states: Dict[str, ObservedEntityState] = {}

    def add_observation(self, obs: Observation) -> None:
        """Stores an observation and updates observed entity states."""
        self.observations[obs.observation_id] = obs
        
        # Update visibility states
        for ent in obs.entities:
            self.entity_states[ent.entity_id] = ObservedEntityState(
                entity_id=ent.entity_id,
                visibility=EntityVisibility.CURRENTLY_VISIBLE,
                existence=EntityExistence.PERSISTENT,
                last_observed_at=obs.observed_at
            )

    def get_observation(self, observation_id: str) -> Optional[Observation]:
        """Retrieves observation if not expired."""
        obs = self.observations.get(observation_id)
        if obs and obs.expires_at and obs.expires_at < datetime.now(timezone.utc):
            return None
        return obs

    def sweep_expired(self, current_time: Optional[datetime] = None) -> List[str]:
        """
        Purges expired ephemeral observations while preserving persistent entity existence.
        """
        now = current_time or datetime.now(timezone.utc)
        expired_ids = []

        for oid, obs in list(self.observations.items()):
            if obs.expires_at and obs.expires_at <= now:
                # Mark associated entities as NOT_CURRENTLY_VISIBLE rather than non-existent
                for ent in obs.entities:
                    if ent.entity_id in self.entity_states:
                        prev = self.entity_states[ent.entity_id]
                        self.entity_states[ent.entity_id] = ObservedEntityState(
                            entity_id=prev.entity_id,
                            visibility=EntityVisibility.NOT_CURRENTLY_VISIBLE,
                            existence=prev.existence,
                            last_observed_at=prev.last_observed_at
                        )
                del self.observations[oid]
                expired_ids.append(oid)

        return expired_ids

    def get_active_entities(self) -> List[ObservedEntityState]:
        """Returns currently tracked entities."""
        return list(self.entity_states.values())
