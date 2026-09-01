"""
Aurelia Cognitive OS V6 - Multimodal Entity & Pronoun Grounding Engine
======================================================================
Resolves deictic pronouns ("this", "that", "the other one") against active
screen state, open documents, and historical dossier records.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v6_contracts import ObservedEntity


@dataclass(frozen=True)
class GroundedReference:
    """Resolved entity reference with resolution source."""
    pronoun_or_phrase: str
    target_entity_id: str
    target_title: str
    resolution_source: str # "ACTIVE_FOREGROUND_DOC", "DOSSIER_BACKGROUND_DOC", "ACTIVE_EDITOR_CODE"
    confidence: float


class MultimodalEntityResolver:
    """
    Grounds user queries to concrete multimodal environmental entities.
    """

    @classmethod
    def resolve_references(
        cls,
        user_query: str,
        active_foreground_doc: Optional[Dict[str, Any]] = None,
        dossier_documents: Optional[List[Dict[str, Any]]] = None,
        active_editor_code: Optional[str] = None
    ) -> List[GroundedReference]:
        """
        Resolves linguistic references ("this", "other", "code") to physical entities.
        """
        resolved: List[GroundedReference] = []
        q_lower = user_query.lower()

        # 1. Resolve "this" / "this offer" / "this document" -> active foreground document
        if any(p in q_lower for p in ["this", "current offer", "current doc", "active document"]):
            if active_foreground_doc:
                resolved.append(GroundedReference(
                    pronoun_or_phrase="this",
                    target_entity_id=active_foreground_doc.get("id", "doc_active"),
                    target_title=active_foreground_doc.get("title", "Active Document"),
                    resolution_source="ACTIVE_FOREGROUND_DOC",
                    confidence=0.95
                ))

        # 2. Resolve "the other one" / "other offer" / "competing offer" -> background dossier doc
        if any(p in q_lower for p in ["other", "the other one", "previous offer", "second offer"]):
            if dossier_documents:
                # Find document not matching the active one
                active_id = active_foreground_doc.get("id") if active_foreground_doc else None
                other_docs = [d for d in dossier_documents if d.get("id") != active_id]
                if other_docs:
                    target = other_docs[0]
                    resolved.append(GroundedReference(
                        pronoun_or_phrase="other",
                        target_entity_id=target.get("id", "doc_other"),
                        target_title=target.get("title", "Other Document"),
                        resolution_source="DOSSIER_BACKGROUND_DOC",
                        confidence=0.91
                    ))

        # 3. Resolve "this code" / "the error" -> active code editor
        if any(p in q_lower for p in ["this code", "the traceback", "this error", "the function"]):
            if active_editor_code:
                resolved.append(GroundedReference(
                    pronoun_or_phrase="this code",
                    target_entity_id="ent_active_editor_code",
                    target_title="Active Code Editor Buffer",
                    resolution_source="ACTIVE_EDITOR_CODE",
                    confidence=0.94
                ))

        return resolved
