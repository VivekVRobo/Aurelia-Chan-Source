"""
Aurelia Cognitive OS V4 - Numerical Firewall V2 & Symbolic Units
=================================================================
Deterministic mathematical and financial primitives.
Absolute Invariant: LLM arithmetic is never authoritative. All financial,
equity, percentage, and timeline operations are verified here.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, Union


@dataclass(frozen=True)
class Money:
    """
    Normalized monetary value with explicit currency and pay period.
    """
    amount: float
    currency: str = "USD"               # USD, EUR, GBP, JPY, INR
    period: str = "year"                # year, month, hour, one_time

    def to_annual_usd(self, exchange_rates: Optional[Dict[str, float]] = None) -> float:
        """Converts any monetary figure to normalized annual USD."""
        rates = exchange_rates or {"USD": 1.0, "EUR": 1.08, "GBP": 1.28, "JPY": 0.0065, "INR": 0.012}
        rate = rates.get(self.currency.upper(), 1.0)
        usd_amount = self.amount * rate
        
        if self.period == "year":
            return usd_amount
        elif self.period == "month":
            return usd_amount * 12.0
        elif self.period == "hour":
            return usd_amount * 2080.0  # 40 hrs * 52 weeks
        elif self.period == "one_time":
            return usd_amount
        return usd_amount


@dataclass(frozen=True)
class EquityGrant:
    """
    Structured equity package representation.
    """
    ownership_percentage: float         # e.g., 0.5% = 0.005
    vesting_years: float = 4.0
    cliff_months: float = 12.0
    estimated_company_valuation: Optional[Money] = None
    strike_price: Optional[Money] = None
    shares_count: Optional[int] = None
    dilution_assumption_per_round: float = 0.20  # 20% dilution standard per round

    def calculate_estimated_annual_value(self, target_valuation_usd: float) -> float:
        """Calculates normalized annualized expected equity value."""
        total_grant_value = self.ownership_percentage * target_valuation_usd
        return total_grant_value / max(1.0, self.vesting_years)


@dataclass(frozen=True)
class TimelineMonths:
    """
    Structured duration with confidence bounds.
    """
    expected_months: float
    min_months: float
    max_months: float

    def __post_init__(self):
        if self.min_months > self.expected_months or self.expected_months > self.max_months:
            raise ValueError(f"Invalid timeline bounds: min={self.min_months}, expected={self.expected_months}, max={self.max_months}")


class NumericalFirewall:
    """
    Deterministic validator for all numeric, financial, and metric calculations.
    """

    @staticmethod
    def calculate_total_target_compensation(
        base_salary: Money,
        target_bonus_pct: float,
        annual_equity_value: float,
        signing_bonus_first_year: float = 0.0
    ) -> Money:
        """Calculates total annualized cash + equity package deterministically."""
        base_annual = base_salary.to_annual_usd()
        bonus_cash = base_annual * (target_bonus_pct / 100.0)
        total_annual = base_annual + bonus_cash + annual_equity_value + signing_bonus_first_year
        return Money(amount=total_annual, currency="USD", period="year")

    @staticmethod
    def verify_arithmetic_claim(
        claim_description: str,
        expected_value: float,
        actual_value: float,
        tolerance_pct: float = 1.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifies if an arithmetic statement matches exact calculation within tolerance.
        """
        if expected_value == 0.0:
            diff = abs(actual_value)
            passed = diff <= 0.01
        else:
            diff_pct = abs((actual_value - expected_value) / expected_value) * 100.0
            passed = diff_pct <= tolerance_pct
            
        if passed:
            return True, None
        return False, f"Numerical discrepancy in '{claim_description}': Claimed {actual_value}, verified calculation is {expected_value} (Diff: {diff_pct:.2f}%)."
