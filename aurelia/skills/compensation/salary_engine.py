"""
Aurelia Cognitive OS V3 - Phase 2: Salary Benchmark Engine
==========================================================
Salary benchmarking using structured market data.

Specialist engine that provides salary ranges from structured data,
not LLM hallucination of numbers.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
from aurelia.cognition.contracts import (
    Prediction,
    KnowledgeRecord,
    ConfidenceLevel
)


class Currency(Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"


class MarketSegment(Enum):
    """Market segments for salary data."""
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    EXECUTIVE_LEVEL = "executive_level"
    DIRECTOR_LEVEL = "director_level"
    VP_LEVEL = "vp_level"
    C_LEVEL = "c_level"


@dataclass
class SalaryDataPoint:
    """A single salary data point."""
    role: str
    level: str
    location: str
    industry: str
    min_salary: float
    median_salary: float
    max_salary: float
    currency: Currency
    sample_size: int
    data_year: int
    source: str


@dataclass
class SalaryBenchmark:
    """Benchmark result for a specific role and location."""
    role: str
    level: str
    location: str
    industry: str
    salary_range: Tuple[float, float]  # (min, max)
    median_salary: float
    percentile_25: float
    percentile_75: float
    currency: Currency
    confidence: float
    data_freshness: str
    sample_size: int
    last_updated: datetime


@dataclass
class SalaryAnalysisRequest:
    """Request for salary analysis."""
    role: str
    level: str
    location: str
    industry: str
    years_experience: Optional[float] = None
    current_salary: Optional[float] = None
    target_percentile: Optional[float] = None  # e.g., 75th percentile


class SalaryEngine:
    """
    Specialist engine for salary benchmarking.
    
    Uses structured market data, not LLM number generation.
    LLM only explains the results, never creates them.
    """
    
    def __init__(self):
        # In production, this would load from a database
        # For now, we create sample data
        self.salary_database = self._create_sample_database()
        self.last_refresh = datetime.now()
    
    def _create_sample_database(self) -> List[SalaryDataPoint]:
        """Create sample salary database."""
        # Sample data for engineering roles in US tech industry
        return [
            # Manager level
            SalaryDataPoint(
                role="Engineering Manager",
                level="mid_level",
                location="San Francisco",
                industry="Technology",
                min_salary=150000,
                median_salary=180000,
                max_salary=220000,
                currency=Currency.USD,
                sample_size=245,
                data_year=2024,
                source="Glassdoor_combined"
            ),
            SalaryDataPoint(
                role="Engineering Manager",
                level="mid_level",
                location="New York",
                industry="Technology",
                min_salary=140000,
                median_salary=165000,
                max_salary=200000,
                currency=Currency.USD,
                sample_size=198,
                data_year=2024,
                source="Glassdoor_combined"
            ),
            SalaryDataPoint(
                role="Engineering Manager",
                level="mid_level",
                location="Austin",
                industry="Technology",
                min_salary=130000,
                median_salary=155000,
                max_salary=185000,
                currency=Currency.USD,
                sample_size=89,
                data_year=2024,
                source="Glassdoor_combined"
            ),
            # Senior Manager level
            SalaryDataPoint(
                role="Senior Engineering Manager",
                level="senior_level",
                location="San Francisco",
                industry="Technology",
                min_salary=180000,
                median_salary=220000,
                max_salary=280000,
                currency=Currency.USD,
                sample_size=156,
                data_year=2024,
                source="Glassdoor_combined"
            ),
            SalaryDataPoint(
                role="Senior Engineering Manager",
                level="senior_level",
                location="New York",
                industry="Technology",
                min_salary=170000,
                median_salary=205000,
                max_salary=260000,
                currency=Currency.USD,
                sample_size=132,
                data_year=2024,
                source="Glassdoor_combined"
            ),
            # Director level
            SalaryDataPoint(
                role="Director of Engineering",
                level="director_level",
                location="San Francisco",
                industry="Technology",
                min_salary=250000,
                median_salary=320000,
                max_salary=420000,
                currency=Currency.USD,
                sample_size=98,
                data_year=2024,
                source="Levels_fyi"
            ),
            SalaryDataPoint(
                role="Director of Engineering",
                level="director_level",
                location="New York",
                industry="Technology",
                min_salary=230000,
                median_salary=295000,
                max_salary=390000,
                currency=Currency.USD,
                sample_size=87,
                data_year=2024,
                source="Levels_fyi"
            ),
            SalaryDataPoint(
                role="Director of Engineering",
                level="director_level",
                location="Seattle",
                industry="Technology",
                min_salary=220000,
                median_salary=285000,
                max_salary=370000,
                currency=Currency.USD,
                sample_size=65,
                data_year=2024,
                source="Levels_fyi"
            ),
            # VP level
            SalaryDataPoint(
                role="VP of Engineering",
                level="vp_level",
                location="San Francisco",
                industry="Technology",
                min_salary=350000,
                median_salary=450000,
                max_salary=600000,
                currency=Currency.USD,
                sample_size=45,
                data_year=2024,
                source="Levels_fyi"
            ),
            SalaryDataPoint(
                role="VP of Engineering",
                level="vp_level",
                location="New York",
                industry="Technology",
                min_salary=330000,
                median_salary=425000,
                max_salary=570000,
                currency=Currency.USD,
                sample_size=38,
                data_year=2024,
                source="Levels_fyi"
            ),
        ]
    
    def _get_freshness_status(self, data_year: int) -> str:
        """Determine freshness of salary data."""
        current_year = datetime.now().year
        age = current_year - data_year
        
        if age == 0:
            return "FRESH"
        elif age == 1:
            return "FRESH"
        elif age == 2:
            return "AGING"
        elif age <= 3:
            return "STALE"
        else:
            return "UNKNOWN"
    
    def _calculate_percentiles(self, min_salary: float, median_salary: float, max_salary: float) -> Tuple[float, float]:
        """
        Estimate 25th and 75th percentiles.
        
        Using normal distribution approximation.
        """
        # Standard deviation approximation from range
        std_dev = (max_salary - min_salary) / 4.0
        
        # 25th percentile: median - 0.67 * std_dev
        percentile_25 = median_salary - (0.67 * std_dev)
        
        # 75th percentile: median + 0.67 * std_dev
        percentile_75 = median_salary + (0.67 * std_dev)
        
        return (max(min_salary, percentile_25), min(max_salary, percentile_75))
    
    def _adjust_for_experience(self, base_salary: float, years_experience: float, level: str) -> float:
        """
        Adjust salary based on years of experience.
        
        More experience = higher salary, but diminishing returns.
        """
        if years_experience is None:
            return base_salary
        
        # Experience adjustment curve
        if level in ["director_level", "vp_level", "c_level"]:
            # Executive level: 10-15 years is optimal
            optimal_years = 12
        elif level in ["senior_level"]:
            # Senior level: 8-12 years is optimal
            optimal_years = 10
        else:
            # Other levels: 5-8 years is optimal
            optimal_years = 6
        
        # Calculate adjustment factor
        if years_experience < optimal_years:
            # Less experience than optimal
            adjustment = 0.8 + (years_experience / optimal_years) * 0.2
        else:
            # More experience than optimal (diminishing returns)
            excess = years_experience - optimal_years
            adjustment = 1.0 - (excess * 0.01)  # 1% penalty per excess year
            adjustment = max(0.9, adjustment)  # Max 10% penalty
        
        return base_salary * adjustment
    
    def find_matching_data(self, request: SalaryAnalysisRequest) -> List[SalaryDataPoint]:
        """Find salary data points matching the request."""
        matches = []
        
        for data_point in self.salary_database:
            # Match role (fuzzy matching for similar roles)
            if request.role.lower() in data_point.role.lower() or data_point.role.lower() in request.role.lower():
                # Match level
                if request.level == data_point.level:
                    # Match location (exact or broader)
                    if request.location.lower() in data_point.location.lower():
                        # Match industry
                        if request.industry.lower() in data_point.industry.lower():
                            matches.append(data_point)
        
        return matches
    
    def calculate_benchmark(self, request: SalaryAnalysisRequest) -> Optional[SalaryBenchmark]:
        """
        Calculate salary benchmark for the request.
        
        Returns structured data that the LLM explains, not generates.
        """
        matches = self.find_matching_data(request)
        
        if not matches:
            return None
        
        # Aggregate from multiple matches
        total_sample_size = sum(dp.sample_size for dp in matches)
        weighted_median = sum(dp.median_salary * dp.sample_size for dp in matches) / total_sample_size
        weighted_min = sum(dp.min_salary * dp.sample_size for dp in matches) / total_sample_size
        weighted_max = sum(dp.max_salary * dp.sample_size for dp in matches) / total_sample_size
        
        # Calculate percentiles
        percentile_25, percentile_75 = self._calculate_percentiles(weighted_min, weighted_median, weighted_max)
        
        # Adjust for experience if provided
        if request.years_experience:
            weighted_median = self._adjust_for_experience(weighted_median, request.years_experience, request.level)
            percentile_25 = self._adjust_for_experience(percentile_25, request.years_experience, request.level)
            percentile_75 = self._adjust_for_experience(percentile_75, request.years_experience, request.level)
        
        # Calculate confidence based on sample size and match quality
        confidence = min(total_sample_size / 100.0, 1.0)  # Max confidence at 100 samples
        
        # Determine freshness
        most_recent_year = max(dp.data_year for dp in matches)
        freshness = self._get_freshness_status(most_recent_year)
        
        return SalaryBenchmark(
            role=request.role,
            level=request.level,
            location=request.location,
            industry=request.industry,
            salary_range=(weighted_min, weighted_max),
            median_salary=weighted_median,
            percentile_25=percentile_25,
            percentile_75=percentile_75,
            currency=matches[0].currency,
            confidence=confidence,
            data_freshness=freshness,
            sample_size=total_sample_size,
            last_updated=self.last_refresh
        )
    
    def predict_salary(self, request: SalaryAnalysisRequest) -> Prediction:
        """
        Predict salary with uncertainty quantification.
        
        Never fake precision - always include confidence intervals.
        """
        benchmark = self.calculate_benchmark(request)
        
        if benchmark is None:
            return Prediction(
                value=0.0,
                interval=(0.0, 0.0),
                confidence=0.0,
                features=[],
                limitations=["No matching salary data found"]
            )
        
        # Target percentile adjustment
        if request.target_percentile:
            # Linear interpolation between percentiles
            if request.target_percentile <= 50:
                # Between 25th and 50th percentile
                factor = request.target_percentile / 50.0
                predicted = benchmark.percentile_25 + (benchmark.median_salary - benchmark.percentile_25) * factor
            else:
                # Between 50th and 75th percentile
                factor = (request.target_percentile - 50) / 50.0
                predicted = benchmark.median_salary + (benchmark.percentile_75 - benchmark.median_salary) * factor
        else:
            predicted = benchmark.median_salary
        
        # Calculate confidence interval
        interval_width = (benchmark.salary_range[1] - benchmark.salary_range[0]) * 0.3
        lower_bound = predicted - interval_width
        upper_bound = predicted + interval_width
        
        return Prediction(
            value=predicted,
            interval=(max(0, lower_bound), upper_bound),
            confidence=benchmark.confidence,
            features=[
                f"Based on {benchmark.sample_size} data points",
                f"Data freshness: {benchmark.data_freshness}",
                f"Location: {benchmark.location}",
                f"Industry: {benchmark.industry}"
            ],
            limitations=[
                "Sample size may affect accuracy",
                "Location-specific variations not fully captured",
                "Individual factors may cause deviation"
            ]
        )
    
    def compare_current_vs_market(self, request: SalaryAnalysisRequest) -> Dict[str, any]:
        """
        Compare current salary to market benchmark.
        
        Returns structured comparison data.
        """
        benchmark = self.calculate_benchmark(request)
        
        if benchmark is None or request.current_salary is None:
            return {
                "status": "insufficient_data",
                "message": "Cannot compare - missing benchmark or current salary"
            }
        
        current = request.current_salary
        median = benchmark.median_salary
        percentile_25 = benchmark.percentile_25
        percentile_75 = benchmark.percentile_75
        
        # Determine percentile position
        if current < percentile_25:
            position = "below_25th"
            position_label = "Below market"
        elif current < median:
            position = "25th_to_50th"
            position_label = "Below median"
        elif current < percentile_75:
            position = "50th_to_75th"
            position_label = "Above median"
        else:
            position = "above_75th"
            position_label = "Above market"
        
        # Calculate gap
        gap = current - median
        gap_percentage = (gap / median) * 100
        
        return {
            "status": "success",
            "current_salary": current,
            "market_median": median,
            "market_range": benchmark.salary_range,
            "gap": gap,
            "gap_percentage": gap_percentage,
            "position": position,
            "position_label": position_label,
            "percentile_25": percentile_25,
            "percentile_75": percentile_75,
            "confidence": benchmark.confidence,
            "freshness": benchmark.data_freshness
        }