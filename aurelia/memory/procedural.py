"""
Aurelia Cognitive OS V3 - Phase 4: Procedural Memory
=================================================
Memory of how Aurelia performs tasks.

Procedural memory stores HOW Aurelia performs tasks:
- How to audit a resume
- How to assess STAR responses
- How to create an interview loop
- How to compare roles
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
from enum import Enum


class ProcedureType(Enum):
    """Types of procedures."""
    RESUME_AUDIT = "resume_audit"
    INTERVIEW_SCORING = "interview_scoring"
    CAREER_PATH_ANALYSIS = "career_path_analysis"
    GAP_ANALYSIS = "gap_analysis"
    SALARY_BENCHMARKING = "salary_benchmarking"
    GOAL_PLANNING = "goal_planning"
    SKILL_ASSESSMENT = "skill_assessment"


@dataclass
class Procedure:
    """
    A procedural memory entry.
    
    Defines HOW to perform a specific task.
    """
    name: str
    procedure_type: ProcedureType
    description: str
    steps: List[str]
    required_capabilities: List[str]
    success_criteria: List[str]
    version: str = "1.0"


@dataclass
class ProcedureExecution:
    """Record of a procedure execution."""
    procedure_name: str
    timestamp: datetime
    success: bool
    execution_time_ms: float
    notes: List[str] = field(default_factory=list)


class ProceduralMemory:
    """
    Memory of how Aurelia performs tasks.
    
    Examples:
    - How to audit a resume
    - How to assess STAR responses
    - How to create an interview loop
    - How to compare roles
    """
    
    def __init__(self):
        self.procedures: Dict[str, Procedure] = {}
        self.execution_history: List[ProcedureExecution] = []
    
    def register_procedure(self, procedure: Procedure):
        """Register a procedure."""
        self.procedures[procedure.name] = procedure
    
    def get_procedure(self, name: str) -> Optional[Procedure]:
        """Get a procedure by name."""
        return self.procedures.get(name)
    
    def get_procedures_by_type(self, procedure_type: ProcedureType) -> List[Procedure]:
        """Get all procedures of a specific type."""
        return [p for p in self.procedures.values() if p.procedure_type == procedure_type]
    
    def record_execution(self, execution: ProcedureExecution):
        """Record a procedure execution."""
        self.execution_history.append(execution)
    
    def get_execution_history(self, procedure_name: str, limit: int = 10) -> List[ProcedureExecution]:
        """Get execution history for a specific procedure."""
        history = [e for e in self.execution_history if e.procedure_name == procedure_name]
        return sorted(history, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def get_success_rate(self, procedure_name: str) -> float:
        """Calculate success rate for a procedure."""
        history = self.get_execution_history(procedure_name)
        if not history:
            return 0.0
        successful = sum(1 for e in history if e.success)
        return successful / len(history)
    
    def get_average_execution_time(self, procedure_name: str) -> Optional[float]:
        """Get average execution time for a procedure."""
        history = self.get_execution_history(procedure_name)
        if not history:
            return None
        times = [e.execution_time_ms for e in history]
        return sum(times) / len(times)
    
    def initialize_default_procedures(self):
        """Initialize default procedures for common tasks."""
        # Resume audit procedure
        self.register_procedure(Procedure(
            name="resume_audit_standard",
            procedure_type=ProcedureType.RESUME_AUDIT,
            description="Standard resume audit process",
            steps=[
                "Parse resume text into structured bullets",
                "Classify bullets as achievements vs responsibilities",
                "Detect action verbs and strength",
                "Identify quantified metrics",
                "Calculate leadership/technical/strategic signals",
                "Generate structured evidence",
                "Compare against executive standards"
            ],
            required_capabilities=["resume.parse"],
            success_criteria=[
                "All bullets classified",
                "Metrics extracted",
                "Evidence structured"
            ]
        ))
        
        # Interview scoring procedure
        self.register_procedure(Procedure(
            name="interview_scoring_standard",
            procedure_type=ProcedureType.INTERVIEW_SCORING,
            description="Standard interview response scoring",
            steps=[
                "Detect question type (behavioral/situational/technical)",
                "Analyze STAR method completeness",
                "Calculate specificity score",
                "Detect ownership clarity",
                "Score relevant competencies",
                "Identify quantified metrics",
                "Generate improvement feedback"
            ],
            required_capabilities=["interview.score_response"],
            success_criteria=[
                "STAR analysis complete",
                "Competency scores calculated",
                "Feedback generated"
            ]
        ))
        
        # Gap analysis procedure
        self.register_procedure(Procedure(
            name="gap_analysis_standard",
            procedure_type=ProcedureType.GAP_ANALYSIS,
            description="Standard career gap analysis",
            steps=[
                "Get target role requirements",
                "Get user current skill levels",
                "Calculate gaps for each required skill",
                "Determine gap severity",
                "Estimate time to close gaps",
                "Generate development suggestions",
                "Calculate overall readiness score"
            ],
            required_capabilities=["career.gap_analysis"],
            success_criteria=[
                "All required skills analyzed",
                "Gaps identified and prioritized",
                "Readiness score calculated"
            ]
        ))
        
        # Career path analysis procedure
        self.register_procedure(Procedure(
            name="career_path_analysis_standard",
            procedure_type=ProcedureType.CAREER_PATH_ANALYSIS,
            description="Standard career path finding",
            steps=[
                "Identify current role in career graph",
                "Identify target role in career graph",
                "Find all possible paths between roles",
                "Calculate path lengths",
                "Identify required skills for each path",
                "Rank paths by feasibility and user fit",
                "Generate path recommendations"
            ],
            required_capabilities=["career.find_path"],
            success_criteria=[
                "At least one path found",
                "Required skills identified",
                "Paths ranked"
            ]
        ))
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of procedural memory state."""
        return {
            "total_procedures": len(self.procedures),
            "total_executions": len(self.execution_history),
            "procedures_by_type": {pt.value: len(self.get_procedures_by_type(pt)) for pt in ProcedureType}
        }