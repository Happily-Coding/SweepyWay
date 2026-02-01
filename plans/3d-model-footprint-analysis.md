# 3D Model Footprint Analysis for SweepyWay Keyboard

## Executive Summary

This document analyzes the footprint configurations for the controller, power switch, SMD diodes, reset switch, and JST PH connector in the SweepyWay keyboard project. It identifies which footprints currently support 3D models, which don't, and provides recommendations for adding 3D model support.

**Note:** Reset switch and JST PH connector 3D model implementation is deferred for now.

## Current Status Overview

### 1. Controller (Nice!Nano V2)

**Footprint File:** [`ergogen/footprints/ceoloide/mcu_nice_nano.js`](../ergogen/footprints/ceoloide/mcu_nice_nano.js)

**3D Model Support:** ✅ **YES - Already Configured**

**Parameters Available:**
- `mcu_3dmodel_filename`: Path to STEP/WRL file
- `mcu_3dmodel_xyz_offset`: [x, y, z] offset in mm
- `mcu_3dmodel_xyz_scale`: [x, y, z] scale factors
- `mcu_3dmodel_xyz_rotation`: [x, y, z] rotation in degrees

**Current Usage in config.yaml:**
```yaml
promicro:
  what: ceoloide/mcu_nice_nano
  params:
    reverse_mount: true
    include_extra_pins: true
    # Pin assignments...
```

**Status:** The footprint supports 3D models but the parameters are not currently set in [`config.yaml`](../ergogen/config.yaml:805-844).

**Available 3D Model:**
- File exists: [`component_3d_models/Nice_Nano_V2.step`](../component_3d_models/Nice_Nano_V2.step)
- Source: https://github.com/infused-kim/kb_ergogen_fp/tree/main/3d_models

**Recommendation:** ✅ **EASY TO CONFIGURE** - Add the 3D model parameters to the config.yaml file.

---

### 2. Power Switch (Alps SSSS811101)

**Footprint File:** [`ergogen/footprints/ceoloide/power_switch_smd_side.js`](../ergogen/footprints/ceoloide/power_switch_smd_side.js)

**3D Model Support:** ✅ **YES - Already Configured**

**Parameters Available:**
- `switch_3dmodel_filename`: Path to STEP/WRL file
- `switch_3dmodel_xyz_offset`: [x, y, z] offset in mm
- `switch_3dmodel_xyz_scale`: [x, y, z] scale factors
- `switch_3dmodel_xyz_rotation`: [x, y, z] rotation in degrees

**Current Usage in config.yaml:**
```yaml
power:
  what: ceoloide/power_switch_smd_side
  params:
    side: F
  adjust:
    rotate: 90
  where:
    ref: mcu
    shift: [mcu_x/2 +16, 8]
```

**Status:** The footprint supports 3D models but the parameters are not currently set in [`config.yaml`](../ergogen/config.yaml:863-873).

**Available 3D Model Sources:**
- UltraLibrarian: https://app.ultralibrarian.com/details/877b6255-2882-11e9-ab3a-0a3560a4cccc/Alps-Electric/SSSS811101
- SnapEDA: https://www.snapeda.com/parts/SSSS811101/ALPS/view-part/
- Datasheet: https://cdn.shopify.com/s/files/1/0618/5674/3655/files/ALPS-SSSS811101.pdf?v=1670451309

**Recommendation:** ✅ **EASY TO CONFIGURE** - Download a 3D model and add the parameters to config.yaml.

---

### 3. SMD Diode (SOD-123 Package - 1N4148W)

**Footprint File:** [`ergogen/footprints/ceoloide/diode_tht_sod123.js`](../ergogen/footprints/ceoloide/diode_tht_sod123.js)

**3D Model Support:** ✅ **YES - Already Configured**

