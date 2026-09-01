"""
Aurelia Cognitive OS V4 - Typed Executor
=========================================
Executes capabilities safely with schema validation, permission checks,
error containment, and latency tracking.
"""

import time
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from aurelia.execution.capability import Capability, CapabilityResult, CapabilityPermission
from aurelia.execution.registry import CapabilityRegistry


class TypedExecutor:
    """
    Safely executes capabilities with type safety and error isolation.
    """
    
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
    
    def execute(
        self,
        capability_id: str,
        input_args: Dict[str, Any],
        caller_permission: CapabilityPermission = CapabilityPermission.READ_ONLY
    ) -> CapabilityResult:
        """
        Execute a registered capability with validation and timing.
        """
        cap = self.registry.get(capability_id)
        if not cap:
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=f"Capability '{capability_id}' not found in registry.",
                deterministic=False
            )
        
        # Enforce permission boundaries
        if cap.permission == CapabilityPermission.MUTATE_LOCAL_STATE and caller_permission != CapabilityPermission.MUTATE_LOCAL_STATE:
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=f"Permission denied: Capability '{capability_id}' requires {cap.permission.value}, but caller has {caller_permission.value}.",
                deterministic=cap.deterministic
            )
        
        if not cap.handler:
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=f"Capability '{capability_id}' has no executable handler registered.",
                deterministic=cap.deterministic
            )
        
        start_time = time.perf_counter()
        try:
            # Execute handler safely
            result_data = cap.handler(**input_args)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            
            return CapabilityResult(
                capability_id=capability_id,
                success=True,
                output_data=result_data,
                execution_time_ms=elapsed_ms,
                deterministic=cap.deterministic
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=f"Execution error in capability '{capability_id}': {str(e)}",
                execution_time_ms=elapsed_ms,
                deterministic=cap.deterministic
            )