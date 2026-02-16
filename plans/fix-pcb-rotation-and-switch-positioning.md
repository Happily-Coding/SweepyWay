# Plan: Fix PCB Rotation and Switch Positioning in Unified 3D Model

## Problem Analysis

### Root Cause Identified

The issue is in [`create_full_3d_visual.py`](../create_full_3d_visual.py:28-34):

```python
# Load PCB 3D models (GLB format - already contains all components with materials)
# Use scene mode to preserve the structure, then extract geometry
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)
if isinstance(left_pcb_scene, trimesh.Scene):
    left_pcb_mesh = trimesh.util.concatenate(list(left_pcb_scene.geometry.values()))
else:
    left_pcb_mesh = left_pcb_scene
```

**The problem:** When the GLB file is loaded as a `trimesh.Scene`, it contains:
- Multiple geometries (PCB board, switches, components)
- Node transforms (position, rotation, scale) for each geometry

By calling `trimesh.util.concatenate(list(left_pcb_scene.geometry.values()))`, we:
1. **Lose all node transforms** - Each geometry is concatenated into a single mesh at origin (0,0,0)
2. **Lose the scene hierarchy** - All components become one flat mesh
3. **Cause switches to merge** - Without proper transforms, switches overlap at the same position
4. **Lose PCB orientation** - The rotation transform that makes the PCB horizontal is discarded

### Why the Original GLB Files Are Correct

The KiCad-generated GLB files (`left_pcb-3d.glb`, `right_pcb-3d.glb`) contain:
- Proper scene graph with nodes
- Correct transforms for each component
- Proper orientation (PCB is horizontal)
- Switches positioned correctly at their actual locations

## Solution Design

### Approach: Preserve Scene Structure Instead of Concatenating

Instead of concatenating all geometries into one mesh, we should:
1. Keep the GLB scene structure intact
2. Apply the scene's transforms to each geometry
3. Add each transformed geometry to the combined scene individually
4. **Phase 1:** Test without rotation to see the baseline orientation
5. **Phase 2:** Apply rotation if needed based on Phase 1 results

### Implementation Strategy

#### Option 1: Add Scene to Scene (Recommended)
Use trimesh's ability to merge scenes while preserving transforms:

```python
# Load PCB as scene
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)

if isinstance(left_pcb_scene, trimesh.Scene):
    # Phase 1: Add without rotation first to see baseline orientation
    # Phase 2: Apply rotation if needed (see below)
    
    # Merge the PCB scene into the combined scene
    for node_name, geometry in left_pcb_scene.geometry.items():
        scene.add_geometry(
            geometry,
            node_name=f"Left_PCB_{node_name}",
            geom_name=f"Left_PCB_{node_name}"
        )
```

#### Option 2: Apply Transforms Before Concatenating
For each geometry in the scene, apply its node transform before concatenating:

```python
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)
if isinstance(left_pcb_scene, trimesh.Scene):
    # Get all geometries with their transforms
    transformed_geometries = []
    for node_name, geometry in left_pcb_scene.geometry.items():
        # Get the node transform for this geometry
        node = left_pcb_scene.graph.get(node_name)
        if node is not None:
            transform = left_pcb_scene.graph.get_transform(node_name)
            geometry = geometry.apply_transform(transform)
        transformed_geometries.append(geometry)
    
    # Now concatenate with all transforms applied
    left_pcb_mesh = trimesh.util.concatenate(transformed_geometries)
```

### Recommended Approach: Option 1 (Two-Phase)

**Advantages:**
- Preserves the scene hierarchy and component names
- Maintains materials and colors from GLB
- Easier to debug (can inspect individual components)
- More flexible for future modifications
- Better performance (no need to concatenate large meshes)
- **Two-phase approach allows testing before applying rotation**

## Implementation Steps

### Phase 1: Modify `create_full_3d_visual.py` (No Rotation)

Update the PCB loading section to preserve scene structure **without** applying rotation:

```python
# Load PCB 3D models (GLB format - already contains all components with materials)
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)
if isinstance(left_pcb_scene, trimesh.Scene):
    # Add each geometry from the PCB scene to the combined scene
    # This preserves all transforms from the original GLB file
    for node_name, geometry in left_pcb_scene.geometry.items():
        scene.add_geometry(
            geometry,
            node_name=f"Left_PCB_{node_name}",
            geom_name=f"Left_PCB_{node_name}"
        )
else:
    # Fallback for non-scene files
    scene.add_geometry(
        left_pcb_scene,
        node_name="Left_PCB",
        geom_name="Left_PCB"
    )
```

