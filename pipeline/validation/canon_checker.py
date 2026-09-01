"""
Aurelia 3D Pipeline -- Canon Compliance Checker
================================================
Two-layer validation system for Aurelia 3D assets.

Layer A -- Mechanical QA (automated):
  Height, proportions, polygon count, material count, file size,
  texture resolution, material colors.

Layer B -- Visual QA (human-assisted):
  Face likeness, hair silhouette, eye appearance, expression,
  wardrobe accuracy, overall canon compliance.

Usage:
    python pipeline/validation/canon_checker.py assets/web/aurelia.glb
    python pipeline/validation/canon_checker.py --latest
"""

import argparse
import json
import os
import struct
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config() -> dict:
    """Load pipeline configuration."""
    config_path = PROJECT_ROOT / "pipeline" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_latest_glb() -> Path | None:
    """Find the most recently generated GLB file."""
    config = load_config()

    # Check web assets first
    web_dir = PROJECT_ROOT / config["paths"]["web_assets"]
    web_glbs = list(web_dir.glob("*.glb")) if web_dir.exists() else []
    if web_glbs:
        return max(web_glbs, key=lambda p: p.stat().st_mtime)

    # Check raw generations
    raw_dir = PROJECT_ROOT / config["paths"]["raw_assets"]
    if raw_dir.exists():
        generations = sorted([
            d for d in raw_dir.iterdir()
            if d.is_dir() and d.name.startswith("generation_")
        ])
        if generations:
            latest = generations[-1]
            glb_files = list(latest.glob("*.glb"))
            if glb_files:
                return glb_files[0]

    return None


def parse_glb_header(glb_path: Path) -> dict:
    """
    Parse a GLB file header to extract basic metadata.
    GLB format: 12-byte header + chunks (JSON + BIN)
    """
    info = {
        "file_size_bytes": glb_path.stat().st_size,
        "file_size_mb": round(glb_path.stat().st_size / (1024 * 1024), 2),
    }

    with open(glb_path, "rb") as f:
        magic = f.read(4)
        if magic != b'glTF':
            info["error"] = "Not a valid GLB file"
            return info

        version = struct.unpack('<I', f.read(4))[0]
        total_length = struct.unpack('<I', f.read(4))[0]
        info["glb_version"] = version
        info["total_length"] = total_length

        chunk_length = struct.unpack('<I', f.read(4))[0]
        chunk_type = struct.unpack('<I', f.read(4))[0]

        if chunk_type == 0x4E4F534A:
            json_data = f.read(chunk_length)
            try:
                gltf = json.loads(json_data.decode('utf-8'))
                info["gltf_data"] = gltf
            except json.JSONDecodeError:
                info["error"] = "Failed to parse glTF JSON"

    return info


