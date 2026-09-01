"""
Aurelia Cognitive OS V3 - Skills Module
======================================
Specialist intelligence engines that outperform LLMs on
domain-specific tasks.
"""

from .resume.parser import (
    ResumeParser,
    ResumeBullet,
    ResumeSection,
    ParsedResume,
    BulletType,
    ActionVerb
)

from .career.gap_analyzer import (
    CareerGapAnalyzer,
    GapAnalysisInput,
    UserSkill,
    SkillGapDetail,
    GapSeverity
)

from .interview.scorer import (
    InterviewScorer,
    InterviewResponse,
    InterviewQuestionType,
    STARAnalysis,
    CompetencyScore
)

from .compensation.salary_engine import (
    SalaryEngine,
    SalaryBenchmark,
    SalaryAnalysisRequest,
    SalaryDataPoint,
    Currency,
    MarketSegment
)

from .registry import (
    SkillRegistry,
    SkillContract,
    SpecialistSkill,
    skill_registry,
    register_skill
)

__all__ = [
    # Resume
    'ResumeParser',
    'ResumeBullet',
    'ResumeSection',
    'ParsedResume',
    'BulletType',
    'ActionVerb',
    
    # Career
    'CareerGapAnalyzer',
    'GapAnalysisInput',
    'UserSkill',
    'SkillGapDetail',
    'GapSeverity',
    
    # Interview
    'InterviewScorer',
    'InterviewResponse',
    'InterviewQuestionType',
    'STARAnalysis',
    'CompetencyScore',
    
    # Compensation
    'SalaryEngine',
    'SalaryBenchmark',
    'SalaryAnalysisRequest',
    'SalaryDataPoint',
    'Currency',
    'MarketSegment',
    
    # Registry
    'SkillRegistry',
    'SkillContract',
    'SpecialistSkill',
    'skill_registry',
    'register_skill'
]