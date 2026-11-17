# Updated 3D Model Export Issue Summary

**Last Updated:** 2026-03-08  
**Author:** User provided analysis + Investigation

---

## Source of Truth Hierarchy

The following hierarchy determines what information is authoritative:

1. **User verbal confirmation** - What the user explicitly states takes highest priority
2. **Code in .js footprint files** - The actual JavaScript footprint definitions
3. **Values in config.yaml** - The ergogen configuration values
4. **Documentation (comments, MD files)** - May contain errors or become outdated

---

## Executive Summary

Based on analysis of `ergogen/config.yaml` and footprint JavaScript files, the 3D model export issues are NOT a single unified problem. There are likely **two or three distinct issues** affecting different components:

1. **JST Connector Issue**: Completely missing from both STEP and GLB exports - likely a separate, unrelated problem
2. **MCU/Reset Switch Issue**: Nodes exist in GLB but have no mesh attached - likely related to each other but possibly different root causes
3. The investigation must treat these as separate cases until proven otherwise

---

## Component Status Summary

| Component | Footprint | STEP Export | GLB Export | Config Parameter Used |
|-----------|-----------|-------------|------------|----------------------|
| MCU (Nice Nano) | mcu_nice_nano.js | ✅ Works | ❌ Node exists, no mesh | `mcu_3dmodel_filename` |
| Reset Switch | reset_switch_smd_side.js | ✅ Works | ❌ Node exists, no mesh | `model_filename` |
| JST Connector | battery_connector_jst_ph_2.js | ❌ Missing | ❌ Missing completely | `model_filename` |
| Power Switch | power_switch_smd_side.js | ✅ Works | ✅ Works | `model_filename` |
| Choc Switch | switch_choc_v1_v2.js | ✅ Works | ✅ Works | `model_filename` |
| Pin Headers | header-preview_nano.js | ✅ Works | ✅ Works | `model_filename` |
| Standoffs | standoff-preview.js | ✅ Works | ✅ Works | Auto-selected |

---

## Issue #1: JST Connector - Completely Missing

### Symptom
- Missing from both STEP and GLB exports entirely
- No node exists in the exported files
- This is fundamentally different from MCU/Reset Switch issue

### Investigation Status
**This issue appears to be UNRELATED to the MCU/Reset Switch issue.** The JST is completely absent from exports, while MCU/Reset Switch at least have nodes (just without meshes).

### Configuration (from config.yaml)
**Source: config.yaml lines 941-951 (left_pcb), 1251-1261 (right_pcb)**

```yaml
pads_bat:
  what: ceoloide/battery_connector_jst_ph_2
  params:
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/JSTPH2-S2B-PH-K-LF-SN.step"
    model_xyz_rotation: [-90,0,0]
    model_xyz_offset: [0,1.5,0]
    model_xyz_scale: [1, 1, 1]
```

**Parameter naming is CORRECT** - The footprint uses `model_filename` (line 66 of battery_connector_jst_ph_2.js), not `connector_3dmodel_filename` as incorrectly documented in the header comments.

**Model file exists:** `component_3d_models/JSTPH2-S2B-PH-K-LF-SN.step`

### Possible Causes
1. **3D Model file issue**: The file may be corrupted, incompatible, or have formatting issues that cause KiCad to skip it entirely
2. **Footprint model reference issue**: Unlike other footprints, the model may not be included in the generated KiCad s-expression due to some condition
3. **Path resolution issue**: The `${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}` variable may not be resolving correctly for this specific component
4. **KiCad internal filtering**: KiCad may be filtering out this component before 3D export for reasons unrelated to other components

### Next Steps for JST
1. Verify the file `JSTPH2-S2B-PH-K-LF-SN.step` is valid by testing with another component
2. Check if other components using `${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}` work (they do - MCU, Reset Switch)
3. Compare the generated PCB s-expression to see if the JST `(model ...)` line is present
4. Try using an absolute path instead of the variable
5. Try a different 3D model format (WRL instead of STEP)
6. Check if KiCad 9 has specific issues with this component type

