# Variant 5: Export and Re-import
# This approach exports the PCB scene to bytes and re-imports it as a single mesh
# with all transforms baked in.
#
# Key insight: When exporting a scene to GLB and re-importing, trimesh should
# apply all transforms to the geometry vertices, effectively "baking" them in.
#
# Expected outcome: All transforms baked into geometry, correct positions

import trimesh
import numpy as np
import os
import io

# -----------------------------
# Paths
# -----------------------------
CASE_STL = "./filtered-output/cases/case.stl"
L_COVER_STL = "./filtered-output/cases/l_cover.stl"
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
OUTPUT_GLB = "./filtered-output/combined_scene_v5_reexport.glb"

# -----------------------------
# Load meshes
# -----------------------------
case_mesh = trimesh.load(CASE_STL, force="mesh")
l_cover_mesh = trimesh.load(L_COVER_STL, force="mesh")
tenting_mesh = trimesh.load(TENTING_STL, force="mesh")
palm_mesh = trimesh.load(PALM_REST_STL, force="mesh")

# Load PCB 3D models (GLB format - already contains all components with materials)
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)

# -----------------------------
# Create scene with named objects
# -----------------------------
scene = trimesh.Scene()

# Add PCB models using re-export approach
if isinstance(left_pcb_scene, trimesh.Scene):
    # Export the PCB scene to a bytes buffer
    # This should bake all transforms into the geometry
    try:
        # Export to GLB format (binary glTF)
        glb_bytes = left_pcb_scene.export(file_type='glb')
        
        # Handle different return types from export
        if isinstance(glb_bytes, dict):
            # Some versions return a dict, we need to get the binary data
            # Try common keys
            if 'model' in glb_bytes:
                glb_bytes = glb_bytes['model']
            elif 'gltf' in glb_bytes:
                glb_bytes = glb_bytes['gltf']
            else:
                # Get first value from dict
                glb_bytes = list(glb_bytes.values())[0]
        
        # Ensure we have bytes
        if not isinstance(glb_bytes, (bytes, bytearray)):
            raise ValueError(f"Export returned unexpected type: {type(glb_bytes)}")
        
        # Re-import from the bytes buffer
        # Use force='mesh' to get a single mesh with transforms applied
        pcb_mesh = trimesh.load(
            io.BytesIO(glb_bytes),
            file_type='glb',
            force='mesh'
        )
        
        scene.add_geometry(
            pcb_mesh,
            node_name="Left_PCB",
            geom_name="Left_PCB"
        )
        
        print(f"  Re-export approach successful")
    except Exception as e:
        print(f"  Warning: Re-export failed: {e}")
        print(f"  Falling back to concatenate approach")
        
        # Fallback: concatenate all geometries
        # Note: This won't have transforms applied
        all_geometries = list(left_pcb_scene.geometry.values())
        if all_geometries:
            pcb_mesh = trimesh.util.concatenate(all_geometries)
            scene.add_geometry(
                pcb_mesh,
                node_name="Left_PCB",
                geom_name="Left_PCB"
            )
else:
    # Fallback for non-scene files
    scene.add_geometry(
        left_pcb_scene,
        node_name="Left_PCB",
        geom_name="Left_PCB"
    )

# Add case and cover models
scene.add_geometry(
    case_mesh,
    node_name="Case",
    geom_name="Case"
)

scene.add_geometry(
    l_cover_mesh,
    node_name="L_Cover",
    geom_name="L_Cover"
)

# Add tenting and palm rest
scene.add_geometry(
    tenting_mesh,
    node_name="Tenting_System",
    geom_name="Tenting_System"
)

scene.add_geometry(
    palm_mesh,
    node_name="Palm_Rest",
    geom_name="Palm_Rest"
)

# -----------------------------
# Export GLB
# -----------------------------
scene.export(OUTPUT_GLB)

print(f"GLB scene saved to: {OUTPUT_GLB}")
print(f"  Variant: v5_reexport (exports and re-imports to bake transforms)")
print(f"  Left PCB: {LEFT_PCB_GLB}")
print(f"  Case: {CASE_STL}")
print(f"  L Cover: {L_COVER_STL}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
