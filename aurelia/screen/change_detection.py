"""
Aurelia Cognitive OS V6 - Screen Intelligence & Change-Driven Perception
========================================================================
Implements perceptual hash diffing and semantic change detection to ensure
zero vision inference is executed when the display is static.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


@dataclass(frozen=True)
class ScreenRegion:
    """Bounded region of screen."""
    region_id: str
    x: int
    y: int
    width: int
    height: int
    region_hash: str


@dataclass(frozen=True)
class ScreenState:
    """Snapshot of active application and visual state."""
    window_title: str
    process_name: str
    global_hash: str
    regions: Tuple[ScreenRegion, ...]
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ScreenDiffReport:
    """Delta between consecutive screen states."""
    has_meaningful_change: bool
    changed_region_ids: Tuple[str, ...]
    window_changed: bool
    requires_vision_inference: bool
    delta_score: float # 0.0 (identical) to 1.0 (completely new)


class ChangeDetectionEngine:
    """
    Evaluates visual diffs and gates vision model invocation.
    """

    @classmethod
    def compute_screen_hash(cls, raw_content: str) -> str:
        """Computes deterministic SHA256 digest of screen content."""
        return hashlib.sha256(raw_content.encode('utf-8')).hexdigest()

    @classmethod
    def evaluate_screen_change(
        cls,
        previous_state: Optional[ScreenState],
        current_state: ScreenState,
        change_threshold: float = 0.05
    ) -> ScreenDiffReport:
        """
        Calculates diff. If identical or below threshold, requires_vision_inference is False.
        """
        if previous_state is None:
            return ScreenDiffReport(
                has_meaningful_change=True,
                changed_region_ids=tuple(r.region_id for r in current_state.regions),
                window_changed=True,
                requires_vision_inference=True,
                delta_score=1.0
            )

        window_changed = (previous_state.window_title != current_state.window_title or
                          previous_state.process_name != current_state.process_name)

        if window_changed:
            return ScreenDiffReport(
                has_meaningful_change=True,
                changed_region_ids=tuple(r.region_id for r in current_state.regions),
                window_changed=True,
                requires_vision_inference=True,
                delta_score=1.0
            )

        if previous_state.global_hash == current_state.global_hash:
            # Identical screen and same window -> ZERO vision inference
            return ScreenDiffReport(
                has_meaningful_change=False,
                changed_region_ids=(),
                window_changed=False,
                requires_vision_inference=False,
                delta_score=0.0
            )

        # Region-level diffing
        prev_region_map = {r.region_id: r.region_hash for r in previous_state.regions}
        changed_regions = []

        for r in current_state.regions:
            prev_hash = prev_region_map.get(r.region_id)
            if prev_hash != r.region_hash:
                changed_regions.append(r.region_id)

        delta = len(changed_regions) / max(1, len(current_state.regions))
        is_meaningful = delta >= change_threshold or window_changed

        return ScreenDiffReport(
            has_meaningful_change=is_meaningful,
            changed_region_ids=tuple(changed_regions),
            window_changed=window_changed,
            requires_vision_inference=is_meaningful,
            delta_score=round(delta, 3)
        )
