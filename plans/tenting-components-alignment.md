# Tenting Components Alignment Plan

## Problem Statement

The final preview's components (Case, PCB, L_Cover, Palm_Rest) need to be tented at the same angle as the tenting system (6.5 degrees) so they sit on top of it instead of going through it.

## Current State Analysis

### Tenting System Creation
From [`create_tenting_system.py`](../palmrest_and_tenting_creation/create_tenting_system.py):
- **Tenting angle**: 6.5 degrees (`SLOPE_ANGLE_DEG = 6.5`)
- **Slope direction**: Z increases as X increases (line 32: `z = z_min + tan(angle) * (x - x_smallest)`)
- **Minimum height**: `Z_MIN = 3.0` mm
- **Pivot point**: At the smallest X coordinate of the polygon

### Current Transformations in create_full_3d_visual.py
From [`create_full_3d_visual.py`](../create_full_3d_visual.py):
1. **STL rotation**: -90° around X-axis (lines 27-31) to align with PCB orientation
2. **PCB translation**: +7 units along Y-axis (line 248)
3. **L_Cover translation**: -12 units along Y-axis (line 325)

### Coordinate System After -90° X Rotation
When rotating -90° around X-axis:
- Original X → stays as X
- Original Y → becomes Z (upward)
- Original Z → becomes -Y

So the tenting slope (originally Z increasing with X) becomes Y increasing with X after rotation.

## Solution

### Rotation Details
- **Angle**: 6.5 degrees (same as tenting system)
- **Axis**: X-axis (same as tenting system slope direction)
- **Direction**: Positive rotation to tilt the "tall" end up
- **Pivot**: Should be at the smallest X coordinate to match tenting system behavior

### Components to Rotate
All components that sit on top of the tenting system:
1. **Case** - the main keyboard case
2. **PCB** - the printed circuit board with components
3. **L_Cover** - the cover plate
4. **Palm_Rest** - the palm rest area

**Note**: The Tenting_System itself should NOT be rotated - it already has the slope built in.

## Implementation Plan

### Step 1: Add Tenting Angle Constant
Add a constant at the top of the file for the tenting angle:
```python
TENTING_ANGLE_DEG = 6.5  # Must match create_tenting_system.py
```

### Step 2: Modify create_glb_from_stls Function
Apply the tenting rotation to STL meshes (except Tenting_System) in the `create_glb_from_stls` function:

```python
def create_glb_from_stls(stl_files: dict, output_path: str) -> str:
    scene = trimesh.Scene()
    
    # -90° rotation around X-axis (existing)
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=-1.5708,
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    
    # Tenting rotation: 6.5° around X-axis
    tenting_angle_rad = np.deg2rad(TENTING_ANGLE_DEG)
    tenting_matrix = trimesh.transformations.rotation_matrix(
        angle=tenting_angle_rad,
        direction=[1, 0, 0],
        point=[0, 0, 0]  # Rotate around origin
    )
    
    for node_name, stl_path in stl_files.items():
        if os.path.exists(stl_path):
            mesh = trimesh.load(stl_path, force="mesh")
            mesh.apply_transform(rotation_matrix)  # Existing -90° rotation
            
            # Apply tenting rotation to all EXCEPT Tenting_System
            if node_name != "Tenting_System":
                mesh.apply_transform(tenting_matrix)
            
            scene.add_geometry(mesh, node_name=node_name, geom_name=node_name)
```

### Step 3: Modify merge_glb_files Function
Apply the tenting rotation to the PCB nodes. This requires rotating the root node of the PCB:

```python
# After moving PCB upward, also apply tenting rotation
if hasattr(pcb_gltf, 'scenes') and pcb_gltf.scenes and pcb_gltf.scenes[0].nodes:
    root_node_idx = pcb_gltf.scenes[0].nodes[0]
    root_node = pcb_gltf.nodes[root_node_idx]
    
    # Create rotation quaternion for 6.5° around X-axis
    tenting_angle_rad = np.deg2rad(TENTING_ANGLE_DEG)
    # Quaternion for rotation around X-axis: (cos(θ/2), sin(θ/2), 0, 0)
    half_angle = tenting_angle_rad / 2
    rotation_quaternion = [
        np.cos(half_angle),  # w
        np.sin(half_angle),  # x
        0,                   # y
        0                    # z
    ]
    
    # Combine with existing rotation if any
    if hasattr(root_node, 'rotation') and root_node.rotation:
        # Multiply quaternions (existing * new)
        existing_quat = root_node.rotation
        root_node.rotation = quaternion_multiply(existing_quat, rotation_quaternion)
    else:
        root_node.rotation = rotation_quaternion
```

### Step 4: Adjust Vertical Positioning
The tenting rotation will change the effective height of components. May need to adjust:
- PCB Y translation (currently +7)
- L_Cover Y translation (currently -12)

This may require testing to find optimal values.

## Technical Considerations

### Quaternion Multiplication Helper
Need to add a helper function for quaternion multiplication:
```python
def quaternion_multiply(q1, q2):
    """Multiply two quaternions q1 * q2."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return [
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ]
```

### glTF Rotation Format
glTF uses quaternions in format `[x, y, z, w]` (not `[w, x, y, z]`), so adjust accordingly:
```python
rotation_quaternion = [
    np.sin(half_angle),  # x
    0,                   # y
    0,                   # z
    np.cos(half_angle)   # w
]
```

## Summary of Changes

| File Section | Change |
|--------------|--------|
| Constants | Add `TENTING_ANGLE_DEG = 6.5` |
| `create_glb_from_stls()` | Apply tenting rotation to all STL meshes except Tenting_System |
| `merge_glb_files()` | Apply tenting rotation to PCB root node via quaternion |
| Helper functions | Add `quaternion_multiply()` function |

## Testing

After implementation:
1. Run `python create_full_3d_visual.py`
2. Open `./filtered-output/combined_scene.glb` in a 3D viewer
3. Verify all components sit on top of the tenting system
4. Check that there's no intersection between components and tenting system
