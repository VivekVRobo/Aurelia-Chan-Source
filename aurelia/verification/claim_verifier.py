"""
Aurelia Cognitive OS V3 - Phase 6: Claim Verification
======================================================
Validates assertions against available evidence.

Claim verification ensures that assertions made by the system
are backed by evidence and removes unsupported claims before response.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import Enum
from aurelia.cognition.contracts import Evidence, MemoryFact


class ClaimStatus(Enum):
    """Status of a claim verification."""
    VERIFIED = "verified"  # Strong evidence supports the claim
    LIKELY = "likely"  # Some evidence supports the claim
    UNCERTAIN = "uncertain"  # Insufficient evidence
    UNVERIFIED = "unverified"  # No evidence found
    CONTRADICTED = "contradicted"  # Evidence contradicts the claim
    REJECTED = "rejected"  # Claim is false or unreliable


class ClaimType(Enum):
    """Types of claims."""
    FACTUAL = "factual"  # Verifiable facts
    NUMERICAL = "numerical"  # Numbers, statistics, measurements
    CAUSAL = "causal"  # Cause-effect relationships
    PREDICTIVE = "predictive"  # Predictions about the future
    SUBJECTIVE = "subjective"  # Opinions, preferences


@dataclass
class Claim:
    """
    A claim that needs verification.
    
    Claims are assertions that need to be validated against evidence.
    """
    id: str
    claim_text: str
    claim_type: ClaimType
    source: str  # Where the claim came from (e.g., "LLM", "user", "specialist_engine")
    status: ClaimStatus = ClaimStatus.UNCERTAIN
    confidence: float = 0.0
    supporting_evidence: List[Evidence] = field(default_factory=list)
    contradicting_evidence: List[Evidence] = field(default_factory=list)
    verification_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Result of claim verification."""
    claim_id: str
    claim_text: str
    status: ClaimStatus
    confidence: float
    supporting_evidence_count: int
    contradicting_evidence_count: int
    notes: List[str]
    should_include_in_response: bool


