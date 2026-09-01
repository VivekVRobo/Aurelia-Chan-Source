#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 2 Specialist Engines Tests
===========================================================
Tests the specialist intelligence engines (gap analysis, interview scoring, salary engine).
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.skills.career.gap_analyzer import (
    CareerGapAnalyzer,
    GapAnalysisInput,
    UserSkill,
    GapSeverity
)
from aurelia.skills.interview.scorer import (
    InterviewScorer,
    InterviewQuestionType
)
from aurelia.skills.compensation.salary_engine import (
    SalaryEngine,
    SalaryAnalysisRequest,
    Currency
)
from aurelia.cognition.contracts import Evidence
from datetime import datetime


def test_gap_analyzer():
    """Test career gap analysis."""
    print("Testing Career Gap Analyzer...")
    
    analyzer = CareerGapAnalyzer()
    
    # Create test input
    user_skills = [
        UserSkill(
            skill_id="skill.people_management",
            current_level=3.0,
            evidence=[Evidence(source="interview", reference="interview_1")],
            confidence=0.8,
            last_assessed="2024-01-15"
        ),
        UserSkill(
            skill_id="skill.strategic_planning",
            current_level=2.0,
            evidence=[Evidence(source="resume", reference="resume_2024")],
            confidence=0.7,
            last_assessed="2024-01-15"
        ),
        UserSkill(
            skill_id="skill.executive_communication",
            current_level=3.5,
            evidence=[Evidence(source="interview", reference="interview_2")],
            confidence=0.85,
            last_assessed="2024-01-15"
        )
    ]
    
    input_data = GapAnalysisInput(
        target_role="Director",
        current_role="Senior Manager",
        user_skills=user_skills
    )
    
    result = analyzer.analyze_gaps(input_data)
    
    assert result.target_role == "Director"
    assert len(result.gaps) > 0  # Should have some gaps
    assert result.readiness_score >= 0.0
    assert result.readiness_score <= 1.0
    assert result.confidence >= 0.0
    assert result.confidence <= 1.0
    
    print("  Career Gap Analyzer: PASS")
    return True


def test_gap_severity():
    """Test gap severity calculation."""
    print("Testing Gap Severity Calculation...")
    
    analyzer = CareerGapAnalyzer()
    
    # Test different gap sizes
    critical = analyzer.calculate_gap_severity(5.0, 5.0)  # 100% gap
    significant = analyzer.calculate_gap_severity(2.0, 5.0)  # 40% gap
    moderate = analyzer.calculate_gap_severity(1.0, 5.0)  # 20% gap
    minor = analyzer.calculate_gap_severity(0.5, 5.0)  # 10% gap
    none = analyzer.calculate_gap_severity(0.0, 5.0)  # No gap
    
    assert critical == GapSeverity.CRITICAL
    assert significant == GapSeverity.SIGNIFICANT
    assert moderate == GapSeverity.MODERATE
    assert minor == GapSeverity.MINOR
    assert none == GapSeverity.NONE
    
    print("  Gap Severity Calculation: PASS")
    return True


def test_interview_scorer():
    """Test interview response scoring."""
    print("Testing Interview Scorer...")
    
    scorer = InterviewScorer()
    
    # Test behavioral question (correct detection)
    question = "Tell me about a time you led a team through a challenging project."
    answer = """In my previous role, I led a team of 8 engineers through a critical cloud migration project. 
    The task was to migrate our infrastructure to AWS within 6 months while maintaining 99.9% uptime. 
    I implemented a phased migration strategy, established clear communication channels, and conducted daily standups. 
    As a result, we completed the migration 2 weeks ahead of schedule and reduced infrastructure costs by 24%, 
    saving the company $450,000 annually."""
    
    response = scorer.score_response(question, answer)
    
    assert response.question_type == InterviewQuestionType.BEHAVIORAL  # Correct detection
    assert response.star_analysis is not None
    assert response.star_analysis.completeness_score > 0.5  # Should have STAR
    assert response.overall_score >= 0.0
    assert response.overall_score <= 10.0
    assert len(response.competency_scores) > 0
    
    print("  Interview Scorer: PASS")
    return True


def test_star_analysis():
    """Test STAR method analysis."""
    print("Testing STAR Analysis...")
    
    scorer = InterviewScorer()
    
    # Complete STAR response
    complete_answer = "In my previous role (situation), I needed to improve team performance (task). I implemented a new process (action). This resulted in 20% improvement (result)."
    star_complete = scorer.analyze_star_completeness(complete_answer)
    assert star_complete.completeness_score == 1.0
    assert star_complete.issue_count == 0
    
    # Incomplete STAR response
    incomplete_answer = "I implemented a new process."  # Only action
    star_incomplete = scorer.analyze_star_completeness(incomplete_answer)
    assert star_incomplete.completeness_score < 1.0
    assert star_incomplete.issue_count > 0
    
    print("  STAR Analysis: PASS")
    return True


