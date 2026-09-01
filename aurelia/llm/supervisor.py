"""
Aurelia Cognitive OS V4 - Local Ollama Model Supervisor
========================================================
Supervises local Ollama model health, manages circuit breaking, records
the inference ledger, and enforces fallback degradation when Ollama is unavailable.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional, Any
from aurelia.contracts.receipt import InferenceRecord
from aurelia.llm.hardware import HardwareProfile


class SupervisorState(Enum):
    OFFLINE = "offline"
    READY = "ready"
    BUSY = "busy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"


class OllamaSupervisor:
    """
    Manages local model state, tracks inference metrics, and protects runtime stability.
    """

    def __init__(self, default_model: str = "llama3.2"):
        self.default_model = default_model
        self.state: SupervisorState = SupervisorState.READY
        self.consecutive_failures: int = 0
        self.circuit_breaker_threshold: int = 3
        self.inference_ledger: List[InferenceRecord] = []

    def record_inference(
        self,
        inference_id: str,
        cognitive_role: str,
        snapshot_id: str,
        prompt_version: str,
        latency_ms: float,
        parse_success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> InferenceRecord:
        """Records an execution event to the immutable inference ledger."""
        record = InferenceRecord(
            inference_id=inference_id,
            model_name=self.default_model,
            cognitive_role=cognitive_role,
            snapshot_id=snapshot_id,
            prompt_template_version=prompt_version,
            temperature=0.2,
            input_tokens_est=input_tokens,
            output_tokens_est=output_tokens,
            latency_ms=latency_ms,
            parse_success=parse_success
        )
        self.inference_ledger.append(record)
        
        if parse_success:
            self.consecutive_failures = 0
            if self.state == SupervisorState.DEGRADED:
                self.state = SupervisorState.READY
        else:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.circuit_breaker_threshold:
                self.state = SupervisorState.DEGRADED
                
        return record

    def is_available(self) -> bool:
        """Returns True if model is healthy and ready to accept requests."""
        return self.state in [SupervisorState.READY, SupervisorState.BUSY]

    def trigger_circuit_break(self) -> None:
        """Manually forces degraded mode (e.g. during timeout or connection failure)."""
        self.state = SupervisorState.DEGRADED
