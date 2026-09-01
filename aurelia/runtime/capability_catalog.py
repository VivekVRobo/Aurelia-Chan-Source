"""Capability registrations for the executable Aurelia V4 DAG."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aurelia.character.persona_renderer import PersonaRenderer
from aurelia.cognition.router import CognitiveBudget
from aurelia.contracts.core_types import UserGoal
from aurelia.contracts.meaning_frame import IntentType
from aurelia.contracts.snapshot import CognitiveSnapshot
from aurelia.execution.capability import Capability, CapabilityPermission, ExecutionMode
from aurelia.execution.registry import CapabilityRegistry
from aurelia.runtime import capability_handlers
from aurelia.runtime.dag_verification import verify_rendered_response
from aurelia.runtime.grounding import GroundedContext


@dataclass(frozen=True)
class RuntimeExecutionContext:
    """Inputs shared by every capability in one cognitive cycle."""

    user_text: str
    user_role: str
    target_role: str
    intent: IntentType
    entities: dict[str, Any]
    snapshot: CognitiveSnapshot
    active_goal: UserGoal
    budget: CognitiveBudget
    grounded: GroundedContext
    persona_renderer: PersonaRenderer


class RuntimeCapabilityCatalog:
    """Register every capability ID emitted by CognitivePlanner."""

    @classmethod
    def register_all(cls, registry: CapabilityRegistry) -> None:
        definitions = (
            ("memory.lookup.fast", capability_handlers.memory_lookup_fast),
            ("response.format.direct", capability_handlers.response_format_direct),
            ("comp.parse.offer", capability_handlers.parse_offer),
            ("memory.retrieve.hybrid", capability_handlers.retrieve_hybrid),
            ("comp.calc.total_target", capability_handlers.calculate_total_target),
            ("sim.monte_carlo.equity", capability_handlers.simulate_equity),
            ("cognition.search.hypotheses", capability_handlers.search_hypotheses),
            ("cognition.critics.evaluate", capability_handlers.evaluate_critics),
            ("specialist.evaluate", capability_handlers.evaluate_specialist),
            ("response.render.aurelia", capability_handlers.render_response),
            ("verification.firewall.verify", verify_rendered_response),
            ("artifact.workspace.create", capability_handlers.create_artifact),
        )
        hybrid_ids = {"response.render.aurelia"}
        for capability_id, handler in definitions:
            is_hybrid = capability_id in hybrid_ids
            registry.register(
                Capability(
                    id=capability_id,
                    description=f"Executable runtime capability: {capability_id}",
                    permission=(
                        CapabilityPermission.INFERENCE_LOCAL
                        if is_hybrid
                        else CapabilityPermission.READ_ONLY
                    ),
                    mode=ExecutionMode.HYBRID if is_hybrid else ExecutionMode.DETERMINISTIC,
                    deterministic=not is_hybrid,
                    requires_llm=is_hybrid,
                    handler=handler,
                )
            )
