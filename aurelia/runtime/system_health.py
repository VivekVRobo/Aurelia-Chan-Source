"""
Aurelia Cognitive OS V3 - Phase 12: System Health Monitor
=========================================================
Monitors system health and performance metrics.

The system health monitor tracks various metrics to ensure
the cognitive system is operating correctly and efficiently.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class HealthMetricType(Enum):
    """Types of health metrics."""
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    CONFIDENCE_LEVEL = "confidence_level"
    UPTIME = "uptime"


class HealthStatus(Enum):
    """Overall system health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthMetric:
    """
    A health metric measurement.
    
    Represents a single measurement of a system metric.
    """
    metric_type: HealthMetricType
    value: float
    unit: str
    timestamp: datetime
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthAlert:
    """
    An alert about system health.
    
    Generated when a metric exceeds thresholds.
    """
    id: str
    metric_type: HealthMetricType
    severity: str  # "warning", "critical"
    message: str
    value: float
    threshold: float
    timestamp: datetime


class SystemHealthMonitor:
    """
    Monitors system health and performance metrics.
    
    The system health monitor:
    - Tracks various system metrics
    - Evaluates metrics against thresholds
    - Generates alerts when thresholds are exceeded
    - Provides overall health status
    """
    
    def __init__(self):
        self.metrics: List[HealthMetric] = []
        self.alerts: List[HealthAlert] = []
        self.alert_counter = 0
        self.start_time = datetime.now()
    
    def record_metric(
        self,
        metric_type: HealthMetricType,
        value: float,
        unit: str,
        threshold_warning: Optional[float] = None,
        threshold_critical: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HealthMetric:
        """Record a health metric."""
        metric = HealthMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            threshold_warning=threshold_warning,
            threshold_critical=threshold_critical,
            metadata=metadata or {}
        )
        
        self.metrics.append(metric)
        
        # Check thresholds
        self._check_thresholds(metric)
        
        return metric
    
    def _check_thresholds(self, metric: HealthMetric):
        """Check if metric exceeds thresholds and generate alerts."""
        # Check critical threshold
        if metric.threshold_critical and metric.value >= metric.threshold_critical:
            self._generate_alert(
                metric.metric_type,
                "critical",
                f"{metric.metric_type.value} exceeded critical threshold: {metric.value} {metric.unit}",
                metric.value,
                metric.threshold_critical
            )
        
        # Check warning threshold
        elif metric.threshold_warning and metric.value >= metric.threshold_warning:
            self._generate_alert(
                metric.metric_type,
                "warning",
                f"{metric.metric_type.value} exceeded warning threshold: {metric.value} {metric.unit}",
                metric.value,
                metric.threshold_warning
            )
    
    def _generate_alert(self, metric_type: HealthMetricType, severity: str, message: str, value: float, threshold: float):
        """Generate a health alert."""
        alert_id = f"health_alert_{self.alert_counter}"
        
        alert = HealthAlert(
            id=alert_id,
            metric_type=metric_type,
            severity=severity,
            message=message,
            value=value,
            threshold=threshold,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        self.alert_counter += 1
    
    def get_overall_health_status(self) -> HealthStatus:
        """Determine overall system health status."""
        if not self.alerts:
            return HealthStatus.HEALTHY
        
        # Check for critical alerts
        critical_alerts = [a for a in self.alerts if a.severity == "critical"]
        if critical_alerts:
            return HealthStatus.CRITICAL
        
        # Check for recent warning alerts
        recent_warning_alerts = [
            a for a in self.alerts
            if a.severity == "warning" and (datetime.now() - a.timestamp).total_seconds() < 3600
        ]
        if recent_warning_alerts:
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def get_metrics_by_type(self, metric_type: HealthMetricType, limit: int = 50) -> List[HealthMetric]:
        """Get recent metrics of a specific type."""
        type_metrics = [m for m in self.metrics if m.metric_type == metric_type]
        return type_metrics[-limit:]
    
    def get_recent_alerts(self, limit: int = 10) -> List[HealthAlert]:
        """Get recent health alerts."""
        return self.alerts[-limit:]
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_average_metric(self, metric_type: HealthMetricType, limit: int = 50) -> Optional[float]:
        """Get average value for a metric type."""
        metrics = self.get_metrics_by_type(metric_type, limit)
        if not metrics:
            return None
        
        return sum(m.value for m in metrics) / len(metrics)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of system health."""
        return {
            "overall_status": self.get_overall_health_status().value,
            "uptime_seconds": self.get_uptime(),
            "total_metrics": len(self.metrics),
            "total_alerts": len(self.alerts),
            "critical_alerts": len([a for a in self.alerts if a.severity == "critical"]),
            "warning_alerts": len([a for a in self.alerts if a.severity == "warning"]),
            "by_metric_type": {
                mt.value: len(self.get_metrics_by_type(mt))
                for mt in HealthMetricType
            }
        }