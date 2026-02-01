# Plan: Activate POS File Generation in GitHub Actions

## Current State

### What's Already Implemented

1. **POS File Generation** (`.github/workflows/build.yaml:73-77`)
   - KiBot generates POS files using `jlpcb_pos.kibot.yaml` configuration
   - Files are output to `ergogen/output/pos/` directory
   - Separate files for front and back sides

2. **Post-Processing Script** (`kibot/fix_pos_package_name.py`)
   - Replaces footprint names with JLCPCB part numbers
   - Maps `switch_choc_v1_v2` → `CPG135001S30`
   - Already tested and working (verified in `manualboms/manualpos 2026-02-01/`)

3. **KiBot Configuration** (`kibot/jlpcb_pos.kibot.yaml`)
   - Generates ASCII format position files
   - Units in millimeters
   - Separate files for front and back
   - Only SMD components (hotswap sockets are SMD)

### What's Missing

The GitHub Actions workflow does **not**:
1. Run the post-processing script on generated POS files
2. Copy the processed POS files to `filtered-output` directory for deployment

## Required Changes

### 1. Add Post-Processing Step to Workflow

Add a new step after the POS file generation (after line 77 in `.github/workflows/build.yaml`):

```yaml
- name: Post-process POS files for JLCPCB
  run: |
    for board in left_pcb right_pcb; do
      for side in bottom top; do
        input_file="ergogen/output/pos/${board}/${board}-${side}.pos"
        if [ -f "$input_file" ]; then
          python kibot/fix_pos_package_name.py "$input_file" "${input_file}-jlcpcb.pos"
        fi
      done
    done
```

### 2. Copy Processed POS Files to filtered-output

Add a step after the post-processing step:

```yaml
- name: Copy processed POS files to filtered-output
  run: |
    mkdir -p filtered-output/pos
    for board in left_pcb right_pcb; do
      for side in bottom top; do
        if [ -f "ergogen/output/pos/${board}/${board}-${side}-jlcpcb.pos" ]; then
          cp "ergogen/output/pos/${board}/${board}-${side}-jlcpcb.pos" "filtered-output/pos/"
        fi
      done
    done
```

### 3. Update Existing "Make filtered output" Step

The existing step (lines 70-72) already copies `ergogen/output/` to `filtered-output/`, but it excludes `fp-info-cache`. We need to ensure POS files are included.

Current step:
```yaml
- name: Make filtered output (excluding fp-info-cache) 1
  run: |
    rsync -a --exclude='fp-info-cache' ergogen/output/ filtered-output/
```

This should already include POS files, but we should verify the directory structure is correct.

## Expected Output Structure

After activation, the `filtered-output/` directory will contain:

```
filtered-output/
├── pos/
│   ├── left_pcb-bottom-jlcpcb.pos
│   ├── left_pcb-top-jlcpcb.pos
│   ├── right_pcb-bottom-jlcpcb.pos
│   └── right_pcb-top-jlcpcb.pos
├── gerbers/
├── images/
└── cases/
```

## POS File Format

The processed POS files will have the format:

```
### Footprint positions - created on <timestamp> ###
### Printed by KiCad version 9.0.2
## Unit = mm, Angle = deg.
## Side : bottom
# Ref     Val       Package                 PosX       PosY       Rot  Side
S1                  CPG135001S30            35.0000  -133.0000  180.0000  bottom
S2                  CPG135001S30            35.0000  -116.0000  180.0000  bottom
...
## End
```

## Workflow Changes

Here's the complete workflow section that needs modification:

```yaml
# ... existing steps ...

- name: Run KiBot to generate jlpcb pos
  uses: ./.github/actions/kibot
  with:
    boards: left_pcb right_pcb
    config: jlpcb_pos

- name: Post-process POS files for JLCPCB
  run: |
    for board in left_pcb right_pcb; do
      for side in bottom top; do
        input_file="ergogen/output/pos/${board}/${board}-${side}.pos"
        if [ -f "$input_file" ]; then
          python kibot/fix_pos_package_name.py "$input_file" "${input_file}-jlcpcb.pos"
        fi
      done
    done

- name: Copy processed POS files to filtered-output
  run: |
    mkdir -p filtered-output/pos
    for board in left_pcb right_pcb; do
      for side in bottom top; do
        if [ -f "ergogen/output/pos/${board}/${board}-${side}-jlcpcb.pos" ]; then
          cp "ergogen/output/pos/${board}/${board}-${side}-jlcpcb.pos" "filtered-output/pos/"
        fi
      done
    done

- name: Run KiBot to generate jlpcb bom
  uses: ./.github/actions/kibot
  with:
    boards: left_pcb right_pcb
    config: jlpcb_bom

# ... rest of workflow ...
```

## Benefits

1. **Automated JLCPCB Assembly**: POS files with correct part numbers will be automatically generated
2. **No Manual Steps**: Eliminates the need to manually run the post-processing script
3. **Consistent Output**: Every build will have the same POS file format
4. **Version Control**: POS files are tracked in the build artifacts
5. **Easy Deployment**: Files are automatically deployed to GitHub Pages

## Testing

After implementing the changes:

1. Trigger a workflow run (either by pushing to main or using workflow_dispatch)
2. Check the workflow logs to ensure:
   - POS files are generated by KiBot
   - Post-processing script runs successfully
   - Files are copied to filtered-output
3. Download the build artifacts
4. Verify POS files contain `CPG135001S30` instead of `switch_choc_v1_v2`

## Notes

- The post-processing script is idempotent (can be run multiple times safely)
- If a POS file doesn't exist (e.g., no components on that side), the script will skip it gracefully
- The `-jlcpcb.pos` suffix distinguishes processed files from raw POS files
- Both raw and processed files are preserved for debugging purposes

## Related Files

- `.github/workflows/build.yaml` - Main workflow file to modify
- `kibot/jlpcb_pos.kibot.yaml` - POS file generation configuration (already complete)
- `kibot/fix_pos_package_name.py` - Post-processing script (already complete)
- `ergogen/footprints/ceoloide/switch_choc_v1_v2.js` - Switch footprint with include_in_pos_files parameter
- `ergogen/config.yaml` - Config with include_in_pos_files: true for switches