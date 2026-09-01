"""
Aurelia Cognitive OS V6 - Cross-Document Graph Engine
======================================================
Maintains a unified relational graph across active documents (resumes,
job descriptions, offer letters, performance reviews).
"""

from typing import Dict, Any, List, Optional, Tuple
from aurelia.documents.parser import ParsedDocument
from aurelia.contracts.v6_contracts import ObservedEntity


class CrossDocumentGraph:
    """
    Relational graph linking documents and extracting comparative facts.
    """

    def __init__(self):
        self.documents: Dict[str, ParsedDocument] = {}
        # entity_type -> list of (doc_id, ObservedEntity)
        self.entity_index: Dict[str, List[Tuple[str, ObservedEntity]]] = {}

    def add_document(self, doc: ParsedDocument) -> None:
        """Indexes document and its extracted entities."""
        self.documents[doc.doc_id] = doc
        for ent in doc.extracted_entities:
            if ent.entity_type not in self.entity_index:
                self.entity_index[ent.entity_type] = []
            self.entity_index[ent.entity_type].append((doc.doc_id, ent))

    def get_entities_by_type(self, entity_type: str) -> List[Tuple[str, ObservedEntity]]:
        """Returns all entities of a specified type across documents."""
        return self.entity_index.get(entity_type, [])

    def compare_compensation_across_documents(self) -> Dict[str, float]:
        """Returns map of doc_id -> normalized compensation amount."""
        res = {}
        for doc_id, ent in self.get_entities_by_type("COMPENSATION_AMOUNT"):
            res[doc_id] = float(ent.normalized_value)
        return res
