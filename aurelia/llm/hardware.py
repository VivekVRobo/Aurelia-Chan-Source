"""
Aurelia Cognitive OS V4 - Hardware-Aware Resource Manager
==========================================================
Monitors local CPU, RAM, and VRAM availability to safely scale
cognitive workloads and prevent system freezing during local inference.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class HardwareProfile:
    """Snapshot of local compute resources."""
    cpu_cores: int
    ram_total_gb: float
    ram_available_gb: float
    gpu_name: Optional[str] = None
    vram_total_gb: Optional[float] = None
    vram_available_gb: Optional[float] = None

    def is_memory_pressured(self) -> bool:
        """Returns True if available RAM is dangerously low (< 1.5 GB)."""
        return self.ram_available_gb < 1.5

    def get_max_safe_context_tokens(self) -> int:
        """Calculates safe maximum context window given available RAM."""
        if self.is_memory_pressured():
            return 2048
        if self.ram_available_gb > 8.0:
            return 16384
        return 8192
