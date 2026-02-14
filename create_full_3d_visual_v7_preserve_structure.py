# Variant 7: Preserve Object Structure with Transforms
# This approach uses the `transform` parameter in add_geometry() to set the transform
# in the scene graph WITHOUT modifying the geometry itself.
#
# Key insight: scene.add_geometry(transform=...) sets the node's transform in the scene
# graph, which preserves the original geometry while still positioning it correctly.
#
# Expected outcome: 
# - Switches at correct positions (transforms applied via scene graph)
# - PCB orientation correct (transforms applied via scene graph)
# - Object structure preserved (geometries not modified)

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
OUTPUT_GLB = "./filtered-output/combined_scene_v7_preserve_structure.glb"

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

# Add PCB models with transforms preserved via scene graph
if isinstance(left_pcb_scene, trimesh.Scene):
    graph = left_pcb_scene.graph
    
    # Track which geometries we've already added to avoid duplicates
    added_geometries = set()
    
    # Iterate over all nodes in the scene graph
    for node_name in graph.nodes:
        # Get the world transform and geometry name for this node
        # graph.get(node_name) returns (transform_matrix, geometry_name)
        result = graph.get(node_name)
        
        if result is None:
            continue
        
        transform_matrix, geometry_name = result
        
        # Skip if there's no geometry associated with this node
        if geometry_name is None or geometry_name not in left_pcb_scene.geometry:
            continue
        
        # Skip if already added (some geometries may be referenced by multiple nodes)
        if geometry_name in added_geometries:
            continue
        
        # Get the geometry (DO NOT modify it - we'll use the transform parameter)
        geometry = left_pcb_scene.geometry[geometry_name]
        added_geometries.add(geometry_name)
        
        # Add to the combined scene with the transform set in the scene graph
        # This preserves the original geometry structure while applying the transform
        scene.add_geometry(
            geometry,
            node_name=f"Left_PCB_{node_name}",
            geom_name=f"Left_PCB_{geometry_name}",
            transform=transform_matrix  # Set transform in scene graph, not on geometry
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
print(f"  Variant: v7_preserve_structure (uses transform parameter to preserve object structure)")
print(f"  Left PCB: {LEFT_PCB_GLB}")
print(f"  Case: {CASE_STL}")
print(f"  L Cover: {L_COVER_STL}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
