# Variant 4: Iterate Over Graph Edges
# This approach traverses the scene graph using edges, which represent parent->child
# relationships with transforms.
#
# Key insight: The scene.graph is a directed graph where edges contain transforms.
# We need to use the correct trimesh SceneGraph API.
#
# Expected outcome: Correct transforms for all components

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
OUTPUT_GLB = "./filtered-output/combined_scene_v4_graph_edges.glb"

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

# Add PCB models using graph edges approach
if isinstance(left_pcb_scene, trimesh.Scene):
    graph = left_pcb_scene.graph
    
    # Track which geometries we've already added to avoid duplicates
    added_geometries = set()
    
    # The trimesh SceneGraph has an 'edges' attribute that returns (parent, child) tuples
    # We need to use the transform attribute from the graph
    try:
        # Try to iterate over edges (may be called 'edge_data' in some versions)
        # The graph stores transforms internally
        for node_name in graph.nodes:
            # Get the world transform for this node
            # graph.get(node_name) returns (transform_matrix, geometry_name)
            result = graph.get(node_name)
            
            if result is None:
                continue
            
            transform_matrix, geometry_name = result
            
            # Skip if no geometry associated
            if geometry_name is None or geometry_name not in left_pcb_scene.geometry:
                continue
            
            # Skip if already added
            if geometry_name in added_geometries:
                continue
            
            # Get the geometry
            geometry = left_pcb_scene.geometry[geometry_name]
            added_geometries.add(geometry_name)
            
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
    except Exception as e:
        print(f"  Warning: Error iterating graph nodes: {e}")
        # Fallback to simple iteration
        for geom_name, geometry in left_pcb_scene.geometry.items():
            scene.add_geometry(
                geometry,
                node_name=f"Left_PCB_{geom_name}",
                geom_name=f"Left_PCB_{geom_name}"
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
print(f"  Variant: v4_graph_edges (uses graph.get() for world transforms)")
print(f"  Left PCB: {LEFT_PCB_GLB}")
print(f"  Case: {CASE_STL}")
print(f"  L Cover: {L_COVER_STL}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
