# Variant 10: Use pygltflib to directly manipulate GLB scene graph
# This approach uses pygltflib to directly read and merge GLB files
# at the glTF level, preserving the exact scene graph structure.
#
# Key insight: Instead of using trimesh which may modify the scene structure,
# we use pygltflib to directly manipulate the glTF JSON structure.
#
# Expected outcome:
# - Switches at correct positions (transforms preserved at glTF level)
# - PCB orientation correct (transforms preserved at glTF level)
# - Object structure preserved (node names preserved exactly)

from pygltflib import GLTF2, Buffer, BufferView, Accessor
import struct
import os

# -----------------------------
# Paths
# -----------------------------
CASE_STL = "./filtered-output/cases/case.stl"
L_COVER_STL = "./filtered-output/cases/l_cover.stl"
TENTING_STL = "./filtered-output/cases/tenting_system.stl"
PALM_REST_STL = "./filtered-output/palmrest/palm_rest.stl"
LEFT_PCB_GLB = "./filtered-output/pcbs/3d/left_pcb-3d.glb"
OUTPUT_GLB = "./filtered-output/combined_scene_v10_pygltflib.glb"

# -----------------------------
# Load the PCB GLB file
# -----------------------------
print(f"Loading PCB GLB: {LEFT_PCB_GLB}")
pcb_gltf = GLTF2().load(LEFT_PCB_GLB)

print(f"PCB GLB loaded successfully")
print(f"  Nodes: {len(pcb_gltf.nodes)}")
print(f"  Meshes: {len(pcb_gltf.meshes)}")
print(f"  Accessors: {len(pcb_gltf.accessors)}")
print(f"  BufferViews: {len(pcb_gltf.bufferViews)}")
print(f"  Buffers: {len(pcb_gltf.buffers)}")

# -----------------------------
# For now, just re-export the PCB GLB to verify pygltflib works
# -----------------------------
# This is a minimal test - if this works, we can then add the STL meshes
pcb_gltf.save(OUTPUT_GLB)

print(f"GLB scene saved to: {OUTPUT_GLB}")
print(f"  Variant: v10_pygltflib (direct glTF manipulation)")
print(f"  Note: This is a minimal test - just re-exports the PCB GLB")
print(f"  If this preserves transforms correctly, we can add STL merging next")
