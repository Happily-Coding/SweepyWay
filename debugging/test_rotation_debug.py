from pygltflib import GLTF2
import math

# Paths
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
INTERMEDIATE_GLB = "./filtered-output/pcb_plus_stl_no_tenting.glb"

def print_node_transformations(gltf, title):
    print(f"\n=== {title} ===")
    print(f"  Nodes: {len(gltf.nodes)}")
    for i in [0, 1, 2, 3, 4, 5, 27, 28, 29, 30, 31, 32]:  # Print some key nodes
        if i < len(gltf.nodes):
            node = gltf.nodes[i]
            name = node.name if hasattr(node, 'name') and node.name else 'Unnamed'
            print(f"\n  Node {i}: {name}")
            if hasattr(node, 'matrix') and node.matrix:
                print(f"    matrix: {node.matrix[:4]}...")  # Print first 4 values
            if hasattr(node, 'translation') and node.translation:
                print(f"    translation: {node.translation}")
            if hasattr(node, 'rotation') and node.rotation:
                print(f"    rotation: {node.rotation}")
            if hasattr(node, 'scale') and node.scale:
                print(f"    scale: {node.scale}")

# Load and print original PCB GLB
print("Loading original PCB GLB...")
gltf_original = GLTF2().load(LEFT_PCB_GLB)
print_node_transformations(gltf_original, "Original PCB GLB (left_pcb-3d.glb)")

# Load and print intermediate GLB
print("\nLoading intermediate GLB...")
gltf_intermediate = GLTF2().load(INTERMEDIATE_GLB)
print_node_transformations(gltf_intermediate, "Intermediate GLB (pcb_plus_stl_no_tenting.glb)")

# Now let's manually apply a -6.5 degree rotation to Node 0 and see what happens
print("\n=== Manual Rotation Test ===")
angle_deg = -6.5
angle_rad = math.radians(angle_deg)
cos_a = math.cos(angle_rad)
sin_a = math.sin(angle_rad)

# Calculate quaternion for Z-axis rotation
half_angle = angle_rad / 2
q_rot_z = [0, 0, math.sin(half_angle), math.cos(half_angle)]
print(f"  Rotation angle: {angle_deg}°")
print(f"  Z-axis rotation quaternion: {q_rot_z}")

# Test rotating Node 0 (PCB body)
node_0 = gltf_intermediate.nodes[0]
print(f"\n  Node 0 before rotation:")
print(f"    name: {node_0.name}")
if hasattr(node_0, 'translation') and node_0.translation:
    print(f"    translation: {node_0.translation}")
    x, y, z = node_0.translation[0], node_0.translation[1], node_0.translation[2]
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    print(f"    rotated translation: [{new_x:.4f}, {new_y:.4f}, {z}]")

if hasattr(node_0, 'rotation') and node_0.rotation:
    print(f"    rotation: {node_0.rotation}")
    qx, qy, qz, qw = node_0.rotation[0], node_0.rotation[1], node_0.rotation[2], node_0.rotation[3]
    new_qx = q_rot_z[3] * qx + q_rot_z[2] * qy
    new_qy = q_rot_z[3] * qy - q_rot_z[2] * qx
    new_qz = q_rot_z[3] * qz + q_rot_z[2] * qw
    new_qw = q_rot_z[3] * qw - q_rot_z[2] * qz
    print(f"    rotated rotation: [{new_qx:.4f}, {new_qy:.4f}, {new_qz:.4f}, {new_qw:.4f}]")

# Test rotating Node 27 (MCU1 - has translation)
node_27 = gltf_intermediate.nodes[27]
print(f"\n  Node 27 (MCU1) before rotation:")
if hasattr(node_27, 'translation') and node_27.translation:
    print(f"    translation: {node_27.translation}")
    x, y, z = node_27.translation[0], node_27.translation[1], node_27.translation[2]
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    print(f"    rotated translation: [{new_x:.4f}, {new_y:.4f}, {z}]")
if hasattr(node_27, 'rotation') and node_27.rotation:
    print(f"    rotation: {node_27.rotation}")

# Test rotating Node 28 (Nice_Nano_V2_Flipped)
node_28 = gltf_intermediate.nodes[28]
print(f"\n  Node 28 (Nice_Nano_V2_Flipped) before rotation:")
if hasattr(node_28, 'translation') and node_28.translation:
    print(f"    translation: {node_28.translation}")
if hasattr(node_28, 'rotation') and node_28.rotation:
    print(f"    rotation: {node_28.rotation}")

print("\n=== Debug Analysis Complete ===")
print("\nKey observations:")
print("  - Node 0: Root node (PCB body)")
print("  - Nodes 1-156: Components mounted on PCB")
print("  - The issue is that rotating around origin (0,0,0) affects PCB and components differently")
print("  - We need to understand the coordinate system relationship")
