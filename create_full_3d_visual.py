import pygltflib
import trimesh
import numpy as np
import os
import struct
from copy import deepcopy
import math

# -----------------------------
# Paths
# -----------------------------
CASE_STL = "./filtered-output/cases/case.stl"
COVER_STL = "./filtered-output/cases/cover.stl"
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
OUTPUT_GLB = "./filtered-output/combined_scene.glb"

# Tenting angle in degrees (from create_tenting_system.py)
TENTING_ANGLE = 6.5

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
    
    # Handle materials for STL GLB - create default material if none exist
    if hasattr(stl_gltf, 'meshes') and stl_gltf.meshes:
        # Check if any meshes have materials assigned
        meshes_without_materials = []
        for i, mesh in enumerate(stl_gltf.meshes):
            if mesh.primitives:
                for primitive in mesh.primitives:
                    if primitive.material is None:
                        meshes_without_materials.append(i)
                        break
        
        # If any meshes don't have materials, create a default transparent material
        if len(meshes_without_materials) > 0:
            # Create a default material with 40% transparency
            default_material = pygltflib.Material(
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                    baseColorFactor=[1.0, 1.0, 1.0, 0.4]  # White with 40% transparency
                ),
                alphaMode="BLEND"
            )
            
            # Add the default material to the materials list
            stl_gltf.materials.append(default_material)
            default_material_index = len(stl_gltf.materials) - 1
            
            # Assign this material to all meshes that didn't have one
            for mesh_index in meshes_without_materials:
                mesh = stl_gltf.meshes[mesh_index]
                if mesh.primitives:
                    for primitive in mesh.primitives:
                        if primitive.material is None:
                            primitive.material = default_material_index
    
    # Set transparency (40% alpha) for all materials in PCB GLB
    if hasattr(pcb_gltf, 'materials') and pcb_gltf.materials:
        for material in pcb_gltf.materials:
            if hasattr(material, 'pbrMetallicRoughness') and material.pbrMetallicRoughness:
                base_color_factor = material.pbrMetallicRoughness.baseColorFactor
                if base_color_factor is not None and isinstance(base_color_factor, list) and len(base_color_factor) >= 3:
                    # Keep original RGB values, set alpha to 0.4 (40% transparency)
                    material.pbrMetallicRoughness.baseColorFactor = [
                        base_color_factor[0],
                        base_color_factor[1],
                        base_color_factor[2],
                        0.4
                    ]
                else:
                    # Default to white with 40% transparency if no baseColorFactor exists
                    material.pbrMetallicRoughness.baseColorFactor = [1.0, 1.0, 1.0, 0.4]
            
            # Ensure alpha mode is set to BLEND for transparency
            material.alphaMode = "BLEND"
    
    # Set transparency (40% alpha) for all materials in STL GLB
    if hasattr(stl_gltf, 'materials') and stl_gltf.materials:
        for material in stl_gltf.materials:
            if hasattr(material, 'pbrMetallicRoughness') and material.pbrMetallicRoughness:
                base_color_factor = material.pbrMetallicRoughness.baseColorFactor
                if base_color_factor is not None and isinstance(base_color_factor, list) and len(base_color_factor) >= 3:
                    # Keep original RGB values, set alpha to 0.4 (40% transparency)
                    material.pbrMetallicRoughness.baseColorFactor = [
                        base_color_factor[0],
                        base_color_factor[1],
                        base_color_factor[2],
                        0.4
                    ]
                else:
                    # Default to white with 40% transparency if no baseColorFactor exists
                    material.pbrMetallicRoughness.baseColorFactor = [1.0, 1.0, 1.0, 0.4]
            
            # Ensure alpha mode is set to BLEND for transparency
            material.alphaMode = "BLEND"
    
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
    l_cover_node_idx = None
    cover_node_idx = None
    if hasattr(stl_gltf, 'nodes'):
        for i, node in enumerate(stl_gltf.nodes):
            if hasattr(node, 'name') and node.name in ["Case", "L_Cover", "Cover", "Tenting_System", "Palm_Rest"]:
                stl_model_indices.append(i)
                if node.name == "L_Cover":
                    l_cover_node_idx = i
                if node.name == "Cover":
                    cover_node_idx = i
    
    # Add these STL model nodes to the PCB scene's root nodes
    if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes is not None:
        for stl_model_idx in stl_model_indices:
            adjusted_idx = stl_model_idx + pcb_node_count
            if adjusted_idx not in pcb_gltf.scenes[0].nodes:
                pcb_gltf.scenes[0].nodes.append(adjusted_idx)
    
    # Move L_Cover down by 12 units along Y-axis
    if l_cover_node_idx is not None:
        # Get the adjusted node index in the merged GLB
        adjusted_l_cover_idx = l_cover_node_idx + pcb_node_count
        # Find the node in the PCB GLB
        if adjusted_l_cover_idx < len(pcb_gltf.nodes):
            node = pcb_gltf.nodes[adjusted_l_cover_idx]
            # Apply downward translation (negative Y)
            if hasattr(node, 'translation') and node.translation is not None:
                translation = node.translation
                if isinstance(translation, list) and len(translation) >= 2:
                    translation[1] -= 12  # Subtract 12 from Y component
                    node.translation = translation
                else:
                    node.translation = [0, -12, 0]
            else:
                node.translation = [0, -12, 0]
    
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

