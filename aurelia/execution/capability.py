"""
Aurelia Cognitive OS V4 - Capability & Execution Contracts
==========================================================
Enforces a formal boundary between cognitive planning and execution.
The LLM or planner can propose capability IDs, but the TypedExecutor
strictly controls schema validation, deterministic invocation, and permissions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, Callable, Type, Tuple


class CapabilityPermission(Enum):
    """Permission boundaries for capabilities."""
    READ_ONLY = "read_only"            # Reading local graph, memory, knowledge
    INFERENCE_LOCAL = "inference_local"# Querying local Ollama models
    MUTATE_LOCAL_STATE = "mutate_state"# Committing memory or writing local files
    EXTERNAL_NETWORK = "network_call"  # Strictly prohibited in 100% local mode


class ExecutionMode(Enum):
    """Execution modes for capabilities."""
    DETERMINISTIC = "deterministic"    # Python code / graph lookup / math
    PROBABILISTIC_LLM = "llm_model"   # Local Ollama inference
    HYBRID = "hybrid"                  # Solver + LLM formatting


@dataclass(frozen=True)
class Capability:
    """
    Typed registration descriptor for a system capability.
    """
    id: str
    description: str
    permission: CapabilityPermission
    mode: ExecutionMode
    input_schema: Optional[Type[Any]] = None
    output_schema: Optional[Type[Any]] = None
    deterministic: bool = True
    side_effect: bool = False
    requires_llm: bool = False
    cost_budget_units: int = 1
    handler: Optional[Callable[..., Any]] = None


@dataclass(frozen=True)
class CapabilityResult:
    """
    Immutable execution result from a capability invocation.
    """
    capability_id: str
    success: bool
    output_data: Any
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    deterministic: bool = True
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
