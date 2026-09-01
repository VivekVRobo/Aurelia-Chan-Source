"""
Aurelia Cognitive OS V3 - Phase 6: Freshness Tracker
=====================================================
Tracks the freshness and staleness of information.

The freshness tracker ensures that the system uses current
information and flags stale data.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class FreshnessStatus(Enum):
    """Status of information freshness."""
    CURRENT = "current"  # Recently updated
    STALE = "stale"  # Getting old
    EXPIRED = "expired"  # Too old to use
    FRESHNESS_UNKNOWN = "freshness_unknown"  # No timestamp available


class InformationCategory(Enum):
    """Categories of information with different freshness requirements."""
    SALARY_DATA = "salary_data"  # Stale quickly (6 months)
    MARKET_TRENDS = "market_trends"  # Stale moderately (1 year)
    ROLE_REQUIREMENTS = "role_requirements"  # Changes slowly (2 years)
    SKILL_DEFINITIONS = "skill_definitions"  # Very stable (5 years)
    USER_DATA = "user_data"  # Depends on last update


@dataclass
class FreshnessInfo:
    """
    Information about the freshness of a piece of data.
    """
    id: str
    data_id: str  # ID of the data this freshness info applies to
    category: InformationCategory
    last_updated: datetime
    status: FreshnessStatus = FreshnessStatus.FRESHNESS_UNKNOWN
    staleness_score: float = 0.0  # 0 = fresh, 1 = completely stale
    recommended_action: Optional[str] = None


class FreshnessTracker:
    """
    Tracks the freshness and staleness of information.
    
    The freshness tracker:
    - Monitors when information was last updated
    - Determines if information is stale or expired
    - Provides recommendations for refreshing data
    - Different freshness requirements by category
    """
    
    def __init__(self):
        self.freshness_info: Dict[str, FreshnessInfo] = {}
        self.freshness_counter = 0
        
        # Freshness thresholds for different categories (in days)
        self.freshness_thresholds = {
            InformationCategory.SALARY_DATA: 180,  # 6 months
            InformationCategory.MARKET_TRENDS: 365,  # 1 year
            InformationCategory.ROLE_REQUIREMENTS: 730,  # 2 years
            InformationCategory.SKILL_DEFINITIONS: 1825,  # 5 years
            InformationCategory.USER_DATA: 90  # 3 months
        }
    
    def record_update(
        self,
        data_id: str,
        category: InformationCategory,
        timestamp: Optional[datetime] = None
    ) -> FreshnessInfo:
        """Record that data was updated."""
        if timestamp is None:
            timestamp = datetime.now()
        
        freshness_id = f"freshness_{self.freshness_counter}"
        
        info = FreshnessInfo(
            id=freshness_id,
            data_id=data_id,
            category=category,
            last_updated=timestamp
        )
        
        self.freshness_info[freshness_id] = info
        self.freshness_counter += 1
        
        # Calculate initial status
        self.update_freshness_status(freshness_id)
        
        return info
    
    def update_freshness_status(self, freshness_id: str):
        """Update the freshness status of a piece of information."""
        info = self.get_freshness_info(freshness_id)
        if not info:
            return
        
        threshold_days = self.freshness_thresholds.get(info.category, 365)
        age_days = (datetime.now() - info.last_updated).total_seconds() / 86400
        
        # Calculate staleness score (0 = fresh, 1 = completely stale)
        info.staleness_score = min(1.0, age_days / threshold_days)
        
        # Determine status
        if age_days < threshold_days * 0.5:
            info.status = FreshnessStatus.CURRENT
            info.recommended_action = None
        elif age_days < threshold_days:
            info.status = FreshnessStatus.STALE
            info.recommended_action = f"Data is {age_days:.0f} days old. Consider refreshing within {threshold_days - age_days:.0f} days."
        else:
            info.status = FreshnessStatus.EXPIRED
            info.recommended_action = f"Data is {age_days:.0f} days old and exceeds the {threshold_days} day threshold. Refresh required."
    
    def get_freshness_info(self, freshness_id: str) -> Optional[FreshnessInfo]:
        """Get freshness info by ID."""
        return self.freshness_info.get(freshness_id)
    
    def get_freshness_for_data(self, data_id: str) -> Optional[FreshnessInfo]:
        """Get freshness info for a specific data ID."""
        for info in self.freshness_info.values():
            if info.data_id == data_id:
                return info
        return None
    
    def get_stale_data(self) -> List[FreshnessInfo]:
        """Get all stale data."""
        return [info for info in self.freshness_info.values() if info.status == FreshnessStatus.STALE]
    
    def get_expired_data(self) -> List[FreshnessInfo]:
        """Get all expired data."""
        return [info for info in self.freshness_info.values() if info.status == FreshnessStatus.EXPIRED]
    
    def get_current_data(self) -> List[FreshnessInfo]:
        """Get all current data."""
        return [info for info in self.freshness_info.values() if info.status == FreshnessStatus.CURRENT]
    
    def refresh_all_statuses(self):
        """Refresh all freshness statuses based on current time."""
        for freshness_id in self.freshness_info:
            self.update_freshness_status(freshness_id)
    
    def set_custom_threshold(self, category: InformationCategory, days: int):
        """Set a custom freshness threshold for a category."""
        self.freshness_thresholds[category] = days
    
    def get_freshness_report(self) -> Dict[str, Any]:
        """Generate a comprehensive freshness report."""
        self.refresh_all_statuses()
        
        return {
            "total_items": len(self.freshness_info),
            "by_status": {
                status.value: len([info for info in self.freshness_info.values() if info.status == status])
                for status in FreshnessStatus
            },
            "by_category": {
                category.value: len([info for info in self.freshness_info.values() if info.category == category])
                for category in InformationCategory
            },
            "stale_count": len(self.get_stale_data()),
            "expired_count": len(self.get_expired_data()),
            "current_count": len(self.get_current_data()),
            "average_staleness": sum(info.staleness_score for info in self.freshness_info.values()) / len(self.freshness_info) if self.freshness_info else 0.0
        }
    
    def get_actionable_items(self) -> List[Dict[str, Any]]:
        """Get items that need action (stale or expired)."""
        actionable = []
        
        for info in self.freshness_info.values():
            if info.status in [FreshnessStatus.STALE, FreshnessStatus.EXPIRED]:
                actionable.append({
                    "data_id": info.data_id,
                    "category": info.category.value,
                    "status": info.status.value,
                    "staleness_score": info.staleness_score,
                    "recommended_action": info.recommended_action,
                    "last_updated": info.last_updated.isoformat()
                })
        
        # Sort by staleness score (most stale first)
        actionable.sort(key=lambda x: x["staleness_score"], reverse=True)
        
        return actionable