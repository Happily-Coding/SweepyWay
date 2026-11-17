# Configurator ↔ config.yaml drift (blocker B22)

**Found:** 2026-11-16 (session 3), while explaining B1 to the author.
**Status:** **fixed for the default preset** (session 4). The generator now reproduces
`ergogen/config.yaml`, and `scripts/check_config_drift.mjs` (pre-push + CI) fails if that ever
stops being true. Non-default presets are still only partly covered — see §Current state at the end.

## What "checked-in config" vs "configurator-generated config" means

There are two ways `ergogen/config.yaml` comes into existence:

1. **Checked-in / hand-maintained** — the file in git. Human-edited over time (it even contains a
   `#MODIFIED` marker at the MCU pin block). This is what Ergogen actually reads.
2. **Configurator-generated** — `configurator/lib/generate.mjs` reads the current
   `ergogen/config.yaml` (exported as `CANONICAL_CONFIG`, generate.mjs line 18) as a *template*,
   then rewrites specific regions from the JSON config: pin maps from `ROW_PIN_POOL` /
   `COLUMN_PIN_POOL` (`schema.mjs` lines 256–257), the screw points, the standoff previews, the rim
   formula, etc.

They **drift**, because the generator only rewrites the regions it knows about and nothing forces
the checked-in file to match what it would emit. B1 and B4 are two different symptoms of that drift.

## Evidence 1 — the pin maps (this is B1)

Checked-in `ergogen/config.yaml`, left half (~lines 936–942):

```
P3: "R2"    P4: "R3"    P5: "R5"    P6: "R4"    P7: "R7"    P8: "R6"    P9: "R5"
```

Right half (~lines 1250–1256):

```
P3: "R2"    P4: "R3"    P5: "R4"    P6: "R5"    P7: "R5"    P8: "R6"    P9: "R7"
```

Two bugs on each half: **no pin carries R1** (so every R1 key is dead) and **two pins share R5**
(shorted GPIOs). R6 and R7 are assigned but no key uses them. `check_matrix.py` reports exactly this.

What the generator would emit — `buildPinMap()` maps rows in declaration order (the config lists
`row5 … row1`, descending) onto `ROW_PIN_POOL` = `P3,P4,P5,P6,P7`:

```
P3: R5   P4: R4   P5: R3   P6: R2   P7: R1        (P8/P9 unused)
```

A correct bijection. The generator was right; the hand-edited file was never brought back in line.

## Evidence 2 — the screw points (this is B4, and a regression risk)

`generate.mjs` (~lines 228–258) emits, for each left screw, an **explicit right-hand twin**:

```yaml
    r_screw_left_top:
      anchor:
        - ref: mirror_matrix_col1_row1
          shift: [screw_offset_x , screw_offset_y]
      key.tags:
        - right_screw
```

That is precisely B4's missing piece — ergogen addresses a mirrored point as `mirror_<name>`, and
the right half needs its own definitions tagged `right_screw`. The generator has had the fix all
along; the checked-in config never received it (there is even a TODO in the config admitting the
right side is undefined).

**But the same block writes `shift: [screw_offset_x , screw_offset_y]` with no offsets.** The
checked-in points now carry the B13 deltas (`+ 2, −0.75`, `+ 2, 0`, `+ 2, −1.5`, and the thumb's
`+ 1.65, −3.506` because its frame is rotated ~25°).

> **Therefore: running the configurator today silently reverts B13.** The screws would move back
> inside the switch cutouts, `check_assembly.py` would fail, and the plate holes would be swallowed
> again. This is the regression risk, and the reason "just adopt the generated config" is unsafe.

## Why this matters for the two fixes

- **B4** is being fixed *in `config.yaml`* (worker), aligned to the generator's structure. The
  generator is not wrong here — the file is stale.
- **B1** must be a **targeted patch of the 14 pin lines**, *not* a regeneration. Regenerating would
  fix B1 and B4 in one stroke but revert B13, and possibly the F3b work (`standoff_body_length`,
  the boss outlines) and the B17 rim formula, none of which the generator knows about.

## The real fix (do this eventually)

Make the generator the single source of truth, then regenerate once and diff to prove nothing is
lost:

