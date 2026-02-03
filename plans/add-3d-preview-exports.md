# Plan: Add 3D Preview Exports to KiBot Configuration

## Overview
Add 3D preview exports to KiBot configuration to generate both 3D model files and 3D rendered images, similar to what's viewable in KiCad's 3D viewer.

**IMPORTANT: Two-Phase Process**

This plan is intentionally split into two phases to minimize risk:

1. **Phase 1**: Update to KiCad 9 and verify the build still works
   - Update the KiBot Docker image from KiCad 8 to KiCad 9
   - Run the build workflow and verify all existing outputs work correctly
   - Manual verification of output files

2. **Phase 2**: Add 3D preview exports after verification
   - Create KiBot configuration for 3D exports
   - Test locally with the correct environment variable
   - Update the build workflow to include 3D exports

This approach isolates the KiCad version upgrade from the new feature addition, making it easier to troubleshoot if any issues arise.

## Research Summary

### KiBot 3D Export Capabilities

**Yes, KiBot is capable of exporting 3D previews!** Based on research:

1. **3D Model Files** (`export_3d` output type)
   - Exports PCB as 3D model files in multiple formats
   - Supported formats: STEP, GLB, STL, XAO, BREP
   - Requires KiCad 9 or newer
   - Can export with or without components
   - Configurable origin (grid, drill, center, or custom coordinates)

2. **3D Rendered Images** (`render_3d` output type)
   - Exports PNG images from KiCad's 3D viewer
   - Multiple viewing angles (top, bottom, front, rear, right, left, etc.)
   - Customizable zoom, colors, and backgrounds
   - Auto-crop options
   - Note: Documentation mentions this is deprecated in favor of Blender Export

### Recommended Formats

- **STEP** (.step) - Most common for CAD exchange, compatible with mechanical CAD tools
- **GLB** (.glb) - Binary glTF format, ideal for web viewing and interactive 3D viewers
- **PNG** - For static 3D rendered images from multiple angles

## Implementation Plan

**IMPORTANT: Multi-Step Process**

This plan is divided into two phases:
1. **Phase 1**: Update to KiCad 9 and verify the build still works
2. **Phase 2**: Add 3D preview exports after verification

### Phase 1: Update to KiCad 9

#### Step 1: Update KiBot Action to Use KiCad 9

**KiCad 9 Docker Image Available:**
- `ghcr.io/inti-cmnb/kicad9_auto:latest` - Official KiBot image with KiCad 9
- `ghcr.io/inti-cmnb/kicad9_auto_full:latest` - Full version with 3D rendering support

**Update `.github/actions/kibot/action.yaml`:**

```yaml
name: 'Run KiBot'
description: 'Run KiBot automation to generate images and gerbers'
inputs:
  boards:
    description: 'KiCad PCB names'
    required: true
  config:
    description: 'KiBot config file'
    required: true
runs:
  using: 'docker'
  image: 'docker://ghcr.io/inti-cmnb/kicad9_auto:latest'  # Changed from kicad8_auto
  entrypoint: '/bin/bash'
  args:
    - '-c'
    - |
      for board in ${{ inputs.boards }};
      do
        echo "Processing $board";
        kibot -b $GITHUB_WORKSPACE/ergogen/output/pcbs/${board}.kicad_pcb -c $GITHUB_WORKSPACE/kibot/${{ inputs.config }}.kibot.yaml
      done
      wait
      echo "✅ Finished kibot step"
```

#### Step 2: Verify Build Works with KiCad 9

After updating the Docker image, run the build workflow to ensure:
- All existing outputs (gerbers, drill files, images, PDFs) still generate correctly
- No breaking changes from KiCad 8 to KiCad 9
- The workflow completes successfully

**Verification Checklist:**
- [ ] Gerber files generate correctly
- [ ] Drill files generate correctly
- [ ] PCB images (pcbdraw) generate correctly
- [ ] PDF files generate correctly
- [ ] Position files generate correctly
- [ ] BOM files generate correctly
- [ ] No errors or warnings in the build log

**Manual Verification Step:**
After the CI build succeeds, manually verify the output files to ensure they look correct.

### Phase 2: Add 3D Preview Exports

#### Step 3: Set Up 3D Models Environment Variable

KiBot needs to know where to find your 3D models. The project has custom 3D models in `component_3d_models/` directory, including:
- STEP files: `Choc_V1_Hotswap.step`, `Choc_V1_Switch.step`, `D_SOD-123.step`, `Nice_Nano_V2.step`, `SW_SPST_EVQPE1.step`, etc.
- WRL files: `D_SOD-123.wrl`, `SW_SPST_EVQPE1.wrl`

**Environment Variable for KiCad 9:**
- `KICAD9_3DMODEL_DIR` - Path to 3D models directory (KiCad 9 specific)
- Note: KiCad 9 will automatically resolve `KICAD6_3DMODEL_DIR` to `KICAD9_3DMODEL_DIR` if not explicitly defined

**Setting the variable:**

For Windows (cmd.exe):
```cmd
set KICAD9_3DMODEL_DIR=%CD%\component_3d_models
```

For Windows (PowerShell):
```powershell
$env:KICAD9_3DMODEL_DIR = "$PWD\component_3d_models"
```

For Linux/macOS:
```bash
export KICAD9_3DMODEL_DIR="$PWD/component_3d_models"
```

**Passing to KiBot:**
```bash
KICAD9_3DMODEL_DIR="$PWD/component_3d_models" kibot -c kibot/3d_preview.kibot.yaml
```

