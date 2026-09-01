"""
Aurelia Cognitive OS V3 - Phase 2: Career Gap Analysis
=======================================================
Deterministic skill gap analysis using evidence and requirements.

Specialist engine that compares current capabilities against
target role requirements using structured evidence, not LLM guessing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from aurelia.cognition.contracts import (
    SkillGap,
    CareerGapResult,
    Evidence,
    EntityRef,
    ConfidenceLevel
)
from aurelia.knowledge.ontology import (
    normalize_skill,
    get_required_level_for_role,
    SKILL_ONTOLOGY
)


class GapSeverity(Enum):
    """Severity levels for skill gaps."""
    CRITICAL = "critical"  # Required for role, missing entirely
    SIGNIFICANT = "significant"  # Required, but below threshold
    MODERATE = "moderate"  # Below optimal but functional
    MINOR = "minor"  # Slight improvement needed
    NONE = "none"  # Meets or exceeds requirement


@dataclass
class UserSkill:
    """User's current skill level with evidence."""
    skill_id: str
    current_level: float  # 0-10 scale
    evidence: List[Evidence]
    confidence: float
    last_assessed: str  # ISO date


@dataclass
class GapAnalysisInput:
    """Input for gap analysis."""
    target_role: str
    current_role: str
    user_skills: List[UserSkill]
    resume_evidence: List[Evidence] = field(default_factory=list)
    interview_evidence: List[Evidence] = field(default_factory=list)


@dataclass
class SkillGapDetail:
    """Detailed analysis of a single skill gap."""
    skill_id: str
    skill_name: str
    required_level: float
    current_level: float
    gap_size: float
    severity: GapSeverity
    evidence_strength: float
    development_suggestions: List[str]
    time_to_close: Optional[str] = None  # e.g., "3-6 months"


