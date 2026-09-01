"""Canonical application bootstrap for a durable Aurelia server runtime."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime


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
    """Replace the legacy backend's transient runtime with the durable runtime."""
    import integrated_backend as backend

    workspace_root = Path(backend.WORKSPACE_ROOT)
    runtime = create_application_runtime(workspace_root)
    backend.v4_runtime = runtime
    backend.COGNITIVE_MODULES_AVAILABLE = True
    return backend.app, runtime


def main() -> None:
    """Launch the canonical Flask server with durable cognitive state."""
    app, _runtime = configure_integrated_backend()
    host = os.environ.get("AURELIA_HOST", "127.0.0.1")
    port = int(os.environ.get("AURELIA_PORT", "5000"))
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