**Parameters Available:**
- `diode_3dmodel_filename`: Path to STEP/WRL file
- `diode_3dmodel_xyz_offset`: [x, y, z] offset in mm
- `diode_3dmodel_xyz_scale`: [x, y, z] scale factors
- `diode_3dmodel_xyz_rotation`: [x, y, z] rotation in degrees

**Current Usage in config.yaml:**
```yaml
diode:
  what: ceoloide/diode_tht_sod123
  where:
    - leftkey
  params:
    from: "{{colrow}}"
    to: "{{row_net}}"
    side: F
    include_tht: false
    reversible: false
  adjust:
    shift: [horizontal_diode_shift,vertical_diode_shift]
    rotate: 90 + diode_rotation
```

**Status:** The footprint supports 3D models but the parameters are not currently set in [`config.yaml`](../ergogen/config.yaml:791-803).

**Available 3D Model Sources:**
- UltraLibrarian: Search for "SOD-123" or "1N4148W"
- SnapEDA: https://www.snapeda.com/ (search for 1N4148W)
- Datasheet: https://cdn.shopify.com/s/files/1/0618/5674/3655/files/Semtech-1N4148W.pdf?v=1670451309
- KiCad library: Many KiCad installations include SOD-123 3D models in the default libraries

**Recommendation:** ✅ **EASY TO CONFIGURE** - Download a 3D model and add the parameters to config.yaml.

**Note:** Since there are multiple diodes in the keyboard (one per key), adding 3D models for all of them may significantly increase the file size and rendering time. Consider whether you need 3D models for all diodes or just a representative sample.

---

### 4. Reset Switch (Panasonic EVQ-PU[A|C|J|L]02K) ⏸️ **DEFERRED**

**Footprint File:** [`ergogen/footprints/ceoloide/reset_switch_smd_side.js`](../ergogen/footprints/ceoloide/reset_switch_smd_side.js)

**3D Model Support:** ❌ **NO - Not Configured**

**Parameters Available:** None

**Current Usage in config.yaml:**
```yaml
reset:
  what: ceoloide/reset_switch_smd_side
  params:
    side: F
    from: GND
    to: RST
  adjust:
    rotate: 270
  where:
    ref: mcu
    shift: [mcu_x/2 +18 +2, -0]
```

**Status:** The footprint does NOT have 3D model parameters. The code would need to be modified.

**Available 3D Model Sources:**
- SnapEDA: https://www.snapeda.com/parts/EVQ-PUC02K/Panasonic/view-part/
- UltraLibrarian: https://app.ultralibrarian.com/details/a0479524-2b3d-11ea-a124-0ad2c9526b44/Panasonic/EVQ-PUJ02K
- Datasheet: https://cdn.shopify.com/s/files/1/0618/5674/3655/files/PANASONIC-EVQPUC02K.pdf?v=1670451309

**Recommendation:** ⚠️ **REQUIRES CODE MODIFICATION** - Add 3D model parameters to the footprint file following the pattern used in power_switch_smd_side.js.

---

### 5. JST PH 2-Pin Battery Connector ⏸️ **DEFERRED**

**Footprint File:** [`ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js`](../ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js)

**3D Model Support:** ❌ **NO - Not Configured**

**Parameters Available:** None

**Current Usage in config.yaml:**
```yaml
pads_bat:
  what: ceoloide/battery_connector_jst_ph_2
  params:
  where:
    ref: mcu
    shift: [mcu_x/2 +22, -10]
    rotate: 270
```

**Status:** The footprint does NOT have 3D model parameters. The code would need to be modified.

**Available 3D Model Sources:**
- JST official website may have CAD models
- SnapEDA typically has JST connector models
- Datasheet: https://cdn.shopify.com/s/files/1/0618/5674/3655/files/JST-S2B-PH-K.pdf?v=1670451309

**Recommendation:** ⚠️ **REQUIRES CODE MODIFICATION** - Add 3D model parameters to the footprint file.

---

## Summary Table