**In GitHub Actions (add env section):**
```yaml
      - name: Run KiBot to generate 3D previews
        uses: ./.github/actions/kibot
        with:
          boards: left_pcb right_pcb
          config: 3d_preview
        env:
          KICAD9_3DMODEL_DIR: ${{ github.workspace }}/component_3d_models
```

#### Step 4: Create New KiBot Configuration File
Create `kibot/3d_preview.kibot.yaml` with simplified 3D export outputs (STEP + top + bottom only).

**File Structure:**
```yaml
kibot:
  version: 1

preflight:
  fill_zones: true
  drc: false
  run_erc: false

outputs:
  # 3D Model File Export (STEP format)
  - name: 3d_model_step
    comment: "3D model in STEP format"
    type: export_3d
    dir: ergogen/output/3d-models
    options:
      format: step
      output: '%f-3d.%x'
      origin: grid
      no_virtual: false
      download: true

  # 3D Rendered Images (top and bottom views only)
  - name: 3d_render_top
    comment: "3D rendered top view"
    type: render_3d
    dir: ergogen/output/images/3d
    options:
      view: top
      zoom: 0
      background1: '#66667F'
      background2: '#CCCCE5'
      board: '#332B16'
      output: '%f-3d-top.%x'
      download: true
      no_virtual: false

  - name: 3d_render_bottom
    comment: "3D rendered bottom view"
    type: render_3d
    dir: ergogen/output/images/3d
    extends: 3d_render_top
    options:
      view: bottom

global:
  filters:
    - number: 8
      regex: 'Unable to find KiCad configuration file'
    - number: 10
      regex: 'Unable to find KiCad user templates'
    - number: 10
      regex: 'Unable to find KiCad 3D models'
    - number: 58
      regex: 'KiCad project file not found|Missing KiCad main config file'
```

#### Step 5: Test the Configuration
Run KiBot with the new configuration to verify it works:
```bash
KICAD9_3DMODEL_DIR="$PWD/component_3d_models" kibot -c kibot/3d_preview.kibot.yaml
```

Or for individual boards:
```bash
KICAD9_3DMODEL_DIR="$PWD/component_3d_models" kibot -b ergogen/output/pcbs/left_pcb.kicad_pcb -c kibot/3d_preview.kibot.yaml
```

#### Step 6: Update Build Workflow

Add to `.github/workflows/build.yaml` after the existing KiBot steps:

```yaml
      - name: Run KiBot to generate 3D previews
        uses: ./.github/actions/kibot
        with:
          boards: left_pcb right_pcb
          config: 3d_preview
        env:
          KICAD9_3DMODEL_DIR: ${{ github.workspace }}/component_3d_models
```

#### Step 7: Document the Output Files
Create documentation explaining the generated files:
- `ergogen/output/3d-models/` - Contains STEP and GLB 3D model files
- `ergogen/output/images/3d/` - Contains PNG rendered images from multiple angles

## Key Configuration Options

### export_3d Options
- `format`: step, glb, stl, xao, brep
- `origin`: grid, drill, center, or custom 'X,Y' coordinates
- `no_virtual`: Exclude components with 'virtual' attribute
- `download`: Download missing 3D models from KiCad git
- `board_only`: Export board without components

### render_3d Options
- `view`: top, bottom, front, rear, right, left, z (isometric), etc.
- `zoom`: Positive to enlarge, negative to reduce
- `background1`, `background2`: Background gradient colors
- `board`: Board color
- `auto_crop`: Remove empty space around image
- `move_x`, `move_y`: Pan the view

## Notes

1. **KiCad Version Requirements**:
   - `export_3d` (STEP model export) requires KiCad 9 or newer
   - `render_3d` (PNG image export) works with KiCad 8+
   - KiCad 9 Docker image is available: `ghcr.io/inti-cmnb/kicad9_auto:latest`

2. **Environment Variables**:
   - KiCad 9 uses `KICAD9_3DMODEL_DIR` for 3D models path
   - KiCad 9 will automatically resolve `KICAD6_3DMODEL_DIR` to `KICAD9_3DMODEL_DIR` if not explicitly defined
   - Must set this variable to point to your `component_3d_models/` directory

3. **3D Models**: Ensure your footprints have 3D models assigned (STEP or WRL format)
   - Project has models in `component_3d_models/` directory
   - Includes: Choc switches, diodes, Nice Nano V2, buttons, etc.

4. **Multi-Step Process**: This plan is intentionally split into two phases:
   - Phase 1: Update to KiCad 9 and verify the build still works
   - Phase 2: Add 3D preview exports after verification
   - This approach minimizes risk by isolating the KiCad version upgrade

5. **render_3d Status**: Documentation indicates `render_3d` is deprecated in favor of Blender Export

6. **Alternative**: For higher quality 3D renders, consider using KiBot's `blender_export` output type

## Output Directory Structure
```
ergogen/output/
├── 3d-models/
│   └── left_pcb-3d.step
└── images/
    └── 3d/
        ├── left_pcb-3d-top.png
        └── left_pcb-3d-bottom.png
```

## References
- KiBot export_3d documentation: https://kibot.readthedocs.io/en/latest/configuration/outputs/export_3d.html
- KiBot render_3d documentation: https://kibot.readthedocs.io/en/v1.7.0/configuration/outputs/render_3d.html
- KiCad 9 3D export documentation: https://docs.kicad.org/9.0/en/kicad/kicad.html