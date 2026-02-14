# Variant 8: Copy Scene Graph Structure Directly
# This approach copies the entire scene graph from the PCB scene to the new scene,
# preserving the node hierarchy and transforms.
#
# Key insight: Instead of iterating over geometries, we need to copy the scene graph
# structure which contains the node names (S25, HS8, K8, etc.) and their transforms.
#
# Expected outcome:
# - Switches at correct positions (transforms preserved via scene graph)
# - PCB orientation correct (transforms preserved via scene graph)
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
OUTPUT_GLB = "./filtered-output/combined_scene_v8_copy_graph.glb"

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

# Add PCB models by copying the scene graph structure
if isinstance(left_pcb_scene, trimesh.Scene):
    # Get the scene graph and geometry from the PCB scene
    pcb_graph = left_pcb_scene.graph
    pcb_geometry = left_pcb_scene.geometry
    
    # First, add all geometries to the new scene (without transforms)
    for geom_name, geom in pcb_geometry.items():
        scene.add_geometry(
            geom,
            node_name=f"Left_PCB_geom_{geom_name}",
            geom_name=f"Left_PCB_{geom_name}"
        )
    
    # Now, we need to update the scene graph to use the correct transforms
    # The scene.graph is a directed graph where each edge has a transform
    # We need to copy this structure
    
    # Get the base frame of the PCB scene
    base_frame = pcb_graph.base_frame
    
    # Iterate over all nodes in the PCB scene graph
    for node in pcb_graph.nodes:
        # Get the transform from base_frame to this node
        try:
            # Get the transform to this node
            to_node = pcb_graph.get(node)
            if to_node is not None:
                transform, geom_name = to_node
                
                # If this node has a geometry, update the transform in our scene
                if geom_name is not None and geom_name in pcb_geometry:
                    # Update the node's transform in the new scene's graph
                    # The node name in our scene is "Left_PCB_geom_{geom_name}"
                    new_node_name = f"Left_PCB_geom_{geom_name}"
                    
                    # Set the transform for this node
                    scene.graph.update(frame_from=base_frame, frame_to=new_node_name, matrix=transform)
        except Exception as e:
            # Skip nodes that don't have valid transforms
            continue
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
print(f"  Variant: v8_copy_graph (copies scene graph structure)")
print(f"  Left PCB: {LEFT_PCB_GLB}")
print(f"  Case: {CASE_STL}")
print(f"  L Cover: {L_COVER_STL}")
print(f"  Tenting: {TENTING_STL}")
print(f"  Palm Rest: {PALM_REST_STL}")
