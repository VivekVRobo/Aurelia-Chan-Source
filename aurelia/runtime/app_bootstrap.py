"""Canonical application bootstrap for a durable Aurelia server runtime."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import jsonify, request

from aurelia.persistence.database import PersistenceError
from aurelia.runtime.api_contract import serialize_cognitive_cycle, serialize_runtime_status
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime, CognitiveExecutionError


def resolve_database_path(workspace_root: Path) -> Path:
    """Resolve the durable SQLite path, honoring `AURELIA_DB_PATH`."""
    configured = os.environ.get("AURELIA_DB_PATH")
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            path = workspace_root / path
        return path.resolve()
    return (workspace_root / "data" / "aurelia.db").resolve()


def create_application_runtime(workspace_root: Path) -> AureliaCognitiveRuntime:
    """Create the file-backed runtime used by the actual application server."""
    db_path = resolve_database_path(workspace_root)
    return AureliaCognitiveRuntime(db_path=str(db_path))


def configure_integrated_backend() -> tuple[Any, AureliaCognitiveRuntime]:
    """Install the durable runtime and hardened canonical HTTP handlers."""
    import integrated_backend as backend

    workspace_root = Path(backend.WORKSPACE_ROOT)
    previous_runtime = getattr(backend, "v4_runtime", None)
    runtime = create_application_runtime(workspace_root)
    backend.v4_runtime = runtime
    backend.COGNITIVE_MODULES_AVAILABLE = True
    _close_replaced_runtime(previous_runtime, replacement=runtime)
    _install_hardened_cognitive_cycle(backend)
    _install_runtime_status(backend)
    return backend.app, runtime


def _install_hardened_cognitive_cycle(backend: Any) -> None:
    """Replace the legacy success-looking fallback with a fail-closed API handler."""

    def hardened_cognitive_cycle() -> Any:
        data = request.get_json(silent=True) or {}
        user_message = str(data.get("message", "")).strip()
        if not user_message:
            return jsonify({"error": "No message provided", "safe_to_publish": False}), 400

        runtime = getattr(backend, "v4_runtime", None)
        if not isinstance(runtime, AureliaCognitiveRuntime):
            return (
                jsonify(
                    {
                        "error": "Aurelia cognitive runtime is unavailable.",
                        "safe_to_publish": False,
                    }
                ),
                503,
            )

        try:
            result = runtime.process_query(
                user_text=user_message,
                user_role=str(data.get("user_role", "Senior Engineering Manager")),
                target_role=str(data.get("target_role", "Director of Engineering")),
                chat_history=data.get("history", []),
            )
        except (CognitiveExecutionError, PersistenceError) as exc:
            return (
                jsonify(
                    {
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                        "safe_to_publish": False,
                    }
                ),
                500,
            )
        except Exception:
            return (
                jsonify(
                    {
                        "error": "Aurelia cognitive cycle failed unexpectedly.",
                        "error_type": "RuntimeError",
                        "safe_to_publish": False,
                    }
                ),
                500,
            )

        return jsonify(serialize_cognitive_cycle(result)), 200

    backend.app.view_functions["cognitive_cycle"] = hardened_cognitive_cycle


def _install_runtime_status(backend: Any) -> None:
    """Expose non-sensitive readiness diagnostics for the canonical server."""

    def runtime_status() -> Any:
        runtime = getattr(backend, "v4_runtime", None)
        if not isinstance(runtime, AureliaCognitiveRuntime):
            return (
                jsonify(
                    {
                        "runtime_configured": False,
                        "persona_renderer": False,
                        "safe_to_publish": False,
                    }
                ),
                503,
            )
        status = serialize_runtime_status(runtime.persistence.diagnostics())
        status["registered_capabilities"] = len(runtime.registry.list_all())
        return jsonify(status), 200

    if "aurelia_runtime_status" not in backend.app.view_functions:
        backend.app.add_url_rule(
            "/api/runtime-status",
            endpoint="aurelia_runtime_status",
            view_func=runtime_status,
            methods=["GET"],
        )
    else:
        backend.app.view_functions["aurelia_runtime_status"] = runtime_status


def _close_replaced_runtime(previous: Any, *, replacement: AureliaCognitiveRuntime) -> None:
    """Close a replaced runtime database connection to avoid leaked SQLite handles."""
    if previous is None or previous is replacement:
        return
    database = getattr(previous, "database", None)
    close = getattr(database, "close", None)
    if callable(close):
        close()


def main() -> None:
    """Launch the canonical Flask server with durable cognitive state."""
    app, _runtime = configure_integrated_backend()
    host = os.environ.get("AURELIA_HOST", "127.0.0.1")
    port = int(os.environ.get("AURELIA_PORT", "5000"))
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