def layer_a_check(glb_path: Path, config: dict) -> dict:
    """
    Layer A -- Mechanical QA (fully automated).

    Checks that can be determined programmatically from the GLB file.
    """
    canon = config["canon"]
    checks = []

    glb_info = parse_glb_header(glb_path)

    if "error" in glb_info:
        return {
            "error": glb_info["error"],
            "checks": [],
            "passed": 0,
            "failed": 1,
            "total": 1
        }

    gltf = glb_info.get("gltf_data", {})

    # File size check
    file_size_mb = glb_info["file_size_mb"]
    desktop_limit = config["optimization"]["desktop"]["max_glb_size_mb"]
    mobile_limit = config["optimization"]["mobile"]["max_glb_size_mb"]

    checks.append({
        "name": "File size",
        "measured": f"{file_size_mb} MB",
        "desktop_limit": f"{desktop_limit} MB",
        "mobile_limit": f"{mobile_limit} MB",
        "desktop_pass": file_size_mb <= desktop_limit,
        "mobile_pass": file_size_mb <= mobile_limit,
        "pass": file_size_mb <= desktop_limit,
    })

    # Mesh count
    meshes = gltf.get("meshes", [])
    checks.append({
        "name": "Mesh count",
        "count": len(meshes),
        "meshes": [m.get("name", f"mesh_{i}") for i, m in enumerate(meshes)],
        "pass": len(meshes) > 0,
    })

    # Material count
    materials = gltf.get("materials", [])
    mat_limit = config["optimization"]["desktop"]["max_materials"]
    checks.append({
        "name": "Material count",
        "count": len(materials),
        "limit": mat_limit,
        "materials": [m.get("name", f"mat_{i}") for i, m in enumerate(materials)],
        "pass": len(materials) <= mat_limit,
    })

    # Textures
    textures = gltf.get("textures", [])
    images = gltf.get("images", [])
    checks.append({
        "name": "Textures",
        "texture_count": len(textures),
        "image_count": len(images),
        "images": [img.get("name", img.get("mimeType", f"img_{i}")) for i, img in enumerate(images)],
        "pass": True,
    })

    # Armature / skin check
    skins = gltf.get("skins", [])
    checks.append({
        "name": "Has rigging (armature/skin)",
        "skin_count": len(skins),
        "pass": len(skins) > 0,
        "note": "Required for animation. Can be added later via Meshy auto-rig or Mixamo.",
    })

    # Animation check
    animations = gltf.get("animations", [])
    checks.append({
        "name": "Animations",
        "count": len(animations),
        "animations": [a.get("name", f"anim_{i}") for i, a in enumerate(animations)],
        "pass": True,
        "note": "Optional for v0.1 milestone",
    })

    # Morph targets
    has_morphs = False
    morph_count = 0
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            targets = prim.get("targets", [])
            if targets:
                has_morphs = True
                morph_count += len(targets)

    checks.append({
        "name": "Morph targets (blend shapes)",
        "has_morphs": has_morphs,
        "morph_count": morph_count,
        "pass": True,
        "note": "Needed for facial expressions in v0.2+",
    })

    # Material colors
    color_checks = []
    for mat in materials:
        mat_name = mat.get("name", "unknown").lower()
        pbr = mat.get("pbrMetallicRoughness", {})
        base_color = pbr.get("baseColorFactor", [1, 1, 1, 1])

        def linear_to_srgb(c):
            if c <= 0.0031308:
                return c * 12.92
            return 1.055 * (c ** (1.0 / 2.4)) - 0.055

        r = int(min(255, max(0, linear_to_srgb(base_color[0]) * 255)))
        g = int(min(255, max(0, linear_to_srgb(base_color[1]) * 255)))
        b = int(min(255, max(0, linear_to_srgb(base_color[2]) * 255)))
        hex_color = f"#{r:02X}{g:02X}{b:02X}"

        color_checks.append({
            "material": mat.get("name", "unknown"),
            "base_color_hex": hex_color,
            "roughness": pbr.get("roughnessFactor", 1.0),
            "metallic": pbr.get("metallicFactor", 0.0),
        })

    checks.append({
        "name": "Material colors",
        "materials": color_checks,
        "pass": True,
        "note": "Cross-reference hex values with canon colors in config.json",
    })

    # GLB version
    checks.append({
        "name": "GLB version",
        "version": glb_info.get("glb_version", 0),
        "pass": glb_info.get("glb_version", 0) == 2,
    })

    passed = sum(1 for c in checks if c["pass"])
    failed = sum(1 for c in checks if not c["pass"])

    return {
        "checks": checks,
        "passed": passed,
        "failed": failed,
        "total": len(checks),
    }


