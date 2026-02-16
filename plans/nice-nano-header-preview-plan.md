# Nice!Nano Header Preview Footprint Plan

## Overview

Create a virtual footprint for displaying pin headers on the nice!nano controller in fabrication previews, POS files, and BOM - without adding any actual holes or pads to the PCB.

## Requirements

1. **Virtual Footprint**: No holes, pads, or silkscreen added to PCB
2. **3D Model**: Display header in 3D preview
3. **BOM Entry**: Include in bill of materials
4. **POS File Entry**: Include in pick-and-place file
5. **Two Headers**: One for left side, one for right side of nice!nano

## Technical Details

### Nice!Nano Dimensions (from mcu_nice_nano.js)

- Socket hole positions: X = -7.62 (left) and X = 7.62 (right)
- Row spacing: 2.54mm (standard pin header pitch)
- Number of pins per side: 12
- Y range: -12.7 to 15.24 (12 rows × 2.54mm)

### Available 3D Model

- `PinHeader_1x12_P2.54mm_Vertical.step` - Single row 12-pin vertical header
- Located in: `${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/`

### Header Positioning

The nice!nano in config.yaml is:
- Placed at `ref: mcu` 
- Rotated 90 degrees
- Has `reverse_mount: true` (MCU faces PCB)

For headers:
- Left header: positioned at the left pin row border
- Right header: positioned at the right pin row border
- Both headers should have the same rotation as the nice!nano (90 degrees)

## Implementation Plan

### Step 1: Create `header-preview_nano.js` Footprint

Create a new footprint file at:
```
ergogen/footprints/ceoloide/header-preview_nano.js
```

**Parameters:**
- `designator`: 'H' (Header)
- `side`: 'F' or 'B' (default: 'F')
- `include_silkscreen`: boolean (default: false)
- `pin_count`: number of pins (default: 12)
- `model_filename`: path to 3D model
- `model_xyz_offset`: [x, y, z] offset for 3D model positioning
- `model_xyz_rotation`: [x, y, z] rotation for 3D model
- `model_xyz_scale`: [x, y, z] scale for 3D model
- `supplier_link`: URL for BOM
- `manufacturer_part_number`: Part number for BOM
- `do_not_populate`: 'DNP' flag

**Key Features:**
- Uses `(attr exclude_from_pos_files exclude_from_bom)` is NOT set (we want it in POS/BOM)
- Or better: uses `(attr allow_soldermask_bridges)` like other preview footprints
- Includes 3D model reference
- Includes BOM properties

### Step 2: Add to config.yaml

Add two header preview entries in the `left_pcb` footprints section:

```yaml
# Left side header preview
header_left:
  what: ceoloide/header-preview_nano
  where:
    ref: mcu
  params:
    side: 'B'  # Same side as the nice_nano
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/PinHeader_1x12_P2.54mm_Vertical.step"
    model_xyz_offset: [-7.62, 0, 0]  # Offset to left pin row
    model_xyz_rotation: [0, 0, 0]  # Adjust for rotation
    supplier_link: 'https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC121LFMS-RC/810154'
    manufacturer_part_number: 'PPTC121LFMS-RC'
    do_not_populate: 'DNP'

# Right side header preview  
header_right:
  what: ceoloide/header-preview_nano
  where:
    ref: mcu
  params:
    side: 'B'
    model_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/PinHeader_1x12_P2.54mm_Vertical.step"
    model_xyz_offset: [7.62, 0, 0]  # Offset to right pin row
    model_xyz_rotation: [0, 0, 0]
    supplier_link: 'https://www.digikey.com/en/products/detail/sullins-connector-solutions/PPTC121LFMS-RC/810154'
    manufacturer_part_number: 'PPTC121LFMS-RC'
    do_not_populate: 'DNP'
```

### Step 3: Handle Rotation

The nice!nano is rotated 90 degrees in the config. The headers need to be positioned correctly:

- When MCU is rotated 90°, the X-axis becomes Y-axis and vice versa
- Headers should be placed at the correct offset relative to the MCU orientation
- The 3D model rotation may need adjustment to align properly

### Step 4: Duplicate for Right PCB

Add similar entries for `right_pcb` using `ref: mirror_mcu`.

## File Structure

```
ergogen/
├── footprints/
│   └── ceoloide/
│       ├── header-preview_nano.js  (NEW)
│       ├── standoff-preview.js     (reference)
│       └── hs-socket-fab-preview_choc_v1_v2.js  (reference)
└── config.yaml                      (MODIFY)
```

## Testing

1. Run ergogen to generate PCB files
2. Open in KiCad and verify:
   - Headers appear in 3D viewer
   - Headers are positioned correctly on nice!nano borders
   - Headers appear in BOM export
   - Headers appear in POS file

## Notes

- The `do_not_populate: 'DNP'` flag indicates these should not be auto-placed by the manufacturer
- Headers are typically hand-soldered after the MCU is installed
- The Z-offset may need adjustment based on actual header height