### Phase 2: Test Phase 1 Changes

1. Run the updated script
2. Verify that:
   - Switches are positioned correctly (not merged together)
   - All components maintain their proper spacing
   - Materials and colors are preserved
3. Check the PCB orientation:
   - Is it horizontal or vertical?
   - Does it match the original `left_pcb-3d.glb` orientation?

### Phase 3: Add Rotation (If Needed)

**Based on Phase 2 results**, if the PCB orientation is still incorrect, add rotation:

```python
# Load PCB 3D models (GLB format - already contains all components with materials)
left_pcb_scene = trimesh.load(LEFT_PCB_GLB)
if isinstance(left_pcb_scene, trimesh.Scene):
    # Apply rotation to the entire PCB scene
    # Adjust angle and axis based on Phase 2 testing
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.pi,  # 180 degrees (adjust as needed)
        direction=[1, 0, 0]  # X-axis (adjust as needed)
    )
    left_pcb_scene.apply_transform(rotation_matrix)
    
    # Add each geometry from the PCB scene to the combined scene
    for node_name, geometry in left_pcb_scene.geometry.items():
        scene.add_geometry(
            geometry,
            node_name=f"Left_PCB_{node_name}",
            geom_name=f"Left_PCB_{node_name}"
        )
else:
    # Fallback for non-scene files
    scene.add_geometry(
        left_pcb_scene,
        node_name="Left_PCB",
        geom_name="Left_PCB"
    )
```

**Possible rotation adjustments based on Phase 2 results:**
- If PCB is vertical and needs to be horizontal: Try 180° around X-axis or 90° around Y-axis
- If PCB is flipped: Try 180° around Z-axis
- If PCB is rotated: Try 90° around X-axis

## Alternative Considerations

### If Phase 1 Shows Switches Are Still Merged

If switches are still overlapping after preserving scene structure, check:
1. Whether the GLB file itself has incorrect transforms
2. Whether the `fix_glb_scale.py` script is affecting transforms
3. Whether the KiCad 3D model footprints have correct positions
4. Try Option 2 (apply transforms before concatenating) as an alternative

### If Rotation is Still Incorrect After Phase 3

If the PCB orientation is still wrong after applying the rotation, we may need to:

1. **Inspect the original GLB file** to understand its coordinate system
2. **Check the KiCad export settings** to see if there's an option to adjust orientation
3. **Apply a different rotation** based on the actual orientation needed
4. **Try multiple rotation combinations** (e.g., rotate around X then Y)

## Dependencies

- `trimesh` - Already in use
- `numpy` - Already in use (for rotation matrices in Phase 3)

## Files to Modify

1. [`create_full_3d_visual.py`](../create_full_3d_visual.py) - Main implementation (Phase 1 and Phase 3)
2. No changes needed to [`fix_glb_scale.py`](../fix_glb_scale.py) - Scale fixing is separate from orientation

## Expected Outcome

### After Phase 1:
- ✅ Switches will be positioned correctly (not merged)
- ✅ All components maintain proper spacing
- ✅ Scene hierarchy is preserved
- ✅ Materials and colors are maintained
- ⏳ PCB orientation will be visible (may need Phase 3 adjustment)

### After Phase 3 (if needed):
- ✅ PCB will be horizontal (matching other models)
- ✅ All Phase 1 benefits maintained
- ✅ The unified 3D model will be accurate and usable

## Testing Checklist

### Phase 1 Testing:
- [ ] Run `python3 create_full_3d_visual.py`
- [ ] Open `filtered-output/combined_scene.glb` in a 3D viewer
- [ ] Verify switches are not merged
- [ ] Verify all components are visible and positioned correctly
- [ ] Verify materials and colors look correct
- [ ] Compare with original `left_pcb-3d.glb` to ensure consistency
- [ ] Note the PCB orientation (horizontal/vertical, any rotation needed)

### Phase 3 Testing (if needed):
- [ ] Add rotation code based on Phase 1 observations
- [ ] Run `python3 create_full_3d_visual.py` again
- [ ] Open `filtered-output/combined_scene.glb` in a 3D viewer
- [ ] Verify PCB is horizontal
- [ ] Verify all Phase 1 benefits are maintained

## Notes

- **Two-phase approach**: First fix the scene structure (Phase 1), then adjust orientation (Phase 3)
- This allows us to see the baseline behavior before applying any rotation
- The rotation angle and axis will be determined based on Phase 1 results
- The solution preserves the scene structure, making it easier to debug and modify
- This approach is more maintainable than concatenating geometries
- If Phase 1 already produces correct orientation, Phase 3 may not be needed
