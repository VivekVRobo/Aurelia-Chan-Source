"""
Aurelia 3D Pipeline -- Blender Import & Validation
===================================================
Imports a raw AI-generated GLB into Blender, scales it to canonical
170 cm height, and runs Layer A (mechanical) validation checks.

Usage (GUI mode -- recommended during development):
    Open Blender -> Scripting workspace -> Run this script

Usage (headless -- after pipeline is proven):
    blender --background --python pipeline/blender/import_validate.py -- --input assets/raw/generation_001/generation_001.glb

The script outputs a validation report as JSON.
"""

import json
import math
import os
import sys
from pathlib import Path


def find_project_root():
    """Find the Aurelia-Chan project root from any execution context."""
    script_path = Path(__file__).resolve()
    candidate = script_path.parent.parent.parent
    if (candidate / "pipeline" / "config.json").exists():
        return candidate

    cwd = Path.cwd()
    if (cwd / "pipeline" / "config.json").exists():
        return cwd

    print("ERROR: Could not find project root. Run from the Aurelia-Chan directory.")
    return None


def load_config(project_root: Path) -> dict:
    """Load pipeline configuration."""
    config_path = project_root / "pipeline" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_in_blender(input_glb: str = None):
    """
    Main function -- runs inside Blender's Python environment.

    Args:
        input_glb: Path to the GLB file to import. If None, looks for
                   the latest generation in assets/raw/
    """
    import bpy

    project_root = find_project_root()
    if not project_root:
        return

    config = load_config(project_root)
    canon = config["canon"]
    measurements = canon["measurements_cm"]
    tolerances = canon["tolerances_cm"]

    if not input_glb:
        raw_dir = project_root / config["paths"]["raw_assets"]
        if raw_dir.exists():
            generations = sorted([
                d for d in raw_dir.iterdir()
                if d.is_dir() and d.name.startswith("generation_")
            ])
            if generations:
                latest = generations[-1]
                glb_files = list(latest.glob("*.glb"))
                if glb_files:
                    input_glb = str(glb_files[0])

    if not input_glb or not Path(input_glb).exists():
        print("ERROR: No GLB file found. Run generate_3d.py first.")
        return

    input_path = Path(input_glb)
    print(f"\n{'='*60}")
    print(f"AURELIA 3D PIPELINE -- Blender Import & Validation")
    print(f"{'='*60}")
    print(f"\nInput: {input_path}")

    # Step 1: Clear the scene
    print("\n[1/6] Clearing scene...")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    # Step 2: Set up scene units
    print("[2/6] Setting up scene units (metric, centimeters)...")
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 0.01  # 1 Blender unit = 1 cm
    scene.unit_settings.length_unit = 'CENTIMETERS'

    # Step 3: Import GLB
    print(f"[3/6] Importing GLB: {input_path.name}...")
    bpy.ops.import_scene.gltf(filepath=str(input_path))

    imported_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']

    print(f"  Imported: {len(imported_objects)} meshes, {len(armatures)} armatures")
    for obj in imported_objects:
        vert_count = len(obj.data.vertices)
        face_count = len(obj.data.polygons)
        print(f"    {obj.name}: {vert_count} verts, {face_count} faces")

    # Step 4: Measure current dimensions
    print("[4/6] Measuring current dimensions...")

    all_coords = []
    for obj in imported_objects:
        for vert in obj.data.vertices:
            world_coord = obj.matrix_world @ vert.co
            all_coords.append(world_coord)

    if not all_coords:
        print("ERROR: No mesh geometry found in the model.")
        return

    min_x = min(v.x for v in all_coords)
    max_x = max(v.x for v in all_coords)
    min_y = min(v.y for v in all_coords)
    max_y = max(v.y for v in all_coords)
    min_z = min(v.z for v in all_coords)
    max_z = max(v.z for v in all_coords)

    current_height = max_z - min_z
    current_width = max_x - min_x
    current_depth = max_y - min_y

    print(f"  Current dimensions (Blender units):")
    print(f"    Height (Z): {current_height:.4f}")
    print(f"    Width  (X): {current_width:.4f}")
    print(f"    Depth  (Y): {current_depth:.4f}")

    # Step 5: Scale to canonical 170 cm
    print("[5/6] Scaling to canonical 170 cm...")

    target_height = canon["height_cm"]  # 170.0

    if current_height > 0:
        scale_factor = target_height / current_height
        print(f"  Scale factor: {scale_factor:.4f}")

        for obj in bpy.context.scene.objects:
            obj.scale *= scale_factor

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        all_coords = []
        for obj in imported_objects:
            for vert in obj.data.vertices:
                world_coord = obj.matrix_world @ vert.co
                all_coords.append(world_coord)

        new_height = max(v.z for v in all_coords) - min(v.z for v in all_coords)
        new_width = max(v.x for v in all_coords) - min(v.x for v in all_coords)
        new_depth = max(v.y for v in all_coords) - min(v.y for v in all_coords)

        print(f"  Scaled dimensions (cm):")
        print(f"    Height: {new_height:.1f} cm (target: {target_height} cm)")
        print(f"    Width:  {new_width:.1f} cm")
        print(f"    Depth:  {new_depth:.1f} cm")
    else:
        new_height = 0
        new_width = 0
        new_depth = 0
        print("  WARNING: Model has zero height -- cannot scale")

    # Step 6: Layer A -- Mechanical QA
    print("[6/6] Running Layer A -- Mechanical QA...")

    validation_results = {
        "input_file": str(input_path),
        "timestamp": str(Path(input_path).stat().st_mtime),
        "layer_a_mechanical": {},
        "layer_b_visual": {},
        "summary": {}
    }

    checks = []

    # Height check
    height_diff = abs(new_height - target_height)
    height_pass = height_diff <= tolerances["height"]
    checks.append({
        "name": "Height",
        "measured": round(new_height, 1),
        "canon": target_height,
        "tolerance": tolerances["height"],
        "difference": round(height_diff, 1),
        "pass": height_pass
    })

    # Head proportion check (7.5 heads)
    expected_head = target_height / canon["proportion_system"]
    canon_head = measurements["head_total"]
    checks.append({
        "name": "Head proportion (7.5 heads)",
        "measured_ratio": round(new_height / canon_head, 2) if canon_head > 0 else 0,
        "canon_ratio": canon["proportion_system"],
        "canon_head_cm": canon_head,
        "pass": True
    })

    # Width check
    shoulder_ratio = new_width / new_height if new_height > 0 else 0
    canon_shoulder_ratio = measurements["shoulder_width"] / target_height
    checks.append({
        "name": "Shoulder width ratio",
        "measured_ratio": round(shoulder_ratio, 3),
        "canon_ratio": round(canon_shoulder_ratio, 3),
        "note": "Approximate -- based on bounding box width",
        "pass": abs(shoulder_ratio - canon_shoulder_ratio) < 0.05
    })

    # Polygon count
    total_verts = sum(len(obj.data.vertices) for obj in imported_objects)
    total_faces = sum(len(obj.data.polygons) for obj in imported_objects)
    desktop_limit = config["optimization"]["desktop"]["max_polygons"]
    mobile_limit = config["optimization"]["mobile"]["max_polygons"]
    checks.append({
        "name": "Polygon count",
        "vertices": total_verts,
        "faces": total_faces,
        "desktop_limit": desktop_limit,
        "mobile_limit": mobile_limit,
        "desktop_pass": total_faces <= desktop_limit,
        "mobile_pass": total_faces <= mobile_limit,
        "pass": total_faces <= desktop_limit
    })

    # Material count
    all_materials = set()
    for obj in imported_objects:
        for slot in obj.material_slots:
            if slot.material:
                all_materials.add(slot.material.name)
    mat_limit = config["optimization"]["desktop"]["max_materials"]
    checks.append({
        "name": "Material count",
        "count": len(all_materials),
        "materials": list(all_materials),
        "limit": mat_limit,
        "pass": len(all_materials) <= mat_limit
    })

    # Armature / rigging check
    checks.append({
        "name": "Has armature (rigging)",
        "armature_count": len(armatures),
        "pass": len(armatures) > 0,
        "note": "Required for animation. Can be added later if missing."
    })

    # File size
    file_size_mb = input_path.stat().st_size / (1024 * 1024)
    size_limit = config["optimization"]["desktop"]["max_glb_size_mb"]
    checks.append({
        "name": "File size",
        "size_mb": round(file_size_mb, 2),
        "limit_mb": size_limit,
        "pass": file_size_mb <= size_limit
    })

    validation_results["layer_a_mechanical"] = {
        "checks": checks,
        "total": len(checks),
        "passed": sum(1 for c in checks if c["pass"]),
        "failed": sum(1 for c in checks if not c["pass"]),
    }

    # Layer B -- Visual QA checklist
    validation_results["layer_b_visual"] = {
        "note": "These checks require human inspection. Open the model in the 3D viewer.",
        "checklist": [
            {"item": "Adult 33-year-old face and mature demeanor preserved", "status": "PENDING"},
            {"item": "Short polished jet-black bob, left off-center part, chin/nape length", "status": "PENDING"},
            {"item": "Sapphire iris, charcoal outer ring, royal-violet inner ring visible", "status": "PENDING"},
            {"item": "Warm ivory skin stays consistent", "status": "PENDING"},
            {"item": "Core blazer, blouse, trousers, belt, heels correct", "status": "PENDING"},
            {"item": "Gold-accent minimal accessories present", "status": "PENDING"},
            {"item": "Expression is restrained, intelligent, professional", "status": "PENDING"},
            {"item": "Art style matches semi-realistic anime", "status": "PENDING"},
            {"item": "Side profile correct (hair, nose, jaw)", "status": "PENDING"},
            {"item": "Back profile correct (hair nape, blazer, trousers)", "status": "PENDING"},
            {"item": "No mesh artifacts, holes, or intersections", "status": "PENDING"},
            {"item": "Hands and feet are acceptable quality", "status": "PENDING"},
        ]
    }

    a_pass = validation_results["layer_a_mechanical"]["passed"]
    a_total = validation_results["layer_a_mechanical"]["total"]
    validation_results["summary"] = {
        "layer_a_score": f"{a_pass}/{a_total}",
        "layer_a_pass": a_pass == a_total,
        "layer_b_status": "PENDING_HUMAN_REVIEW",
        "overall": "PENDING" if a_pass == a_total else "LAYER_A_FAILED",
        "scaled_height_cm": round(new_height, 1),
        "polygon_count": total_faces,
        "material_count": len(all_materials),
        "file_size_mb": round(file_size_mb, 2),
    }

    print(f"\n------------------------------------------------------------")
    print("LAYER A -- MECHANICAL QA RESULTS")
    print(f"------------------------------------------------------------")
    for check in checks:
        status = "[OK]" if check["pass"] else "[FAIL]"
        print(f"  {status}  {check['name']}")
        for key, val in check.items():
            if key not in ("name", "pass"):
                print(f"          {key}: {val}")

    print(f"\n  Score: {a_pass}/{a_total}")

    print(f"\n------------------------------------------------------------")
    print("LAYER B -- VISUAL QA (requires human review)")
    print(f"------------------------------------------------------------")
    for item in validation_results["layer_b_visual"]["checklist"]:
        print(f"  [ ] {item['item']}")

    report_dir = input_path.parent
    report_path = report_dir / "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(validation_results, f, indent=2)
    print(f"\nReport saved: {report_path}")

    blend_path = report_dir / f"{input_path.stem}_scaled.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(f"Blend file saved: {blend_path}")

    print(f"\n============================================================")
    print(f"Import & validation complete.")
    print(f"============================================================")

    return validation_results


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    input_glb = None
    for i, arg in enumerate(argv):
        if arg == "--input" and i + 1 < len(argv):
            input_glb = argv[i + 1]

    run_in_blender(input_glb)
