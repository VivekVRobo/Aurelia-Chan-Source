"""
Aurelia 3D Pipeline -- Blender GLB Export
=========================================
Exports the processed model as a web-ready GLB file with
Draco compression and embedded textures.

Usage (GUI mode):
    Run in Blender after optimization

Usage (headless):
    blender --background processed.blend --python pipeline/blender/export.py -- --target desktop
"""

import json
import sys
from pathlib import Path


def find_project_root():
    """Find the Aurelia-Chan project root."""
    script_path = Path(__file__).resolve()
    candidate = script_path.parent.parent.parent
    if (candidate / "pipeline" / "config.json").exists():
        return candidate
    cwd = Path.cwd()
    if (cwd / "pipeline" / "config.json").exists():
        return cwd
    return None


def export_glb(target: str = "desktop", output_name: str = None):
    """
    Export the current Blender scene as a GLB file.

    Args:
        target: "desktop" or "mobile" -- determines output directory name
        output_name: Custom output filename (without extension)
    """
    import bpy

    project_root = find_project_root()
    if not project_root:
        print("ERROR: Could not find project root.")
        return

    config_path = project_root / "pipeline" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    web_dir = project_root / config["paths"]["web_assets"]
    web_dir.mkdir(parents=True, exist_ok=True)

    if not output_name:
        if target == "mobile":
            output_name = "aurelia_mobile"
        else:
            output_name = "aurelia"

    output_path = web_dir / f"{output_name}.glb"

    print(f"\n============================================================")
    print(f"AURELIA 3D PIPELINE -- GLB Export ({target})")
    print(f"============================================================")
    print(f"\nOutput: {output_path}")

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']

    total_faces = sum(len(obj.data.polygons) for obj in mesh_objects)
    all_materials = set()
    for obj in mesh_objects:
        for slot in obj.material_slots:
            if slot.material:
                all_materials.add(slot.material.name)

    print(f"\nScene contents:")
    print(f"  Meshes: {len(mesh_objects)}")
    print(f"  Armatures: {len(armatures)}")
    print(f"  Total faces: {total_faces}")
    print(f"  Materials: {len(all_materials)}")

    bpy.ops.object.select_all(action='SELECT')

    print(f"\nExporting GLB...")

    export_settings = {
        "filepath": str(output_path),
        "check_existing": False,
        "export_format": "GLB",
        "use_selection": False,
        "use_visible": True,
        "use_active_collection": False,
        "export_yup": True,
        "export_apply": True,
        "export_texcoords": True,
        "export_normals": True,
        "export_tangents": True,
        "export_colors": True,
        "export_draco_mesh_compression_enable": True,
        "export_draco_mesh_compression_level": 6,
        "export_draco_position_quantization": 14,
        "export_draco_normal_quantization": 10,
        "export_draco_texcoord_quantization": 12,
        "export_draco_color_quantization": 10,
        "export_materials": "EXPORT",
        "export_image_format": "AUTO",
        "export_animations": len(armatures) > 0,
        "export_morph": True,
        "export_morph_normal": True,
        "export_skins": len(armatures) > 0,
        "export_all_influences": False,
        "export_extras": True,
        "export_cameras": False,
        "export_lights": False,
    }

    try:
        bpy.ops.export_scene.gltf(**export_settings)
        print(f"  [OK] Export successful")
    except Exception as e:
        print(f"  [FAIL] Export failed: {e}")
        print(f"  Retrying without Draco compression...")
        export_settings["export_draco_mesh_compression_enable"] = False
        try:
            bpy.ops.export_scene.gltf(**export_settings)
            print(f"  [OK] Export successful (without Draco)")
        except Exception as e2:
            print(f"  [FAIL] Export failed again: {e2}")
            return None

    if output_path.exists():
        file_size = output_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        max_size = config["optimization"][target]["max_glb_size_mb"]

        print(f"\n------------------------------------------------------------")
        print(f"Export Report:")
        print(f"  File: {output_path}")
        print(f"  Size: {size_mb:.2f} MB (budget: {max_size} MB)")
        print(f"  Faces: {total_faces}")
        print(f"  Materials: {len(all_materials)}")

        if size_mb <= max_size:
            print(f"  [OK] Within {target} size budget")
        else:
            print(f"  [WARN] Over {target} size budget by {size_mb - max_size:.2f} MB")

        print(f"\n============================================================")
        print(f"GLB export complete.")
        print(f"============================================================")

        return output_path
    else:
        print(f"\n  [FAIL] Output file not found after export")
        return None


def export_and_approve(target: str = "desktop", version: str = "v001"):
    """Export and copy to the approved assets directory."""
    import bpy
    import shutil

    output_path = export_glb(target)

    if output_path and output_path.exists():
        project_root = find_project_root()
        if project_root:
            approved_dir = project_root / "assets" / "approved"
            approved_dir.mkdir(parents=True, exist_ok=True)
            approved_path = approved_dir / f"aurelia_{version}.glb"
            shutil.copy2(output_path, approved_path)
            print(f"\n  [OK] Approved copy: {approved_path}")


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    target = "desktop"
    output_name = None
    approve = False

    for i, arg in enumerate(argv):
        if arg == "--target" and i + 1 < len(argv):
            target = argv[i + 1]
        elif arg == "--name" and i + 1 < len(argv):
            output_name = argv[i + 1]
        elif arg == "--approve":
            approve = True

    if approve:
        export_and_approve(target)
    else:
        export_glb(target, output_name)
