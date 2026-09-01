"""
Aurelia 3D AI-Assisted Production Pipeline v0.1
=================================================
Master orchestrator that chains all pipeline steps.

Usage:
    python pipeline/run_pipeline.py                     # Full pipeline
    python pipeline/run_pipeline.py --step prepare      # Prepare references only
    python pipeline/run_pipeline.py --step generate     # AI generation only
    python pipeline/run_pipeline.py --step validate     # Validate latest GLB
    python pipeline/run_pipeline.py --provider tripo    # Use Tripo instead of Meshy
    python pipeline/run_pipeline.py --skip-generate     # Skip AI generation (use existing GLB)

Workflow:
    1. Prepare reference images from master sheets
    2. Generate 3D model via AI (Meshy/Tripo)
    3. Validate the generated model (Layer A: mechanical)
    4. Display results and instructions for Layer B (visual) review
    5. After human approval -> Blender processing, materials, optimization, export
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_config() -> dict:
    """Load pipeline configuration."""
    config_path = PROJECT_ROOT / "pipeline" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_header():
    """Print the pipeline header."""
    print()
    print("============================================================")
    print("    AURELIA 3D AI-ASSISTED PRODUCTION PIPELINE v0.1")
    print("    -------------------------------------------------")
    print("    Master Sheets -> AI 3D -> Blender -> GLB -> Viewer")
    print("============================================================")
    print()


def step_prepare():
    """Step 1: Prepare reference images from master sheets."""
    print("------------------------------------------------------------")
    print("  STEP 1/4 -- PREPARE REFERENCE IMAGES")
    print("------------------------------------------------------------")
    print()

    from pipeline.prepare_references import prepare_all_references
    results = prepare_all_references()

    if not results:
        print("[FAIL] FAILED: No reference images prepared")
        return False

    print(f"[OK] Prepared {len(results)} reference images")
    return True


def step_generate(provider_name: str = None):
    """Step 2: Generate 3D model using AI."""
    print("------------------------------------------------------------")
    print("  STEP 2/4 -- AI 3D GENERATION")
    print("------------------------------------------------------------")
    print()

    from pipeline.generate_3d import generate
    result = generate(provider_name=provider_name)

    if result and result.success:
        print(f"\n[OK] Model generated: {result.model_path}")
        return True
    else:
        error = result.error_message if result else "Unknown error"
        print(f"\n[FAIL] Generation failed: {error}")
        return False


def step_validate():
    """Step 3: Run canon validation on the latest GLB."""
    print("------------------------------------------------------------")
    print("  STEP 3/4 -- CANON VALIDATION")
    print("------------------------------------------------------------")
    print()

    from pipeline.validation.canon_checker import find_latest_glb, run_validation

    glb_path = find_latest_glb()
    if not glb_path:
        print("[FAIL] No GLB file found to validate")
        return False

    report = run_validation(glb_path)

    if report["summary"]["layer_a_pass"]:
        print(f"\n[OK] Layer A passed: {report['summary']['layer_a_score']}")
    else:
        print(f"\n[WARN] Layer A issues: {report['summary']['layer_a_score']}")

    return True


def step_review():
    """Step 4: Instructions for human review."""
    print("------------------------------------------------------------")
    print("  STEP 4/4 -- HUMAN REVIEW REQUIRED")
    print("------------------------------------------------------------")
    print()

    config = load_config()
    viewer_dir = PROJECT_ROOT / config["paths"]["viewer"]

    print("  The pipeline has completed automated processing.")
    print("  You now need to visually inspect the model.")
    print()
    print("  +-------------------------------------------+")
    print("  |  OPEN THE 3D VIEWER:                      |")
    print(f"  |  {viewer_dir / 'index.html'}")
    print("  |                                           |")
    print("  |  Then:                                    |")
    print("  |  1. Click 'Load aurelia.glb'              |")
    print("  |     (or drag-drop the raw GLB)            |")
    print("  |  2. Rotate the model 360 deg              |")
    print("  |  3. Check face, hair, eyes, body          |")
    print("  |  4. Compare against master sheets         |")
    print("  |  5. Check all Layer B items               |")
    print("  |  6. Click Approve or Reject               |")
    print("  +-------------------------------------------+")
    print()
    print("  If APPROVED:")
    print("    -> Run Blender scripts for materials + optimization + export")
    print()
    print("  If REJECTED:")
    print("    -> Re-run: python pipeline/run_pipeline.py --step generate")
    print("    -> Or correct in Blender GUI")
    print()

    return True


def run_pipeline(
    provider: str = None,
    step: str = None,
    skip_generate: bool = False
):
    """
    Run the full pipeline or a specific step.

    Args:
        provider: AI provider to use (meshy/tripo)
        step: Specific step to run (prepare/generate/validate/review)
        skip_generate: Skip the AI generation step (use existing GLB)
    """
    print_header()

    start_time = datetime.now()
    config = load_config()

    # Single step mode
    if step:
        steps = {
            "prepare": step_prepare,
            "generate": lambda: step_generate(provider),
            "validate": step_validate,
            "review": step_review,
        }
        if step not in steps:
            print(f"ERROR: Unknown step '{step}'. Available: {', '.join(steps.keys())}")
            return
        steps[step]()
        return

    # Full pipeline
    print(f"  Provider: {provider or config['provider']['active']}")
    print(f"  Skip generation: {skip_generate}")
    print()

    # Step 1: Prepare references
    if not step_prepare():
        print("\n[FAIL] Pipeline stopped: reference preparation failed")
        return
    print()

    # Step 2: AI generation
    if not skip_generate:
        if not step_generate(provider):
            print("\n[WARN] Pipeline continuing without new generation")
            print("  Will attempt to validate existing GLB files")
    else:
        print("------------------------------------------------------------")
        print("  STEP 2/4 -- SKIPPED (--skip-generate)")
        print("------------------------------------------------------------")
    print()

    # Step 3: Validate
    step_validate()
    print()

    # Step 4: Human review instructions
    step_review()

    # Timing
    elapsed = datetime.now() - start_time
    print(f"  Pipeline completed in {elapsed.total_seconds():.1f}s")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Aurelia 3D AI-Assisted Production Pipeline v0.1"
    )
    parser.add_argument(
        "--provider", type=str,
        help="AI provider to use (meshy/tripo)"
    )
    parser.add_argument(
        "--step", type=str,
        choices=["prepare", "generate", "validate", "review"],
        help="Run a specific step only"
    )
    parser.add_argument(
        "--skip-generate", action="store_true",
        help="Skip AI generation (use existing GLB)"
    )

    args = parser.parse_args()
    run_pipeline(
        provider=args.provider,
        step=args.step,
        skip_generate=args.skip_generate,
    )
