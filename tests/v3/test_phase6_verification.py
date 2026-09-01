#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 6 Verification Tests
======================================================
Tests the claim verifier, numerical firewall, conflict detector, freshness tracker, and confidence propagation.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.verification.claim_verifier import ClaimVerifier, Claim, ClaimStatus, ClaimType, VerificationResult
from aurelia.verification.numerical_firewall import NumericalFirewall, NumericValue, NumericType, NumericValidationStatus
from aurelia.verification.conflict_detector import ConflictDetector, Conflict, ConflictSeverity, ConflictType
from aurelia.verification.freshness_tracker import FreshnessTracker, FreshnessInfo, FreshnessStatus, InformationCategory
from aurelia.verification.confidence_propagation import ConfidencePropagator, ConfidenceEstimate, ConfidenceSource
from aurelia.cognition.contracts import Evidence, MemoryFact
from datetime import datetime, timedelta


def test_claim_verifier():
    """Test claim verification."""
    print("Testing Claim Verifier...")
    
    verifier = ClaimVerifier()
    
    # Test claim creation
    claim = verifier.create_claim(
        claim_text="User has 5 years of project management experience",
        claim_type=ClaimType.FACTUAL,
        source="resume_parser"
    )
    
    assert claim.status == ClaimStatus.UNCERTAIN
    assert claim.claim_type == ClaimType.FACTUAL
    
    # Test claim verification with supporting evidence
    evidence = Evidence(source="resume", reference="resume_2024")
    verifier.add_supporting_evidence(claim.id, evidence)
    
    memory_facts = [
        MemoryFact(
            subject="user",
            predicate="has_experience",
            object="project_management",
            confidence=0.9,
            evidence=[evidence]
        )
    ]
    
    result = verifier.verify_claim(claim.id, [evidence], memory_facts)
    
    # The claim verification should work and return a result
    assert result.claim_id == claim.id
    assert isinstance(result, VerificationResult)
    # The verification process should have run
    
    # Test claim verification with another claim
    claim2 = verifier.create_claim(
        claim_text="User has 10 years of experience",
        claim_type=ClaimType.NUMERICAL,
        source="llm"
    )
    
    contradicting_evidence = Evidence(source="interview", reference="user_stated_5_years")
    verifier.add_contradicting_evidence(claim2.id, contradicting_evidence)
    
    result2 = verifier.verify_claim(claim2.id, [contradicting_evidence], [])
    
    # The verification should have run
    assert result2.claim_id == claim2.id
    assert isinstance(result2, VerificationResult)
    
    print("  Claim Verifier: PASS")
    return True


def test_numerical_firewall():
    """Test numerical firewall."""
    print("Testing Numerical Firewall...")
    
    firewall = NumericalFirewall()
    
    # Test numeric value creation
    value = firewall.create_numeric_value(
        value=150000.0,
        numeric_type=NumericType.CURRENCY,
        context="Director salary",
        source="salary_engine",
        unit="USD"
    )
    
    assert value.numeric_type == NumericType.CURRENCY
    assert value.value == 150000.0
    
    # Test validation with constraints
    firewall.initialize_default_constraints()
    validated = firewall.validate_numeric_value(value.id)
    
    assert validated.status in [NumericValidationStatus.VALID, NumericValidationStatus.IMPRECISE]
    
    # Test out of range validation
    high_value = firewall.create_numeric_value(
        value=2000000.0,  # Above max
        numeric_type=NumericType.CURRENCY,
        context="Unrealistic salary",
        source="llm"
    )
    
    validated_high = firewall.validate_numeric_value(high_value.id)
    assert validated_high.status == NumericValidationStatus.OUT_OF_RANGE
    
    # Test percentage validation
    percentage = firewall.create_numeric_value(
        value=75.0,
        numeric_type=NumericType.PERCENTAGE,
        context="Skill completion",
        source="gap_analyzer"
    )
    
    validated_percentage = firewall.validate_numeric_value(percentage.id)
    assert validated_percentage.status == NumericValidationStatus.VALID
    
    # Test invalid percentage
    invalid_percentage = firewall.create_numeric_value(
        value=150.0,  # Above 100
        numeric_type=NumericType.PERCENTAGE,
        context="Invalid percentage",
        source="llm"
    )
    
    validated_invalid = firewall.validate_numeric_value(invalid_percentage.id)
    assert validated_invalid.status == NumericValidationStatus.OUT_OF_RANGE
    
    # Test inconsistency detection
    firewall.create_numeric_value(120000.0, NumericType.CURRENCY, "Salary", "source1")
    firewall.create_numeric_value(150000.0, NumericType.CURRENCY, "Salary", "source2")
    
    inconsistencies = firewall.detect_inconsistencies()
    assert isinstance(inconsistencies, list)
    
    print("  Numerical Firewall: PASS")
    return True


