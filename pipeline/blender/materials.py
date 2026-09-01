"""
Aurelia 3D Pipeline -- Blender Material Setup
==============================================
Creates and assigns PBR materials based on canonical colors from the
Character Bible. Each material uses Blender's Principled BSDF shader.

Usage (GUI mode):
    Open the scaled .blend file -> Scripting -> Run this script

Usage (headless):
    blender --background scaled.blend --python pipeline/blender/materials.py
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


def hex_to_linear(hex_color: str) -> tuple:
    """
    Convert a hex color string to linear RGB values for Blender.
    Blender's Principled BSDF expects linear color space.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    def srgb_to_linear(c):
        if c <= 0.04045:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


def create_canon_material(name: str, mat_config: dict) -> 'bpy.types.Material':
    """
    Create a Principled BSDF material from canonical configuration.

    Args:
        name: Material name (e.g., 'Aurelia_Skin')
        mat_config: Material config dict with base_color, roughness, etc.

    Returns:
        Blender Material object
    """
    import bpy

    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)

    links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

    base_color = hex_to_linear(mat_config["base_color"])
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = mat_config.get("roughness", 0.5)
    bsdf.inputs['Metallic'].default_value = mat_config.get("metallic", 0.0)

    specular = mat_config.get("specular", 0.5)
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = specular
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = specular

    if "subsurface" in mat_config:
        subsurface_val = mat_config["subsurface"]
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = subsurface_val
        elif 'Subsurface' in bsdf.inputs:
            bsdf.inputs['Subsurface'].default_value = subsurface_val

        if "subsurface_color" in mat_config:
            ss_color = hex_to_linear(mat_config["subsurface_color"])
            if 'Subsurface Color' in bsdf.inputs:
                bsdf.inputs['Subsurface Color'].default_value = ss_color

    if "sheen" in mat_config:
        sheen_val = mat_config["sheen"]
        if 'Sheen Weight' in bsdf.inputs:
            bsdf.inputs['Sheen Weight'].default_value = sheen_val
        elif 'Sheen' in bsdf.inputs:
            bsdf.inputs['Sheen'].default_value = sheen_val

    print(f"  [OK] Created material: {name}")
    print(f"    Base Color: {mat_config['base_color']} | Roughness: {mat_config.get('roughness', 0.5):.2f} | Metallic: {mat_config.get('metallic', 0.0):.2f}")

    return mat


def setup_all_materials():
    """
    Create all canonical materials and attempt to assign them
    to appropriate mesh objects based on naming heuristics.
    """
    import bpy

    project_root = find_project_root()
    if not project_root:
        print("ERROR: Could not find project root.")
        return

    config_path = project_root / "pipeline" / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    materials_config = config["materials"]

    print(f"\n============================================================")
    print("AURELIA 3D PIPELINE -- Material Setup")
    print(f"============================================================\n")

    canon_materials = {}
    for mat_name, mat_config in materials_config.items():
        full_name = f"Aurelia_{mat_name.title()}"
        canon_materials[mat_name] = create_canon_material(full_name, mat_config)

    print(f"\nCreated {len(canon_materials)} canonical materials.")

    print(f"\n------------------------------------------------------------")
    print("Attempting material assignment...")
    print(f"------------------------------------------------------------\n")

    keyword_map = {
        "skin": "skin",
        "face": "skin",
        "body": "skin",
        "hand": "skin",
        "arm": "skin",
        "leg": "skin",
        "neck": "skin",
        "head": "skin",

        "hair": "hair",

        "blazer": "blazer",
        "jacket": "blazer",
        "coat": "blazer",
        "suit": "blazer",

        "shirt": "shirt",
        "blouse": "shirt",
        "top": "shirt",

        "trouser": "trousers",
        "pant": "trousers",
        "bottom": "trousers",

        "belt": "belt",
        "strap": "belt",

        "shoe": "heels",
        "heel": "heels",
        "boot": "heels",
        "foot": "heels",

        "gold": "gold",
        "buckle": "gold",
        "earring": "gold",
        "necklace": "gold",
        "pendant": "gold",
        "jewelry": "gold",
        "accessory": "gold",

        "watch": "watch_face",

        "eye": "eye_iris",
        "iris": "eye_iris",
        "pupil": "eye_iris",
    }

    assigned_count = 0
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue

        obj_name_lower = obj.name.lower()

        matched_material = None
        for keyword, mat_key in keyword_map.items():
            if keyword in obj_name_lower:
                matched_material = mat_key
                break

        if not matched_material:
            for slot in obj.material_slots:
                if slot.material:
                    slot_name_lower = slot.material.name.lower()
                    for keyword, mat_key in keyword_map.items():
                        if keyword in slot_name_lower:
                            matched_material = mat_key
                            break
                    if matched_material:
                        break

        if matched_material and matched_material in canon_materials:
            if obj.material_slots:
                obj.material_slots[0].material = canon_materials[matched_material]
            else:
                obj.data.materials.append(canon_materials[matched_material])
            print(f"  [OK] {obj.name} -> Aurelia_{matched_material.title()}")
            assigned_count += 1
        else:
            print(f"  [-] {obj.name} -> no match (manual assignment needed)")

    print(f"\nAssigned {assigned_count} materials automatically.")
    print(f"Remaining objects may need manual material assignment in Blender GUI.")

    print(f"\n------------------------------------------------------------")
    print("Setting viewport to Material Preview mode...")

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    break

    print(f"\n============================================================")
    print("Material setup complete.")
    print("Inspect the result in Blender's viewport.")
    print(f"============================================================")


if __name__ == "__main__":
    setup_all_materials()