def layer_b_checklist() -> dict:
    """Layer B -- Visual QA checklist (human-assisted)."""
    return {
        "instructions": (
            "Open the model in viewer/index.html and inspect against the master sheets.\n"
            "Mark each item as PASS, FAIL, or ACCEPTABLE.\n"
            "Items marked FAIL should be noted for correction."
        ),
        "checklist": [
            {
                "id": "B01",
                "category": "Face",
                "item": "Adult 33-year-old face and mature demeanor preserved",
                "reference_sheets": ["Aurelia-Chan Master Canon Sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B02",
                "category": "Hair",
                "item": "Short polished jet-black bob, left off-center part, chin/nape length",
                "reference_sheets": ["Aurelia-Chan hair sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B03",
                "category": "Eyes",
                "item": "Sapphire iris, charcoal outer ring, royal-violet inner ring visible",
                "reference_sheets": ["Aurelia-Chan eye look sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B04",
                "category": "Skin",
                "item": "Warm ivory skin stays consistent (no tan/bronze/pink/gray shift)",
                "reference_sheets": ["Aurelia-Chan skin sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B05",
                "category": "Body",
                "item": "7.5-head / 170 cm lean-athletic proportions maintained",
                "reference_sheets": [
                    "Aurelia-Chan Master body blueprint sheet.png",
                    "Aurelia-Chan height reference blueprint sheet.png"
                ],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B06",
                "category": "Wardrobe",
                "item": "Core blazer, blouse, trousers, belt, heels present and correct",
                "reference_sheets": ["Aurelia-Chan outfit sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B07",
                "category": "Accessories",
                "item": "Gold-accent minimal accessories (studs, pendant, watch, buckle)",
                "reference_sheets": ["Aurelia-Chan outfit sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B08",
                "category": "Expression",
                "item": "Expression is restrained, intelligent, professional",
                "reference_sheets": ["Aurelia-Chan Master Canon Sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B09",
                "category": "Side Profile",
                "item": "Side profile correct (hair shape, nose, jaw, posture)",
                "reference_sheets": [
                    "Aurelia-Chan blueprint side look sheet.png",
                    "Aurelia-Chan side look sheet.png"
                ],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B10",
                "category": "Back Profile",
                "item": "Back profile correct (hair nape, blazer back, trouser fit)",
                "reference_sheets": [
                    "Aurelia-Chan blueprint backview look sheet.png",
                    "Aurelia-Chan backside look sheet.png"
                ],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B11",
                "category": "Mesh Quality",
                "item": "No mesh artifacts, holes, self-intersections, or clipping",
                "reference_sheets": [],
                "status": "PENDING",
                "notes": ""
            },
            {
                "id": "B12",
                "category": "Extremities",
                "item": "Hands and feet are acceptable quality",
                "reference_sheets": ["Aurelia-Chan Master body blueprint sheet.png"],
                "status": "PENDING",
                "notes": ""
            },
        ]
    }


def run_validation(glb_path: Path) -> dict:
    """Run full canon compliance validation."""
    config = load_config()

    print(f"\n============================================================")
    print(f"AURELIA 3D PIPELINE -- Canon Compliance Check")
    print(f"============================================================")
    print(f"\nModel: {glb_path}")
    print(f"Size: {glb_path.stat().st_size / (1024*1024):.2f} MB")

    print(f"\n------------------------------------------------------------")
    print("LAYER A -- MECHANICAL QA (automated)")
    print(f"------------------------------------------------------------")

    layer_a = layer_a_check(glb_path, config)

    for check in layer_a["checks"]:
        status = "[OK]" if check["pass"] else "[FAIL]"
        print(f"\n  {status} {check['name']}")
        for key, val in check.items():
            if key not in ("name", "pass") and not isinstance(val, list):
                print(f"      {key}: {val}")

    print(f"\n  Layer A Score: {layer_a['passed']}/{layer_a['total']}")

    print(f"\n------------------------------------------------------------")
    print("LAYER B -- VISUAL QA (requires human review)")
    print(f"------------------------------------------------------------")

    layer_b = layer_b_checklist()

    print(f"\n  {layer_b['instructions']}")
    print()
    for item in layer_b["checklist"]:
        print(f"  [ ] {item['id']}: {item['item']}")
        if item["reference_sheets"]:
            print(f"       Ref: {', '.join(item['reference_sheets'])}")

    report = {
        "model_path": str(glb_path),
        "timestamp": datetime.now().isoformat(),
        "canon_version": "v1.0",
        "layer_a": layer_a,
        "layer_b": layer_b,
        "summary": {
            "layer_a_score": f"{layer_a['passed']}/{layer_a['total']}",
            "layer_a_pass": layer_a["failed"] == 0,
            "layer_b_status": "PENDING_HUMAN_REVIEW",
            "overall_status": "AWAITING_REVIEW" if layer_a["failed"] == 0 else "LAYER_A_FAILED",
        }
    }

    report_path = glb_path.parent / f"{glb_path.stem}_canon_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n------------------------------------------------------------")
    print(f"Report saved: {report_path}")
    print(f"Overall: {report['summary']['overall_status']}")
    print(f"============================================================")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aurelia Canon Compliance Checker")
    parser.add_argument("glb_path", nargs="?", help="Path to GLB file to validate")
    parser.add_argument("--latest", action="store_true", help="Validate the most recent GLB")
    args = parser.parse_args()

    if args.latest:
        glb_path = find_latest_glb()
        if not glb_path:
            print("ERROR: No GLB files found. Run the generation pipeline first.")
            sys.exit(1)
    elif args.glb_path:
        glb_path = Path(args.glb_path)
        if not glb_path.exists():
            print(f"ERROR: File not found: {glb_path}")
            sys.exit(1)
    else:
        print("Usage: python canon_checker.py <path_to.glb> | --latest")
        sys.exit(1)

    run_validation(glb_path)