class ClaimVerifier:
    """
    Validates assertions against available evidence.
    
    The claim verifier:
    - Checks claims against available evidence
    - Determines claim status (verified, likely, uncertain, etc.)
    - Identifies contradictions
    - Recommends whether to include claims in responses
    """
    
    def __init__(self):
        self.claims: Dict[str, Claim] = {}
        self.claim_counter = 0
    
    def create_claim(
        self,
        claim_text: str,
        claim_type: ClaimType,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Claim:
        """Create a new claim for verification."""
        claim_id = f"claim_{self.claim_counter}"
        
        claim = Claim(
            id=claim_id,
            claim_text=claim_text,
            claim_type=claim_type,
            source=source,
            metadata=metadata or {}
        )
        
        self.claims[claim_id] = claim
        self.claim_counter += 1
        
        return claim
    
    def get_claim(self, claim_id: str) -> Optional[Claim]:
        """Get a claim by ID."""
        return self.claims.get(claim_id)
    
    def add_supporting_evidence(self, claim_id: str, evidence: Evidence):
        """Add supporting evidence to a claim."""
        if claim_id in self.claims:
            self.claims[claim_id].supporting_evidence.append(evidence)
    
    def add_contradicting_evidence(self, claim_id: str, evidence: Evidence):
        """Add contradicting evidence to a claim."""
        if claim_id in self.claims:
            self.claims[claim_id].contradicting_evidence.append(evidence)
    
    def verify_claim(
        self,
        claim_id: str,
        available_evidence: List[Evidence],
        memory_facts: List[MemoryFact]
    ) -> VerificationResult:
        """
        Verify a claim against available evidence and memory facts.
        
        Returns a verification result with status and recommendation.
        """
        claim = self.get_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")
        
        # Find relevant evidence
        supporting = []
        contradicting = []
        
        for evidence in available_evidence:
            if self._evidence_supports_claim(claim, evidence):
                supporting.append(evidence)
            elif self._evidence_contradicts_claim(claim, evidence):
                contradicting.append(evidence)
        
        # Check against memory facts
        for fact in memory_facts:
            if self._fact_supports_claim(claim, fact):
                supporting.append(Evidence(source="memory", reference=fact.subject))
            elif self._fact_contradicts_claim(claim, fact):
                contradicting.append(Evidence(source="memory", reference=fact.subject))
        
        # Update claim with evidence
        claim.supporting_evidence = supporting
        claim.contradicting_evidence = contradicting
        
        # Determine status
        status = self._determine_claim_status(claim, supporting, contradicting)
        claim.status = status
        
        # Calculate confidence
        confidence = self._calculate_claim_confidence(claim, supporting, contradicting)
        claim.confidence = confidence
        
        # Determine if should be included in response
        should_include = self._should_include_in_response(claim, status, confidence)
        
        return VerificationResult(
            claim_id=claim.id,
            claim_text=claim.claim_text,
            status=status,
            confidence=confidence,
            supporting_evidence_count=len(supporting),
            contradicting_evidence_count=len(contradicting),
            notes=claim.verification_notes,
            should_include_in_response=should_include
        )
    
    def _evidence_supports_claim(self, claim: Claim, evidence: Evidence) -> bool:
        """Check if evidence supports the claim."""
        # Simple implementation - in full system would use semantic matching
        claim_lower = claim.claim_text.lower()
        evidence_lower = str(evidence).lower()
        
        # Check for direct evidence matches
        if evidence_lower in claim_lower or claim_lower in evidence_lower:
            return True
        
        return False
    
    def _evidence_contradicts_claim(self, claim: Claim, evidence: Evidence) -> bool:
        """Check if evidence contradicts the claim."""
        # Simple implementation - in full system would use semantic contradiction detection
        claim_lower = claim.claim_text.lower()
        evidence_lower = str(evidence).lower()
        
        # Check for negation words
        contradiction_words = ["not", "never", "no", "false", "incorrect", "wrong"]
        for word in contradiction_words:
            if word in evidence_lower and word not in claim_lower:
                return True
        
        return False
    
    def _fact_supports_claim(self, claim: Claim, fact: MemoryFact) -> bool:
        """Check if a memory fact supports the claim."""
        # Simple semantic matching
        claim_lower = claim.claim_text.lower()
        fact_lower = f"{fact.subject} {fact.predicate} {fact.object}".lower()
        
        return claim_lower in fact_lower or fact_lower in claim_lower
    
    def _fact_contradicts_claim(self, claim: Claim, fact: MemoryFact) -> bool:
        """Check if a memory fact contradicts the claim."""
        # Simple contradiction detection
        claim_lower = claim.claim_text.lower()
        fact_lower = f"{fact.subject} {fact.predicate} {fact.object}".lower()
        
        # Check for opposite predicates
        opposite_predicates = {
            "is": "is not",
            "has": "does not have",
            "can": "cannot",
            "will": "will not"
        }
        
        for pred, opposite in opposite_predicates.items():
            if pred in fact_lower and opposite in claim_lower:
                return True
            if opposite in fact_lower and pred in claim_lower:
                return True
        
        return False
    
    def _determine_claim_status(
        self,
        claim: Claim,
        supporting: List[Evidence],
        contradicting: List[Evidence]
    ) -> ClaimStatus:
        """Determine the status of a claim based on evidence."""
        if len(contradicting) > len(supporting):
            return ClaimStatus.CONTRADICTED
        
        if len(supporting) == 0 and len(contradicting) == 0:
            return ClaimStatus.UNVERIFIED
        
        if len(supporting) >= 3:
            return ClaimStatus.VERIFIED
        
        if len(supporting) >= 1:
            return ClaimStatus.LIKELY
        
        return ClaimStatus.UNCERTAIN
    
    def _calculate_claim_confidence(
        self,
        claim: Claim,
        supporting: List[Evidence],
        contradicting: List[Evidence]
    ) -> float:
        """Calculate confidence in a claim based on evidence."""
        total_evidence = len(supporting) + len(contradicting)
        
        if total_evidence == 0:
            return 0.0
        
        supporting_ratio = len(supporting) / total_evidence
        
        # Adjust based on claim type
        if claim.claim_type == ClaimType.FACTUAL:
            return supporting_ratio
        elif claim.claim_type == ClaimType.NUMERICAL:
            return supporting_ratio * 0.9  # Numerical claims need strong evidence
        elif claim.claim_type == ClaimType.PREDICTIVE:
            return supporting_ratio * 0.7  # Predictions are inherently uncertain
        else:
            return supporting_ratio * 0.8
    
    def _should_include_in_response(
        self,
        claim: Claim,
        status: ClaimStatus,
        confidence: float
    ) -> bool:
        """Determine if a claim should be included in the response."""
        # Don't include contradicted or rejected claims
        if status in [ClaimStatus.CONTRADICTED, ClaimStatus.REJECTED]:
            return False
        
        # Include verified and likely claims
        if status in [ClaimStatus.VERIFIED, ClaimStatus.LIKELY]:
            return True
        
        # Include uncertain claims only if high confidence
        if status == ClaimStatus.UNCERTAIN and confidence >= 0.7:
            return True
        
        # Don't include unverified claims
        if status == ClaimStatus.UNVERIFIED:
            return False
        
        return False
    
    def verify_all_claims(
        self,
        available_evidence: List[Evidence],
        memory_facts: List[MemoryFact]
    ) -> List[VerificationResult]:
        """Verify all pending claims."""
        results = []
        
        for claim_id in self.claims:
            result = self.verify_claim(claim_id, available_evidence, memory_facts)
            results.append(result)
        
        return results
    
    def get_verified_claims(self) -> List[Claim]:
        """Get all verified claims."""
        return [c for c in self.claims.values() if c.status == ClaimStatus.VERIFIED]
    
    def get_contradicted_claims(self) -> List[Claim]:
        """Get all contradicted claims."""
        return [c for c in self.claims.values() if c.status == ClaimStatus.CONTRADICTED]
    
    def clear_claims(self):
        """Clear all claims (e.g., for new conversation)."""
        self.claims = {}
        self.claim_counter = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the claim verifier state."""
        return {
            "total_claims": len(self.claims),
            "by_status": {status.value: len([c for c in self.claims.values() if c.status == status]) for status in ClaimStatus},
            "by_type": {ctype.value: len([c for c in self.claims.values() if c.claim_type == ctype]) for ctype in ClaimType},
            "average_confidence": sum(c.confidence for c in self.claims.values()) / len(self.claims) if self.claims else 0.0
        }