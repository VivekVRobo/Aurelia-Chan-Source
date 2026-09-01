"""
Aurelia Cognitive OS V4 - Capability Registry
=============================================
Maintains registration and lookup of all executable capabilities.
"""

from typing import Dict, List, Optional
from aurelia.execution.capability import Capability, CapabilityPermission, ExecutionMode


class CapabilityRegistry:
    """
    Central registry for all executable capabilities in Aurelia OS V4.
    """
    
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
    
    def register(self, capability: Capability) -> None:
        """Register a new capability."""
        if capability.id in self._capabilities:
            raise ValueError(f"Capability with ID '{capability.id}' is already registered.")
        self._capabilities[capability.id] = capability
    
    def get(self, capability_id: str) -> Optional[Capability]:
        """Retrieve capability by ID."""
        return self._capabilities.get(capability_id)
    
    def list_all(self) -> List[Capability]:
        """List all registered capabilities."""
        return list(self._capabilities.values())
    
    def list_by_permission(self, permission: CapabilityPermission) -> List[Capability]:
        """Filter capabilities by permission level."""
        return [c for c in self._capabilities.values() if c.permission == permission]
    
    def list_deterministic(self) -> List[Capability]:
        """Filter strictly deterministic capabilities."""
        return [c for c in self._capabilities.values() if c.deterministic]
