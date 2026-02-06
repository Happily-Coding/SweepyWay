#TODO: recommend Per-object transforms (offset, rotation)
# https://gltf-viewer.donmccurdy.com/

import trimesh
import os

# -----------------------------
# Paths
# -----------------------------
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
RIGHT_PCB_GLB = "./filtered-output/pcbs/3d/right_pcb-3d.glb"
OUTPUT_GLB = "./filtered-output/combined_scene.glb"

# -----------------------------
# Load meshes
# -----------------------------
tenting_mesh = trimesh.load(TENTING_STL, force="mesh")
palm_mesh = trimesh.load(PALM_REST_STL, force="mesh")

# Load PCB 3D models (GLB format - already contains all components with materials)
# Use scene mode to preserve the structure, then extract geometry
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)
if isinstance(left_pcb_scene, trimesh.Scene):
    left_pcb_mesh = trimesh.util.concatenate(list(left_pcb_scene.geometry.values()))
else:
    left_pcb_mesh = left_pcb_scene

right_pcb_scene = trimesh.load(RIGHT_PCB_GLB)
if isinstance(right_pcb_scene, trimesh.Scene):
    right_pcb_mesh = trimesh.util.concatenate(list(right_pcb_scene.geometry.values()))
else:
    right_pcb_mesh = right_pcb_scene

# -----------------------------
# Create scene with named objects
# -----------------------------
scene = trimesh.Scene()

# Add PCB models (GLB files already have correct materials/colors)
scene.add_geometry(
    left_pcb_mesh,
    node_name="Left_PCB",
    geom_name="Left_PCB"
)

scene.add_geometry(
    right_pcb_mesh,
    node_name="Right_PCB",
    geom_name="Right_PCB"
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
print(f"  Right PCB: {RIGHT_PCB_GLB}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
