# Variant 2: Use Scene Graph Transforms
# This approach gets transforms from the scene graph and applies them to geometries.
#
# Key insight: In trimesh, transforms are stored in scene.graph, not in geometry objects.
# We need to get the transform for each node and apply it before adding to the scene.
#
# Expected outcome: Switches at correct positions, PCB orientation may need adjustment

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
OUTPUT_GLB = "./filtered-output/combined_scene_v2_graph_transforms.glb"

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

# Add PCB models with transforms from the scene graph
if isinstance(left_pcb_scene, trimesh.Scene):
    # Get the scene graph to access transforms
    graph = left_pcb_scene.graph
    
    # Iterate over all nodes in the scene graph
    for node_name in graph.nodes:
        # Get the geometry associated with this node
        # graph.get(node_name) returns (transform_matrix, geometry_name) or (transform_matrix, None)
        result = graph.get(node_name)
        
        if result is None:
            continue
            
        transform_matrix, geometry_name = result
        
        # Skip if there's no geometry associated with this node
        if geometry_name is None or geometry_name not in left_pcb_scene.geometry:
            continue
        
        # Get the geometry
        geometry = left_pcb_scene.geometry[geometry_name]
        
        # Apply the transform to a copy of the geometry
        if transform_matrix is not None:
            transformed_geom = geometry.copy()
            transformed_geom.apply_transform(transform_matrix)
        else:
            transformed_geom = geometry
        
        # Add to the combined scene
        scene.add_geometry(
            transformed_geom,
            node_name=f"Left_PCB_{node_name}",
            geom_name=f"Left_PCB_{geometry_name}"
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
print(f"  Variant: v2_graph_transforms (uses scene.graph for transforms)")
print(f"  Left PCB: {LEFT_PCB_GLB}")
print(f"  Case: {CASE_STL}")
print(f"  L Cover: {L_COVER_STL}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
