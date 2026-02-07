# Add 3D Model Support to battery_connector_jst_ph_2 Footprint

## Overview

This plan outlines the steps to add 3D model support to the [`battery_connector_jst_ph_2.js`](../ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js) footprint, following the same pattern used in other footprints like [`diode_tht_sod123.js`](../ergogen/footprints/ceoloide/diode_tht_sod123.js) and [`switch_choc_v1_v2.js`](../ergogen/footprints/ceoloide/switch_choc_v1_v2.js).

## Current Status

- **Footprint File**: [`ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js`](../ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js)
- **3D Model Support**: ❌ No - Not Configured
- **Available 3D Models**: ✅ Yes - Files already exist in [`component_3d_models/`](../component_3d_models/):
  - `JSTPH2 S2B-PH-K-S(LF)(SN).STEP`
  - `JSTPH2 S2B-PH-K-S(LF)(SN).wrl`

## Pattern Analysis

Based on analysis of other footprints, the 3D model implementation follows this pattern:

### 1. Parameters Section
Add four parameters to the `params` object:
- `<component>_3dmodel_filename`: Path to STEP/WRL file (default: '')
- `<component>_3dmodel_xyz_offset`: [x, y, z] offset in mm (default: [0, 0, 0])
- `<component>_3dmodel_xyz_scale`: [x, y, z] scale factors (default: [1, 1, 1])
- `<component>_3dmodel_xyz_rotation`: [x, y, z] rotation in degrees (default: [0, 0, 0])

### 2. Template String
Create a template string constant that generates the KiCad 3D model entry.

### 3. Conditional Inclusion
Add a conditional check before the footprint closing parenthesis to include the 3D model only if a filename is provided.

### 4. Documentation
Add parameter documentation in the comments section.

## Implementation Steps

### Step 1: Add Parameter Documentation

Add the following documentation after line 41 (after `include_courtyard` parameter description):

```javascript
//    connector_3dmodel_filename: default is ''
//      Allows you to specify the path to a 3D model STEP or WRL file to be
//      used when rendering the PCB. Use the ${VAR_NAME} syntax to point to
//      a KiCad configured path.
//    connector_3dmodel_xyz_offset: default is [0, 0, 0]
//      xyz offset (in mm), used to adjust the position of the 3d model
//      relative the footprint.
//    connector_3dmodel_xyz_scale: default is [1, 1, 1]
//      xyz scale, used to adjust the size of the 3d model relative to its
//      original size.
//    connector_3dmodel_xyz_rotation: default is [0, 0, 0]
//      xyz rotation (in degrees), used to adjust the orientation of the 3d
//      model relative the footprint.
```

### Step 2: Add Parameters to params Object

Add the following parameters to the `params` object after line 52 (after `BAT_N` parameter):

```javascript
    connector_3dmodel_filename: '',
    connector_3dmodel_xyz_offset: [0, 0, 0],
    connector_3dmodel_xyz_scale: [1, 1, 1],
    connector_3dmodel_xyz_rotation: [0, 0, 0],
```

### Step 3: Add 3D Model Template String

Add the following template string constant after line 282 (after `reversible_traces` constant):

```javascript
    const connector_3dmodel = `
        (model ${p.connector_3dmodel_filename}
            (offset (xyz ${p.connector_3dmodel_xyz_offset[0]} ${p.connector_3dmodel_xyz_offset[1]} ${p.connector_3dmodel_xyz_offset[2]}))
            (scale (xyz ${p.connector_3dmodel_xyz_scale[0]} ${p.connector_3dmodel_xyz_scale[1]} ${p.connector_3dmodel_xyz_scale[2]}))
            (rotate (xyz ${p.connector_3dmodel_xyz_rotation[0]} ${p.connector_3dmodel_xyz_rotation[1]} ${p.connector_3dmodel_xyz_rotation[2]}))
        )
        `
```

### Step 4: Add Conditional Inclusion