1. Teach `generate.mjs` the B13 screw offsets (data, not a literal: the offsets differ per point and
   the thumb's are expressed in a rotated frame — store the final ergogen-space deltas).
2. Teach it `standoff_body_length` / `standoff_boss_height` and emit the `l_/r_standoff_bosses`
   outlines plus the 3D extrude (F3b).
3. Teach it the B17 rim derivation (it already writes the formula — verify).
4. Then run it once, `git diff` the result, and **adopt the generated file as the committed one**.
5. Add a CI gate: regenerate into a temp dir and fail if it differs from the committed
   `config.yaml` (that is what makes the drift impossible, the same way `BUILD-STAMP.txt` makes
   stale `filtered-output/` impossible).

Until step 5 exists, any configurator run can silently undo hand-fixes. That is B22.

## Current state after the B22 fix (session 4)

**What is guaranteed now.** Every measured/decided value the generator emits lives in
`configurator/lib/schema.mjs` as data — `PRESETS` (the whole `presets:` block, including the MBK
baseline that `choc_spacing` keeps and the three keys `cfx_spacing` overrides), `SCREW_SHIFTS` (the
B13 deltas **as final ergogen-space offsets**, so the rotated thumb's `+1.65 / −3.506` is stored and
not derived), `ROW_PIN_POOL`/`COLUMN_PIN_POOL` (B1) and the `case`/`fab` block of `defaults()`
(`standoff_length`, `standoff_body_length`, `pcb_thickness`, the B17 derived `case_border_height`).
`generate()` now (a) emits the per-point screw shifts instead of the bare
`screw_offset_x, screw_offset_y`, (b) leaves outline point references **exactly as written** when
the point still exists (`matrix_col2_row4` is not `matrix_col1_row4`; the old rename map silently
reshaped the thumb/hand-rest polygons) and throws instead of snapping an unresolvable reference to
the wrong key, (c) asserts that both halves carry an NPTH mounting hole (B4) instead of injecting a
second coincident `r_screws:` block next to the existing one, and (d) no longer unifies
`mcu_3dmodel_xyz_offset` (the committed 2.5/5 asymmetry is left to the config). The F3b bosses
(`l_/r_standoff_bosses`, their `extrude: standoff_boss_height` and the `l_case_3d` shift) are
preserved because the generator never rewrites them — they are template text, and the gate proves
nothing touches them.

**The gate.** `node scripts/check_config_drift.mjs` regenerates the default preset **in memory**
(it never writes `ergogen/config.yaml`), parses both documents, and compares them structurally:
comments/key order are ignored and ergogen expressions are evaluated against each file's own
`units`/`presets`, so `key.stagger: 0.25 ky` equals `4.25` and `14.0` equals `14`. Anything else
fails with the path and both values. It is step 3/4 of `scripts/pre-push.sh` and the
`config-drift` job in `.github/workflows/build.yaml`. Sanity check that the gate is honest: feeding
the previous generator's output through `ergogen` produced **19 differing artifacts** (both
`l_/r_screws_outline`, `l_/r_standoff_bosses`, both case bottoms, the plate outlines, the thumb
polygon and the PCBs — the thumb screw moved from `(131.71, −160.30)` back to `(131.70, −156.42)`,
inside the cutout); the current generator's output is **byte-identical** to the committed config's
ergogen output.

**What remains.** Only the default preset round-trips. `minimal-3x5.json` and
`row-stagger-1u.json` still cannot be regenerated faithfully: the canonical `outlines:` section
hardcodes 7-column/5-row point names (`matrix_col7_row2`, `thumbfan_col3_*`) that those layouts do
not have, so the generator now **throws** a readable error for them instead of emitting an outline
snapped to an arbitrary key. That is deliberate: a loud failure is acceptable, silent wrong
geometry is not. Making other presets work means authoring per-preset outline reference maps (or
parameterising the outlines), which is a design change, not a drift fix. The textual diff between
the generated file and the committed one is also still non-empty - comments, hand-formatted
expressions (`0.25 ky` vs `4.25`, `spread: kx` vs `17`, `+ -0.75` vs `- 0.75`) and key order only;
the values are identical, which is what the gate enforces. Adopting the generated file as the
committed one (old step 4) is therefore still optional and now safe to do at any time.
