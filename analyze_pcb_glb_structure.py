from pygltflib import GLTF2
import os

# Paths
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"

# Verify file exists
if not os.path.exists(LEFT_PCB_GLB):
    print(f"ERROR: File not found: {LEFT_PCB_GLB}")
    exit(1)

# Load the PCB GLB file
print(f"Loading PCB GLB: {LEFT_PCB_GLB}")
try:
    gltf = GLTF2().load(LEFT_PCB_GLB)
    print(f"PCB GLB loaded successfully")
except Exception as e:
    print(f"ERROR: Failed to load GLB file: {e}")
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
        print(f"  Node {i}: {node.name if hasattr(node, 'name') and node.name else 'Unnamed'}")
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

# Print mesh details
print(f"\n=== Mesh Details ===")
if hasattr(gltf, 'meshes'):
    for i, mesh in enumerate(gltf.meshes):
        print(f"  Mesh {i}: {mesh.name if hasattr(mesh, 'name') and mesh.name else 'Unnamed'}")
        print(f"    Primitives: {len(mesh.primitives) if hasattr(mesh, 'primitives') else 'Unknown'}")
        if hasattr(mesh, 'primitives'):
            for j, primitive in enumerate(mesh.primitives):
                print(f"      Primitive {j}:")
                if hasattr(primitive, 'attributes') and primitive.attributes:
                    # Handle Attributes object properly - it's a dict-like object
                    if hasattr(primitive.attributes, '__dict__'):
                        for attr_name, accessor_idx in primitive.attributes.__dict__.items():
                            if not attr_name.startswith('_') and accessor_idx is not None:
                                print(f"        {attr_name}: accessor[{accessor_idx}]")
                    else:
                        # Fallback for direct dict access
                        for attr_name, accessor_idx in primitive.attributes.items():
                            print(f"        {attr_name}: accessor[{accessor_idx}]")
                if hasattr(primitive, 'indices') and primitive.indices is not None:
                    print(f"        indices: accessor[{primitive.indices}]")
else:
    print("No meshes available")

# Print accessor details
print(f"\n=== Accessor Details ===")
if hasattr(gltf, 'accessors'):
    for i, accessor in enumerate(gltf.accessors):
        print(f"  Accessor {i}:")
        print(f"    componentType: {accessor.componentType if hasattr(accessor, 'componentType') else 'Unknown'}")
        print(f"    count: {accessor.count if hasattr(accessor, 'count') else 'Unknown'}")
        print(f"    type: {accessor.type if hasattr(accessor, 'type') else 'Unknown'}")
        print(f"    bufferView: {accessor.bufferView if hasattr(accessor, 'bufferView') else 'Unknown'}")
        if hasattr(accessor, 'min') and accessor.min:
            print(f"    min: {accessor.min}")
        if hasattr(accessor, 'max') and accessor.max:
            print(f"    max: {accessor.max}")
else:
    print("No accessors available")

# Print bufferView details
print(f"\n=== BufferView Details ===")
if hasattr(gltf, 'bufferViews'):
    for i, buffer_view in enumerate(gltf.bufferViews):
        print(f"  BufferView {i}:")
        print(f"    buffer: {buffer_view.buffer if hasattr(buffer_view, 'buffer') else 'Unknown'}")
        print(f"    byteOffset: {buffer_view.byteOffset if hasattr(buffer_view, 'byteOffset') else 'Unknown'}")
        print(f"    byteLength: {buffer_view.byteLength if hasattr(buffer_view, 'byteLength') else 'Unknown'}")
        print(f"    target: {buffer_view.target if hasattr(buffer_view, 'target') else 'Unknown'}")
else:
    print("No buffer views available")

# Print buffer details
print(f"\n=== Buffer Details ===")
if hasattr(gltf, 'buffers'):
    for i, buffer in enumerate(gltf.buffers):
        print(f"  Buffer {i}:")
        print(f"    uri: {buffer.uri if hasattr(buffer, 'uri') else 'Unknown'}")
        print(f"    byteLength: {buffer.byteLength if hasattr(buffer, 'byteLength') else 'Unknown'}")
else:
    print("No buffers available")

# Print scene details
print(f"\n=== Scene Details ===")
if hasattr(gltf, 'scenes'):
    for i, scene in enumerate(gltf.scenes):
        print(f"  Scene {i}: {scene.name if hasattr(scene, 'name') and scene.name else 'Unnamed'}")
        print(f"    Nodes: {scene.nodes if hasattr(scene, 'nodes') and scene.nodes else '[]'}")
else:
    print("No scenes available")

print(f"\nGLB structure analysis complete.")
print(f"This information will help identify compatibility issues with STL GLB files.")
