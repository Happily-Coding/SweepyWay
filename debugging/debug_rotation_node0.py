from pygltflib import GLTF2
import math

# Paths
INTERMEDIATE_GLB = "./filtered-output/pcb_plus_stl_no_tenting.glb"
ROTATED_GLB = "./filtered-output/pcb_plus_stl_no_tenting_tented.glb"

# Tenting angle
TENTING_ANGLE = 6.5

def print_node_details(gltf, title):
    print(f"\n=== {title} ===")
    print(f"Nodes: {len(gltf.nodes)}")
    
    # Print Node 0 (PCB body)
    node = gltf.nodes[0]
    name = node.name if hasattr(node, 'name') and node.name else 'Unnamed'
    print(f"\nNode 0 ({name}):")
    
    if hasattr(node, 'matrix') and node.matrix is not None:
        print(f"  Matrix: {node.matrix}")
    
    if hasattr(node, 'translation') and node.translation is not None:
        print(f"  Translation: {node.translation}")
    
    if hasattr(node, 'rotation') and node.rotation is not None:
        print(f"  Rotation: {node.rotation}")
    
    if hasattr(node, 'scale') and node.scale is not None:
        print(f"  Scale: {node.scale}")
    
    if not hasattr(node, 'matrix') or node.matrix is None:
        if not hasattr(node, 'translation') or node.translation is None:
            if not hasattr(node, 'rotation') or node.rotation is None:
                if not hasattr(node, 'scale') or node.scale is None:
                    print(f"  NO TRANSFORMATION")

# Load and print intermediate GLB
print(f"Loading intermediate GLB: {INTERMEDIATE_GLB}")
try:
    intermediate_gltf = GLTF2().load(INTERMEDIATE_GLB)
    print_node_details(intermediate_gltf, "Intermediate GLB (Before Rotation)")
except Exception as e:
    print(f"ERROR: Failed to load GLB file: {e}")
    exit(1)

# Load and print rotated GLB
print(f"\nLoading rotated GLB: {ROTATED_GLB}")
try:
    rotated_gltf = GLTF2().load(ROTATED_GLB)
    print_node_details(rotated_gltf, "Rotated GLB (After Rotation)")
except Exception as e:
    print(f"ERROR: Failed to load GLB file: {e}")
    exit(1)
