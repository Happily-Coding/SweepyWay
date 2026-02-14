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
    Applies a -90-degree rotation around the X-axis to align with PCB orientation (upward rotation).
    """
    scene = trimesh.Scene()
    
    # Create a -90-degree rotation matrix around X-axis to rotate STL models upward
    # This matches the orientation needed to align with the PCB's tall end
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-1.5708,  # -90 degrees in radians
        direction=[1, 0, 0],  # X-axis
        point=[0, 0, 0]
    )
    
    for node_name, stl_path in stl_files.items():
        if os.path.exists(stl_path):
            mesh = trimesh.load(stl_path, force="mesh")
            # Apply the rotation to the mesh
            mesh.apply_transform(rotation_matrix)
            scene.add_geometry(mesh, node_name=node_name, geom_name=node_name)
            print(f"  Added: {stl_path} as {node_name} (rotated -90° around X-axis upward)")
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
    6. Moving the PCB upward by 7 units along Y-axis to align with STL models
    """
    print("\nLoading PCB GLB...")
    try:
        pcb_gltf = pygltflib.GLTF2().load(pcb_glb_path)
        if pcb_gltf is None:
            raise ValueError("Failed to load PCB GLB file")
        print(f"  PCB GLB loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to load PCB GLB file: {e}")
        return
    
    pcb_node_count = len(pcb_gltf.nodes) if hasattr(pcb_gltf, 'nodes') else 0
    pcb_mesh_count = len(pcb_gltf.meshes) if hasattr(pcb_gltf, 'meshes') else 0
    pcb_accessor_count = len(pcb_gltf.accessors) if hasattr(pcb_gltf, 'accessors') else 0
    pcb_bufferView_count = len(pcb_gltf.bufferViews) if hasattr(pcb_gltf, 'bufferViews') else 0
    print(f"  Nodes: {pcb_node_count}, Meshes: {pcb_mesh_count}")
    print(f"  Accessors: {pcb_accessor_count}, BufferViews: {pcb_bufferView_count}")
    
    print("\nLoading STL GLB...")
    try:
        stl_gltf = pygltflib.GLTF2().load(stl_glb_path)
        if stl_gltf is None:
            raise ValueError("Failed to load STL GLB file")
        print(f"  STL GLB loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to load STL GLB file: {e}")
        return
    
    stl_node_count = len(stl_gltf.nodes) if hasattr(stl_gltf, 'nodes') else 0
    stl_mesh_count = len(stl_gltf.meshes) if hasattr(stl_gltf, 'meshes') else 0
    stl_accessor_count = len(stl_gltf.accessors) if hasattr(stl_gltf, 'accessors') else 0
    stl_bufferView_count = len(stl_gltf.bufferViews) if hasattr(stl_gltf, 'bufferViews') else 0
    print(f"  Nodes: {stl_node_count}, Meshes: {stl_mesh_count}")
    print(f"  Accessors: {stl_accessor_count}, BufferViews: {stl_bufferView_count}")
    
    # Get binary data from both files
    try:
        pcb_binary = pcb_gltf.binary_blob()
        stl_binary = stl_gltf.binary_blob()
    except Exception as e:
        print(f"ERROR: Failed to get binary data from GLB files: {e}")
        return
    
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
    if hasattr(stl_gltf, 'bufferViews'):
        for buffer_view in stl_gltf.bufferViews:
            buffer_view.byteOffset = (buffer_view.byteOffset or 0) + stl_buffer_offset
    
    # Add STL buffer views to PCB
    if hasattr(stl_gltf, 'bufferViews') and hasattr(pcb_gltf, 'bufferViews'):
        for buffer_view in stl_gltf.bufferViews:
            pcb_gltf.bufferViews.append(buffer_view)
    
    # Update STL accessor buffer view indices
    if hasattr(stl_gltf, 'accessors') and hasattr(pcb_gltf, 'accessors'):
        for accessor in stl_gltf.accessors:
            if accessor.bufferView is not None:
                accessor.bufferView += pcb_bufferView_count
    
    # Add STL accessors to PCB
    if hasattr(stl_gltf, 'accessors') and hasattr(pcb_gltf, 'accessors'):
        for accessor in stl_gltf.accessors:
            pcb_gltf.accessors.append(accessor)
    
    # Update STL mesh primitive attribute and accessor indices
    if hasattr(stl_gltf, 'meshes'):
        for mesh in stl_gltf.meshes:
            for primitive in mesh.primitives:
                # Update attributes
                if hasattr(primitive.attributes, 'POSITION') and primitive.attributes.POSITION is not None:
                    primitive.attributes.POSITION += pcb_accessor_count
                if hasattr(primitive.attributes, 'NORMAL') and primitive.attributes.NORMAL is not None:
                    primitive.attributes.NORMAL += pcb_accessor_count
                # Update indices
                if primitive.indices is not None:
                    primitive.indices += pcb_accessor_count
    
    # Add STL meshes to PCB
    mesh_offset = pcb_mesh_count
    if hasattr(stl_gltf, 'meshes') and hasattr(pcb_gltf, 'meshes'):
        for mesh in stl_gltf.meshes:
            pcb_gltf.meshes.append(mesh)
    
    # Update STL node mesh indices
    if hasattr(stl_gltf, 'nodes'):
        for node in stl_gltf.nodes:
            if hasattr(node, 'mesh') and node.mesh is not None:
                node.mesh += mesh_offset
    
    # Add STL nodes to PCB
    if hasattr(stl_gltf, 'nodes') and hasattr(pcb_gltf, 'nodes'):
        for node in stl_gltf.nodes:
            pcb_gltf.nodes.append(node)
    
    # Move the entire PCB upward by 7 units along Y-axis by modifying the root node
    # The PCB GLB has a complex hierarchy with 157 nodes, so we need to preserve all of them
    # We'll modify the translation of the root node (node 0) to move the entire PCB upward
    if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None and len(pcb_gltf.scenes[0].nodes) > 0:
        # Get the first root node of the PCB scene (node 0)
        root_node_idx = pcb_gltf.scenes[0].nodes[0]
        
        # Apply translation to the root node to move the entire PCB upward
        if hasattr(pcb_gltf.nodes[root_node_idx], 'translation') and pcb_gltf.nodes[root_node_idx].translation is not None:
            translation = pcb_gltf.nodes[root_node_idx].translation
            if isinstance(translation, list) and len(translation) >= 2:
                translation[1] += 7  # Add 7 to Y component
                pcb_gltf.nodes[root_node_idx].translation = translation
            else:
                pcb_gltf.nodes[root_node_idx].translation = [0, 7, 0]
        else:
            pcb_gltf.nodes[root_node_idx].translation = [0, 7, 0]
    
    # We don't need to create new nodes since we're preserving the existing structure
    # The PCB GLB already has all 157 nodes with their correct relationships
    # We just need to ensure they're all included in the final scene
    
    # Ensure the scene's root nodes include the PCB root node
    if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
        # Make sure the PCB root node is in the scene's root nodes
        if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
            root_node_idx = pcb_gltf.scenes[0].nodes[0]
            # Ensure the root node is in the scene's nodes list
            if root_node_idx not in pcb_gltf.scenes[0].nodes:
                pcb_gltf.scenes[0].nodes.append(root_node_idx)
    
    # Ensure all PCB nodes are properly referenced in the scene
    # The scene structure should already be correct, but we'll ensure the root node is properly set
    if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
        # Set the first node as the root node if it's not already
        if len(pcb_gltf.scenes[0].nodes) > 0:
            pcb_gltf.scenes[0].nodes = [pcb_gltf.scenes[0].nodes[0]]
    
    # We need to ensure the scene's root nodes include the PCB root node
    # This is already handled by the scene structure, but we'll ensure it's correct
    if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
        # Make sure the scene has exactly one root node (the PCB root node)
        if len(pcb_gltf.scenes[0].nodes) == 0:
            # If no root nodes, add the PCB root node
            if hasattr(pcb_gltf, 'nodes') and len(pcb_gltf.nodes) > 0:
                pcb_gltf.scenes[0].nodes = [0]
        else:
            # Make sure the first node is the PCB root node (node 0)
            pcb_gltf.scenes[0].nodes = [pcb_gltf.scenes[0].nodes[0]]
    
    # Update the scene to include STL root nodes
    # Find the root nodes of the STL scene
    if hasattr(stl_gltf, 'scenes') and stl_gltf.scenes and stl_gltf.scenes[0].nodes is not None:
        for root_node_idx in stl_gltf.scenes[0].nodes:
            # Add this node to the PCB scene's root nodes
            adjusted_idx = root_node_idx + pcb_node_count
            if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
                pcb_gltf.scenes[0].nodes.append(adjusted_idx)
    
    # Additionally, explicitly add the STL model nodes to the scene's root nodes
    # This ensures they are visible even if the STL scene structure is different
    stl_model_indices = []
    if hasattr(stl_gltf, 'nodes'):
        for i, node in enumerate(stl_gltf.nodes):
            if hasattr(node, 'name') and node.name in ["Case", "L_Cover", "Tenting_System", "Palm_Rest"]:
                stl_model_indices.append(i)
    
    # Add these STL model nodes to the PCB scene's root nodes
    if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
        for stl_model_idx in stl_model_indices:
            adjusted_idx = stl_model_idx + pcb_node_count
            if adjusted_idx not in pcb_gltf.scenes[0].nodes:
                pcb_gltf.scenes[0].nodes.append(adjusted_idx)
    
    # Set the combined binary data
    try:
        pcb_gltf.set_binary_blob(combined_binary)
    except Exception as e:
        print(f"ERROR: Failed to set combined binary blob: {e}")
        return
    
    # Save the merged GLB
    try:
        pcb_gltf.save(output_path)
        print(f"\nMerged GLB saved to: {output_path}")
        print(f"  Total nodes: {len(pcb_gltf.nodes) if hasattr(pcb_gltf, 'nodes') else 'Unknown'}")
        print(f"  Total meshes: {len(pcb_gltf.meshes) if hasattr(pcb_gltf, 'meshes') else 'Unknown'}")
    except Exception as e:
        print(f"ERROR: Failed to save merged GLB file: {e}")
        return

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