---

## Issue #2: MCU (Nice Nano) - GLB Missing Mesh

### Symptom
- STEP export: Works correctly, 3D model visible
- GLB export: Node exists with correct name ("MCU1") but `mesh: None`

### Configuration (from config.yaml)
**Source: config.yaml lines 855-898**

```yaml
promicro:
  what: ceoloide/mcu_nice_nano
  params:
    reverse_mount: true
    include_extra_pins: true
    mcu_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/Nice_Nano_V2.step"
    mcu_3dmodel_xyz_offset: [0, 0, 2.5]
    mcu_3dmodel_xyz_scale: [1, 1, 1]
    mcu_3dmodel_xyz_rotation: [0, 0, 0]
```

### Footprint Analysis: mcu_nice_nano.js

**Source: actual JavaScript code**

**Attribute** (line 514):
```
(attr through_hole allow_soldermask_bridges)
```

**3D Model Definition** (lines 553-559):
```javascript
const mcu_3dmodel = `
(model ${p.mcu_3dmodel_filename}
  (offset (xyz ${p.mcu_3dmodel_xyz_offset[0]} ${p.mcu_3dmodel_xyz_offset[1]} ${p.mcu_3dmodel_xyz_offset[2]}))
  (scale (xyz ${p.mcu_3dmodel_xyz_scale[0]} ${p.mcu_3dmodel_xyz_scale[1]} ${p.mcu_3dmodel_xyz_scale[2]}))
  (rotate (xyz ${p.mcu_3dmodel_xyz_rotation[0]} ${p.mcu_3dmodel_xyz_rotation[1]} ${p.mcu_3dmodel_xyz_rotation[2]}))
)
`
```

**Model inclusion logic** (line 568):
```javascript
${p.mcu_3dmodel_filename ? mcu_3dmodel : ''}
```

**Key observation**: This footprint has NO NPTH (Non-Plated Through-Hole) features. It uses through-hole socket pads.

---

## Issue #3: Reset Switch - GLB Missing Mesh

### Symptom
- STEP export: Works correctly, 3D model visible
- GLB export: Node exists with correct name ("RST1") but `mesh: None`

### Configuration (from config.yaml)
**Source: config.yaml lines 952-965**

```yaml
reset:
  what: ceoloide/reset_switch_smd_side
  params:
    side: F
    from: GND
    to: RST
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/EVQ-PUC02K.step"
    model_xyz_offset: [0, 0, 0]
    model_xyz_rotation: [180, 180, 0]
```

### Footprint Analysis: reset_switch_smd_side.js

**Source: actual JavaScript code**

**Attribute** (line 60):
```
(attr smd allow_soldermask_bridges)
```

**3D Model Definition** (lines 111-117):
```javascript
const model = `
(model ${p.model_filename}
  (offset (xyz ${p.model_xyz_offset[0]} ${p.model_xyz_offset[1]} ${p.model_xyz_offset[2]}))
  (scale (xyz ${p.model_xyz_scale[0]} ${p.model_xyz_scale[1]} ${p.model_xyz_scale[2]}))
  (rotate (xyz ${p.model_xyz_rotation[0]} ${p.model_xyz_rotation[1]} ${p.model_xyz_rotation[2]}))
)
`
```

**NPTH Features (OPTIONAL)** (lines 107-110):
```javascript
const bosses = `
(pad "" np_thru_hole circle (at 0 -1.375 ${180 + p.r}) (size 0.75 0.75) (drill 0.75) (layers "*.Cu" "*.Mask"))
(pad "" np_thru_hole circle (at 0 1.375 ${180 + p.r}) (size 0.75 0.75) (drill 0.75) (layers "*.Cu" "*.Mask"))
`
```

**NPTH Inclusion** (lines 122-125):
```javascript
if (p.include_bosses) {
  final += bosses
}
```

