"""
Aurelia 3D Pipeline — 3D Generation Orchestrator
==================================================
Coordinates the AI 3D generation process using the configured provider.
Manages generation versioning and keeps a log of all attempts.

Usage:
    python pipeline/generate_3d.py
    python pipeline/generate_3d.py --provider tripo
    python pipeline/generate_3d.py --provider meshy --name custom_run
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.providers import get_provider
from pipeline.providers.base import GenerationRequest


def load_config() -> dict:
    """Load pipeline configuration."""
    config_path = PROJECT_ROOT / "pipeline" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_next_generation_number(raw_dir: Path) -> int:
    """Determine the next generation number based on existing directories."""
    existing = [
        d.name for d in raw_dir.iterdir()
        if d.is_dir() and d.name.startswith("generation_")
    ] if raw_dir.exists() else []

    if not existing:
        return 1

    numbers = []
    for name in existing:
        try:
            num = int(name.split("_")[1])
            numbers.append(num)
        except (IndexError, ValueError):
            pass

    return max(numbers, default=0) + 1


def get_reference_images(config: dict) -> list[Path]:
    """
    Load prepared reference images.
    Returns paths to the best images for multi-view generation.

    Priority order for AI generation:
    1. front (most important)
    2. side
    3. back
    4. three_quarter (if available)
    """
    ref_dir = PROJECT_ROOT / config["paths"]["reference_images"]
    manifest_path = ref_dir / "manifest.json"

    if not manifest_path.exists():
        print("ERROR: Reference images not prepared yet.")
        print("Run: python pipeline/prepare_references.py")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Priority order for multi-view generation
    priority_order = ["front", "side", "back", "three_quarter"]
    images = []

    for name in priority_order:
        path_str = manifest.get("references", {}).get(name)
        if path_str:
            path = Path(path_str)
            if path.exists():
                images.append(path)
                print(f"  ✓ {name}: {path.name}")
            else:
                print(f"  ⚠ {name}: file missing ({path_str})")
        else:
            print(f"  ─ {name}: not in manifest")

    return images


def generate(provider_name: str = None, generation_name: str = None):
    """
    Run the 3D generation pipeline.

    Args:
        provider_name: Override provider (default: from config)
        generation_name: Custom name for this generation run
    """
    print("=" * 60)
    print("AURELIA 3D PIPELINE — AI 3D Generation")
    print("=" * 60)
    print()

    config = load_config()

    # Determine provider
    provider_name = provider_name or config["provider"]["active"]
    print(f"Provider: {provider_name}")
    print()

    # Get reference images
    print("Reference images:")
    images = get_reference_images(config)
    if not images:
        print("\nERROR: No reference images found.")
        print("Run: python pipeline/prepare_references.py")
        return None
    print()

    # Create provider
    try:
        provider = get_provider(provider_name, config)
    except ValueError as e:
        print(f"ERROR: {e}")
        return None

    # Determine generation name/number
    raw_dir = PROJECT_ROOT / config["paths"]["raw_assets"]
    if not generation_name:
        gen_num = get_next_generation_number(raw_dir)
        generation_name = f"generation_{gen_num:03d}"

    output_dir = raw_dir / generation_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generation: {generation_name}")
    print(f"Output: {output_dir}")
    print()

    # Create generation request
    request = GenerationRequest(
        reference_images=images,
        output_dir=output_dir,
        generation_name=generation_name,
    )

    # Run generation
    print("─" * 60)
    print("Starting 3D generation (this may take 2–5 minutes)...")
    print("─" * 60)
    print()

    result = provider.generate(request)

    # Log the result
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "provider": provider_name,
        "generation_name": generation_name,
        "success": result.success,
        "model_path": str(result.model_path) if result.model_path else None,
        "task_id": result.task_id,
        "error": result.error_message,
        "metadata": result.metadata,
        "reference_images": [str(p) for p in images],
    }

    log_path = output_dir / "generation_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2)

    # Report
    print()
    print("─" * 60)
    if result.success:
        print(f"✓ SUCCESS: {result.model_path}")
        print(f"  Provider: {provider_name}")
        print(f"  Task ID: {result.task_id}")
        print(f"  Log: {log_path}")
        print()
        print("Next steps:")
        print("  1. Run Blender import + validation")
        print("  2. Inspect in the 3D viewer")
        print("  3. If approved, run material setup + optimization")
    else:
        print(f"✗ FAILED: {result.error_message}")
        print(f"  Provider: {provider_name}")
        print(f"  Log: {log_path}")
        print()
        print("Troubleshooting:")
        print("  - Check your API key in pipeline/config.json")
        print("  - Check your internet connection")
        print("  - Try a different provider")

    print("─" * 60)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aurelia 3D AI Generation")
    parser.add_argument("--provider", type=str, help="Provider to use (meshy/tripo)")
    parser.add_argument("--name", type=str, help="Custom generation name")
    args = parser.parse_args()

    generate(provider_name=args.provider, generation_name=args.name)
