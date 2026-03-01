from pygltflib import GLTF2
import math

# Paths
INTERMEDIATE_GLB = "./filtered-output/pcb_plus_stl_no_tenting.glb"
ROTATED_GLB = "./filtered-output/pcb_plus_stl_no_tenting_tented.glb"

# Tenting angle
TENTING_ANGLE = 6.5

def print_node_transformations(gltf, title):
    print(f"\n=== {title} ===")
    print(f"Nodes: {len(gltf.nodes)}")
    for i, node in enumerate(gltf.nodes):
        name = node.name if hasattr(node, 'name') and node.name else 'Unnamed'
        print(f"\nNode {i} ({name}):")
        
        if hasattr(node, 'matrix') and node.matrix is not None:
            print(f"  Matrix: {node.matrix}")
        
        if hasattr(node, 'translation') and node.translation is not None:
            print(f"  Translation: {node.translation}")
        
        if hasattr(node, 'rotation') and node.rotation is not None:
            print(f"  Rotation: {node.rotation}")
        
        if hasattr(node, 'scale') and node.scale is not None:
            print(f"  Scale: {node.scale}")

# Load and print intermediate GLB
print(f"Loading intermediate GLB: {INTERMEDIATE_GLB}")
try:
    intermediate_gltf = GLTF2().load(INTERMEDIATE_GLB)
    print_node_transformations(intermediate_gltf, "Intermediate GLB (Before Rotation)")
except Exception as e:
    print(f"ERROR: Failed to load GLB file: {e}")
    exit(1)

# Load and print rotated GLB
print(f"\nLoading rotated GLB: {ROTATED_GLB}")
try:
    rotated_gltf = GLTF2().load(ROTATED_GLB)
    print_node_transformations(rotated_gltf, "Rotated GLB (After Rotation)")
except Exception as e:
    print(f"ERROR: Failed to load GLB file: {e}")
    exit(1)

# Calculate expected rotation
angle_rad = math.radians(TENTING_ANGLE)
cos_a = math.cos(angle_rad)
sin_a = math.sin(angle_rad)
half_angle = angle_rad / 2
q_rot_z = [0, 0, math.sin(half_angle), math.cos(half_angle)]

print(f"\n=== Expected Z-axis Rotation ===")
print(f"Angle: {TENTING_ANGLE}°")
print(f"Quaternion: {q_rot_z}")
print(f"cos(a): {cos_a}, sin(a): {sin_a}")

# Print expected transformation for Node 0 (PCB body)
print(f"\n=== Expected Node 0 (PCB body) Transformation ===")
print(f"Before: No transformation")
print(f"After: Should have rotation = {q_rot_z}")

# Print expected transformation for Node 1 (D21)
print(f"\n=== Expected Node 1 (D21) Transformation ===")
print(f"Before: Translation = [95.25, 1.595, 88.83000000000001], Rotation = [0.0, 0.7071067811865475, 0.0, 0.7071067811865475]")
qx, qy, qz, qw = 0.0, 0.7071067811865475, 0.0, 0.7071067811865475
q_rot_x, q_rot_y, q_rot_z_val, q_rot_w = q_rot_z
# new_qx = cos(a/2) * qx + sin(a/2) * qy
# new_qy = cos(a/2) * qy - sin(a/2) * qx
# new_qz = cos(a/2) * qz + sin(a/2) * qw
# new_qw = cos(a/2) * qw - sin(a/2) * qz
new_qx = q_rot_w * qx + q_rot_z_val * qy
new_qy = q_rot_w * qy - q_rot_z_val * qx
new_qz = q_rot_w * qz + q_rot_z_val * qw
new_qw = q_rot_w * qw - q_rot_z_val * qz
print(f"After rotation: Translation = [95.25, 1.595, 88.83000000000001] (unchanged), Rotation = [{new_qx}, {new_qy}, {new_qz}, {new_qw}]")