**Critical detail**: The `include_bosses` parameter defaults to `false` (line 39), meaning NPTH holes are NOT included in the current configuration. The NPTH holes EXIST in the code but are OPTIONAL and disabled.

---

## Working Components Comparison

### Power Switch (WORKS in both STEP and GLB)

**Configuration** (config.yaml lines 966-979):
```yaml
power:
  what: ceoloide/power_switch_smd_side
  params:
    side: F
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/SSSS811101--3DModel-STEP-269445.STEP"
    model_xyz_offset: [0, 0, 0]
    model_xyz_rotation: [90, 180, 90]
```

**Footprint**: power_switch_smd_side.js

**Attribute** (line 87):
```
(attr smd)
```

**NPTH Features** (lines 178-179) - **MANDATORY, ALWAYS INCLUDED**:
```
(pad "" np_thru_hole circle (at 0.025 -1.5 ${90 + p.r}) (size 0.9 0.9) (drill 0.9) (layers "*.Cu" "*.Mask"))
(pad "" np_thru_hole circle (at 0.025 1.5 ${90 + p.r}) (size 0.9 0.9) (drill 0.9) (layers "*.Cu" "*.Mask"))
```

**Key Difference**: The power switch ALWAYS includes 2 NPTH holes - they are not optional.

---

### Choc Switch (WORKS in both STEP and GLB)

**Configuration** (config.yaml lines 747-770):
```yaml
choc:
  what: ceoloide/switch_choc_v1_v2
  params:
    include_keycap: true
    hotswap: true
    side: 'B'
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/Choc_V1_Switch.step"
    model_xyz_rotation: [180, 0, 0]
```

**Footprint**: switch_choc_v1_v2.js

**Attribute** (line 213):
```
(attr exclude_from_pos_files allow_soldermask_bridges)
```

**NPTH Features** (lines 222-223):
```
(pad "" np_thru_hole circle (at 0 0 ${p.r}) (size ${p.choc_v2_support ? '5 5' : '3.4 3.4'}) (drill ${p.choc_v2_support ? '5' : '3.4'}) (layers "*.Cu" "*.Mask"))
```

**Stabilizer NPTH** (lines 231-232):
```
(pad "" np_thru_hole circle (at 5.5 0 ${p.r}) (size ${p.choc_v1_stabilizers_diameter} ${p.choc_v1_stabilizers_diameter}) (drill ${p.choc_v1_stabilizers_diameter}) (layers "*.Cu" "*.Mask"))
(pad "" np_thru_hole circle (at -5.5 0 ${p.r}) (size ${p.choc_v1_stabilizers_diameter} ${p.choc_v1_stabilizers_diameter}) (drill ${p.choc_v1_stabilizers_diameter}) (layers "*.Cu" "*.Mask"))
```

**Side NPTH** (line 367):
```
(pad "" np_thru_hole circle (at 5 -3.75 ${195 + p.r}) (size 3 3) (drill 3) (layers "*.Cu" "*.Mask"))
```

**Key Observations**:
- Uses `attr exclude_from_pos_files` (not `through_hole`)
- Has multiple NPTH holes: middle hole + stabilizer holes + side hole
- Works correctly in both STEP and GLB

---

## Comparative Analysis

### Attribute Comparison

| Footprint | Attribute | Has NPTH | NPTH Mandatory? | GLB Works |
|-----------|-----------|----------|-----------------|-----------|
| mcu_nice_nano.js | through_hole allow_soldermask_bridges | NO | N/A | NO |
| reset_switch_smd_side.js | smd allow_soldermask_bridges | OPTIONAL | No (default false) | NO |
| battery_connector_jst_ph_2.js | through_hole allow_soldermask_bridges | NO | N/A | NO |
| power_switch_smd_side.js | smd | YES (2) | YES | YES |
| switch_choc_v1_v2.js | exclude_from_pos_files allow_soldermask_bridges | YES (3+) | YES | YES |
| header-preview_nano.js | allow_soldermask_bridges | NO | N/A | YES |
| standoff-preview.js | allow_soldermask_bridges | NO | N/A | YES |

