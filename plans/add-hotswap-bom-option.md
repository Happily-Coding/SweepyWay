# Plan: Enhanced BOM Control for Switch Footprint

## Problem Statement

The hotswap sockets in the Choc v1/v2 switch footprint are currently hardcoded to be excluded from the Bill of Materials (BOM). This prevents users from including hotswap sockets in their BOM when ordering components.

## Solution Overview

The implementation has evolved through multiple approaches:

1. **Initial approach (deprecated):** Modified the switch footprint to include BOM control parameters
2. **Current approach (recommended):** Separate virtual footprints for hotswap sockets and keycaps

Since KiCad only allows one `attr` line per footprint, it's impossible to have a single footprint generate multiple separate BOM entries for its internal components (hotswap socket, switch, keycap). To work around this limitation, separate virtual footprints have been created.

## Current Implementation

### Main Switch Footprint: switch_choc_v1_v2.js

The main switch footprint ([`ergogen/footprints/ceoloide/switch_choc_v1_v2.js`](ergogen/footprints/ceoloide/switch_choc_v1_v2.js)) now includes:

**Parameters:**
- `switch_supplier_link` - Supplier link for switches
- `switch_mpn` - Manufacturer part number for switches
- `switch_do_not_populate` - DNP flag for switches (default: 'DNP')
- `switch_3dmodel_filename`, `switch_3dmodel_xyz_offset`, `switch_3dmodel_xyz_rotation`, `switch_3dmodel_xyz_scale` - 3D model configuration

**Note:** The main switch footprint does NOT include hotswap socket or keycap parameters. Those are handled by separate virtual footprints.

### Virtual Hotswap Socket Footprint: hs-socket-fab-preview_choc_v1_v2.js

Created a minimal virtual footprint at [`ergogen/footprints/ceoloide/hs-socket-fab-preview_choc_v1_v2.js`](ergogen/footprints/ceoloide/hs-socket-fab-preview_choc_v1_v2.js) that:

- **Designator:** 'HS' (Hotswap Socket)
- **Adds NOTHING to the PCB:** No pads, holes, or silkscreen
- **Only provides:**
  - 3D model for the hotswap socket
  - BOM entry for hotswap sockets
  - POS file entry for hotswap sockets
  - KiCad properties for supplier link, MPN, and DNP flag

**Parameters:**
```javascript
side: 'B'                              // Board side for reference
hotswap_3dmodel_filename: ''           // Path to 3D model file
hotswap_3dmodel_xyz_offset: [0, 0, 0]  // 3D model offset
hotswap_3dmodel_xyz_rotation: [0, 0, 0] // 3D model rotation
hotswap_3dmodel_xyz_scale: [1, 1, 1]   // 3D model scale
hotswap_supplier_link: ''              // Supplier URL
hotswap_mpn: ''                        // Manufacturer part number
hotswap_do_not_populate: ''            // DNP flag (default: '')
```

### Virtual Keycap Footprint: keycap-fab-preview_choc_v1_v2.js

Created a minimal virtual footprint at [`ergogen/footprints/ceoloide/keycap-fab-preview_choc_v1_v2.js`](ergogen/footprints/ceoloide/keycap-fab-preview_choc_v1_v2.js) that:

- **Designator:** 'KC' (Keycap)
- **Adds NOTHING to the PCB:** No pads, holes, or silkscreen
- **Only provides:**
  - 3D model for the keycap
  - BOM entry for keycaps
  - POS file entry for keycaps
  - KiCad properties for supplier link, MPN, and DNP flag

**Parameters:**
```javascript
side: 'B'                              // Board side for reference
keycap_3dmodel_filename: ''            // Path to 3D model file
keycap_3dmodel_xyz_offset: [0, 0, 0]   // 3D model offset
keycap_3dmodel_xyz_rotation: [0, 0, 0] // 3D model rotation
keycap_3dmodel_xyz_scale: [1, 1, 1]    // 3D model scale
keycap_supplier_link: ''               // Supplier URL
keycap_mpn: ''                         // Manufacturer part number
keycap_do_not_populate: 'DNP'          // DNP flag (default: 'DNP')
```

**Note:** The `do_not_populate` flag defaults to 'DNP' for keycaps since manufacturers typically don't populate keycaps during assembly.

### Usage in config.yaml

The current implementation uses separate virtual footprints for hotswap sockets and keycaps. Here's how to configure them:

**Main Switch Footprint (choc):**
```yaml
choc:
  what: ceoloide/switch_choc_v1_v2
  where:
    - [ leftkey]
  adjust:
    rotate: 180
  params:
    include_keycap: true
    choc_v2_support: false
    reversible: false
    hotswap: true
    side: 'B'
    keycap_width: 16.5
    keycap_height: 16.5
    include_in_pos_files: true
    # Supplier Link (optional)
    switch_supplier_link: 'https://kailhswitch.com/products/choc-v1'
    # Manufacturer Part Number (optional)
    switch_mpn: 'Kailh-Choc-PG1350'
    # DNP Flag (optional - set to 'DNP' to indicate the manufacturer should not try to place the part automatically)
    switch_do_not_populate: 'DNP'
    # 3D Model
    switch_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/Choc_V1_Switch.step"
    switch_3dmodel_xyz_rotation: [180, 0, 0]
```

**Hotswap Socket Virtual Footprint (choc_hotswap):**
```yaml
choc_hotswap:
  what: ceoloide/hs-socket-fab-preview_choc_v1_v2
  where:
    - [ leftkey]
  adjust:
    rotate: 180
  params:
    side: 'B'
    # 3D Model
    hotswap_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/Choc_V1_Hotswap.step"
    hotswap_3dmodel_xyz_rotation: [180, 0, 0]
    # Supplier Link (optional)
    hotswap_supplier_link: 'https://kailhswitch.com/products/hotswap-socket'
    # Manufacturer Part Number (optional)
    hotswap_mpn: 'Kailh-Hotswap-PG1350'
    # DNP Flag (optional - set to 'DNP' to indicate the manufacturer should not try to place the part automatically)
    hotswap_do_not_populate: ''
```

**Keycap Virtual Footprint (choc_keycap):**
```yaml
choc_keycap:
  what: ceoloide/keycap-fab-preview_choc_v1_v2
  where:
    - [ leftkey]
  adjust:
    rotate: 180
  params:
    side: 'B'
    # 3D Model
    keycap_3dmodel_filename: "${PATH_TO_SWEEPYWAY_COMPONENT_MODELS}/Choc_V1_Keycap_MBK_White_1u.step"
    keycap_3dmodel_xyz_rotation: [180, 0, 0]
    # Supplier Link (optional)
    keycap_supplier_link: 'https://mechanicalkeyboards.com/product/mbk-choc'
    # Manufacturer Part Number (optional)
    keycap_mpn: 'MBK-Choc-1u-White'
    # DNP Flag (optional - set to 'DNP' to indicate the manufacturer should not try to place the part automatically)
    keycap_do_not_populate: 'DNP'
```

## Usage

### Supplier Links

Add supplier links for easy ordering:

```yaml
params:
  # For switch footprint
  switch_supplier_link: 'https://kailhswitch.com/products/choc-v1'
  
  # For hotswap socket virtual footprint
  hotswap_supplier_link: 'https://kailhswitch.com/products/hotswap-socket'
  
  # For keycap virtual footprint
  keycap_supplier_link: 'https://mechanicalkeyboards.com/product/mbk-choc'
```

### Manufacturer Part Numbers

Add manufacturer part numbers for BOM tracking:

```yaml
params:
  # For switch footprint
  switch_mpn: 'Kailh-Choc-PG1350'
  
  # For hotswap socket virtual footprint
  hotswap_mpn: 'Kailh-Hotswap-PG1350'
  
  # For keycap virtual footprint
  keycap_mpn: 'MBK-Choc-1u-White'
```

### Do Not Populate (DNP) Flags

The `do_not_populate` flag indicates to the manufacturer that they should not try to automatically place the part during assembly.

```yaml
params:
  # For switch footprint (default: 'DNP')
  switch_do_not_populate: 'DNP'    # Don't auto-populate switches
  
  # For hotswap socket virtual footprint (default: '')
  hotswap_do_not_populate: ''      # Auto-populate hotswap sockets
  
  # For keycap virtual footprint (default: 'DNP')
  keycap_do_not_populate: 'DNP'    # Don't auto-populate keycaps
```

**Note:** Set `do_not_populate` to an empty string `''` to allow the manufacturer to auto-populate the part. Set it to `'DNP'` to mark it as do not populate.

## BOM Output Columns

When using KiCad or KiBot to generate BOMs with the virtual footprint approach, you'll get separate entries for each component type:

| Column Name | Description | Example (Switch) | Example (Hotswap) | Example (Keycap) |
|-------------|-------------|------------------|-------------------|------------------|
| Designator | Footprint designator | S1-S32 | HS1-HS32 | KC1-KC32 |
| Footprint | Footprint name | switch_choc_v1_v2 | hs-socket-fab-preview_choc_v1_v2 | keycap-fab-preview_choc_v1_v2 |
| Supplier Link | URL to supplier | https://kailhswitch.com/products/choc-v1 | https://kailhswitch.com/products/hotswap-socket | https://mechanicalkeyboards.com/product/mbk-choc |
| MPN | Manufacturer part number | Kailh-Choc-PG1350 | Kailh-Hotswap-PG1350 | MBK-Choc-1u-White |
| Do Not Populate | DNP flag | DNP | (empty) | DNP |

## Testing

After implementing the changes:

1. **Regenerate the PCB files using ergogen:**
    ```bash
    ergogen ergogen/config.yaml
    ```

2. **Check the generated KiCad files to verify:**
    - Open the generated `.kicad_pcb` file
    - Search for switch footprints (designators S1, S2, etc.)
    - Search for hotswap socket virtual footprints (designators HS1, HS2, etc.)
    - Search for keycap virtual footprints (designators KC1, KC2, etc.)
    - Verify KiCad properties are present when supplier links/MPNs are provided

3. **Generate a BOM using KiBot:**
    ```bash
    kibot -c kibot/jlpcb_bom.kibot.yaml
    ```

4. **Verify the BOM output:**
    - You should see three separate entries for each key position
    - Switch footprints (S1-S32) with switch properties
    - Hotswap socket footprints (HS1-HS32) with hotswap properties
    - Keycap footprints (KC1-KC32) with keycap properties
    - Each should have its own supplier link, MPN, and DNP flag

5. **Test DNP functionality:**
    - Set `switch_do_not_populate: 'DNP'` for some keys
    - Verify those components are marked as DNP in the BOM
    - Set `hotswap_do_not_populate: ''` to allow auto-population
    - Set `keycap_do_not_populate: 'DNP'` to mark keycaps as DNP

6. **Verify 3D preview:**
    - All three 3D models (switch, hotswap socket, keycap) should appear at each key position
    - The virtual footprints should not interfere with the actual switch footprint

## Summary of Changes

### Cleanup Changes (2026-02-11)

The following cleanup changes were made to simplify the implementation:

1. **Removed unused parameters from switch_choc_v1_v2.js:**
   - Removed: `hotswap_mpn`, `keycap_mpn`
   - Removed: `include_hotswap_in_bom`, `include_switch_in_bom`, `include_keycap_in_bom`
   - Removed: `hotswap_3dmodel_filename`, `hotswap_3dmodel_xyz_offset`, `hotswap_3dmodel_xyz_rotation`, `hotswap_3dmodel_xyz_scale`
   - Removed: `keycap_3dmodel_filename`, `keycap_3dmodel_xyz_offset`, `keycap_3dmodel_xyz_rotation`, `keycap_3dmodel_xyz_scale`
   - Removed: `hotswap_supplier_link`, `keycap_supplier_link`
   - Removed: `from` parameter (not needed for switch footprint)

2. **Renamed `dnp` to `do_not_populate` in all footprints:**
   - `switch_dnp` → `switch_do_not_populate`
   - `hotswap_dnp` → `hotswap_do_not_populate`
   - `keycap_dnp` → `keycap_do_not_populate`

3. **Set default values for `do_not_populate`:**
   - `switch_do_not_populate: 'DNP'` (default)
   - `hotswap_do_not_populate: ''` (default)
   - `keycap_do_not_populate: 'DNP'` (default)

4. **Updated config.yaml to remove unused parameters:**
   - Removed all unused parameters from switch footprint calls in `left_pcb` and `right_pcb` sections
   - Kept only relevant parameters for each footprint type

5. **Clarified documentation:**
   - Updated documentation to reflect the virtual footprint approach as the recommended solution
   - Clarified that `do_not_populate` indicates the manufacturer should not try to place the part automatically

### Files Modified

- [`ergogen/footprints/ceoloide/switch_choc_v1_v2.js`](ergogen/footprints/ceoloide/switch_choc_v1_v2.js) - Main switch footprint
- [`ergogen/footprints/ceoloide/hs-socket-fab-preview_choc_v1_v2.js`](ergogen/footprints/ceoloide/hs-socket-fab-preview_choc_v1_v2.js) - Hotswap socket virtual footprint
- [`ergogen/footprints/ceoloide/keycap-fab-preview_choc_v1_v2.js`](ergogen/footprints/ceoloide/keycap-fab-preview_choc_v1_v2.js) - Keycap virtual footprint
- [`ergogen/config.yaml`](ergogen/config.yaml) - Configuration file
- [`plans/add-hotswap-bom-option.md`](plans/add-hotswap-bom-option.md) - Documentation
