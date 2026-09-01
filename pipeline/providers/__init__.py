"""
Aurelia 3D Pipeline -- Providers Package
"""

from .base import BaseProvider, GenerationRequest, GenerationResult
from .meshy import MeshyProvider
from .tripo import TripoProvider

PROVIDERS = {
    "meshy": MeshyProvider,
    "tripo": TripoProvider,
}


def get_provider(name: str, config: dict) -> BaseProvider:
    """
    Get a provider instance by name.

    Args:
        name: Provider name ('meshy' or 'tripo')
        config: Full pipeline config dict

    Returns:
        Configured provider instance

    Raises:
        ValueError: If provider name is unknown or API key is missing
    """
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")

    provider_config = config["provider"].get(name, {})
    api_key = provider_config.get("api_key", "")

    provider = PROVIDERS[name](api_key=api_key, config=provider_config)

    if not provider.validate_api_key():
        raise ValueError(
            f"API key for '{name}' is not configured.\n"
            f"Set it in pipeline/config.json -> provider.{name}.api_key"
        )

    return provider
