"""Runtime health probes for Aurelia Cognitive OS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aurelia.knowledge.career_graph import create_sample_career_graph
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.memory.retrieval import HybridMemoryRetriever
from aurelia.persistence.database import CognitiveDatabase
from aurelia.solvers.numerical import NumericalFirewall


@dataclass(frozen=True)
class SubsystemHealth:
    """Observed status of one runtime subsystem."""

    name: str
    status: str
    message: str
    details: dict[str, Any]
    critical: bool = True


class HealthSupervisor:
    """Probe runtime dependencies instead of returning static READY claims."""

    @classmethod
    def run_doctor(cls) -> dict[str, Any]:
        subsystems = [
            cls._check_numerical_firewall(),
            cls._check_career_graph(),
            cls._check_memory_and_persistence(),
            cls._check_ollama(),
        ]

        critical_failure = any(
            subsystem.critical and subsystem.status != "READY" for subsystem in subsystems
        )
        optional_degraded = any(
            not subsystem.critical and subsystem.status != "READY" for subsystem in subsystems
        )

        if critical_failure:
            overall_status = "DEGRADED"
        elif optional_degraded:
            overall_status = "DEGRADED"
        else:
            overall_status = "HEALTHY"

        return {
            "overall_status": overall_status,
            "runtime_version": "Aurelia Cognitive OS V4.0",
            "subsystems": [
                {
                    "name": subsystem.name,
                    "status": subsystem.status,
                    "message": subsystem.message,
                    "details": subsystem.details,
                    "critical": subsystem.critical,
                }
                for subsystem in subsystems
            ],
        }

    @staticmethod
    def _check_numerical_firewall() -> SubsystemHealth:
        passed, error = NumericalFirewall.verify_arithmetic_claim(
            "health_probe",
            expected_value=2.0,
            actual_value=2.0,
        )
        return SubsystemHealth(
            name="Numerical Firewall",
            status="READY" if passed else "OFFLINE",
            message="Deterministic arithmetic verification passed."
            if passed
            else (error or "Arithmetic verification failed."),
            details={"probe": "2.0 == 2.0"},
        )

    @staticmethod
    def _check_career_graph() -> SubsystemHealth:
        try:
            graph = create_sample_career_graph()
            edge_count = sum(len(edges) for edges in graph.edges.values())
            ready = bool(graph.nodes) and edge_count > 0
            return SubsystemHealth(
                name="Career Knowledge Graph",
                status="READY" if ready else "OFFLINE",
                message="Structured career graph loaded."
                if ready
                else "Career graph contains no usable data.",
                details={"nodes_count": len(graph.nodes), "edges_count": edge_count},
            )
        except Exception as exc:
            return SubsystemHealth(
                name="Career Knowledge Graph",
                status="OFFLINE",
                message=f"Career graph probe failed: {exc}",
                details={},
            )

    @staticmethod
    def _check_memory_and_persistence() -> SubsystemHealth:
        try:
            database = CognitiveDatabase(":memory:")
            retrieved = HybridMemoryRetriever.retrieve(
                query_text="health probe",
                query_entities=[],
                active_goal=None,
                candidate_items=[],
                top_k=1,
            )
            ready = database is not None and retrieved == []
            return SubsystemHealth(
                name="Memory & Persistence",
                status="READY" if ready else "OFFLINE",
                message="Memory retrieval and SQLite initialization passed."
                if ready
                else "Memory or persistence probe returned an unexpected result.",
                details={"sqlite": "initialized", "empty_retrieval_count": len(retrieved)},
            )
        except Exception as exc:
            return SubsystemHealth(
                name="Memory & Persistence",
                status="OFFLINE",
                message=f"Memory/persistence probe failed: {exc}",
                details={},
            )

    @staticmethod
    def _check_ollama() -> SubsystemHealth:
        online = LocalOllamaCortex.is_ollama_online()
        return SubsystemHealth(
            name="Local Ollama Cortex",
            status="READY" if online else "DEGRADED",
            message="Local Ollama model endpoint is reachable."
            if online
            else "Ollama is offline; deterministic response fallback remains available.",
            details={
                "online": online,
                "active_model": LocalOllamaCortex._active_model if online else None,
                "deterministic_fallback_available": True,
            },
            critical=False,
        )