| Component | Footprint Has 3D Support? | Configured in YAML? | Action Required | Priority |
|-----------|---------------------------|---------------------|-----------------|----------|
| Nice!Nano V2 Controller | ✅ Yes | ❌ No | Add parameters to config.yaml | High |
| Power Switch (SSSS811101) | ✅ Yes | ❌ No | Add parameters to config.yaml | High |
| SMD Diode (SOD-123) | ✅ Yes | ❌ No | Add parameters to config.yaml | Medium |
| Reset Switch (EVQ-PU02K) | ❌ No | N/A | Modify footprint file | ⏸️ Deferred |
| JST PH Connector | ❌ No | N/A | Modify footprint file | ⏸️ Deferred |

---

## Implementation Plan

### Phase 1: Easy Wins (No Code Changes) - Current Focus

These components have 3D model support built into their footprints and only need configuration in config.yaml.

#### 1.1 Configure Nice!Nano V2 3D Model

Add to [`config.yaml`](../ergogen/config.yaml:805-844) in the `promicro` section:

```yaml
promicro:
  what: ceoloide/mcu_nice_nano
  params:
    reverse_mount: true
    include_extra_pins: true
    mcu_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/Nice_Nano_V2.step"
    mcu_3dmodel_xyz_offset: [0, 0, 0]
    mcu_3dmodel_xyz_scale: [1, 1, 1]
    mcu_3dmodel_xyz_rotation: [0, 0, 0]
    # ... rest of pin assignments
```

#### 1.2 Configure Power Switch 3D Model

First, download a 3D model from one of the sources above and save it to [`component_3d_models/`](../component_3d_models/).

Then add to [`config.yaml`](../ergogen/config.yaml:863-873) in the `power` section:

```yaml
power:
  what: ceoloide/power_switch_smd_side
  params:
    side: F
    switch_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/Alps_SSSS811101.step"
    switch_3dmodel_xyz_offset: [0, 0, 0]
    switch_3dmodel_xyz_scale: [1, 1, 1]
    switch_3dmodel_xyz_rotation: [0, 0, 0]
  adjust:
    rotate: 90
  where:
    ref: mcu
    shift: [mcu_x/2 +16, 8]
```

#### 1.3 Configure SMD Diode 3D Model

First, download a 3D model from one of the sources above and save it to [`component_3d_models/`](../component_3d_models/).

Then add to [`config.yaml`](../ergogen/config.yaml:791-803) in the `diode` section:

```yaml
diode:
  what: ceoloide/diode_tht_sod123
  where:
    - leftkey
  params:
    from: "{{colrow}}"
    to: "{{row_net}}"
    side: F
    include_tht: false
    reversible: false
    diode_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/SOD123_1N4148W.step"
    diode_3dmodel_xyz_offset: [0, 0, 0]
    diode_3dmodel_xyz_scale: [1, 1, 1]
    diode_3dmodel_xyz_rotation: [0, 0, 0]
  adjust:
    shift: [horizontal_diode_shift,vertical_diode_shift]
    rotate: 90 + diode_rotation
```

**Important Note:** The SweepyWay keyboard has multiple diodes (one per key). Adding 3D models for all diodes will:
- Increase the KiCad file size significantly
- Slow down 3D rendering in KiCad
- May not provide much additional value since diodes are small and uniform

**Recommendation:** Consider starting with just a few diodes to test, or skip diode 3D models entirely if they don't add significant value to your design verification process.

### Phase 2: Deferred - Code Modifications Required ⏸️

The following components require code modifications to their footprint files. Implementation is deferred for now.

#### 2.1 Add 3D Model Support to Reset Switch Footprint

Modify [`ergogen/footprints/ceoloide/reset_switch_smd_side.js`](../ergogen/footprints/ceoloide/reset_switch_smd_side.js):

