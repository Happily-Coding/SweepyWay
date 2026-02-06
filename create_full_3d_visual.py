#TODO: recommend Per-object transforms (offset, rotation)
# https://gltf-viewer.donmccurdy.com/

import trimesh
import numpy as np

# -----------------------------
# Paths
# -----------------------------
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_STEP = "./filtered-output/pcbs/3d/left_pcb-3d.step"
RIGHT_PCB_STEP = "./filtered-output/pcbs/3d/right_pcb-3d.step"
OUTPUT_GLB = "./filtered-output/combined_scene.glb"

# -----------------------------
# Load STL meshes
# -----------------------------
tenting_mesh = trimesh.load(TENTING_STL, force="mesh")
palm_mesh = trimesh.load(PALM_REST_STL, force="mesh")

# Load PCB 3D models (STEP format)
left_pcb_mesh = trimesh.load(LEFT_PCB_STEP, force="mesh")
right_pcb_mesh = trimesh.load(RIGHT_PCB_STEP, force="mesh")

# -----------------------------
# Assign colors (RGBA)
# -----------------------------
tenting_mesh.visual.vertex_colors = np.tile(
    [200, 60, 60, 255], (len(tenting_mesh.vertices), 1)
)

palm_mesh.visual.vertex_colors = np.tile(
    [60, 60, 200, 255], (len(palm_mesh.vertices), 1)
)

# Keep original colors for PCB models (they should have colors from KiCad)

# -----------------------------
# Create scene with named objects
# -----------------------------
scene = trimesh.Scene()

# Add PCB models
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