class CareerGapAnalyzer:
    """
    Specialist engine for career gap analysis.
    
    Uses structured evidence and role requirements to calculate
    skill gaps deterministically, not through LLM inference.
    """
    
    def __init__(self):
        self.skill_development_suggestions = {
            "skill.people_management": [
                "Lead a cross-functional project",
                "Mentor junior team members",
                "Complete management training",
                "Take on performance review responsibilities"
            ],
            "skill.strategic_planning": [
                "Participate in annual planning",
                "Create a 12-month roadmap",
                "Lead a strategic initiative",
                "Complete strategic thinking coursework"
            ],
            "skill.budget_ownership": [
                "Own a departmental budget",
                "Complete finance training",
                "Lead a cost-reduction project",
                "Present financial results"
            ],
            "skill.cross_functional_influence": [
                "Lead a multi-team initiative",
                "Build relationships with other departments",
                "Present to senior leadership",
                "Solve cross-departmental problems"
            ],
            "skill.executive_communication": [
                "Present to executives",
                "Lead quarterly reviews",
                "Write executive summaries",
                "Practice executive presence"
            ]
        }
    
    def calculate_gap_severity(self, gap_size: float, required_level: float) -> GapSeverity:
        """
        Determine gap severity based on size and importance.
        
        Gap size: required_level - current_level
        """
        if gap_size >= required_level * 0.5:
            return GapSeverity.CRITICAL
        elif gap_size >= required_level * 0.3:
            return GapSeverity.SIGNIFICANT
        elif gap_size >= required_level * 0.15:
            return GapSeverity.MODERATE
        elif gap_size > 0:
            return GapSeverity.MINOR
        else:
            return GapSeverity.NONE
    
    def estimate_time_to_close(self, gap_size: float, severity: GapSeverity) -> str:
        """Estimate time to close a skill gap."""
        if severity == GapSeverity.CRITICAL:
            return "6-12 months"
        elif severity == GapSeverity.SIGNIFICANT:
            return "3-6 months"
        elif severity == GapSeverity.MODERATE:
            return "1-3 months"
        elif severity == GapSeverity.MINOR:
            return "2-4 weeks"
        else:
            return "Already met"
    
    def analyze_skill_gap(
        self,
        skill_id: str,
        required_level: float,
        user_skills: List[UserSkill]
    ) -> Optional[SkillGapDetail]:
        """Analyze gap for a single skill."""
        # Find user's current level for this skill
        user_skill = None
        for us in user_skills:
            if us.skill_id == skill_id:
                user_skill = us
                break
        
        if user_skill is None:
            # No evidence of this skill - critical gap
            gap_size = required_level
            severity = self.calculate_gap_severity(gap_size, required_level)
            
            return SkillGapDetail(
                skill_id=skill_id,
                skill_name=SKILL_ONTOLOGY.get(skill_id, type('obj', (object,), {'name': skill_id})).name if skill_id in SKILL_ONTOLOGY else skill_id,
                required_level=required_level,
                current_level=0.0,
                gap_size=gap_size,
                severity=severity,
                evidence_strength=0.0,
                development_suggestions=self.skill_development_suggestions.get(skill_id, ["Develop this skill through relevant experience"]),
                time_to_close=self.estimate_time_to_close(gap_size, severity)
            )
        
        # Calculate gap
        gap_size = max(0, required_level - user_skill.current_level)
        severity = self.calculate_gap_severity(gap_size, required_level)
        
        return SkillGapDetail(
            skill_id=skill_id,
            skill_name=SKILL_ONTOLOGY.get(skill_id, type('obj', (object,), {'name': skill_id})).name if skill_id in SKILL_ONTOLOGY else skill_id,
            required_level=required_level,
            current_level=user_skill.current_level,
            gap_size=gap_size,
            severity=severity,
            evidence_strength=user_skill.confidence,
            development_suggestions=self.skill_development_suggestions.get(skill_id, ["Continue developing this skill"]),
            time_to_close=self.estimate_time_to_close(gap_size, severity)
        )
    
    def analyze_gaps(self, input_data: GapAnalysisInput) -> CareerGapResult:
        """
        Perform comprehensive gap analysis.
        
        Returns structured result that the LLM receives as input,
        not generates itself.
        """
        # Get all skills required for target role
        required_skills = []
        for skill_id, concept in SKILL_ONTOLOGY.items():
            required_level = get_required_level_for_role(skill_id, input_data.target_role)
            if required_level is not None:
                required_skills.append((skill_id, required_level))
        
        # Analyze each required skill
        gap_details = []
        skill_gaps = []
        strengths = []
        
        total_gap_score = 0
        total_possible_gap = 0
        
        for skill_id, required_level in required_skills:
            detail = self.analyze_skill_gap(skill_id, required_level, input_data.user_skills)
            
            if detail:
                gap_details.append(detail)
                
                # Add to structured result
                if detail.severity != GapSeverity.NONE:
                    skill_gaps.append(SkillGap(
                        skill=detail.skill_name,
                        required_level=detail.required_level,
                        observed_level=detail.current_level,
                        evidence=[],
                        confidence=detail.evidence_strength
                    ))
                    total_gap_score += detail.gap_size
                else:
                    strengths.append(f"{detail.skill_name} (level {detail.current_level:.1f})")
                
                total_possible_gap += required_level
        
        # Calculate overall readiness
        if total_possible_gap > 0:
            readiness_score = 1.0 - (total_gap_score / total_possible_gap)
        else:
            readiness_score = 1.0
        
        # Calculate confidence based on evidence strength
        if input_data.user_skills:
            avg_confidence = sum(us.confidence for us in input_data.user_skills) / len(input_data.user_skills)
        else:
            avg_confidence = 0.5
        
        return CareerGapResult(
            target_role=input_data.target_role,
            strengths=strengths,
            gaps=skill_gaps,
            readiness_score=readiness_score,
            confidence=avg_confidence
        )
    
    def get_development_priority(self, gap_details: List[SkillGapDetail]) -> List[SkillGapDetail]:
        """
        Prioritize gaps for development.
        
        Priority: Critical > Significant > Moderate > Minor
        Within same severity: larger gap first
        """
        severity_order = {
            GapSeverity.CRITICAL: 0,
            GapSeverity.SIGNIFICANT: 1,
            GapSeverity.MODERATE: 2,
            GapSeverity.MINOR: 3,
            GapSeverity.NONE: 4
        }
        
        return sorted(
            gap_details,
            key=lambda g: (severity_order.get(g.severity, 5), -g.gap_size)
        )