def rotate_glb_around_z_axis(glb_path: str, angle_degrees: float, output_path: str) -> None:
    """
    Rotate a GLB file around the Z-axis by the specified angle.
    Uses pygltflib to apply rotation ONLY to the root node (node 0).
    
    In a hierarchical glTF structure, rotating the root node automatically
    rotates all children through the transformation hierarchy. This avoids
    the double rotation problem where both parent and children get rotated.
    
    Args:
        glb_path: Path to the input GLB file
        angle_degrees: Rotation angle in degrees (positive = counterclockwise when looking along Z axis)
        output_path: Path to save the rotated GLB file
    """
    print(f"\nLoading GLB for rotation: {glb_path}")
    try:
        gltf = pygltflib.GLTF2().load(glb_path)
        if gltf is None:
            raise ValueError("Failed to load GLB file")
        print(f"  GLB loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to load GLB file: {e}")
        return
    
    # Convert angle to radians
    angle_rad = math.radians(angle_degrees)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    # Calculate quaternion for Z-axis rotation
    # For a rotation around Z-axis by angle a:
    # q = [sin(a/2) * 0, sin(a/2) * 0, sin(a/2) * 1, cos(a/2)]
    #   = [0, 0, sin(a/2), cos(a/2)]
    half_angle = angle_rad / 2
    q_rot_z = [0, 0, math.sin(half_angle), math.cos(half_angle)]
    
    print(f"  Applying {angle_degrees}° rotation around Z-axis to ROOT NODE ONLY")
    print(f"  Z-axis rotation quaternion: {q_rot_z}")
    
    # Get the root node (node 0)
    node_count = len(gltf.nodes) if hasattr(gltf, 'nodes') else 0
    print(f"  Total nodes in file: {node_count}")
    
    if node_count == 0:
        print("ERROR: No nodes found in GLB file")
        return
    
    # Only rotate the root node (node 0)
    # All children will inherit the rotation through the hierarchy
    root_node = gltf.nodes[0]
    root_node_name = root_node.name if hasattr(root_node, 'name') and root_node.name else 'Unnamed'
    print(f"  Rotating root node (node 0: '{root_node_name}')...")
    
    # Handle matrix transformation (4x4 transformation matrix)
    # The matrix is in column-major order:
    # [m0,  m4,  m8,  m12]   [Xx, Yx, Zx, Tx]
    # [m1,  m5,  m9,  m13] = [Xy, Yy, Zy, Ty]
    # [m2,  m6,  m10, m14]   [Xz, Yz, Zz, Tz]
    # [m3,  m7,  m11, m15]   [0,  0,  0,  1]
    if hasattr(root_node, 'matrix') and root_node.matrix is not None:
        matrix = root_node.matrix
        if isinstance(matrix, list) and len(matrix) == 16:
            # Extract translation (columns 3, rows 0-2)
            tx, ty, tz = matrix[12], matrix[13], matrix[14]
            
            # Apply Z-axis rotation to translation
            new_tx = tx * cos_a - ty * sin_a
            new_ty = tx * sin_a + ty * cos_a
            
            # Extract rotation columns (X, Y, Z axes)
            # X axis: matrix[0], matrix[1], matrix[2]
            # Y axis: matrix[4], matrix[5], matrix[6]
            # Z axis: matrix[8], matrix[9], matrix[10]
            
            # Apply Z rotation to X and Y axes
            new_Xx = matrix[0] * cos_a - matrix[4] * sin_a
            new_Xy = matrix[1] * cos_a - matrix[5] * sin_a
            new_Xz = matrix[2] * cos_a - matrix[6] * sin_a
            
            new_Yx = matrix[0] * sin_a + matrix[4] * cos_a
            new_Yy = matrix[1] * sin_a + matrix[5] * cos_a
            new_Yz = matrix[2] * sin_a + matrix[6] * cos_a
            
            # Z axis remains unchanged
            new_Zx = matrix[8]
            new_Zy = matrix[9]
            new_Zz = matrix[10]
            
            # Update the matrix with rotated values
            root_node.matrix = [
                new_Xx, new_Xy, new_Xz, 0,
                new_Yx, new_Yy, new_Yz, 0,
                new_Zx, new_Zy, new_Zz, 0,
                new_tx, new_ty, tz, 1
            ]
            print(f"    Applied rotation to matrix transformation")
    
    # Apply rotation to rotation (quaternion)
    if hasattr(root_node, 'rotation') and root_node.rotation is not None:
        rotation = root_node.rotation
        if isinstance(rotation, list) and len(rotation) >= 4:
            qx, qy, qz, qw = rotation[0], rotation[1], rotation[2], rotation[3]
            # Quaternion multiplication: q_rot_z * rotation
            new_qx = q_rot_z[3] * qx + q_rot_z[2] * qy
            new_qy = q_rot_z[3] * qy - q_rot_z[2] * qx
            new_qz = q_rot_z[3] * qz + q_rot_z[2] * qw
            new_qw = q_rot_z[3] * qw - q_rot_z[2] * qz
            root_node.rotation = [new_qx, new_qy, new_qz, new_qw]
            print(f"    Applied rotation to quaternion transformation")
    else:
        # If no rotation exists, add the Z-axis rotation quaternion
        root_node.rotation = [0, 0, q_rot_z[2], q_rot_z[3]]
        print(f"    Added rotation quaternion to root node")
    
    # Apply rotation to translation (rotate the position around Z-axis)
    # This is done IN ADDITION to the rotation quaternion
    if hasattr(root_node, 'translation') and root_node.translation is not None:
        translation = root_node.translation
        if isinstance(translation, list) and len(translation) >= 3:
            x, y, z = translation[0], translation[1], translation[2]
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            root_node.translation = [new_x, new_y, z]
            print(f"    Applied rotation to translation transformation")
    
    print(f"  Rotation applied to root node only (children inherit through hierarchy)")
    
    # Save the rotated GLB
    try:
        gltf.save(output_path)
        print(f"  Rotated GLB saved to: {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to save rotated GLB file: {e}")
        return