def test_salary_engine():
    """Test salary benchmark engine."""
    print("Testing Salary Engine...")
    
    engine = SalaryEngine()
    
    # Test Director role in San Francisco
    request = SalaryAnalysisRequest(
        role="Director of Engineering",
        level="director_level",
        location="San Francisco",
        industry="Technology",
        years_experience=10,
        current_salary=300000
    )
    
    benchmark = engine.calculate_benchmark(request)
    
    assert benchmark is not None
    assert benchmark.role == "Director of Engineering"
    assert benchmark.location == "San Francisco"
    assert benchmark.median_salary > 0
    assert benchmark.salary_range[0] < benchmark.median_salary
    assert benchmark.salary_range[1] > benchmark.median_salary
    assert benchmark.confidence >= 0.0
    assert benchmark.confidence <= 1.0
    
    print("  Salary Engine: PASS")
    return True


def test_salary_prediction():
    """Test salary prediction with uncertainty."""
    print("Testing Salary Prediction...")
    
    engine = SalaryEngine()
    
    request = SalaryAnalysisRequest(
        role="Director of Engineering",
        level="director_level",
        location="San Francisco",
        industry="Technology",
        years_experience=10,
        target_percentile=75
    )
    
    prediction = engine.predict_salary(request)
    
    assert prediction.value > 0
    assert prediction.interval[0] < prediction.value
    assert prediction.interval[1] > prediction.value
    assert prediction.confidence >= 0.0
    assert prediction.confidence <= 1.0
    assert len(prediction.features) > 0
    assert len(prediction.limitations) > 0
    
    print("  Salary Prediction: PASS")
    return True


def test_salary_comparison():
    """Test current vs market salary comparison."""
    print("Testing Salary Comparison...")
    
    engine = SalaryEngine()
    
    request = SalaryAnalysisRequest(
        role="Director of Engineering",
        level="director_level",
        location="San Francisco",
        industry="Technology",
        years_experience=10,
        current_salary=300000
    )
    
    comparison = engine.compare_current_vs_market(request)
    
    assert comparison["status"] == "success"
    assert "current_salary" in comparison
    assert "market_median" in comparison
    assert "gap" in comparison
    assert "gap_percentage" in comparison
    assert "position" in comparison
    assert "position_label" in comparison
    
    print("  Salary Comparison: PASS")
    return True


def test_development_priority():
    """Test development priority ordering."""
    print("Testing Development Priority...")
    
    analyzer = CareerGapAnalyzer()
    
    from aurelia.skills.career.gap_analyzer import SkillGapDetail
    
    gaps = [
        SkillGapDetail(
            skill_id="skill.people_management",
            skill_name="People Management",
            required_level=4.0,
            current_level=1.0,
            gap_size=3.0,
            severity=GapSeverity.CRITICAL,
            evidence_strength=0.8,
            development_suggestions=[]
        ),
        SkillGapDetail(
            skill_id="skill.strategic_planning",
            skill_name="Strategic Planning",
            required_level=4.0,
            current_level=3.0,
            gap_size=1.0,
            severity=GapSeverity.MODERATE,
            evidence_strength=0.7,
            development_suggestions=[]
        ),
        SkillGapDetail(
            skill_id="skill.executive_communication",
            skill_name="Executive Communication",
            required_level=4.0,
            current_level=2.0,
            gap_size=2.0,
            severity=GapSeverity.SIGNIFICANT,
            evidence_strength=0.9,
            development_suggestions=[]
        )
    ]
    
    prioritized = analyzer.get_development_priority(gaps)
    
    # Critical should come first
    assert prioritized[0].severity == GapSeverity.CRITICAL
    # Significant should come before Moderate
    significant_index = next(i for i, g in enumerate(prioritized) if g.severity == GapSeverity.SIGNIFICANT)
    moderate_index = next(i for i, g in enumerate(prioritized) if g.severity == GapSeverity.MODERATE)
    assert significant_index < moderate_index
    
    print("  Development Priority: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 2 SPECIALIST TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_gap_analyzer,
        test_gap_severity,
        test_interview_scorer,
        test_star_analysis,
        test_salary_engine,
        test_salary_prediction,
        test_salary_comparison,
        test_development_priority
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
        print("SUCCESS: All Phase 2 specialist engines are working correctly!")
        print()
        print("Specialist engines ready:")
        print("  - Career Gap Analyzer (deterministic gap analysis)")
        print("  - Interview Scorer (STAR method, competency scoring)")
        print("  - Salary Engine (benchmarking, prediction, comparison)")
        print()
        print("PHASE 2 COMPLETE!")
        print()
        print("Next: Phase 3 - Cognitive Routing (Skill registry, Capability registry, Router, Execution engine)")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()