"""
Aurelia Cognitive OS V4 - Artifact Renderer
============================================
Renders structured executive artifacts into clean Markdown and interactive HTML tables.
"""

from typing import Dict, Any
from aurelia.artifacts.schemas import ExecutiveArtifact, ArtifactType


class ArtifactRenderer:
    """
    Renders structured artifacts into Markdown and HTML.
    """

    @staticmethod
    def to_markdown(artifact: ExecutiveArtifact) -> str:
        """Renders artifact to formatted Markdown."""
        lines = [f"# {artifact.title} (v{artifact.version})", ""]
        
        if artifact.artifact_type == ArtifactType.ROADMAP_90_DAY:
            milestones = artifact.payload.get("milestones", [])
            for m in milestones:
                status_box = "[x]" if m.get("is_completed") else "[ ]"
                lines.append(f"### {status_box} {m.get('phase_name')}: {m.get('goal')}")
                lines.append("**Key Strategic Actions:**")
                for act in m.get("actions", []):
                    lines.append(f"- {act}")
                lines.append("**Expected Deliverables:**")
                for deliv in m.get("deliverables", []):
                    lines.append(f"- {deliv}")
                lines.append("")
                
        return "\n".join(lines)
