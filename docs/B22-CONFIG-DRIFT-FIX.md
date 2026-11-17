# B22 — the configurator generator can no longer revert a hand-fix

Session 4, 2026-11-16. Scope: `configurator/lib/{generate,schema}.mjs`, `configurator/server.mjs`,
`scripts/check_config_drift.mjs` (new), `scripts/pre-push.sh`, `.github/workflows/build.yaml`.
`ergogen/config.yaml` was **never written** — `git diff ergogen/config.yaml` is empty.

Analysis of the bug itself: `docs/CONFIGURATOR-DRIFT.md` (its final section is the "current state").
This file is only the raw evidence.

## 1. Enumerated: everything `generate()` rewrites

| # | Region | How |
|---|---|---|
| 1 | `presets:` … `units:` | whole span replaced (`buildPresets`) |
| 2 | `points:` … `outlines:` | whole span replaced (`buildPoints`) — incl. the screw points |
| 3 | `top_plate_thickness`, `case_bottom_thickness`, `pcb_thickness`, `standoff_length`, `standoff_body_length`, `case_border_height`, `case_wall_thickness` | one `setScalar` each |
| 4 | `keycap_width` / `keycap_height` (the numeric ones, 10-space indent) | `setScalar` (global) |
| 5 | `choc_v2_support` | `true` unless the switch is V1 |
| 6 | both `promicro` pin blocks (`# Pin Assignments` … `adjust:`) | `rewritePinBlocks` (`buildPinMap`) |
| 7 | `matrix_*` point references inside `outlines:` | `rewritePointRefs` |
| 8 | (removed) an `r_screws:` mounting-hole block injected beside the existing `screws:` block | now an assertion |
| 9 | (removed) `mcu_3dmodel_xyz_offset` unified to `[0, 0, 5]` | now left alone |

## 2. BEFORE — generator output vs committed `ergogen/config.yaml`

`node configurator/lib/generate.mjs configurator/presets/sweepyway.json --out C:/tmp/b22/gen-before.yaml`
then `diff -u ergogen/config.yaml C:/tmp/b22/gen-before.yaml` (430 lines). The *semantic* hunks:

1. **Screw shifts lost (B13)** — every point became `shift: [screw_offset_x , screw_offset_y]`
   instead of `+ 2 / −0.75`, `+ 2 / 0`, `+ 2 / −1.5`, thumb `+ 1.65 / −3.506`.
2. **Outline point references mis-mapped** — `matrix_col2_row4 → matrix_col1_row4`,
   `matrix_col2_row3 → matrix_col1_row4`, `matrix_col6_row3 → matrix_col6_row4`: the hand-rest /
   thumb polygons were snapped to different keys.
3. **A second `r_screws:` mounting-hole block added** — the committed right half already has one
   (`screws:` under `right_pcb`), so the generated config got two coincident NPTH holes.
4. **`mcu_3dmodel_xyz_offset: [0, 0, 2.5]` (left) rewritten to `[0, 0, 5]`.**
5. Preset text replaced (`ky: 18` / `keycap_x_1u: 17.5` of the MBK baseline overwritten with the
   selected CFX numbers, `mbk_spacing` added).
6. Comments/formatting (cosmetic): hand comments inside `presets:`, `points:`, both pin blocks,
   `0.25 ky` vs `4.25`, `spread: kx` vs `17`, `14.0` vs `14`, `+ -0.75` vs `- 0.75`, key order.

That is not a text-only problem — running ergogen on the two files and diffing the artifacts shows
**19 differing artifacts** of 57:

```
cases/l_3d_preview.jscad, cases/l_case_3d.jscad, cases/l_cover.jscad,
outlines/{l,r}_case_bottom.dxf, outlines/{l,r}_coverpart_switch_plate_outline.dxf,
outlines/{l,r}_screws_outline.dxf, outlines/{l,r}_standoff_bosses.dxf,
outlines/{l,r}_tenting_base_border_outline.dxf, outlines/{l,r}_thumb_suplementary_outline.dxf,
pcbs/left_pcb.kicad_pcb, pcbs/right_pcb.kicad_pcb, pcbs/plate_left.kicad_pcb, pcbs/plate_right.kicad_pcb
```

with the concrete proof (circle centres in `l_screws_outline.dxf`):

| | committed | pre-fix generator |
|---|---|---|
| bottom-right screw | `(128.80, −132.63)` | `(126.80, −131.13)` |
| thumb screw | `(131.71, −160.30)` | `(131.70, −156.42)` |

— exactly the "was (126.8, 131.13)" / "was (131.70, 156.42)" values in the B13 comments. And
`scripts/check_assembly.py` on the pre-fix output **FAILS**:

```
FAIL  screw holes clear of switch cutouts   tightest screw 41.8,85.4: clearance -0.200 mm
                                            to a 14.00 mm cutout (need >= 1.7; negative = inside it)
FAIL
```

