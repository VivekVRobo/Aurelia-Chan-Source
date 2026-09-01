"""
Aurelia 3D Pipeline -- Blender Optimization
============================================
Optimizes the model for web delivery. Creates both desktop and mobile
variants with different polygon/texture budgets.

Important: This does NOT blindly decimate. It preserves detail in the
face and hands while reducing less important areas.

Usage (GUI mode):
    Run in Blender after import_validate.py and materials.py

Usage (headless):
    blender --background scaled.blend --python pipeline/blender/optimize.py
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


def optimize_model(target: str = "desktop"):
    """
    Optimize the current scene for web delivery.

    Args:
        target: "desktop" or "mobile" -- determines polygon/texture budgets
    """
    import bpy

    project_root = find_project_root()
    if not project_root:
        print("ERROR: Could not find project root.")
        return

    config_path = project_root / "pipeline" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    opt_config = config["optimization"][target]
    max_polys = opt_config["max_polygons"]
    max_tex = opt_config["max_texture_resolution"]
    max_mats = opt_config["max_materials"]

    print(f"\n============================================================")
    print(f"AURELIA 3D PIPELINE -- Optimization ({target})")
    print(f"============================================================")
    print(f"\nBudget: {max_polys} polys | {max_tex}px textures | {max_mats} materials")

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']

    # Step 1: Inventory
    print(f"\n[1/5] Current inventory:")
    total_verts = 0
    total_faces = 0
    for obj in mesh_objects:
        verts = len(obj.data.vertices)
        faces = len(obj.data.polygons)
        total_verts += verts
        total_faces += faces
        print(f"  {obj.name}: {verts} verts, {faces} faces")

    print(f"\n  Total: {total_verts} verts, {total_faces} faces")
    print(f"  Budget: {max_polys} faces")

    if total_faces <= max_polys:
        print(f"\n  [OK] Already within budget. No decimation needed.")
        reduction_needed = False
    else:
        reduction_needed = True
        reduction_ratio = max_polys / total_faces
        print(f"\n  Need to reduce by {(1 - reduction_ratio) * 100:.0f}%")

    # Step 2: Classify mesh importance
    print(f"\n[2/5] Classifying mesh importance...")

    importance_keywords = {
        "high": ["face", "head", "eye", "hair", "hand"],
        "medium": ["body", "torso", "arm", "leg", "blazer", "shirt"],
        "low": ["shoe", "heel", "belt", "accessory", "watch", "earring", "necklace"],
    }

    def get_importance(obj_name: str) -> str:
        name_lower = obj_name.lower()
        for level, keywords in importance_keywords.items():
            for kw in keywords:
                if kw in name_lower:
                    return level
        return "medium"

    importance_ratios = {
        "high": 0.95,
        "medium": 0.70,
        "low": 0.50,
    }

    for obj in mesh_objects:
        importance = get_importance(obj.name)
        print(f"  {obj.name}: {importance} priority")

    # Step 3: Decimate if needed
    if reduction_needed:
        print(f"\n[3/5] Applying importance-weighted decimation...")

        for obj in mesh_objects:
            importance = get_importance(obj.name)
            ratio = importance_ratios[importance]

            final_ratio = min(1.0, ratio * (reduction_ratio + (1 - reduction_ratio) * 0.3))

            if final_ratio >= 0.99:
                print(f"  {obj.name}: skipping (ratio {final_ratio:.2f})")
                continue

            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            mod_name = f"Decimate_{target}"
            if mod_name in obj.modifiers:
                obj.modifiers.remove(obj.modifiers[mod_name])

            modifier = obj.modifiers.new(name=mod_name, type='DECIMATE')
            modifier.decimate_type = 'COLLAPSE'
            modifier.ratio = final_ratio
            modifier.use_collapse_triangulate = False

            before_faces = len(obj.data.polygons)
            bpy.ops.object.modifier_apply(modifier=mod_name)
            after_faces = len(obj.data.polygons)

            print(f"  {obj.name}: {before_faces} -> {after_faces} faces ({importance}, ratio {final_ratio:.2f})")
    else:
        print(f"\n[3/5] Decimation skipped (within budget)")

    # Step 4: Remove invisible geometry
    print(f"\n[4/5] Checking for optimization opportunities...")

    for obj in mesh_objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)

        bpy.ops.object.mode_set(mode='OBJECT')

    print(f"  [OK] Cleaned loose geometry")

    # Step 5: Final report
    print(f"\n[5/5] Final polygon count:")

    final_verts = 0
    final_faces = 0
    for obj in mesh_objects:
        verts = len(obj.data.vertices)
        faces = len(obj.data.polygons)
        final_verts += verts
        final_faces += faces
        print(f"  {obj.name}: {verts} verts, {faces} faces")

    print(f"\n  Total: {final_verts} verts, {final_faces} faces")
    print(f"  Budget: {max_polys} faces")

    if final_faces <= max_polys:
        print(f"  [OK] Within {target} budget")
    else:
        print(f"  [WARN] Still over {target} budget by {final_faces - max_polys} faces")
        print(f"    Manual optimization may be needed for critical meshes")

    print(f"\n============================================================")
    print(f"Optimization ({target}) complete.")
    print(f"============================================================")


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    target = "desktop"
    for i, arg in enumerate(argv):
        if arg == "--target" and i + 1 < len(argv):
            target = argv[i + 1]

    optimize_model(target)
