"""
Aurelia Cognitive OS V3 - Phase 4: Memory Module
================================================
Episodic, semantic, procedural, and strategic memory systems.
"""

from .working_memory import WorkingMemory, ActiveTask, PendingClarification
from .episodic import EpisodicMemory, EpisodicEvent, EventType
from .semantic import SemanticMemory, SemanticFact, KnowledgeCategory
from .procedural import ProceduralMemory, Procedure, ProcedureExecution, ProcedureType
from .strategic import StrategicMemory, StrategicLearning, LearningCategory

__all__ = [
    'WorkingMemory',
    'ActiveTask',
    'PendingClarification',
    'EpisodicMemory',
    'EpisodicEvent',
    'EventType',
    'SemanticMemory',
    'SemanticFact',
    'KnowledgeCategory',
    'ProceduralMemory',
    'Procedure',
    'ProcedureExecution',
    'ProcedureType',
    'StrategicMemory',
    'StrategicLearning',
    'LearningCategory'
]