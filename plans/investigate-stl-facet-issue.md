# Investigation: STL Files with 3M+ Facets

## Problem
GitHub Actions workflow fails when converting STL files to ASCII format:
- Error: `ValueError: Invalid STL file: ... - vertex data is too short at facet 3041807`
- STL files contain 3M+ facets instead of expected < 10K facets for a PCB

## Root Cause Analysis

### KiBot Configuration (kibot/3d_preview.kibot.yaml)
The STL export configuration has **no mesh quality or resolution settings**:

```yaml
- name: 3d_model_stl
  comment: "3D model in STL format for GitHub rendering"
  type: export_3d
  dir: ergogen/output/3d-models
  options:
    format: stl
    output: '%f-3d.%x'
    origin: grid
    no_virtual: false
    download: true
```

### Component Models
The component 3D models are STEP files from various sources:
- GrabCAD (kailh switches, keycaps)
- SnapEDA (ALPS power switch, Panasonic button)
- KiCad libraries (diodes)
- infused-kim (Choc switches, keycaps, Nice Nano)

STEP files are parametric and can contain very high detail.

### The Issue
When KiBot exports STEP models to STL format:
1. It tessellates the parametric STEP models into triangles
2. Without quality/resolution settings, KiBot uses default tessellation
3. Default settings are too aggressive, generating millions of facets
4. Result: 3M+ facets instead of reasonable < 10K facets

## Solution

Add STL quality settings to KiBot configuration to control tessellation:

```yaml
- name: 3d_model_stl
  comment: "3D model in STL format for GitHub rendering"
  type: export_3d
  dir: ergogen/output/3d-models
  options:
    format: stl
    output: '%f-3d.%x'
    origin: grid
    no_virtual: false
    download: true
    # Add quality settings to reduce facet count
    grid_size: 0.1  # Maximum deviation from the original shape (mm)
    min_angle: 10   # Minimum angle between facets (degrees)
```

### Available KiBot Options for export_3d
According to KiBot documentation, the `export_3d` output type supports:
- `grid_size`: Maximum deviation from the original shape (default: 0.01 mm)
- `min_angle`: Minimum angle between facets (default: 5 degrees)

### Recommended Settings
- `grid_size: 0.1` or `0.2` (default is 0.01, too aggressive)
- `min_angle: 10` or `15` (default is 5, too aggressive)

These settings will:
- Reduce facet count from 3M+ to reasonable < 100K
- Maintain sufficient quality for GitHub 3D preview
- Keep file sizes manageable for ASCII conversion

## Implementation Steps

1. Update `kibot/3d_preview.kibot.yaml` with quality settings
2. Test locally to verify facet count is reasonable
3. Commit and push the fix
4. Verify GitHub Actions workflow succeeds

## Alternative Solutions

If KiBot quality settings don't work:
1. Use STEP format instead of STL for GitHub preview (if supported)
2. Skip STL to ASCII conversion entirely
3. Use a different STL tessellation tool with quality control
4. Simplify component STEP models before export