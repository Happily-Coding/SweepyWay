# Variant 9: Use Scene Addition/Merge
# This approach uses trimesh's scene addition operator to merge scenes.
# This should preserve the entire scene graph structure from the PCB.
#
# Key insight: Instead of extracting geometries, we can merge scenes directly
# using the + operator or by creating a combined scene.
#
# Expected outcome:
# - Switches at correct positions
# - PCB orientation correct
# - Object structure preserved (node names preserved)

import trimesh
import numpy as np
import os

# -----------------------------
# Paths
# -----------------------------
CASE_STL = "./filtered-output/cases/case.stl"
L_COVER_STL = "./filtered-output/cases/l_cover.stl"
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
OUTPUT_GLB = "./filtered-output/combined_scene_v9_scene_add.glb"

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

# Add case and cover models first
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

# Add PCB scene using scene addition
# This should preserve the entire scene graph structure
if isinstance(left_pcb_scene, trimesh.Scene):
    # Try using the + operator to merge scenes
    # This should preserve all node names and transforms
    try:
        combined_scene = scene + left_pcb_scene
        combined_scene.export(OUTPUT_GLB)
        print(f"GLB scene saved to: {OUTPUT_GLB}")
        print(f"  Variant: v9_scene_add (uses scene + operator)")
        print(f"  Left PCB: {LEFT_PCB_GLB}")
        print(f"  Case: {CASE_STL}")
        print(f"  L Cover: {L_COVER_STL}")
        print(f"  Tenting: {TENTING_STL}")
        print(f"  Palm Rest: {PALM_REST_STL}")
    except Exception as e:
        print(f"  Scene addition failed: {e}")
        print(f"  Falling back to geometry iteration...")
        # Fallback to v3 approach
        pcb_mesh = left_pcb_scene.to_mesh()
        scene.add_geometry(
            pcb_mesh,
            node_name="Left_PCB",
            geom_name="Left_PCB"
        )
        scene.export(OUTPUT_GLB)
        print(f"GLB scene saved to: {OUTPUT_GLB}")
        print(f"  Variant: v9_scene_add (fallback to to_mesh)")
else:
    # Fallback for non-scene files
    scene.add_geometry(
        left_pcb_scene,
        node_name="Left_PCB",
        geom_name="Left_PCB"
    )
    scene.export(OUTPUT_GLB)
    print(f"GLB scene saved to: {OUTPUT_GLB}")
    print(f"  Variant: v9_scene_add (non-scene fallback)")
