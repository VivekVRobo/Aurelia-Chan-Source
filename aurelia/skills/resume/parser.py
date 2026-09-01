"""
Aurelia Cognitive OS V3 - Phase 2: Resume Intelligence
=====================================================
Resume parsing and structured evidence extraction.

Specialized analyzer that extracts structured evidence from
resume text, not just "good" or "bad" assessments.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re
from datetime import datetime
from aurelia.cognition.contracts import AchievementEvidence, Evidence


class BulletType(Enum):
    """Types of resume bullet points."""
    ACHIEVEMENT = "achievement"
    RESPONSIBILITY = "responsibility"
    SKILL = "skill"
    UNCLASSIFIED = "unclassified"


class ActionVerb(Enum):
    """Common action verbs and their strength."""
    LED = ("led", 0.9)
    MANAGED = ("managed", 0.8)
    DEVELOPED = ("developed", 0.7)
    IMPLEMENTED = ("implemented", 0.7)
    CREATED = ("created", 0.6)
    BUILT = ("built", 0.6)
    DESIGNED = ("designed", 0.6)
    IMPROVED = ("improved", 0.5)
    ENHANCED = ("enhanced", 0.5)
    INCREASED = ("increased", 0.7)
    REDUCED = ("reduced", 0.7)
    DELIVERED = ("delivered", 0.6)
    ACHIEVED = ("achieved", 0.8)
    EXECUTED = ("executed", 0.7)
    DIRECTED = ("directed", 0.8)
    COORDINATED = ("coordinated", 0.5)
    COLLABORATED = ("collaborated", 0.4)
    SUPPORTED = ("supported", 0.3)
    ASSISTED = ("assisted", 0.2)
    HELPED = ("helped", 0.2)
    
    @classmethod
    def get_strength(cls, verb: str) -> float:
        """Get strength score for a verb."""
        verb_lower = verb.lower()
        for action_verb in cls:
            if action_verb.value[0] == verb_lower:
                return action_verb.value[1]
        return 0.3  # Default for unknown verbs


@dataclass
class ResumeBullet:
    """A single bullet point from a resume."""
    text: str
    bullet_type: BulletType
    action_verb: Optional[str] = None
    action_strength: float = 0.0
    has_metric: bool = False
    metric_value: Optional[float] = None
    metric_type: Optional[str] = None  # e.g., "percentage", "dollar_amount", "count"
    leadership_signal: float = 0.0
    technical_signal: float = 0.0
    strategic_signal: float = 0.0


@dataclass
class ResumeSection:
    """A section of a resume (e.g., Experience, Education)."""
    title: str
    content: List[str]
    bullets: List[ResumeBullet] = field(default_factory=list)


@dataclass
class ParsedResume:
    """Structured parsing of a resume."""
    sections: List[ResumeSection]
    all_bullets: List[ResumeBullet] = field(default_factory=list)
    total_achievements: int = 0
    metrics_count: int = 0
    avg_action_strength: float = 0.0
    leadership_score: float = 0.0
    technical_score: float = 0.0
    strategic_score: float = 0.0


class ResumeParser:
    """
    Resume parser that extracts structured evidence.
    
    Unlike LLM parsing, this is deterministic and explainable.
    """
    
    # Keywords for signal detection
    LEADERSHIP_KEYWORDS = [
        "led", "managed", "directed", "supervised", "oversaw",
        "team", "lead", "manager", "supervisor", "head", "chief"
    ]
    
    TECHNICAL_KEYWORDS = [
        "developed", "built", "implemented", "engineered", "programmed",
        "coded", "architected", "designed", "technical", "software", "system"
    ]
    
    STRATEGIC_KEYWORDS = [
        "strategy", "strategic", "plan", "roadmap", "vision", "direction",
        "initiative", "transformation", "optimization", "efficiency"
    ]
    
    # Metric patterns
    METRIC_PATTERNS = [
        (r'(\d+)%', 'percentage'),
        (r'\$\d+[kK]?', 'dollar_amount'),
        (r'(\d+)\s*(million|billion|thousand|k|K|M|B)', 'count'),
        (r'by\s+(\d+)%', 'percentage'),
        (r'by\s+\$\d+[kK]?', 'dollar_amount'),
    ]
    
    def parse_bullet(self, text: str) -> ResumeBullet:
        """Parse a single bullet point."""
        bullet = ResumeBullet(text=text, bullet_type=BulletType.UNCLASSIFIED)
        
        # Detect action verb
        words = text.split()
        if words:
            first_word = words[0].lower()
            if first_word.endswith('ed'):
                bullet.action_verb = first_word
                bullet.action_strength = ActionVerb.get_strength(first_word)
        
        # Detect metrics
        for pattern, metric_type in self.METRIC_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bullet.has_metric = True
                bullet.metric_type = metric_type
                try:
                    bullet.metric_value = float(match.group(1))
                except (ValueError, IndexError):
                    pass
                break
        
        # Detect signals
        text_lower = text.lower()
        
        # Leadership signal
        leadership_matches = sum(1 for kw in self.LEADERSHIP_KEYWORDS if kw in text_lower)
        bullet.leadership_signal = min(leadership_matches / 3.0, 1.0)
        
        # Technical signal
        technical_matches = sum(1 for kw in self.TECHNICAL_KEYWORDS if kw in text_lower)
        bullet.technical_signal = min(technical_matches / 3.0, 1.0)
        
        # Strategic signal
        strategic_matches = sum(1 for kw in self.STRATEGIC_KEYWORDS if kw in text_lower)
        bullet.strategic_signal = min(strategic_matches / 3.0, 1.0)
        
        # Classify bullet type
        if bullet.has_metric or bullet.action_strength > 0.6:
            bullet.bullet_type = BulletType.ACHIEVEMENT
        elif bullet.action_verb:
            bullet.bullet_type = BulletType.RESPONSIBILITY
        else:
            bullet.bullet_type = BulletType.UNCLASSIFIED
        
        return bullet
    
    def parse_section(self, title: str, content: List[str]) -> ResumeSection:
        """Parse a resume section."""
        section = ResumeSection(title=title, content=content)
        
        for line in content:
            if line.strip().startswith(('-', '•', '*')):
                bullet_text = line.strip()[1:].strip()
                bullet = self.parse_bullet(bullet_text)
                section.bullets.append(bullet)
        
        return section
    
    def parse_resume(self, resume_text: str) -> ParsedResume:
        """Parse a complete resume."""
        parsed = ParsedResume(sections=[])
        
        # Simple section detection (would be more sophisticated in production)
        lines = resume_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers (all caps or common patterns)
            if line.isupper() or line in ['Experience', 'Education', 'Skills', 'Projects']:
                if current_section:
                    section = self.parse_section(current_section, current_content)
                    parsed.sections.append(section)
                    parsed.all_bullets.extend(section.bullets)
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Don't forget the last section
        if current_section:
            section = self.parse_section(current_section, current_content)
            parsed.sections.append(section)
            parsed.all_bullets.extend(section.bullets)
        
        # Calculate statistics
        parsed.total_achievements = sum(1 for b in parsed.all_bullets if b.bullet_type == BulletType.ACHIEVEMENT)
        parsed.metrics_count = sum(1 for b in parsed.all_bullets if b.has_metric)
        
        if parsed.all_bullets:
            parsed.avg_action_strength = sum(b.action_strength for b in parsed.all_bullets) / len(parsed.all_bullets)
            parsed.leadership_score = sum(b.leadership_signal for b in parsed.all_bullets) / len(parsed.all_bullets)
            parsed.technical_score = sum(b.technical_signal for b in parsed.all_bullets) / len(parsed.all_bullets)
            parsed.strategic_score = sum(b.strategic_signal for b in parsed.all_bullets) / len(parsed.all_bullets)
        
        return parsed
    
    def extract_achievement_evidence(self, bullet: ResumeBullet) -> AchievementEvidence:
        """
        Convert a bullet to structured achievement evidence.
        
        This is what career analysis uses directly, not raw text.
        """
        # Infer domain from text (simplified)
        domain = "general"
        text_lower = bullet.text.lower()
        
        if "software" in text_lower or "code" in text_lower or "system" in text_lower:
            domain = "software"
        elif "budget" in text_lower or "financial" in text_lower or "cost" in text_lower:
            domain = "finance"
        elif "team" in text_lower or "people" in text_lower or "management" in text_lower:
            domain = "leadership"
        
        # Infer impact type
        impact_type = "general"
        if "cost" in text_lower or "saving" in text_lower or "reduced" in text_lower:
            impact_type = "cost_reduction"
        elif "revenue" in text_lower or "growth" in text_lower or "increased" in text_lower:
            impact_type = "revenue_growth"
        elif "time" in text_lower or "faster" in text_lower or "efficiency" in text_lower:
            impact_type = "efficiency"
        
        # Use metric value if available, otherwise estimate from strength
        impact_value = bullet.metric_value if bullet.metric_value else bullet.action_strength * 0.3
        
        return AchievementEvidence(
            action=bullet.action_verb or "contributed",
            domain=domain,
            impact_type=impact_type,
            impact_value=impact_value,
            leadership_signal=bullet.leadership_signal,
            technical_signal=bullet.technical_signal,
            strategic_signal=bullet.strategic_signal
        )