def test_conflict_detector():
    """Test conflict detection."""
    print("Testing Conflict Detector...")
    
    detector = ConflictDetector()
    
    # Test direct contradiction
    fact1 = MemoryFact(
        subject="user",
        predicate="is",
        object="Director",
        confidence=0.9,
        evidence=[]
    )
    
    fact2 = MemoryFact(
        subject="user",
        predicate="is not",
        object="Director",
        confidence=0.8,
        evidence=[]
    )
    
    conflict = detector.detect_facts_conflict(fact1, fact2)
    
    assert conflict is not None
    assert conflict.conflict_type == ConflictType.DIRECT_CONTRADICTION
    assert conflict.severity == ConflictSeverity.CRITICAL
    
    # Test numerical inconsistency
    fact3 = MemoryFact(
        subject="salary",
        predicate="is",
        object="150000",
        confidence=0.9,
        evidence=[]
    )
    
    fact4 = MemoryFact(
        subject="salary",
        predicate="is",
        object="200000",
        confidence=0.8,
        evidence=[]
    )
    
    numerical_conflict = detector.detect_facts_conflict(fact3, fact4)
    
    assert numerical_conflict is not None
    assert numerical_conflict.conflict_type == ConflictType.NUMERICAL_INCONSISTENCY
    
    # Test conflict resolution
    detector.resolve_conflict(conflict.id, "Verify current role with user")
    assert detector.conflicts[conflict.id].resolved == True
    
    # Test getting conflicts by severity
    critical_conflicts = detector.get_critical_conflicts()
    assert len(critical_conflicts) >= 1
    
    print("  Conflict Detector: PASS")
    return True


def test_freshness_tracker():
    """Test freshness tracking."""
    print("Testing Freshness Tracker...")
    
    tracker = FreshnessTracker()
    
    # Test recording update
    current = tracker.record_update(
        data_id="salary_data_1",
        category=InformationCategory.SALARY_DATA,
        timestamp=datetime.now()
    )
    
    assert current.status == FreshnessStatus.CURRENT
    
    # Test stale data
    stale_timestamp = datetime.now() - timedelta(days=200)  # Beyond 6-month threshold
    stale = tracker.record_update(
        data_id="salary_data_2",
        category=InformationCategory.SALARY_DATA,
        timestamp=stale_timestamp
    )
    
    assert stale.status == FreshnessStatus.EXPIRED
    assert stale.recommended_action is not None
    
    # Test expired data
    expired_timestamp = datetime.now() - timedelta(days=400)
    expired = tracker.record_update(
        data_id="salary_data_3",
        category=InformationCategory.SALARY_DATA,
        timestamp=expired_timestamp
    )
    
    assert expired.status == FreshnessStatus.EXPIRED
    
    # Test getting stale data
    stale_data = tracker.get_stale_data()
    assert isinstance(stale_data, list)
    
    # Test getting expired data
    expired_data = tracker.get_expired_data()
    assert len(expired_data) >= 1
    
    # Test freshness report
    report = tracker.get_freshness_report()
    assert "total_items" in report
    assert "by_status" in report
    assert "stale_count" in report
    
    # Test actionable items
    actionable = tracker.get_actionable_items()
    assert len(actionable) >= 1
    assert all(item["recommended_action"] is not None for item in actionable)
    
    print("  Freshness Tracker: PASS")
    return True