### Working Footprints Pattern

Working footprints fall into three categories:

1. **Virtual footprints** (header-preview_nano.js, standoff-preview.js): No physical pads at all
2. **Footprints with mandatory NPTH** (power_switch_smd_side.js, switch_choc_v1_v2.js): Have NPTH holes that cannot be disabled
3. **Working SMD footprints**: All working SMD footprints have NPTH features

### Broken Footprints Pattern

| Footprint | Physical Pads | NPTH | Notes |
|-----------|---------------|------|-------|
| mcu_nice_nano.js | YES (through-hole) | NO | Uses socket holes, not NPTH |
| reset_switch_smd_side.js | YES (SMD) | OPTIONAL (disabled by default) | NPTH available but disabled |
| battery_connector_jst_ph_2.js | YES (through-hole) | NO | Different issue - completely missing |

---

## Hypotheses

### Hypothesis 1: NPTH Correlation (for MCU/Reset Switch)
**Working hypothesis**: Components with NPTH (Non-Plated Through-Hole) features export correctly to GLB, while those without NPTH have nodes created but no mesh attached.

**Evidence**:
- Power switch: Has 2 mandatory NPTH → WORKS
- Choc switch: Has 3+ NPTH → WORKS
- Reset switch: Has optional NPTH (disabled by default) → BROKEN
- MCU: Has NO NPTH → BROKEN

**Test**: Enable `include_bosses: true` for reset_switch_smd_side.js and see if GLB now works.

### Hypothesis 2: Attribute Type (for MCU)
**Alternative hypothesis**: The `through_hole` attribute may cause issues with GLB export, while `smd` or `exclude_from_pos_files` works correctly.

**Evidence**:
- `through_hole`: MCU (broken), JST (broken)
- `smd`: Reset switch (broken), Power switch (works - but has NPTH)
- `exclude_from_pos_files`: Choc switch (works - has NPTH)
- `allow_soldermask_bridges`: Mixed results

**Test**: Change MCU attribute to `smd` or add NPTH holes

### Hypothesis 3: JST is Unrelated
The JST connector issue is fundamentally different - it's completely absent from exports. This suggests:
- A different root cause than MCU/Reset Switch
- Possibly a model file issue
- Possibly a path resolution issue specific to this component
- The footprint may have different model inclusion logic

---

## Investigation Commands

To verify the generated PCB files contain the 3D model references:

```bash
# Check if JST model reference exists in PCB
grep -i "jst" left_pcb.kicad_pcb

# Check if MCU model reference exists
grep -i "nice_nano" left_pcb.kicad_pcb

# Check all model references
grep "(model" left_pcb.kicad_pcb
```

---

## Recommended Tests

### Test 1: Enable NPTH for Reset Switch
Modify `config.yaml` for reset switch - add `include_bosses: true`:

**Left PCB** (line 952-965):
```yaml
reset:
  what: ceoloide/reset_switch_smd_side
  params:
    side: F
    from: GND
    to: RST
    include_bosses: true  # ADD THIS - enables NPTH holes
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/EVQ-PUC02K.step"
    model_xyz_offset: [0, 0, 0]
    model_xyz_rotation: [180, 180, 0]
```

**Right PCB** (line 1262-1276):
```yaml
reset:
  what: ceoloide/reset_switch_smd_side
  params:
    side: F
    from: GND
    to: RST
    include_bosses: true  # ADD THIS - enables NPTH holes
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/EVQ-PUC02K.step"
    model_xyz_offset: [0, 0, 0]
    model_xyz_scale: [1, 1, 1]
    model_xyz_rotation: [180, 180, 0]
```

After adding this, re-run ergogen and export, then verify if GLB now works.

### Test 2: Add NPTH to MCU Footprint
Modify `mcu_nice_nano.js` to add cosmetic NPTH holes that don't affect electrical functionality.

