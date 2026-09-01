"""
Aurelia Cognitive OS V3 - Phase 6: Numerical Firewall
======================================================
Protects against numeric hallucinations and errors.

The numerical firewall validates numbers, statistics, and measurements
to prevent the system from making incorrect quantitative claims.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import re


class NumericType(Enum):
    """Types of numeric values."""
    CURRENCY = "currency"  # Dollar amounts, salaries
    PERCENTAGE = "percentage"  # Percentages, growth rates
    COUNT = "count"  # Counts, quantities
    DURATION = "duration"  # Time periods, years, months
    RATING = "rating"  # Scores, ratings (0-10, 0-100)
    PROBABILITY = "probability"  # Probabilities, confidence scores


class NumericValidationStatus(Enum):
    """Status of numeric validation."""
    VALID = "valid"
    OUT_OF_RANGE = "out_of_range"
    IMPRECISE = "imprecise"
    INCONSISTENT = "inconsistent"
    SUSPICIOUS = "suspicious"
    UNVERIFIED = "unverified"


@dataclass
class NumericValue:
    """A numeric value that needs validation."""
    id: str
    value: float
    numeric_type: NumericType
    context: str  # What this number represents
    source: str  # Where the number came from
    unit: Optional[str] = None  # Unit (e.g., "USD", "years", "%")
    status: NumericValidationStatus = NumericValidationStatus.UNVERIFIED
    validation_notes: List[str] = field(default_factory=list)
    allowed_range: Optional[Tuple[float, float]] = None  # (min, max)
    confidence: float = 0.0


@dataclass
class NumericConstraint:
    """A constraint on numeric values."""
    numeric_type: NumericType
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[float]] = None
    description: str = ""


class NumericalFirewall:
    """
    Protects against numeric hallucinations and errors.
    
    The numerical firewall:
    - Validates numeric values against reasonable ranges
    - Detects inconsistencies in numbers
    - Checks for suspicious patterns
    - Prevents impossible values
    """
    
    def __init__(self):
        self.numeric_values: Dict[str, NumericValue] = {}
        self.constraints: Dict[NumericType, List[NumericConstraint]] = {}
        self.value_counter = 0
    
    def create_numeric_value(
        self,
        value: float,
        numeric_type: NumericType,
        context: str,
        source: str,
        unit: Optional[str] = None
    ) -> NumericValue:
        """Create a new numeric value for validation."""
        value_id = f"numeric_{self.value_counter}"
        
        numeric_value = NumericValue(
            id=value_id,
            value=value,
            numeric_type=numeric_type,
            context=context,
            source=source,
            unit=unit
        )
        
        self.numeric_values[value_id] = numeric_value
        self.value_counter += 1
        
        return numeric_value
    
    def add_constraint(self, constraint: NumericConstraint):
        """Add a constraint for a numeric type."""
        if constraint.numeric_type not in self.constraints:
            self.constraints[constraint.numeric_type] = []
        self.constraints[constraint.numeric_type].append(constraint)
    
    def validate_numeric_value(self, value_id: str) -> NumericValue:
        """Validate a numeric value against constraints."""
        numeric_value = self.get_numeric_value(value_id)
        if not numeric_value:
            raise ValueError(f"Numeric value {value_id} not found")
        
        # Get constraints for this type
        constraints = self.constraints.get(numeric_value.numeric_type, [])
        
        # Check against constraints
        status = NumericValidationStatus.VALID
        notes = []
        
        for constraint in constraints:
            if constraint.min_value is not None and numeric_value.value < constraint.min_value:
                status = NumericValidationStatus.OUT_OF_RANGE
                notes.append(f"Value {numeric_value.value} is below minimum {constraint.min_value}")
            
            if constraint.max_value is not None and numeric_value.value > constraint.max_value:
                status = NumericValidationStatus.OUT_OF_RANGE
                notes.append(f"Value {numeric_value.value} exceeds maximum {constraint.max_value}")
            
            if constraint.allowed_values and numeric_value.value not in constraint.allowed_values:
                status = NumericValidationStatus.SUSPICIOUS
                notes.append(f"Value {numeric_value.value} not in allowed values {constraint.allowed_values}")
        
        # Type-specific validation
        type_notes = self._validate_by_type(numeric_value)
        notes.extend(type_notes)
        
        if type_notes and status == NumericValidationStatus.VALID:
            status = NumericValidationStatus.IMPRECISE
        
        numeric_value.status = status
        numeric_value.validation_notes = notes
        numeric_value.confidence = self._calculate_confidence(numeric_value, status)
        
        return numeric_value
    
    def _validate_by_type(self, numeric_value: NumericValue) -> List[str]:
        """Type-specific validation rules."""
        notes = []
        
        if numeric_value.numeric_type == NumericType.PERCENTAGE:
            if numeric_value.value < 0 or numeric_value.value > 100:
                notes.append("Percentage should be between 0 and 100")
        
        elif numeric_value.numeric_type == NumericType.PROBABILITY:
            if numeric_value.value < 0 or numeric_value.value > 1:
                notes.append("Probability should be between 0 and 1")
        
        elif numeric_value.numeric_type == NumericType.RATING:
            if numeric_value.value < 0 or numeric_value.value > 10:
                notes.append("Rating should be between 0 and 10")
        
        elif numeric_value.numeric_type == NumericType.CURRENCY:
            if numeric_value.value < 0:
                notes.append("Currency value should be non-negative")
            if numeric_value.value > 10000000:  # $10M threshold
                notes.append("Currency value is unusually high")
        
        elif numeric_value.numeric_type == NumericType.DURATION:
            if numeric_value.value < 0:
                notes.append("Duration should be non-negative")
            if numeric_value.value > 50:  # 50 years threshold
                notes.append("Duration is unusually long")
        
        return notes
    
    def _calculate_confidence(self, numeric_value: NumericValue, status: NumericValidationStatus) -> float:
        """Calculate confidence in the numeric value."""
        if status == NumericValidationStatus.VALID:
            return 0.95
        elif status == NumericValidationStatus.IMPRECISE:
            return 0.7
        elif status == NumericValidationStatus.OUT_OF_RANGE:
            return 0.3
        elif status == NumericValidationStatus.SUSPICIOUS:
            return 0.2
        elif status == NumericValidationStatus.INCONSISTENT:
            return 0.1
        else:
            return 0.5
    
    def get_numeric_value(self, value_id: str) -> Optional[NumericValue]:
        """Get a numeric value by ID."""
        return self.numeric_values.get(value_id)
    
    def detect_inconsistencies(self) -> List[Tuple[str, str, str]]:
        """
        Detect inconsistencies between numeric values.
        
        Returns a list of tuples (value1_id, value2_id, inconsistency_description).
        """
        inconsistencies = []
        
        # Group values by context
        context_groups: Dict[str, List[NumericValue]] = {}
        for value in self.numeric_values.values():
            if value.context not in context_groups:
                context_groups[value.context] = []
            context_groups[value.context].append(value)
        
        # Check for inconsistencies within same context
        for context, values in context_groups.items():
            if len(values) > 1:
                # Check for duplicate values with same type
                for i, v1 in enumerate(values):
                    for v2 in values[i+1:]:
                        if (v1.numeric_type == v2.numeric_type and 
                            abs(v1.value - v2.value) > 0.01):  # Small tolerance
                            inconsistencies.append((
                                v1.id,
                                v2.id,
                                f"Inconsistent values for {context}: {v1.value} vs {v2.value}"
                            ))
        
        return inconsistencies
    
    def check_suspicious_patterns(self) -> List[str]:
        """Check for suspicious numeric patterns that might indicate hallucination."""
        suspicious = []
        
        for value in self.numeric_values.values():
            # Check for "too perfect" numbers
            if value.value in [0, 1, 10, 100, 1000, 10000]:
                if value.numeric_type not in [NumericType.PERCENTAGE, NumericType.PROBABILITY]:
                    suspicious.append(f"Suspiciously round number: {value.value} for {value.context}")
            
            # Check for unrealistic precision
            if abs(value.value) > 0 and len(str(value.value).split('.')[-1]) > 4:
                suspicious.append(f"Unrealistic precision: {value.value} for {value.context}")
        
        return suspicious
    
    def initialize_default_constraints(self):
        """Initialize default constraints for common numeric types."""
        # Salary constraints
        self.add_constraint(NumericConstraint(
            numeric_type=NumericType.CURRENCY,
            min_value=30000,  # Minimum reasonable salary
            max_value=1000000,  # Maximum reasonable salary (executive level)
            description="Salary should be between $30k and $1M"
        ))
        
        # Percentage constraints
        self.add_constraint(NumericConstraint(
            numeric_type=NumericType.PERCENTAGE,
            min_value=0,
            max_value=100,
            description="Percentage should be between 0 and 100"
        ))
        
        # Rating constraints
        self.add_constraint(NumericConstraint(
            numeric_type=NumericType.RATING,
            min_value=0,
            max_value=10,
            description="Rating should be between 0 and 10"
        ))
        
        # Duration constraints (years)
        self.add_constraint(NumericConstraint(
            numeric_type=NumericType.DURATION,
            min_value=0,
            max_value=40,  # Career duration
            description="Duration should be between 0 and 40 years"
        ))
    
    def extract_numeric_from_text(self, text: str, context: str, source: str) -> List[NumericValue]:
        """Extract numeric values from text."""
        values = []
        
        # Find all numbers in the text
        numbers = re.findall(r'[-+]?\d*\.?\d+', text)
        
        for num_str in numbers:
            try:
                value = float(num_str)
                
                # Determine type based on context
                numeric_type = self._infer_numeric_type(value, context)
                
                numeric_value = self.create_numeric_value(
                    value=value,
                    numeric_type=numeric_type,
                    context=context,
                    source=source
                )
                
                values.append(numeric_value)
            except ValueError:
                continue
        
        return values
    
    def _infer_numeric_type(self, value: float, context: str) -> NumericType:
        """Infer the type of a numeric value from context."""
        context_lower = context.lower()
        
        if "salary" in context_lower or "compensation" in context_lower or "$" in context_lower:
            return NumericType.CURRENCY
        elif "percent" in context_lower or "%" in context_lower or "growth" in context_lower:
            return NumericType.PERCENTAGE
        elif "years" in context_lower or "months" in context_lower or "duration" in context_lower:
            return NumericType.DURATION
        elif "score" in context_lower or "rating" in context_lower:
            return NumericType.RATING
        elif "probability" in context_lower or "chance" in context_lower or "confidence" in context_lower:
            return NumericType.PROBABILITY
        else:
            return NumericType.COUNT
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the numerical firewall state."""
        return {
            "total_values": len(self.numeric_values),
            "by_status": {status.value: len([v for v in self.numeric_values.values() if v.status == status]) for status in NumericValidationStatus},
            "by_type": {ntype.value: len([v for v in self.numeric_values.values() if v.numeric_type == ntype]) for ntype in NumericType},
            "inconsistencies": len(self.detect_inconsistencies()),
            "suspicious_patterns": len(self.check_suspicious_patterns())
        }