"""
Aurelia Cognitive OS V6 - Universal Document Intelligence V2
=============================================================
Parses, segments, and extracts structured entities with character/section
provenance across resumes, job descriptions, offer letters, and performance reviews.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v6_contracts import (
    ObservedEntity,
    Provenance,
    ObservationSource,
    ObservationQuality
)


@dataclass(frozen=True)
class DocumentSection:
    """Segment of a parsed document."""
    section_name: str # e.g. "COMPENSATION", "REQUIREMENTS", "PERFORMANCE_FEEDBACK"
    content: str
    char_start: int
    char_end: int


@dataclass(frozen=True)
class ParsedDocument:
    """Fully structured document with provenance and extracted entities."""
    doc_id: str
    file_path: str
    doc_type: str # "RESUME", "JOB_DESCRIPTION", "OFFER_LETTER", "PERFORMANCE_REVIEW"
    sections: Tuple[DocumentSection, ...]
    extracted_entities: Tuple[ObservedEntity, ...]
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class UniversalDocumentParser:
    """
    Parses and extracts structured sections and typed entities from executive documents.
    """

    @classmethod
    def parse_document(
        cls,
        doc_id: str,
        file_path: str,
        text_content: str,
        doc_type: str = "GENERIC"
    ) -> ParsedDocument:
        """Parses document text into sections and entities."""
        sections: List[DocumentSection] = []
        entities: List[ObservedEntity] = []

        # 1. Segment by headers or structural markers
        lines = text_content.splitlines()
        current_section_name = "HEADER"
        current_section_lines = []
        char_offset = 0
        sec_start = 0

        for line in lines:
            trimmed = line.strip().upper()
            if trimmed.startswith("#") or any(h in trimmed for h in ["COMPENSATION", "SALARY", "REQUIREMENTS", "EXPERIENCE", "FEEDBACK", "EVALUATION"]):
                if current_section_lines:
                    sec_text = "\n".join(current_section_lines)
                    sections.append(DocumentSection(
                        section_name=current_section_name,
                        content=sec_text,
                        char_start=sec_start,
                        char_end=char_offset
                    ))
                current_section_name = trimmed.replace("#", "").strip()
                current_section_lines = [line]
                sec_start = char_offset
            else:
                current_section_lines.append(line)
            char_offset += len(line) + 1

        if current_section_lines:
            sections.append(DocumentSection(
                section_name=current_section_name,
                content="\n".join(current_section_lines),
                char_start=sec_start,
                char_end=char_offset
            ))

        # 2. Extract Entities with Regex
        # Compensation entity
        comp_match = re.search(r'(\$|₹|INR|USD)\s*([0-9,]+(?:\.[0-9]+)?)\s*(k|K|L|Lakh|lakh|M)?', text_content)
        if comp_match:
            raw_text = comp_match.group(0)
            val_num = float(comp_match.group(2).replace(',', ''))
            mult = comp_match.group(3)
            if mult and mult.upper() in ['K']:
                val_num *= 1000
            elif mult and mult.lower() in ['l', 'lakh']:
                val_num *= 100000
            elif mult and mult.upper() in ['M']:
                val_num *= 1000000

            entities.append(ObservedEntity(
                entity_id=f"ent_comp_{doc_id}",
                entity_type="COMPENSATION_AMOUNT",
                raw_text=raw_text,
                normalized_value=val_num,
                confidence=0.95
            ))

        # Target Role / Job Title
        role_match = re.search(r'(Director|VP|Vice President|Head of|Senior Engineering Manager|Staff Engineer|Lead)', text_content, re.IGNORECASE)
        if role_match:
            entities.append(ObservedEntity(
                entity_id=f"ent_role_{doc_id}",
                entity_type="TARGET_ROLE",
                raw_text=role_match.group(0),
                normalized_value=role_match.group(0).title(),
                confidence=0.92
            ))

        # Team Size entity
        team_match = re.search(r'([0-9]+)\s*(?:engineers|direct reports|members|people)', text_content, re.IGNORECASE)
        if team_match:
            entities.append(ObservedEntity(
                entity_id=f"ent_team_{doc_id}",
                entity_type="TEAM_SIZE",
                raw_text=team_match.group(0),
                normalized_value=int(team_match.group(1)),
                confidence=0.90
            ))

        return ParsedDocument(
            doc_id=doc_id,
            file_path=file_path,
            doc_type=doc_type,
            sections=tuple(sections),
            extracted_entities=tuple(entities)
        )