### Test 3: Verify JST Model File
Check if `JSTPH2-S2B-PH-K-LF-SN.step` file is valid. Try a different format (WRL).

### Test 4: Check Generated S-Expression
Examine the generated `.kicad_pcb` file to see exactly what KiCad receives for each component.

---

## Environment Details

- **KiCad Version**: 9 (from user confirmation)
- **Export Method**: KiBot
- **Build System**: GitHub Actions
- **3D Model Variable**: `${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}`

---

## Important Notes

### PCB Files Are Generated by Ergogen

The `.kicad_pcb` files in `ergogen/output/pcbs/` are **generated files** - they are recreated from:
1. `ergogen/config.yaml` - The configuration you edit
2. `ergogen/footprints/` - The footprint JavaScript definitions

**To see your config changes reflected, you must run ergogen first:**
```bash
cd ergogen
npm run build  # or whatever the ergogen command is
```

The output PCB files are NOT source files - they are derived from the config and footprints.

### Verification Requires GitHub Actions

Currently, the 3D model export verification requires:
1. Push changes to GitHub
2. Wait for GitHub Actions to run
3. Download the generated artifacts
4. Analyze the GLB/STEP files

There is no local 3D export verification yet.

### filtered-output Directory Is Manually Updated

The `filtered-output/` directory contains files that were **manually downloaded from GitHub Actions** and placed there. They are NOT automatically generated locally and can easily become outdated.

**To get fresh 3D exports:**
1. Push changes to GitHub
2. Wait for the workflow to complete
3. Download the `compressed_keyboard_files` artifact
4. Extract to update `filtered-output/`

When analyzing 3D issues, always verify you have the latest exports from GitHub Actions.

---

## Local 3D Export (Future Enhancement)

A local script to run 3D exports without pushing to GitHub would greatly accelerate debugging.

### GitHub Actions Workflow Analysis

From `.github/workflows/build.yaml`, the 3D export process consists of:

1. **Generate PCBs with Ergogen** (line 38):
   ```bash
   npm run build
   ```

2. **Run KiBot to generate 3D previews** (lines 87-94):
   ```bash
   kibot -b left_pcb right_pcb -c 3d_preview
   ```
   With environment variables:
   ```
   KICAD9_3DMODEL_DIR=<path>/component_3d_models
   PATH_TO_SWEEPYWAY_COMPONENT_MODELS=<path>/component_3d_models
   ```

3. **Output files** are written to:
   - `ergogen/output/pcbs/3d/` (STEP/GLB files)
   - `filtered-output/pcbs/3d/` (after copy step)

### Required Dependencies for Local Setup

To run 3D exports locally, you would need:

1. **Node.js 20** - For ergogen
2. **Ergogen** - Run `npm install` in project root
3. **KiCad 9** - Already installed
4. **KiBot** - Python package, can install via:
   ```bash
   pip install kibot
   # or
   uv pip install kibot
   ```
5. **Environment variables**:
   - Set `PATH_TO_SWEEPYWAY_COMPONENT_MODELS` to the full path of `component_3d_models` folder

### Local 3D Export Steps (Draft)

```bash
# 1. Navigate to project root
cd /path/to/SweepyWay

# 2. Install dependencies
npm install

# 3. Generate PCBs
npm run build

# 4. Set environment variables (Windows PowerShell)
$env:PATH_TO_SWEEPYWAY_COMPONENT_MODELS = "C:\Users\uriel\Asuntos\IRL Products\Keyboard design\SweepyWay\component_3d_models"

# 5. Run KiBot for 3D export
kibot -b left_pcb right_pcb -c 3d_preview

# 6. Check output in ergogen/output/pcbs/3d/
```

The user prefers to set up local execution themselves. This section provides the reference information needed.

---

## Historical Context: Previous Fix Attempts

### Commit 13c8ffa (2024)

**Reference:** https://github.com/Happily-Coding/SweepyWay/commit/13c8ffa8f970685f1326647f3570db3eb98de7a4

