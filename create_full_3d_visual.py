#TODO: recommend Per-object transforms (offset, rotation)
# https://gltf-viewer.donmccurdy.com/

import trimesh
import os

# -----------------------------
# Paths
# -----------------------------
CASE_STL = "./filtered-output/cases/case.stl"
L_COVER_STL = "./filtered-output/cases/l_cover.stl"
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
#RIGHT_PCB_GLB = "./filtered-output/pcbs/3d/right_pcb-3d.glb" # Commented sicne it makes no sens to create only the right pcb and not the right everythig else too
OUTPUT_GLB = "./filtered-output/combined_scene.glb"

# -----------------------------
# Load meshes
# -----------------------------
# Load case and handrest models from OpenJSCAD exports
case_mesh = trimesh.load(CASE_STL, force="mesh")
l_cover_mesh = trimesh.load(L_COVER_STL, force="mesh")

tenting_mesh = trimesh.load(TENTING_STL, force="mesh")
palm_mesh = trimesh.load(PALM_REST_STL, force="mesh")

# Load PCB 3D models (GLB format - already contains all components with materials)
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)

#right_pcb_scene = trimesh.load(RIGHT_PCB_GLB)
#if isinstance(right_pcb_scene, trimesh.Scene):
#    right_pcb_mesh = trimesh.util.concatenate(list(right_pcb_scene.geometry.values()))
#else:
#    right_pcb_mesh = right_pcb_scene

# -----------------------------
# Create scene with named objects
# -----------------------------
scene = trimesh.Scene()

# Add PCB models (GLB files already have correct materials/colors)
# Preserve scene structure to maintain all transforms and prevent switch merging
if isinstance(left_pcb_scene, trimesh.Scene):
    # Add each geometry from the PCB scene to the combined scene
    # This preserves all transforms from the original GLB file
    for node_name, geometry in left_pcb_scene.geometry.items():
        scene.add_geometry(
            geometry,
            node_name=f"Left_PCB_{node_name}",
            geom_name=f"Left_PCB_{node_name}"
        )
else:
    # Fallback for non-scene files
    scene.add_geometry(
        left_pcb_scene,
        node_name="Left_PCB",
        geom_name="Left_PCB"
    )

#scene.add_geometry(
#    right_pcb_mesh,
#    node_name="Right_PCB",
#    geom_name="Right_PCB"
#)

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
print(f"  Left PCB: {LEFT_PCB_GLB}")
#print(f"  Right PCB: {RIGHT_PCB_GLB}")
print(f"  Case: {CASE_STL}")
print(f"  L Cover: {L_COVER_STL}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
