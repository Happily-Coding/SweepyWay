from pygltflib import GLTF2
import os

# Paths
MERGED_GLB = "./filtered-output/combined_scene_v11_hybrid.glb"

# Verify file exists
if not os.path.exists(MERGED_GLB):
    print(f"ERROR: File not found: {MERGED_GLB}")
    exit(1)

# Load the merged GLB file
print(f"Loading merged GLB: {MERGED_GLB}")
try:
    gltf = GLTF2().load(MERGED_GLB)
    print(f"Merged GLB loaded successfully")
except Exception as e:
    print(f"ERROR: Failed to load merged GLB file: {e}")
    exit(1)

# Check if gltf is properly loaded
if gltf is None:
    print("ERROR: GLB file loaded as None")
    exit(1)

# Analyze scene structure
print(f"\n=== Scene Structure ===")
print(f"  Version: {gltf.asset.version if hasattr(gltf, 'asset') and hasattr(gltf.asset, 'version') else 'Unknown'}")
print(f"  Generator: {gltf.asset.generator if hasattr(gltf, 'asset') and hasattr(gltf.asset, 'generator') else 'Unknown'}")
print(f"  Nodes: {len(gltf.nodes) if hasattr(gltf, 'nodes') else 'Unknown'}")
print(f"  Meshes: {len(gltf.meshes) if hasattr(gltf, 'meshes') else 'Unknown'}")
print(f"  Accessors: {len(gltf.accessors) if hasattr(gltf, 'accessors') else 'Unknown'}")
print(f"  BufferViews: {len(gltf.bufferViews) if hasattr(gltf, 'bufferViews') else 'Unknown'}")
print(f"  Buffers: {len(gltf.buffers) if hasattr(gltf, 'buffers') else 'Unknown'}")
print(f"  Scenes: {len(gltf.scenes) if hasattr(gltf, 'scenes') else 'Unknown'}")

# Print node details
print(f"\n=== Node Details ===")
if hasattr(gltf, 'nodes'):
    for i, node in enumerate(gltf.nodes):
        node_name = node.name if hasattr(node, 'name') and node.name else 'Unnamed'
        print(f"  Node {i}: {node_name}")
        if node.mesh is not None:
            print(f"    Mesh: {node.mesh}")
        if hasattr(node, 'translation') and node.translation:
            print(f"    Translation: {node.translation}")
        if hasattr(node, 'rotation') and node.rotation:
            print(f"    Rotation: {node.rotation}")
        if hasattr(node, 'scale') and node.scale:
            print(f"    Scale: {node.scale}")
else:
    print("No nodes available")

# Print scene details
print(f"\n=== Scene Details ===")
if hasattr(gltf, 'scenes'):
    for i, scene in enumerate(gltf.scenes):
        scene_name = scene.name if hasattr(scene, 'name') and scene.name else 'Unnamed'
        print(f"  Scene {i}: {scene_name}")
        if hasattr(scene, 'nodes') and scene.nodes:
            print(f"    Root Nodes: {scene.nodes}")
            # Check if any of the root nodes correspond to STL models
            for node_idx in scene.nodes:
                if node_idx >= len(gltf.nodes):
                    print(f"      WARNING: Node index {node_idx} out of range!")
                else:
                    node = gltf.nodes[node_idx]
                    node_name = node.name if hasattr(node, 'name') and node.name else 'Unnamed'
                    print(f"      Root Node {node_idx}: {node_name}")
        else:
            print(f"    No root nodes defined")
else:
    print("No scenes available")

# Check for STL model nodes by name
print(f"\n=== Checking for STL Model Nodes ===")
stl_model_names = ["Case", "L_Cover", "Tenting_System", "Palm_Rest"]
found_stl_nodes = []
if hasattr(gltf, 'nodes'):
    for i, node in enumerate(gltf.nodes):
        if hasattr(node, 'name') and node.name in stl_model_names:
            found_stl_nodes.append((i, node.name))
            print(f"  Found STL node: {node.name} at index {i}")

if not found_stl_nodes:
    print("  No STL model nodes found in the node list!")

print(f"\nGLB structure analysis complete.")
print(f"This will help identify why the STL models are not appearing in the final output.")