Modify the code after line 325 (after `final += standard_closing;`) to add conditional inclusion:

```javascript
    final += standard_closing;
    
    if (p.connector_3dmodel_filename) {
      final += connector_3dmodel
    }
    
    if (p.reversible && p.include_traces) {
      final += reversible_traces;
    }
```

**Note**: The 3D model should be added inside the footprint before the closing parenthesis, so we need to add it BEFORE `standard_closing`, not after. Let me correct this:

### Step 4 (Corrected): Add Conditional Inclusion

Modify the code around line 325 to add conditional inclusion BEFORE `standard_closing`:

```javascript
    if (p.reversible) {
      final += reversible_pads;
    } else if (p.side == "F") {
      final += front_pads;
    } else if (p.side == "B") {
      final += back_pads;
    }
    
    if (p.connector_3dmodel_filename) {
      final += connector_3dmodel
    }
    
    final += standard_closing;
    if (p.reversible && p.include_traces) {
      final += reversible_traces;
    }
```

## Expected Result

After implementation, the footprint will support 3D models that can be configured in [`ergogen/config.yaml`](../ergogen/config.yaml) like this:

```yaml
pads_bat:
  what: ceoloide/battery_connector_jst_ph_2
  params:
    connector_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/JSTPH2 S2B-PH-K-S(LF)(SN).wrl"
    connector_3dmodel_xyz_offset: [0, 0, 0]
    connector_3dmodel_xyz_scale: [1, 1, 1]
    connector_3dmodel_xyz_rotation: [0, 0, 0]
  where:
    ref: mcu
    shift: [mcu_x/2 +22, -10]
    rotate: 270
```

## Testing Checklist

After implementation:

- [ ] Verify the modified footprint file has correct syntax
- [ ] Run `ergogen .` in the `ergogen` directory to regenerate PCB files
- [ ] Open the generated KiCad files
- [ ] Use the 3D viewer (Alt+3) to verify the model appears correctly
- [ ] Check that the connector model is properly positioned and oriented
- [ ] Verify no errors in KiCad console
- [ ] Test with both STEP and WRL formats
- [ ] Test with reversible and non-reversible configurations

## Notes

1. **Parameter Naming**: Using `connector_3dmodel_*` prefix to be consistent with the component type and avoid conflicts with other parameters.

2. **Model Format**: KiCad supports both STEP (.step, .stp) and WRL (.wrl) formats. WRL is typically preferred for KiCad 3D viewer performance.

3. **Offset and Rotation**: The default values (0, 0, 0) may need adjustment based on the actual 3D model's origin and orientation. Users can fine-tune these values in their config.yaml.

4. **Reversible Footprints**: For reversible footprints, the 3D model should only appear once (not duplicated on both sides) since the component is only mounted on one side.

5. **Existing Models**: The 3D model files already exist in the project at:
   - [`component_3d_models/JSTPH2 S2B-PH-K-S(LF)(SN).STEP`](../component_3d_models/JSTPH2%20S2B-PH-K-S(LF)(SN).STEP)
   - [`component_3d_models/JSTPH2 S2B-PH-K-S(LF)(SN).wrl`](../component_3d_models/JSTPH2%20S2B-PH-K-S(LF)(SN).wrl)

## References

- Similar implementation in [`diode_tht_sod123.js`](../ergogen/footprints/ceoloide/diode_tht_sod123.js:24-36, 55-58, 102-107, 124-126)
- Similar implementation in [`switch_choc_v1_v2.js`](../ergogen/footprints/ceoloide/switch_choc_v1_v2.js:79-117, 180-191, 453-475, 535-541)
- JST PH 2.0mm connector datasheet: https://cdn.shopify.com/s/files/1/0618/5674/3655/files/JST-S2B-PH-K.pdf?v=1670451309
- 3D model source: https://www.snapeda.com/parts/S2B-PH-K-S(LF)(SN)/JST/view-part/