1. Add parameters to the `params` object (around line 34):
```javascript
module.exports = {
  params: {
    designator: 'RST',
    side: 'F',
    reversible: false,
    include_bosses: false,
    include_silkscreen: true,
    include_courtyard: false,
    switch_3dmodel_filename: '',
    switch_3dmodel_xyz_offset: [0, 0, 0],
    switch_3dmodel_xyz_rotation: [0, 0, 0],
    switch_3dmodel_xyz_scale: [1, 1, 1],
    from: { type: 'net', value: 'GND' },
    to: { type: 'net', value: 'RST' },
  },
```

2. Add 3D model generation code before the `common_end` (around line 107):
```javascript
    const switch_3dmodel = `
    (model ${p.switch_3dmodel_filename}
      (offset (xyz ${p.switch_3dmodel_xyz_offset[0]} ${p.switch_3dmodel_xyz_offset[1]} ${p.switch_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.switch_3dmodel_xyz_scale[0]} ${p.switch_3dmodel_xyz_scale[1]} ${p.switch_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.switch_3dmodel_xyz_rotation[0]} ${p.switch_3dmodel_xyz_rotation[1]} ${p.switch_3dmodel_xyz_rotation[2]}))
    )
    `
```

3. Add conditional inclusion before `common_end` (around line 132):
```javascript
    if (p.switch_3dmodel_filename) {
      final += switch_3dmodel
    }

    final += common_end;
```

4. Update config.yaml to use the new parameters (similar to power switch).

#### 2.2 Add 3D Model Support to JST PH Connector Footprint

Modify [`ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js`](../ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js):

1. Add parameters to the `params` object (around line 43):
```javascript
module.exports = {
  params: {
    designator: 'JST',
    side: 'F',
    reversible: false,
    include_traces: true,
    trace_width: 0.250,
    include_silkscreen: true,
    include_fabrication: true,
    include_courtyard: true,
    connector_3dmodel_filename: '',
    connector_3dmodel_xyz_offset: [0, 0, 0],
    connector_3dmodel_xyz_rotation: [0, 0, 0],
    connector_3dmodel_xyz_scale: [1, 1, 1],
    BAT_P: { type: 'net', value: 'BAT_P' },
    BAT_N: { type: 'net', value: 'GND' },
  },
```

2. Add 3D model generation code before `standard_closing` (around line 283):
```javascript
    const connector_3dmodel = `
    (model ${p.connector_3dmodel_filename}
      (offset (xyz ${p.connector_3dmodel_xyz_offset[0]} ${p.connector_3dmodel_xyz_offset[1]} ${p.connector_3dmodel_xyz_offset[2]}))
      (scale (xyz ${p.connector_3dmodel_xyz_scale[0]} ${p.connector_3dmodel_xyz_scale[1]} ${p.connector_3dmodel_xyz_scale[2]}))
      (rotate (xyz ${p.connector_3dmodel_xyz_rotation[0]} ${p.connector_3dmodel_xyz_rotation[1]} ${p.connector_3dmodel_xyz_rotation[2]}))
    )
    `
```

3. Add conditional inclusion before `standard_closing` (around line 325):
```javascript
    final += standard_closing;
    if (p.connector_3dmodel_filename) {
      final += connector_3dmodel
    }
    if (p.reversible && p.include_traces) {
      final += reversible_traces;
    }
```

4. Update config.yaml to use the new parameters.

---

## Additional Resources

### 3D Model Sources

1. **infused-kim's 3D Models** (Already used in project):
   - https://github.com/infused-kim/kb_ergogen_fp/tree/main/3d_models
   - Contains: Choc switches, keycaps, Nice!Nano V2, and more

2. **GrabCAD**:
   - https://grabcad.com/library/nice-nano-v2-1
   - https://grabcad.com/library/kailh-low-profile-mechanical-keyboard-switch-1

3. **UltraLibrarian**:
   - Alps SSSS811101: https://app.ultralibrarian.com/details/877b6255-2882-11e9-ab3a-0a3560a4cccc
   - Panasonic EVQ-PUJ02K: https://app.ultralibrarian.com/details/a0479524-2b3d-11ea-a124-0ad2c9526b44