This commit made changes to fix 3D model preview issues. The user believes some of these changes may have been unnecessary or counterproductive:

**Changes made in that commit:**

1. **config.yaml**: Changed JST parameter names from `connector_3dmodel_*` to `model_*`
   - This was actually CORRECT - the footprint uses `model_filename`
   - Added `model_xyz_scale: [1, 1, 1]`

2. **footprints/ceoloide submodule update**: Updated to newer versions of:
   - `battery_connector_jst_ph_2.js`
   - `mcu_nice_nano.js`
   - `reset_switch_smd_side.js`

**Important**: The current working configuration (parameter names like `model_filename`) are the result of this commit. Some of these changes may have been correct fixes, but some may have been unnecessary since the original footprint code already used `model_filename` in some places.

When reverting or modifying footprints, be aware that some changes were made during this debugging phase and may not all be necessary.

1. `ergogen/config.yaml` - Main configuration file
2. `ergogen/footprints/ceoloide/mcu_nice_nano.js` - MCU footprint
3. `ergogen/footprints/ceoloide/reset_switch_smd_side.js` - Reset switch footprint
4. `ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js` - JST connector footprint
5. `ergogen/footprints/ceoloide/power_switch_smd_side.js` - Power switch (working)
6. `ergogen/footprints/ceoloide/switch_choc_v1_v2.js` - Choc switch (working)
7. `ergogen/footprints/ceoloide/header-preview_nano.js` - Virtual footprint (working)
8. `ergogen/footprints/ceoloide/standoff-preview.js` - Virtual footprint (working)

---

## Conclusion

The 3D model export issues are NOT a single bug but likely multiple distinct issues:

1. **JST Connector**: Completely missing - investigate separately as a different root cause
2. **MCU**: Node exists but no mesh in GLB - possibly related to missing NPTH features
3. **Reset Switch**: Node exists but no mesh in GLB - possibly related to disabled NPTH features

The correlation with NPTH holes is strong but not yet proven. The working hypothesis is that GLB export requires NPTH features to properly attach mesh geometry, while STEP export does not have this requirement.

**Recommended next action**: Test enabling `include_bosses: true` for the reset switch to see if NPTH holes resolve the GLB issue.

---

## Potential Next Steps

### Immediate Test: Enable NPTH for Reset Switch

Add `include_bosses: true` to the reset switch configuration in `config.yaml`:

**For left_pcb** (around line 952):
```yaml
reset:
  what: ceoloide/reset_switch_smd_side
  params:
    side: F
    from: GND
    to: RST
    include_bosses: true  # ADD THIS LINE
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/EVQ-PUC02K.step"
```

**For right_pcb** (around line 1262):
```yaml
reset:
  what: ceoloide/reset_switch_smd_side
  params:
    side: F
    from: GND
    to: RST
    include_bosses: true  # ADD THIS LINE
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/EVQ-PUC02K.step"
```

Then re-run ergogen and verify 3D exports.

### Create Local 3D Export Script

Instead of relying on GitHub Actions, create a local Python script that:
1. Runs ergogen (`npm run build`)
2. Sets the required environment variables
3. Runs KiBot with the `3d_preview` config
4. Outputs to `ergogen/output/pcbs/3d/`

This script would eliminate the need to push to GitHub for every test.

**All Python scripts in this project should be run with `uv run`:**
```bash
uv run python3 <script_name>.py
# or
uv run python <script_name>.py
```

The project uses `uv` for Python dependency management. Using `uv run` ensures the correct environment and dependencies are used.

### Example Local Workflow After Script Creation

```bash
# 1. Modify config.yaml or footprints as needed

# 2. Run local 3D export script
uv run python3 local_3d_export.py

# 3. Check output in ergogen/output/pcbs/3d/
#    or use verify_all_components.py to check results
uv run python3 verify_all_components.py
```

This would be much faster than pushing to GitHub for each test iteration.

---
