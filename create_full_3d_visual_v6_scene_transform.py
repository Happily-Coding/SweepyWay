# Variant 6: Apply Transform to Scene Before Adding
# This approach applies a rotation transform to the entire PCB scene before
# extracting geometries.
#
# Key insight: If we apply a transform to the scene itself, all child nodes
# should inherit the transform. This can fix the PCB orientation issue.
#
# Expected outcome: PCB orientation corrected, but switches may still be stacked
# unless combined with another approach.

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
OUTPUT_GLB = "./filtered-output/combined_scene_v6_scene_transform.glb"

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

# Add PCB models with scene-level transform
if isinstance(left_pcb_scene, trimesh.Scene):
    # Apply a rotation to the entire PCB scene
    # This should affect all geometries in the scene
    # 
    # Common rotations to try:
    # - 180° around X-axis: np.pi, [1, 0, 0]
    # - 90° around X-axis: np.pi/2, [1, 0, 0]
    # - 180° around Z-axis: np.pi, [0, 0, 1]
    # - 90° around Y-axis: np.pi/2, [0, 1, 0]
    
    # Start with 180° around X-axis (common fix for KiCad exports)
    rotation_angle = np.pi  # 180 degrees
    rotation_axis = [1, 0, 0]  # X-axis
    
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=rotation_angle,
        direction=rotation_axis
    )
    
    # Apply the transform to the entire scene
    left_pcb_scene.apply_transform(rotation_matrix)
    
    print(f"  Applied rotation: {np.degrees(rotation_angle):.1f}° around {rotation_axis}")
    
    # Now add geometries - they should have the rotation applied
    # Note: This still has the issue of losing individual transforms
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
print(f"  Variant: v6_scene_transform (applies rotation to entire scene)")
print(f"  Left PCB: {LEFT_PCB_GLB}")
print(f"  Case: {CASE_STL}")
print(f"  L Cover: {L_COVER_STL}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
