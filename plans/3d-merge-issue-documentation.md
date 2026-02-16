# 3D Model Merge Issue Documentation

## Original Problem

**Issue:** The `create_full_3d_visual.py` script produces an invalid unified 3D scene where:
1. All switches are stacked in a single location (not at their correct PCB positions)
2. The PCB is oriented differently than the rest of the 3D models (case, cover, tenting, palm rest)

**Root Cause:** The script iterates over `scene.geometry.items()` which returns raw geometries **without their transforms**. In trimesh, transforms are stored in `scene.graph`, not in geometry objects.

## Input Files

- **Left PCB GLB:** `./filtered-output/pcbs/3d/left_pcb-3d.glb` (contains ~157 nodes with proper transforms)
- **Case STL:** `./filtered-output/cases/case.stl`
- **Cover STL:** `./filtered-output/cases/l_cover.stl`
- **Tenting STL:** `./filtered-output/cases/tenting_system.stl`
- **Palm Rest STL:** `./filtered-output/palmrest/palm_rest.stl`

## Test Variants Created

### v1_baseline (Original/Broken)
**File:** `create_full_3d_visual_v1_baseline.py`

**Approach:** Iterates over `scene.geometry.items()` without transforms.

**Result:** BROKEN - switches stacked at origin, PCB orientation wrong.

---

### v2_graph_transforms
**File:** `create_full_3d_visual_v2_graph_transforms.py`

**Approach:** Uses `scene.graph.get(node_name)` to get transforms, then applies them with `geometry.apply_transform()`.

**Result:** Position/orientation CORRECT, BUT objects are split into fragments (e.g., a keycap becomes separate top/bottom/side pieces).

**Feedback:** "elements were split into the fragments that compose them"

---

### v3_scene_merge
**File:** `create_full_3d_visual_v3_scene_merge.py`

**Approach:** Uses `scene.to_mesh()` to bake transforms into vertices, then adds the merged mesh.

**Result:** Position/orientation CORRECT, BUT all objects merged into ONE object (loses S25, HS8, K8 structure).

**Feedback:** "lost object differentiation entirely"

---

### v4_graph_edges
**File:** `create_full_3d_visual_v4_graph_edges.py`

**Approach:** Iterates over `scene.graph.edges()` to get transforms, applies with `geometry.apply_transform()`.

**Result:** Same as v2 - position correct but objects fragmented.

---

### v5_reexport
**File:** `create_full_3d_visual_v5_reexport.py`

**Approach:** Exports PCB scene to temp GLB, reimports, then adds STL meshes.

**Result:** Same as v3 - correct position but merged into one object.

---

### v6_scene_transform
**File:** `create_full_3d_visual_v6_scene_transform.py`

**Approach:** Applies scene-level transform to all geometries, then uses `to_mesh()`.

**Result:** PCB orientation NOT fixed.

---

### v7_preserve_structure
**File:** `create_full_3d_visual_v7_preserve_structure.py`

**Approach:** Uses `scene.add_geometry(geometry, transform=transform_matrix)` to set transforms in scene graph without modifying geometries.

**Result:** Same as v2/v4 - objects fragmented.

**Feedback:** "same issue as 4 and 2, the elements were split into fragments"

---

### v8_copy_graph
**File:** `create_full_3d_visual_v8_copy_graph.py`

**Approach:** Copies scene graph structure directly using `scene.graph.update()`.

**Result:** Same as v2/v4/v7 - objects fragmented.

---

### v9_scene_add
**File:** `create_full_3d_visual_v9_scene_add.py`

**Approach:** Uses trimesh's `scene + scene` operator to merge scenes.

**Result:** Same issue - objects fragmented.

---

### v10_pygltflib
**File:** `create_full_3d_visual_v10_pygltflib.py`

**Approach:** Uses pygltflib to load and re-export the GLB directly.

**Result:** PCB structure PRESERVED (switches at correct positions with correct names), BUT STL models not included.

**Feedback:** "v10 did actually load the object successfully but it didnt include any of the 3d models that are not part of the left pcb"

---

### v11_hybrid
**File:** `create_full_3d_visual_v11_hybrid.py`

**Approach:** Uses pygltflib for PCB GLB (preserves structure), trimesh to create STL GLB, then merges both.

**Result:** FAILED - issues with buffer manipulation.

---

## Summary of Feedback

| Variant | Position | Orientation | Object Structure | Notes |
|---------|----------|-------------|------------------|-------|
| v1 | ❌ | ❌ | ❌ | Original broken code |
| v2 | ✅ | ✅ | ❌ | Objects fragmented |
| v3 | ✅ | ✅ | ❌ | All merged into one |
| v4 | ✅ | ✅ | ❌ | Objects fragmented |
| v5 | ✅ | ✅ | ❌ | All merged into one |
| v6 | ❌ | ❌ | ❌ | PCB orientation wrong |
| v7 | ✅ | ✅ | ❌ | Objects fragmented |
| v8 | ✅ | ✅ | ❌ | Objects fragmented |
| v9 | ✅ | ✅ | ❌ | Objects fragmented |
| v10 | ✅ | ✅ | ✅ | STL models missing |
| v11 | ❌ | ❌ | ❌ | Buffer merge failed |

## Key Insight

The PCB GLB file (from KiCad) has a proper scene graph where each component (S25 switch, HS8 hotswap, K8 keycap) is a named node with its own transform. When we extract geometries with `scene.geometry.items()`, we lose this structure.

**v10 showed that pygltflib correctly preserves this structure** - the issue is adding the STL models while maintaining the structure.

## Next Steps for New Task

1. **Build on v10's success:** v10 correctly preserved the PCB structure using pygltflib
2. **Focus on STL merging:** The challenge is adding STL models (case, cover, tenting, palm rest) to the GLB while preserving the PCB's scene graph structure
3. **Alternative approaches to try:**
   - Use Blender's Python API for GLB manipulation
   - Use a different glTF library with better merge capabilities
   - Export STL models as separate GLB files and use a GLB viewer that supports multiple files
   - Create a custom solution that manually constructs the glTF JSON structure