## 3. AFTER — generator output vs committed `ergogen/config.yaml`

`diff -u` is no longer empty but contains **no value differences**; every remaining line is
comments, key order or an equal-but-differently-spelled expression:

| Remaining hunk | Why it is not drift |
|---|---|
| 5-line generated header | comment only |
| `presets:` / `units:` / `points:` / scalar comments dropped or reworded | comments only |
| `key.stagger: 0.25 ky` → `4.25`, `.2 ky` → `3.4`, `spread: kx` → `17` | ergogen evaluates to the same number (ky/kx = 17) |
| `plate_kx: 14.0` → `14` | same number |
| `screw_offset_y + -0.75` → `screw_offset_y - 0.75` | same number |
| `col7.rows` order `row1, row5` → `row5, row1`; blank lines | mapping order, irrelevant to ergogen |

Proof that "no value differences" is also "no geometry differences": ergogen's output for the
committed config and for the generated config is **byte-identical** (50 outlines, 4 pcbs, 3 cases):

```
$ diff -rq out-committed out-generated && echo "OUTPUTS IDENTICAL"
OUTPUTS IDENTICAL
```

## 4. The gate — `scripts/check_config_drift.mjs`

Regenerates the default preset **in memory** (never touches `ergogen/config.yaml`), parses both
documents with js-yaml, compares them structurally, and evaluates ergogen expressions against each
file's own `units`/`presets`:

```
$ node scripts/check_config_drift.mjs
generator   : configurator/presets/sweepyway.json -> in memory (ergogen/config.yaml untouched)
canonical   : ergogen/config.yaml
drift       : none - the generator reproduces ergogen/config.yaml

B22 gate: PASS            (exit 0)
```

Perturbed on purpose in a scratch copy (`SCREW_SHIFTS.l_screw_thumb = [1.65, -3.0]`):

```
$ node scripts/check_config_drift.mjs
B22 DRIFT: 2 difference(s) between the generated config and ergogen/config.yaml
           (comments/key order are ignored; ergogen unit expressions are evaluated)

  points.zones.l_screw_thumb.anchor[0].shift[1]
      committed: "screw_offset_y - 3.506"
      generated: "screw_offset_y - 3"
      -> -6.906000000000001 vs -6.4
  points.zones.r_screw_thumb.anchor[0].shift[1]
      committed: "screw_offset_y - 3.506"
      generated: "screw_offset_y - 3"
      -> -6.906000000000001 vs -6.4
B22 gate: FAIL            (exit 1)
```

Two more perturbations (same scratch copy) to show it is not screw-specific:

* `ROW_PIN_POOL` reordered to `P4, P3, …` → 7 diffs, e.g.
  `pcbs.left_pcb.footprints.promicro.params.P3  committed "R5" / generated "R4"`.
* `case.standoffBodyLength` 3 → 6 (F3b) → `units.standoff_body_length 3 vs 6` **and**
  `units.standoff_boss_height -> 3 vs 0` (the derived value follows, as it should).

Wired in as step 3/4 of `scripts/pre-push.sh` and as the `config-drift` job in
`.github/workflows/build.yaml` (also added `configurator/**` + the script to the `paths` filter).

## 5. Repo checks after the change

`ergogen/config.yaml` is byte-identical to HEAD (`git status --porcelain ergogen/config.yaml` empty).
The worktree has no `ergogen/output/` and its `ergogen/footprints/ceoloide` submodule is not checked
out, so the three Python checks were run on a scratch copy of this tree with the submodule populated,
generated with the committed `config.yaml`:

* `scripts/check_assembly.py` → **PASS** (`screw holes clear of switch cutouts … +1.769 mm`)
* `scripts/hardware_bom.py --no-write` → exit **0** (one known warning: 1.0 mm past the stud thread)
* `scripts/check_matrix.py` → **PASS** (`matrix, pin map and net usage are consistent`)

## 6. What is deliberately not done

* **Non-default presets do not round-trip.** `minimal-3x5.json` now fails loudly
  (`canonical outline references "matrix_col6_row4"; this layout has no equivalent point`) instead
  of emitting an outline snapped to an arbitrary key; `row-stagger-1u.json` generates a valid
  config (ergogen accepts it) but obviously differs from the committed 7×5 file. Fixing that means
  per-preset outline references — a design change, not a drift fix. The gate checks the default
  preset only.
* The generated file is **not** adopted as the committed one (the old doc's step 4). It is now safe
  to do, but it would rewrite `ergogen/config.yaml` and drop the hand comments, which this task
  forbids. Left as an editorial decision.
* `r_screws_bottom.params.length: 4` on the right half is still a literal while the left uses
  `screw_bottom_length` (B21 residue). Not a generator region, so untouched.
* `filtered-output/`, `kibot/*`, `ergogen/footprints/*` untouched (B3 owns them).
