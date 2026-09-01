"""
Aurelia 3D Pipeline — Reference Image Preparation
===================================================
Extracts clean character artwork from the annotated master sheets.
The master sheets contain measurements, guides, and text overlays that
would confuse AI 3D generation. This script crops out the clean character
artwork and prepares consistent reference images.

Usage:
    python pipeline/prepare_references.py
"""

import os
import sys
import json
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


# ─── Configuration ───────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "pipeline" / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

MASTER_SHEETS_DIR = PROJECT_ROOT / CONFIG["paths"]["master_sheets"]
OUTPUT_DIR = PROJECT_ROOT / CONFIG["paths"]["reference_images"]

# Target output size — AI services work best with consistent square-ish images
TARGET_SIZE = (1024, 1024)

# ─── Sheet-to-Reference Mapping ─────────────────────────────────────────────
# Each entry maps a master sheet to the region containing clean character art.
# Coordinates are (left, upper, right, lower) as fractions of image dimensions.
# These were determined by visual inspection of each sheet.

EXTRACTION_MAP = {
    "front": {
        "source": "Aurelia-Chan Master body blueprint sheet.png",
        "crop_fraction": (0.27, 0.04, 0.58, 0.80),
        "description": "Front view — neutral stance, full body"
    },
    "side": {
        "source": "Aurelia-Chan blueprint side look sheet.png",
        "crop_fraction": (0.25, 0.04, 0.55, 0.80),
        "description": "Side view — neutral stance, full body"
    },
    "back": {
        "source": "Aurelia-Chan blueprint backview look sheet.png",
        "crop_fraction": (0.27, 0.04, 0.58, 0.80),
        "description": "Back view — neutral stance, full body"
    },
    "three_quarter": {
        "source": "Aurelia-Chan Master Canon Sheet.png",
        "crop_fraction": (0.27, 0.02, 0.62, 0.48),
        "description": "3/4 front turnaround view"
    },
    "face_front": {
        "source": "Aurelia-Chan Master Canon Sheet.png",
        "crop_fraction": (0.68, 0.02, 0.82, 0.16),
        "description": "Face close-up — front view"
    },
    "full_body_front": {
        "source": "Aurelia-Chan full body blueprint.png",
        "crop_fraction": (0.20, 0.02, 0.65, 0.90),
        "description": "Full body front — alternative angle"
    }
}


def load_config():
    """Load and return the pipeline configuration."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_reference(name: str, spec: dict, output_dir: Path) -> Path | None:
    """
    Extract a clean reference image from an annotated master sheet.

    Args:
        name: Output name (e.g., 'front', 'side')
        spec: Extraction specification with source file and crop region
        output_dir: Directory to write the extracted image

    Returns:
        Path to the extracted image, or None if source not found
    """
    source_path = MASTER_SHEETS_DIR / spec["source"]

    if not source_path.exists():
        print(f"  ⚠ Source not found: {spec['source']}")
        return None

    print(f"  Extracting {name}: {spec['description']}")
    print(f"    Source: {spec['source']}")

    try:
        img = Image.open(source_path)
        w, h = img.size

        # Calculate crop box from fractional coordinates
        left_frac, top_frac, right_frac, bottom_frac = spec["crop_fraction"]
        crop_box = (
            int(w * left_frac),
            int(h * top_frac),
            int(w * right_frac),
            int(h * bottom_frac)
        )

        print(f"    Original: {w}x{h}px -> Crop: {crop_box}")

        # Crop the character artwork
        cropped = img.crop(crop_box)

        # Create a clean white background at target size
        # This gives AI services the neutral background they prefer
        output_img = Image.new("RGB", TARGET_SIZE, (255, 255, 255))

        # Fit the cropped image into the target size while preserving aspect ratio
        cropped_w, cropped_h = cropped.size
        scale = min(TARGET_SIZE[0] / cropped_w, TARGET_SIZE[1] / cropped_h) * 0.9
        new_w = int(cropped_w * scale)
        new_h = int(cropped_h * scale)

        cropped_resized = cropped.resize((new_w, new_h), Image.LANCZOS)

        # Center the character on the canvas
        paste_x = (TARGET_SIZE[0] - new_w) // 2
        paste_y = (TARGET_SIZE[1] - new_h) // 2
        output_img.paste(cropped_resized, (paste_x, paste_y))

        # Save
        output_path = output_dir / f"{name}.png"
        output_img.save(output_path, "PNG", quality=95)
        print(f"    Output: {output_path} ({new_w}x{new_h}px centered on {TARGET_SIZE[0]}x{TARGET_SIZE[1]})")

        return output_path
        
    except Exception as e:
        print(f"  ✗ Error processing {spec['source']}: {str(e)}")
        return None


def prepare_all_references():
    """
    Extract all reference images from master sheets.

    Returns:
        dict mapping reference name to output path
    """
    print("=" * 60)
    print("AURELIA 3D PIPELINE -- Reference Image Preparation")
    print("=" * 60)
    print()

    # Verify master sheets exist
    if not MASTER_SHEETS_DIR.exists():
        print(f"ERROR: Master sheets directory not found: {MASTER_SHEETS_DIR}")
        sys.exit(1)

    available_sheets = list(MASTER_SHEETS_DIR.glob("*.png"))
    print(f"Found {len(available_sheets)} master sheets in {MASTER_SHEETS_DIR.name}")
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Extract each reference
    results = {}
    for name, spec in EXTRACTION_MAP.items():
        result = extract_reference(name, spec, OUTPUT_DIR)
        if result:
            results[name] = str(result)
        print()

    # Write manifest
    manifest = {
        "prepared_at": str(Path(__file__).stat().st_mtime),
        "target_size": list(TARGET_SIZE),
        "references": results,
        "source_sheets": [s.name for s in available_sheets]
    }

    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("-" * 60)
    print(f"Prepared {len(results)}/{len(EXTRACTION_MAP)} reference images")
    print(f"Manifest: {manifest_path}")
    print()

    # Summary
    for name, path in results.items():
        print(f"  [OK] {name}: {path}")

    if len(results) < len(EXTRACTION_MAP):
        missing = set(EXTRACTION_MAP.keys()) - set(results.keys())
        for name in missing:
            print(f"  [FAIL] {name}: MISSING")

    print()
    return results


if __name__ == "__main__":
    prepare_all_references()
