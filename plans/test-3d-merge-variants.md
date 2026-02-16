# Plan: Test Multiple 3D Merge Variants Simultaneously

## Problem Summary

The unified 3D scene (`combined_scene.glb`) has two issues:
1. **All switches are stacked at a single location** - transforms are lost
2. **PCB orientation is wrong** - rotation transform is lost

## Root Cause Analysis

In [`create_full_3d_visual.py`](../create_full_3d_visual.py:44-59), the current code:

```python
for node_name, geometry in left_pcb_scene.geometry.items():
    scene.add_geometry(
        geometry,
        node_name=f"Left_PCB_{node_name}",
        geom_name=f"Left_PCB_{node_name}"
    )
```

**Problem**: `scene.geometry.items()` returns raw geometries **without their transforms**. In trimesh, transforms are stored in the scene graph (`scene.graph`), not in the geometry objects.

## Testing Strategy: Create Multiple Variants

To minimize GitHub Actions pushes, we'll create **5 test variants** that will all be generated in a single run:

### Variant 1: Current Implementation (Baseline)
**File**: `create_full_3d_visual_v1_baseline.py`

Keep the current implementation as-is to have a baseline for comparison.

**Expected**: Switches stacked at origin, wrong PCB orientation.

---

### Variant 2: Use Scene Graph Transforms
**File**: `create_full_3d_visual_v2_graph_transforms.py`

Apply transforms from the scene graph before adding geometries:

```python
for node_name, geometry in left_pcb_scene.geometry.items():
    # Get the transform for this node from the scene graph
    transform = left_pcb_scene.graph.get(node_name)[0]  # Returns (transform, geometry_name)
    if transform is not None:
        # Apply the transform to a copy of the geometry
        transformed_geom = geometry.copy()
        transformed_geom.apply_transform(transform)
        scene.add_geometry(transformed_geom, ...)
    else:
        scene.add_geometry(geometry, ...)
```

**Expected**: Switches at correct positions, but PCB orientation may still be wrong.

---

### Variant 3: Merge Scenes Directly
**File**: `create_full_3d_visual_v3_scene_merge.py`

Use trimesh's scene merging capability:

```python
# Convert the loaded scene to a single scene with all transforms applied
# Then merge into the main scene
scene.add_geometry(left_pcb_scene.to_mesh(), ...)
```

Or use:
```python
# Add the entire scene at once
for name, geom in left_pcb_scene.geometry.items():
    # Get the world transform for this geometry
    world_transform = left_pcb_scene.graph.get(name)[0]
    scene.add_geometry(geom, transform=world_transform, ...)
```

**Expected**: All transforms preserved, but may have double-transform issues.

---

### Variant 4: Iterate Over Scene Graph Edges
**File**: `create_full_3d_visual_v4_graph_edges.py`

Traverse the scene graph properly using edges:

```python
# The scene.graph contains the actual transforms
# Each edge in the graph represents a parent->child relationship with a transform
for edge in left_pcb_scene.graph.edges:
    transform, geometry_name = left_pcb_scene.graph.get(edge[1])
    if geometry_name in left_pcb_scene.geometry:
        geom = left_pcb_scene.geometry[geometry_name]
        transformed = geom.copy()
        transformed.apply_transform(transform)
        scene.add_geometry(transformed, ...)
```

**Expected**: Correct transforms for all components.

---

### Variant 5: Export and Re-import
**File**: `create_full_3d_visual_v5_reexport.py`

Export the PCB scene to a temporary file and re-import:

```python
# Export the PCB scene to bytes
pcb_bytes = left_pcb_scene.export(file_type='glb')
# Re-import as a single mesh with transforms baked in
pcb_mesh = trimesh.load(trimesh.util.BytesIO(pcb_bytes), file_type='glb', force='mesh')
scene.add_geometry(pcb_mesh, ...)
```

**Expected**: All transforms baked into geometry, correct positions.

---

### Variant 6: Apply Transform to Scene Before Adding
**File**: `create_full_3d_visual_v6_scene_transform.py`

Apply transform to the entire scene before extracting geometries:

```python
# Apply a rotation to the entire PCB scene
rotation = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
left_pcb_scene.apply_transform(rotation)

# Now extract geometries - they should have the transform applied
for node_name, geometry in left_pcb_scene.geometry.items():
    scene.add_geometry(geometry, ...)
```

**Expected**: PCB orientation corrected, but switches may still be stacked.

---

## Implementation Plan

### Step 1: Create Test Scripts

Create 6 Python scripts, each implementing one variant:

1. `create_full_3d_visual_v1_baseline.py` - Current implementation
2. `create_full_3d_visual_v2_graph_transforms.py` - Use scene graph transforms
3. `create_full_3d_visual_v3_scene_merge.py` - Merge scenes directly
4. `create_full_3d_visual_v4_graph_edges.py` - Iterate over graph edges
5. `create_full_3d_visual_v5_reexport.py` - Export and re-import
6. `create_full_3d_visual_v6_scene_transform.py` - Apply transform to scene

### Step 2: Modify GitHub Workflow

Update `.github/workflows/build.yaml` to run all variants:

```yaml
- name: Run all 3D merge variants
  run: |
    for variant in v1_baseline v2_graph_transforms v3_scene_merge v4_graph_edges v5_reexport v6_scene_transform; do
      echo "Running variant: $variant"
      uv run python3 "create_full_3d_visual_${variant}.py" || echo "Variant $variant failed"
    done
```

### Step 3: Analyze Results

After the workflow runs, download the artifacts and check:
1. `combined_scene_v1.glb` - Baseline
2. `combined_scene_v2.glb` - Graph transforms
3. `combined_scene_v3.glb` - Scene merge
4. `combined_scene_v4.glb` - Graph edges
5. `combined_scene_v5.glb` - Re-export
6. `combined_scene_v6.glb` - Scene transform

Compare each variant to identify which approach:
- Correctly positions switches
- Correctly orients the PCB
- Preserves materials and colors

---

## Expected Outcomes Matrix

| Variant | Switch Positions | PCB Orientation | Materials Preserved |
|---------|-----------------|-----------------|---------------------|
| v1_baseline | ❌ Stacked | ❌ Wrong | ✅ Yes |
| v2_graph_transforms | ✅ Correct | ⚠️ May need rotation | ✅ Yes |
| v3_scene_merge | ⚠️ Unknown | ⚠️ Unknown | ⚠️ May lose |
| v4_graph_edges | ✅ Correct | ⚠️ May need rotation | ✅ Yes |
| v5_reexport | ✅ Correct | ✅ Correct | ⚠️ May lose |
| v6_scene_transform | ❌ Stacked | ✅ Correct | ✅ Yes |

---

## Recommended Approach After Testing

Based on the test results, the winning variant will likely be:
- **v2 or v4** for correct switch positions
- Combined with **v6** rotation approach if PCB orientation is still wrong

The final implementation will combine the best approaches:

```python
# 1. Load the PCB scene
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)

# 2. Apply rotation to the entire scene (if needed)
rotation = trimesh.transformations.rotation_matrix(angle, axis)
left_pcb_scene.apply_transform(rotation)

# 3. Add geometries with their transforms from the graph
for node_name, geometry in left_pcb_scene.geometry.items():
    transform = left_pcb_scene.graph.get(node_name)[0]
    if transform is not None:
        transformed = geometry.copy()
        transformed.apply_transform(transform)
        scene.add_geometry(transformed, ...)
```

---

## Files to Create

1. `create_full_3d_visual_v1_baseline.py`
2. `create_full_3d_visual_v2_graph_transforms.py`
3. `create_full_3d_visual_v3_scene_merge.py`
4. `create_full_3d_visual_v4_graph_edges.py`
5. `create_full_3d_visual_v5_reexport.py`
6. `create_full_3d_visual_v6_scene_transform.py`

## Files to Modify

1. `.github/workflows/build.yaml` - Add step to run all variants

---

## Notes

- Each variant outputs to a different file: `combined_scene_v1.glb`, `combined_scene_v2.glb`, etc.
- This allows testing all approaches in a single push
- The best variant will be used as the basis for the final implementation
- Materials/colors may be lost in some variants - this is acceptable for testing purposes