4. **SnapEDA**:
   - Alps SSSS811101: https://www.snapeda.com/parts/SSSS811101/ALPS/view-part/
   - Panasonic EVQ-PUC02K: https://www.snapeda.com/parts/EVQ-PUC02K/Panasonic/view-part/

5. **Printables** (For printable dummy models):
   - Choc V1/V2 dummies: https://www.printables.com/model/716753-kaliah-choc-v1-v2-dummy/files

### Celoide Footprints Documentation

- https://github.com/ceoloide/ergogen-footprints
- The footprints already follow a consistent pattern for 3D model support

---

## Performance Considerations for Diode 3D Models

The SweepyWay keyboard uses a significant number of diodes (one per key). Before adding 3D models to all diodes, consider:

**Pros:**
- More complete visualization of the board
- Can verify diode orientation and placement
- Useful for documentation and presentations

**Cons:**
- **File Size Impact:** Each 3D model adds to the KiCad file size (typically 50-200KB per model)
- **Rendering Performance:** With 30+ diodes, 3D viewer may become sluggish
- **Limited Value:** Diodes are small, uniform components that don't typically cause clearance issues
- **Build Time:** Ergogen generation may take longer

**Recommendations:**
1. Start without diode 3D models to establish baseline performance
2. If needed, add 3D models to only a few representative diodes for visualization
3. Consider using simplified/low-poly diode models if performance becomes an issue
4. Test with your specific hardware to determine if the performance impact is acceptable

---

## Testing Checklist

After implementing Phase 1 3D models:

- [ ] Run `ergogen .` in the `ergogen` directory to regenerate PCB files
- [ ] Open the generated KiCad files
- [ ] Use the 3D viewer (Alt+3) to verify models appear correctly
- [ ] Check that controller model is properly positioned and oriented
- [ ] Check that power switch model is properly positioned and oriented
- [ ] If diode 3D models added: verify they don't cause performance issues
- [ ] Verify no collisions between components
- [ ] Test with both left and right PCB configurations
- [ ] Ensure the case design accommodates the 3D models
- [ ] Check file size impact (compare before/after)

---

## Notes

1. **Environment Variable**: Remember to set `PATH_TO_SWEEPYWAY_COMPONENT_MODELS` in KiCad preferences as mentioned in the README.

2. **Model Format**: KiCad supports STEP (.step, .stp), WRL (.wrl), and GLTF (.glb, .gltf) formats. STEP is preferred for mechanical parts.

3. **Model Quality**: Ensure downloaded models are of reasonable quality and not overly complex (too many polygons can slow down KiCad).

4. **Offset and Rotation**: You may need to adjust the offset and rotation values to align models correctly with the footprint. The footprint origin is typically at the component's reference point.

5. **Reversible Footprints**: For reversible footprints, the 3D model should only appear on one side (the side where the component is mounted).

---

## Conclusion

The SweepyWay keyboard project has good 3D model support infrastructure in place. Three components (controller, power switch, and SMD diodes) can be configured immediately without code changes. Two components (reset switch and JST connector) would require minor modifications to their footprint files but implementation is deferred for now.

### Immediate Actions (Phase 1)

1. **Nice!Nano V2 Controller** - Add 3D model parameters to config.yaml (model file already exists)
2. **Power Switch** - Download 3D model and add parameters to config.yaml
3. **SMD Diodes** - Optional: Download 3D model and add parameters to config.yaml (consider performance impact)

### Deferred Actions (Phase 2)

4. **Reset Switch** - Requires footprint file modification (deferred)
5. **JST PH Connector** - Requires footprint file modification (deferred)

Implementing the Phase 1 3D models will significantly improve the ability to visualize and verify the design before manufacturing, helping to catch potential issues early in the development process. The deferred components can be addressed later if needed for more detailed design verification.