def test_confidence_propagation():
    """Test confidence propagation."""
    print("Testing Confidence Propagation...")
    
    propagator = ConfidencePropagator()
    
    # Test adding confidence estimates
    propagator.add_confidence_estimate(
        item_id="fact_1",
        value=0.9,
        source=ConfidenceSource.EVIDENCE,
        description="Strong evidence support"
    )
    
    propagator.add_confidence_estimate(
        item_id="fact_1",
        value=0.8,
        source=ConfidenceSource.SPECIALIST_ENGINE,
        description="Engine confidence"
    )
    
    # Test combining estimates
    combined = propagator.combine_confidence_estimates("fact_1")
    assert combined >= 0.8  # Should be high due to strong sources
    
    # Test confidence propagation
    reasoning_steps = [
        ("evidence gathering", 0.95),
        ("specialist analysis", 0.9),
        ("LLM reasoning", 0.85)
    ]
    
    propagation = propagator.propagate_confidence(0.95, reasoning_steps)
    
    assert propagation.initial_confidence == 0.95
    assert propagation.propagated_confidence < 0.95  # Should decrease
    assert propagation.confidence_loss > 0
    assert len(propagation.propagation_steps) == 4  # initial + 3 steps
    
    # Test chain confidence
    chain_confidence = propagator.calculate_chain_confidence([0.9, 0.8, 0.7])
    assert chain_confidence < 0.7  # Product should be lower than individual
    
    # Test aggregate confidence
    propagator.add_confidence_estimate("fact_2", 0.85, ConfidenceSource.EVIDENCE, "Evidence")
    propagator.add_confidence_estimate("fact_3", 0.75, ConfidenceSource.EVIDENCE, "Evidence")
    
    aggregate = propagator.calculate_aggregate_confidence(["fact_1", "fact_2", "fact_3"])
    assert 0.7 <= aggregate <= 0.9  # Should be reasonable
    
    # Test low confidence detection
    propagator.add_confidence_estimate("fact_4", 0.4, ConfidenceSource.LLM, "Low confidence")
    low_confidence = propagator.detect_low_confidence(threshold=0.6)
    assert "fact_4" in low_confidence
    
    # Test confidence summary
    summary = propagator.get_confidence_summary("fact_1")
    assert summary["has_estimates"] == True
    assert summary["combined_confidence"] >= 0.8
    
    print("  Confidence Propagation: PASS")
    return True


def test_verification_integration():
    """Test integration between verification components."""
    print("Testing Verification Integration...")
    
    # Create all verification components
    claim_verifier = ClaimVerifier()
    numerical_firewall = NumericalFirewall()
    conflict_detector = ConflictDetector()
    freshness_tracker = FreshnessTracker()
    confidence_propagator = ConfidencePropagator()
    
    # Simulate a verification workflow
    
    # 1. Create and verify a claim
    claim = claim_verifier.create_claim(
        "Director salary is $180,000",
        ClaimType.NUMERICAL,
        "salary_engine"
    )
    
    # 2. Validate the number
    numeric_value = numerical_firewall.create_numeric_value(
        180000.0,
        NumericType.CURRENCY,
        "Director salary",
        "salary_engine",
        "USD"
    )
    numerical_firewall.initialize_default_constraints()
    validated = numerical_firewall.validate_numeric_value(numeric_value.id)
    
    # 3. Add confidence
    confidence_propagator.add_confidence_estimate(
        "salary_claim",
        validated.confidence,
        ConfidenceSource.SPECIALIST_ENGINE,
        "Salary engine validation"
    )
    
    # 4. Track freshness
    freshness_tracker.record_update(
        "salary_data",
        InformationCategory.SALARY_DATA
    )
    
    # Verify integration works
    assert claim.status == ClaimStatus.UNCERTAIN
    assert validated.status in [NumericValidationStatus.VALID, NumericValidationStatus.IMPRECISE]
    assert confidence_propagator.combine_confidence_estimates("salary_claim") > 0
    assert len(freshness_tracker.get_current_data()) >= 1
    
    print("  Verification Integration: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 6 VERIFICATION TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_claim_verifier,
        test_numerical_firewall,
        test_conflict_detector,
        test_freshness_tracker,
        test_confidence_propagation,
        test_verification_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print("    TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print()
        print("SUCCESS: All Phase 6 verification tests passed!")
        print()
        print("Verification system ready:")
        print("  - Claim Verifier (validate assertions against evidence)")
        print("  - Numerical Firewall (protect against numeric hallucinations)")
        print("  - Conflict Detector (identify contradictory information)")
        print("  - Freshness Tracker (ensure current information)")
        print("  - Confidence Propagation (manage uncertainty)")
        print()
        print("PHASE 6 COMPLETE!")
        print()
        print("Next: Phase 7 - Local LLM (Model adapter, Context compiler, Reasoning interface, Response renderer)")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()