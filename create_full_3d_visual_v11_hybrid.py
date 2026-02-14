# Variant 11: Hybrid approach - pygltflib for PCB + trimesh for STL
# 
# Strategy:
# 1. Load PCB GLB with pygltflib (preserves exact structure and transforms)
# 2. Create a temporary GLB from STL files using trimesh
# 3. Merge the two GLB files by combining their binary buffers and adjusting indices
#
# Expected outcome:
# - Switches at correct positions (PCB GLB preserved exactly)
# - PCB orientation correct (PCB GLB preserved exactly)
# - Object structure preserved (node names preserved)
# - STL models added as additional nodes

import pygltflib
import trimesh
import numpy as np
import os
import struct
from copy import deepcopy

# -----------------------------
# Paths
# -----------------------------
CASE_STL = "./filtered-output/cases/case.stl"
L_COVER_STL = "./filtered-output/cases/l_cover.stl"
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
OUTPUT_GLB = "./filtered-output/combined_scene_v11_hybrid.glb"

def create_glb_from_stls(stl_files: dict, output_path: str) -> str:
    """
    Create a GLB file from multiple STL files using trimesh.
    """
    scene = trimesh.Scene()
    
    for node_name, stl_path in stl_files.items():
        if os.path.exists(stl_path):
            mesh = trimesh.load(stl_path, force="mesh")
            scene.add_geometry(mesh, node_name=node_name, geom_name=node_name)
            print(f"  Added: {stl_path} as {node_name}")
        else:
            print(f"  Warning: {stl_path} not found, skipping")
    
    scene.export(output_path)
    return output_path

def merge_glb_files(pcb_glb_path: str, stl_glb_path: str, output_path: str) -> None:
    """
    Merge two GLB files using pygltflib.
    
    The PCB GLB is the primary file. We add STL GLB content by:
    1. Combining binary buffers
    2. Adjusting buffer view indices
    3. Adjusting accessor indices
    4. Adjusting mesh primitive indices
    5. Adding STL nodes to the scene
    """
    print("\nLoading PCB GLB...")
    pcb_gltf = pygltflib.GLTF2().load(pcb_glb_path)
    pcb_node_count = len(pcb_gltf.nodes)
    pcb_mesh_count = len(pcb_gltf.meshes)
    pcb_accessor_count = len(pcb_gltf.accessors)
    pcb_bufferView_count = len(pcb_gltf.bufferViews)
    print(f"  Nodes: {pcb_node_count}, Meshes: {pcb_mesh_count}")
    print(f"  Accessors: {pcb_accessor_count}, BufferViews: {pcb_bufferView_count}")
    
    print("\nLoading STL GLB...")
    stl_gltf = pygltflib.GLTF2().load(stl_glb_path)
    stl_node_count = len(stl_gltf.nodes)
    stl_mesh_count = len(stl_gltf.meshes)
    stl_accessor_count = len(stl_gltf.accessors)
    stl_bufferView_count = len(stl_gltf.bufferViews)
    print(f"  Nodes: {stl_node_count}, Meshes: {stl_mesh_count}")
    print(f"  Accessors: {stl_accessor_count}, BufferViews: {stl_bufferView_count}")
    
    # Get binary data from both files
    pcb_binary = pcb_gltf.binary_blob()
    stl_binary = stl_gltf.binary_blob()
    
    if pcb_binary is None:
        pcb_binary = b''
    if stl_binary is None:
        stl_binary = b''
    
    print(f"\nBinary sizes: PCB={len(pcb_binary)} bytes, STL={len(stl_binary)} bytes")
    
    # Calculate the offset for STL buffer views
    stl_buffer_offset = len(pcb_binary)
    
    # Combine binary data
    combined_binary = pcb_binary + stl_binary
    
    # Update STL buffer views to point to the correct offset
    for buffer_view in stl_gltf.bufferViews:
        buffer_view.byteOffset = (buffer_view.byteOffset or 0) + stl_buffer_offset
    
    # Add STL buffer views to PCB
    for buffer_view in stl_gltf.bufferViews:
        pcb_gltf.bufferViews.append(buffer_view)
    
    # Update STL accessor buffer view indices
    for accessor in stl_gltf.accessors:
        accessor.bufferView += pcb_bufferView_count
    
    # Add STL accessors to PCB
    for accessor in stl_gltf.accessors:
        pcb_gltf.accessors.append(accessor)
    
    # Update STL mesh primitive attribute and accessor indices
    for mesh in stl_gltf.meshes:
        for primitive in mesh.primitives:
            # Update attributes
            if primitive.attributes.POSITION is not None:
                primitive.attributes.POSITION += pcb_accessor_count
            if primitive.attributes.NORMAL is not None:
                primitive.attributes.NORMAL += pcb_accessor_count
            # Update indices
            if primitive.indices is not None:
                primitive.indices += pcb_accessor_count
    
    # Add STL meshes to PCB
    mesh_offset = pcb_mesh_count
    for mesh in stl_gltf.meshes:
        pcb_gltf.meshes.append(mesh)
    
    # Update STL node mesh indices
    for node in stl_gltf.nodes:
        if node.mesh is not None:
            node.mesh += mesh_offset
    
    # Add STL nodes to PCB
    for node in stl_gltf.nodes:
        pcb_gltf.nodes.append(node)
    
    # Update the scene to include STL root nodes
    # Find the root nodes of the STL scene
    if stl_gltf.scenes and stl_gltf.scenes[0].nodes:
        for root_node_idx in stl_gltf.scenes[0].nodes:
            # Add this node to the PCB scene's root nodes
            adjusted_idx = root_node_idx + pcb_node_count
            if pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
                pcb_gltf.scenes[0].nodes.append(adjusted_idx)
    
    # Set the combined binary data
    pcb_gltf.set_binary_blob(combined_binary)
    
    # Save the merged GLB
    pcb_gltf.save(output_path)
    
    print(f"\nMerged GLB saved to: {output_path}")
    print(f"  Total nodes: {len(pcb_gltf.nodes)}")
    print(f"  Total meshes: {len(pcb_gltf.meshes)}")

# -----------------------------
# Main execution
# -----------------------------
print("=== Variant 11: Hybrid pygltflib + trimesh approach ===\n")

# Define STL files to add
stl_files = {
    "Case": CASE_STL,
    "L_Cover": L_COVER_STL,
    "Tenting_System": TENTING_STL,
    "Palm_Rest": PALM_REST_STL
}

# Create temporary GLB from STL files
temp_stl_glb = "./filtered-output/temp_stl_models.glb"
print("Step 1: Creating GLB from STL files...")
create_glb_from_stls(stl_files, temp_stl_glb)

# Merge GLB files
print("\nStep 2: Merging GLB files...")
merge_glb_files(LEFT_PCB_GLB, temp_stl_glb, OUTPUT_GLB)

# Clean up temp file
if os.path.exists(temp_stl_glb):
    os.remove(temp_stl_glb)
    print(f"\nCleaned up temp file: {temp_stl_glb}")

print(f"\n=== Complete ===")
print(f"Output: {OUTPUT_GLB}")