# -----------------------------
# Main execution
# -----------------------------
print("=== Variant 11: Hybrid pygltflib + trimesh approach (Two-step merge) ===\n")

# Step 1: Create GLB from STL files EXCEPT tenting system
stl_files_no_tenting = {
    "Case": CASE_STL,
    "Cover": COVER_STL,
    "Palm_Rest": PALM_REST_STL
}

temp_stl_glb_no_tenting = "./filtered-output/temp_stl_models_no_tenting.glb"
print("Step 1a: Creating GLB from STL files (without tenting system)...")
create_glb_from_stls(stl_files_no_tenting, temp_stl_glb_no_tenting)

# Merge GLB files (PCB + STL without tenting) → intermediate output
intermediate_output = "./filtered-output/pcb_plus_stl_no_tenting.glb"
print("\nStep 1b: Merging GLB files (PCB + STL without tenting)...")
merge_glb_files(LEFT_PCB_GLB, temp_stl_glb_no_tenting, intermediate_output)

# Step 2: Create GLB from tenting system only
temp_stl_glb_tenting = "./filtered-output/temp_stl_models_tenting.glb"
print("\nStep 2a: Creating GLB from tenting system STL...")
stl_files_tenting = {
    "Tenting_System": TENTING_STL
}
create_glb_from_stls(stl_files_tenting, temp_stl_glb_tenting)

# Rotate the intermediate output by 6.5 degrees around Z-axis (vertical axis)
# Positive angle tilts the left side up to match the tenting system
rotated_output = "./filtered-output/pcb_plus_stl_no_tenting_tented.glb"
print("\nStep 2a-b: Rotating intermediate output by 6.5° around Z-axis...")
rotate_glb_around_z_axis(intermediate_output, 6.5, rotated_output)

# Merge the rotated result with tenting system
print("\nStep 2c: Merging with tenting system...")
merge_glb_files(rotated_output, temp_stl_glb_tenting, OUTPUT_GLB)

print(f"\n=== Complete ===")
print(f"Output: {OUTPUT_GLB}")
print(f"\nIntermediate outputs:")
print(f"  - PCB + STL without tenting: {intermediate_output}")
print(f"  - Rotated (6.5° Y-axis): {rotated_output}")
print(f"\nTemp files kept for debugging:")
print(f"  - {temp_stl_glb_no_tenting}")
print(f"  - {temp_stl_glb_tenting}")
