"""
Aurelia 3D Pipeline -- Base Provider Interface
==============================================
Abstract interface that all 3D generation providers must implement.
This ensures Meshy, Tripo, and any future provider are interchangeable.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class GenerationRequest:
    """Request to generate a 3D model from reference images."""
    reference_images: list[Path]
    output_dir: Path
    generation_name: str  # e.g., "generation_001"

    # Optional overrides
    prompt: str = "Professional woman, 33 years old, short black bob hair, dark blazer, white blouse, black trousers, black heels, full body, neutral standing pose, semi-realistic anime style"
    enable_texture: bool = True
    enable_rigging: bool = True
    topology: str = "smart"  # "smart" or "standard"


@dataclass
class GenerationResult:
    """Result from a 3D generation attempt."""
    success: bool
    provider: str
    model_path: Optional[Path] = None
    task_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        if self.success:
            return f"[OK] [{self.provider}] Model: {self.model_path}"
        else:
            return f"[FAIL] [{self.provider}] Error: {self.error_message}"


class BaseProvider(ABC):
    """Abstract base class for 3D generation providers."""

    def __init__(self, api_key: str, config: dict):
        self.api_key = api_key
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'meshy', 'tripo')."""
        ...

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate a 3D model from reference images.

        This is the main entry point. Implementations should:
        1. Upload reference images to the provider
        2. Submit a generation task
        3. Poll for completion
        4. Download the resulting GLB
        5. Return a GenerationResult

        Args:
            request: GenerationRequest with images and output configuration

        Returns:
            GenerationResult with the path to the downloaded GLB
        """
        ...

    @abstractmethod
    def check_status(self, task_id: str) -> dict:
        """Check the status of a pending generation task."""
        ...

    def validate_api_key(self) -> bool:
        """Check if the API key is configured and non-empty."""
        return bool(self.api_key and self.api_key.strip())
