# Configurator ↔ config.yaml drift (blocker B22)

**Found:** 2026-11-16 (session 3), while explaining B1 to the author.
**Status:** open, **not fixed**. Read this before running the configurator.

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
