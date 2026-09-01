"""
Aurelia Cognitive OS V3 - Phase 12: Autonomous Cognitive Runtime
================================================================
Autonomous operation capabilities for the cognitive system.

Includes event bus, background state updates, goal monitoring,
proactive insights, and system health monitoring.
"""

from .event_bus import (
    EventBus,
    EventType,
    Event
)

from .background_updates import (
    BackgroundStateUpdater,
    UpdateType,
    UpdateStatus,
    BackgroundUpdate
)

from .goal_monitor import (
    GoalMonitor,
    GoalStatus,
    AlertType,
    MonitoredGoal,
    GoalAlert
)

from .proactive_insights import (
    ProactiveInsightGenerator,
    InsightType,
    InsightPriority,
    ProactiveInsight
)

from .system_health import (
    SystemHealthMonitor,
    HealthMetricType,
    HealthStatus,
    HealthMetric,
    HealthAlert
)

__all__ = [
    # Event Bus
    "EventBus",
    "EventType",
    "Event",
    # Background Updates
    "BackgroundStateUpdater",
    "UpdateType",
    "UpdateStatus",
    "BackgroundUpdate",
    # Goal Monitor
    "GoalMonitor",
    "GoalStatus",
    "AlertType",
    "MonitoredGoal",
    "GoalAlert",
    # Proactive Insights
    "ProactiveInsightGenerator",
    "InsightType",
    "InsightPriority",
    "ProactiveInsight",
    # System Health
    "SystemHealthMonitor",
    "HealthMetricType",
    "HealthStatus",
    "HealthMetric",
    "HealthAlert"
]