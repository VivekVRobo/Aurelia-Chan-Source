"""Execution engines for Aurelia Cognitive OS.

The V4 ``TypedExecutor`` is the authoritative capability boundary for the
current runtime. ``ExecutionEngine`` remains as a compatibility facade for the
original V3 phase contracts so the historical test suite continues to verify
the specialist engines during stabilization.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from aurelia.execution.capability import CapabilityPermission, CapabilityResult
from aurelia.execution.capability_registry import CapabilityRegistry as LegacyCapabilityRegistry
from aurelia.execution.registry import CapabilityRegistry
from aurelia.knowledge.career_graph import analyze_career_path, create_sample_career_graph
from aurelia.skills.interview.scorer import InterviewScorer
from aurelia.skills.resume.parser import ResumeParser
from aurelia.skills.compensation.salary_engine import SalaryAnalysisRequest, SalaryEngine


class TypedExecutor:
    """Safely execute registered V4 capabilities with permission enforcement."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def execute(
        self,
        capability_id: str,
        input_args: dict[str, Any],
        caller_permission: CapabilityPermission = CapabilityPermission.READ_ONLY,
    ) -> CapabilityResult:
        cap = self.registry.get(capability_id)
        if not cap:
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=f"Capability '{capability_id}' not found in registry.",
                deterministic=False,
            )

        if (
            cap.permission == CapabilityPermission.MUTATE_LOCAL_STATE
            and caller_permission != CapabilityPermission.MUTATE_LOCAL_STATE
        ):
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=(
                    f"Permission denied: Capability '{capability_id}' requires "
                    f"{cap.permission.value}, but caller has {caller_permission.value}."
                ),
                deterministic=cap.deterministic,
            )

        if not cap.handler:
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=f"Capability '{capability_id}' has no executable handler registered.",
                deterministic=cap.deterministic,
            )

        start_time = time.perf_counter()
        try:
            result_data = cap.handler(**input_args)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return CapabilityResult(
                capability_id=capability_id,
                success=True,
                output_data=result_data,
                execution_time_ms=elapsed_ms,
                deterministic=cap.deterministic,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return CapabilityResult(
                capability_id=capability_id,
                success=False,
                output_data=None,
                error_message=f"Execution error in capability '{capability_id}': {exc}",
                execution_time_ms=elapsed_ms,
                deterministic=cap.deterministic,
            )


class ExecutionStatus(Enum):
    """Legacy V3 execution result states."""

    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ExecutionResult:
    """Compatibility result for one V3 capability execution."""

    capability_name: str
    status: ExecutionStatus
    result: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0


@dataclass(frozen=True)
class ExecutionSummary:
    """Compatibility summary for a V3 execution plan."""

    success: bool
    results: tuple[ExecutionResult, ...]
    combined_result: dict[str, Any]
    total_execution_time_ms: float


class ExecutionEngine:
    """Execute legacy V3 plans against the real deterministic specialist code."""

    def __init__(self, registry: LegacyCapabilityRegistry) -> None:
        self.registry = registry
        self._salary = SalaryEngine()
        self._resume = ResumeParser()
        self._interview = InterviewScorer()
        self._career_graph = create_sample_career_graph()

    @staticmethod
    def execute_reflex(text: str) -> str:
        lower = text.strip().lower()
        if any(token in lower for token in ("hello", "hi", "hey")):
            return "Hello. I am Aurelia. What would you like to work through?"
        if "thank" in lower:
            return "You are welcome. What would you like to address next?"
        return "I am listening."

    def execute_capability(
        self,
        capability_name: str,
        context: dict[str, Any],
    ) -> ExecutionResult:
        start = time.perf_counter()
        capability = self.registry.get(capability_name)
        if capability is None or not capability.available:
            return ExecutionResult(
                capability_name=capability_name,
                status=ExecutionStatus.FAILED,
                error=f"Capability '{capability_name}' is unavailable.",
                execution_time_ms=(time.perf_counter() - start) * 1000.0,
            )

        try:
            result = self._dispatch(capability_name, context)
            return ExecutionResult(
                capability_name=capability_name,
                status=ExecutionStatus.COMPLETED,
                result=result,
                execution_time_ms=(time.perf_counter() - start) * 1000.0,
            )
        except Exception as exc:
            return ExecutionResult(
                capability_name=capability_name,
                status=ExecutionStatus.FAILED,
                error=str(exc),
                execution_time_ms=(time.perf_counter() - start) * 1000.0,
            )

    def execute_plan(self, plan: Any, context: dict[str, Any]) -> ExecutionSummary:
        started = time.perf_counter()
        results = tuple(
            self.execute_capability(capability_name, context)
            for capability_name in plan.required_capabilities
        )
        success = all(result.status == ExecutionStatus.COMPLETED for result in results)
        combined = {
            result.capability_name: result.result
            for result in results
            if result.status == ExecutionStatus.COMPLETED
        }
        return ExecutionSummary(
            success=success,
            results=results,
            combined_result=combined,
            total_execution_time_ms=(time.perf_counter() - started) * 1000.0,
        )

    def _dispatch(self, capability_name: str, context: dict[str, Any]) -> Any:
        if capability_name == "salary.benchmark":
            request = SalaryAnalysisRequest(
                role=str(context["role"]),
                level=str(context["level"]),
                location=str(context["location"]),
                industry=str(context["industry"]),
                years_experience=context.get("years_experience"),
                current_salary=context.get("current_salary"),
                target_percentile=context.get("target_percentile"),
            )
            return self._salary.calculate_benchmark(request)

        if capability_name == "resume.parse":
            return self._resume.parse_resume(str(context.get("resume_text", "")))

        if capability_name == "interview.score_response":
            return self._interview.score_response(
                str(context.get("question", "")),
                str(context.get("answer", "")),
            )

        if capability_name == "career.find_path":
            return analyze_career_path(
                self._career_graph,
                str(context.get("current_role", "")),
                str(context.get("target_role", "")),
            )

        raise ValueError(
            f"Legacy capability '{capability_name}' has no compatibility handler yet."
        )
