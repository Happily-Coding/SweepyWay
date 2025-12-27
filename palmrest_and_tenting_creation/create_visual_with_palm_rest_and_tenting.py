#TODO: recommend Per-object transforms (offset, rotation)
# https://gltf-viewer.donmccurdy.com/

import trimesh
import numpy as np

# -----------------------------
# Paths
# -----------------------------
TENTING_STL = "./filtered-output/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palm_rest.stl"
OUTPUT_GLB = "./filtered-output/combined_scene.glb"

# -----------------------------
# Load STL meshes
# -----------------------------
tenting_mesh = trimesh.load(TENTING_STL, force="mesh")
palm_mesh = trimesh.load(PALM_REST_STL, force="mesh")

# -----------------------------
# Assign colors (RGBA)
# -----------------------------
tenting_mesh.visual.vertex_colors = np.tile(
    [200, 60, 60, 255], (len(tenting_mesh.vertices), 1)
)

palm_mesh.visual.vertex_colors = np.tile(
    [60, 60, 200, 255], (len(palm_mesh.vertices), 1)
)

# -----------------------------
# Create scene with named objects
# -----------------------------
scene = trimesh.Scene()

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
