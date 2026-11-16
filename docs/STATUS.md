# STATUS — SweepyWay v0.2

**Last updated:** 2026-11-15 (documentation pass; evidence gathered from repo + live CI artifacts)
**Last code commit:** `e36e9d5` "Fix submodule branch reference…" (2026-03-08) — **never built by CI**
(workflow `paths:` filter ignores `.gitmodules`).
**Last successful CI run:** #157 on `13c8ffa` (2026-03-08) — this is what is currently published
to GitHub Pages and copied into `filtered-output/`.

---

## 1. One-paragraph summary

The **geometry and electronics definition are complete and reproducible**: one YAML file
generates both PCB halves (132.5 × 134.7 mm each, 7-column staggered + 3-key thumb fan, 32 keys
per half), both switch plates, the left case + cover, the tenting base and the palm rest.
Three things are *not* complete and they are exactly what stands between here and a working
keyboard: **(a)** the row↔MCU pin map is off by one, leaving row `R1` (12 keys) electrically
disconnected; **(b)** the CI pipeline exports the *unrouted* board, so the published gerbers have
zero copper; **(c)** the right half has no screw points, no case/cover, and the assembly (POS)
file is empty. Everything else is polish, documentation, and firmware.

## 2. Phase

> **Phase 2 of 4 — "make it manufacturable"**
>
> 1. ✅ Layout / footprint definition / case geometry (mostly done, left side)
> 2. 🔄 **Electrical correctness + routing + fabrication data** ← *you are here*
> 3. ⬜ Right half parity, mechanical attachments (tenting ↔ case, palm rest), print-file repair
> 4. ⬜ Firmware (ZMK), first physical build, ergonomic iteration

## 3. What is done (and verified how)

| Area | State | Evidence |
|---|---|---|
| Layout | ✅ 32 keys/half, 7 cols × 5 rows + 3 thumbs, splay/stagger | generated PCB footprint counts, `scripts/check_matrix.py --counts` |
| Key spacing | ✅ CFX 17 × 17 mm, 16.5 mm keycaps | `units: $extends: presets.cfx_spacing` |
| Switch | ✅ Choc V1 hotswap, `choc_v2_support: true`, side B, rotated 180° | `config.yaml` `choc:` params |
| Diodes | ✅ SOD-123, 32/half, on F side, COL2ROW | `diode_tht_sod123` + generated footprints |
| MCU | ✅ nice!nano v2, reversible mount, extra pins, display pins reserved | `promicro:` params |
| Power/battery | ✅ JST PH 2-pin on its own 18 × 14 area, side power switch | `l_jsph_area`, `power:` |
| Ergogen build | ✅ Reproducible: local regen == committed output (only the date differs) | ran it |
| Footprints | ✅ Submodule pinned to a pushed commit (`eb14fc3`) | `git ls-remote` |
| Left case | ✅ Base 3 mm + 16 mm wall + USB-C slot + controller housing w/ roof | `cases: l_case_3d`, `l_cover` |
| Tenting base | 🟡 Geometry done: 6.5° sloped hollow shell, 144.6 × 146.8 × 19.5 mm | `create_tenting_system.py` |
| Palm rest | 🟡 Geometry done: curved, 119.6 × 70.7 × 10 mm, not attached | `create_palmrest.py` |
| 3D preview | 🟡 Combined scene builds; JST missing, MCU/reset meshless in GLB | `TROUBLESHOOTING-3D.md` |
| **Cross-part fit + wiring** | ✅/❌ 18 checks: switch↔cutout↔cover alignment (0.000 mm), screw coaxiality PCB/plate/case (0.000/0.025 mm), diode orientation identical on all 32 keys, net names agree with column/row wiring, thumb cluster on one row net. **Fails** screw-vs-cutout clearance (B13) and the cover's missing screw holes | `scripts/check_assembly.py` |
| **Keycap collisions** | ✅ closest cap pair 0.50 mm apart (CFX 16.5 mm on 17 mm pitch, splay included) | same script family, computed from the PCB's switch transforms |
| **Printed-part shape check** | ✅ Sectioned at fixed heights: case = perimeter + 5 screw holes + open USB slot; cover = perimeter + 32 switch holes + controller bay; tenting = hollow; palm rest = solid ramp. No stray bodies except 2 zero-volume CSG slivers in the case | `scripts/inspect_print_model.py` (`CONFIGURATOR.md` §7) |
| **Row-stagger / standard-stagger variant** | ✅ `presets/row-stagger-1u.json`: 34 keys/half, 0.25u/row stagger, all 1u, no thumbs; matrix check PASS | `configurator/`, `check_matrix.py` |
| **Manual-build assumptions** | ✅ Audited against the Lily58 Pro build guide (plate thickness, socket/diode side, 1u thumb keys, M2 hardware) | [`BUILD-REFERENCE.md`](BUILD-REFERENCE.md) |

## 4. Blockers before ordering (must all be closed)

| # | Blocker | Severity | Where |
|---|---|---|---|
| **B1** | ~~**Row `R1` has no MCU pin.**~~ **FIXED 2026-11-16.** Both halves now assign `P3..P7 → R5,R4,R3,R2,R1` (the order the configurator generator intends, row5..row1 against `ROW_PIN_POOL`), and `P8`/`P9` are left deliberately free instead of carrying R6/R7 (nets no key uses). Before: no pin on R1 → **6 dead keys per half**; two pins on R5 → shorted GPIOs; R6/R7 wasted. Verified: `scripts/check_matrix.py` now reports **0 failures** (was 15, of which 4 were B4 parity). | ✅ fixed 2026-11-16 | `config.yaml` pin maps (2 blocks) |
| **B2** | ~~**Published gerbers are unrouted.**~~ **ROOT CAUSE FOUND 2026-11-16.** `autoroute/action.yaml` reads `pcbs/${board}.dsn` **relative to the repo root**, but there is **no `pcbs/` directory there** — and the body sits inside `if [ -e pcbs/... ]`, so the whole step **silently does nothing**. No `.ses` ⇒ `import-ses` (also guarded on the `.ses`) no-ops too ⇒ KiBot exports the unrouted board while every step reports success. **Proven routable locally** (Docker works, see HANDOFF §2): freerouting closed **105 nets, 0 unrouted, 0 violations, score 1000.00**; SES import gave **980 segments + 91 vias** (`check_matrix.py --routing` agrees). Fix: prefix with `ergogen/output/`, use `-mp 3` (default 25 spent >10 min optimising), assert segment count in CI. | 🔴 3-line fix | `autoroute|import-ses|export-dsn` actions |
| **B3** | ~~**Assembly data is missing 96 of 98 placements per half.**~~ **FIXED 2026-11-16.** It was a *declaration* bug, exactly as §5.7 predicted: `only_smd: true` in `kibot/jlpcb_pos.kibot.yaml` was asked of footprints that lied about what they were — the diode had **no `attr` at all**, the switch had `allow_soldermask_bridges` but no `smd`, and the 13 virtual footprints (3D previews, mounting holes) did not say `exclude_from_pos_files`, so removing the filter would have leaked 86 non-parts into the CPL. Fixed in the footprints (`diode` → `attr smd`; `choc_v1_v2` → `attr smd …` when `include_in_pos_files`; all `*-preview-*`/`*-fab-preview_*`/`mounting_hole_npth` → `exclude_from_pos_files exclude_from_bom`) and in the export (JLC's exact five columns, CSV, single file, KiCad y-up + `(180 − rot)` bottom mirroring). **CPL per half: 2 → 67 placements** (66 SMD + 1 THT; the nice!nano is a hand-soldered module and the 87 remaining footprints are previews/holes — all listed in `JLC-ASSEMBLY.md` §5). KiCad and KiBot now agree: `kicad-cli pcb export pos` on the fixed board gives the same 68 placeable parts, `--smd-only` gives the same 66. The hotswap socket question is settled in `JLC-ASSEMBLY.md` §4: its pads live in the switch footprint, so `S1…S32` **are** the socket placements; the 0-pad `hs-socket-fab-preview` stays 3D-only. Gate: `scripts/jlc_assembly.py check` (runs in CI) fails if a placeable part goes missing or a preview leaks in. ⚠️ The committed `filtered-output/` still predates the fix (B14) — it needs one CI run. | ✅ fixed 2026-11-16 | `kibot/jlpcb_pos.kibot.yaml`, `ergogen/footprints/ceoloide/*.js`, `scripts/jlc_assembly.py`, `docs/JLC-ASSEMBLY.md` |
| **B4** | ~~**Right half has no screws/standoffs/mounting holes.**~~ **FIXED 2026-11-16** (subagent). Two omissions, not one: (a) five explicit `r_screw_*` twins anchored on `mirror_<left ref>` carrying the *same* B13 shift expressions (ergogen flips a local shift's x for a mirrored anchor, so this is correct even for the rotated thumb), and (b) the missing `right_pcb.footprints.screws` NPTH declaration — without (b) you get plate holes but still zero PCB holes. Mirror axis **x = 170 mm** (`matrix` distance 340/2; `thumbfan` 120+100/2 — both agree), so `x_right = 340 − x_left`. Verified: 5 NPTH on `right_pcb` at (296.20,86.15) (296.20,137.15) (211.20,80.13) (211.20,132.63) (208.290,160.296), 5 coaxial `gr_circle` on `plate_right`, residual < 1e-6 mm; left unchanged; `check_assembly` PASS. | ✅ fixed 2026-11-16 | `config.yaml` + `STATUS` |
| **B5** | **No right case / cover.** `cases:` only defines `l_case_3d`, `l_cover`, `l_3d_preview`. | 🔴 blocks the build | `config.yaml` → `cases:` |
| **B6** | ~~**Print files not printable as-is.**~~ Tenting base + palm rest mesh generators fixed at the source (weld/orient/fill + constrained triangulation), `scripts/repair_stl.py` added for the OpenJSCAD case shell. Current state: cover/palm/tenting **watertight**, case **closed** with 3 coplanar T-junctions (slicers repair; reported as a warning). Original finding was: Measured with `scripts/check_print_files.py`: `l_case_3d.stl` has 3 non-manifold edges; `l_cover.stl` is clean ✅; `tenting_system.stl` has **inverted normals** (signed volume −60 cm³) + 4 non-manifold edges; `palm_rest.stl` has **inverted normals** (−65 cm³) + 64 boundary + 70 non-manifold edges. | ✅ fixed 2026-11-15 | `scripts/check_print_files.py`, `scripts/repair_stl.py` |
| **B7** | ~~**No BOM / order list.**~~ **Mechanism fixed 2026-11-16, part numbers still missing.** The old `kibot/jlpcb_bom.kibot.yaml` never produced a file at all: KiBot's `bom`/`kibom` outputs read the *schematic*, and Ergogen emits none — it dies with `ERROR: No SCH file found`, which is why the "BOM without an LCSC column" was never seen either. `scripts/jlc_assembly.py bom` now builds the JLC BoM (Comment, Designator, Footprint, **LCSC Part #**) from the PCB into `filtered-output/pcbs/bom/`, plus an audit CSV with a status per part. **Open sub-item (needs a human, not code):** none of the five assembled part types has an LCSC code — diode, hotswap socket, JST, reset switch, power switch. They go in the `lcsc` column of `kibot/jlc_parts.csv`; until then the JLC BoM is header-only and JLC would place nothing. The exact lookups are listed in `JLC-ASSEMBLY.md` §6. | 🟠 data entry | `kibot/jlc_parts.csv`, `scripts/jlc_assembly.py` |
| **B10** | ~~**Every switch-plate cutout was half-size.**~~ `l_keys_outline` used `size: [plate_kx/2, plate_ky/2]`, but `rectangle.size` is the **full** extent → 7.0 × 7.0 mm holes instead of 14 × 14, in both plates *and* in the printed cover. No switch could pass through. **FIXED** (2026-11-15) + guarded by `scripts/check_matrix.py --plates`. | ✅ fixed | `config.yaml` → `l_keys_outline` / `r_keys_outline` |
| **B9** | **The switch plate is too thick.** `top_plate_thickness: 1.6` — choc switches need a **1.2 mm** plate (1.5 mm FR4 absolute max) or the housing shoulders cannot seat and the switches perch above the PCB. Verified against the Kailh PG1350 drawing; see `HARDWARE-STACK.md` §4.0. Affects both the FR-4 plate order and the printed `l_cover`. **FIXED** to 1.2 mm (2026-11-15, D-11). | ✅ fixed | `config.yaml` → `units.top_plate_thickness` |
| **B11** | ~~**The cover STL was exported floating 25 mm above the bed.**~~ Ergogen places `l_cover` at the preview offset `z=25`; a slicer would print it mid-air unless you tick "drop to bed". `repair_stl.py --drop-to-bed` is now applied unconditionally in the configurator's print stage. | ✅ fixed 2026-11-15 | `scripts/repair_stl.py`, `configurator/server.mjs` |
| **B12** | ~~**`check_matrix.py` passed a board with 0 keys.**~~ Pointing `--board` at a YAML (or any non-PCB file) printed "matrix consistent — PASS". A gate that green-lights nothing is worse than no gate. Now fails with "no matrix keys found". | ✅ fixed 2026-11-15 | `scripts/check_matrix.py` |
| **B13** | ~~**4 of the 5 screw points sit INSIDE the switch cutouts.**~~ **FIXED 2026-11-16.** Moved to **(43.80, 86.15) (43.80, 137.15) (128.80, 80.13) (128.80, 132.63) (131.70, 160.30)** (grid screws +2.0..2.5 mm, thumb +3.9 mm). `check_assembly.py` now **PASSES outright** (was 1 FAIL): tightest cutout clearance **+1.769 mm**, plate-outline clearance 1.77–1.80 mm, PCB-edge clearance ≥2.34 mm. Verified downstream: the FR4 plate now carries **5 clean Ø2.2 holes** (previously the four were swallowed and the fifth clipped into a notch), the printed cover's plate level shows **32 keys + 5 screw holes**, and the case floor keeps its 5 holes. The 197.6 mm² cutout anomaly is gone too (all 196.0). | ✅ fixed 2026-11-16 | `config.yaml` → `l_screw_*` shifts |
| **B14** | **`filtered-output/` is a mix of two different builds.** The committed PCB + plate PCB are the current layout (plate cutouts land on the switches to 0.000 mm) but still have **6.9 mm cutouts** (B10 unfixed). The DXF outlines and the `l_cover.stl` are from an **older layout**: they register to the PCB on the screw holes (0.02 mm, because the screws never moved) yet the cover's key openings are **21.77 mm away from the switches**. Ordering from that folder yields an unusable plate and a cover that does not fit. **Root cause + gate added 2026-11-16:** the workflow copied with `rsync -a` (no `--delete`) and never emptied the folder, so files from earlier runs survived; it also never commits back, so the folder is a *manual* merge of artifact zips. The workflow now does `sudo rm -rf filtered-output`, uses `rsync -a --delete`, writes `BUILD-STAMP.txt` (commit + config sha1) and runs `scripts/check_published.py` before publishing. **The committed folder still fails that gate** (no stamp, 6.9 mm cutouts, cover 21.770 mm off) — it must be rebuilt from one CI run. | 🔴 until rebuilt in CI | `filtered-output/`, `.github/workflows/build.yaml`, `scripts/check_published.py` |
| **B15** | **Published junk + unparameterised PCB thickness.** `pcbs/3d/left_pcb-3d-misscaled.glb` is a 0.1 mm-scale mesh published beside the good one; `cases/case.stl` and `cases/cover.stl` are legacy duplicates (`cover.stl` is byte-identical to `l_cover.stl`); and the generated board is **1.6 mm thick with no parameter to change it** — ergogen's default, and there is no `pcb_thickness` in `config.yaml`, so a 0.8/1.2 mm order must patch `(thickness 1.6)` in the `.kicad_pcb` (or the order form must say 1.6). | 🟠 before ordering | `filtered-output/pcbs/3d/`, `filtered-output/cases/`, `config.yaml` |
| **B8** | **Mechanical attachment undefined**: how the case locks onto the tenting base; how the palm rest attaches (if at all). | 🟠 design gap | see `DECISIONS.md` ❓-4, ❓-5 |
| **B16** | ~~**No right tenting base was producible.**~~ **FULLY FIXED 2026-11-16.** The outline subtracted `l_case_bottom expand -5` (wrong side, copy-pasted) so the boolean collapsed: the original emitted a **210-byte DXF with 0 entities**. Rewritten as a true mirror (`r_case_bottom` expand 2 − `r_pcb_outline`, matching the left construction) ⇒ **132 entities, 143.42 × 145.60 mm** at x0 = 178.58. The configurator's print stage hardcoded the `l_` DXF names, so only a left part could ever be printed; it is now side-aware (`cfg.printSides`, default both sides) with an explicit "outline is EMPTY" error. Verified end-to-end: right tenting base watertight 59.29 cm³ (left 59.99) + right palm rest both generate. ⚠️ The SVG preview stays empty even when correct — judge by DXF entity count. | ✅ fixed 2026-11-16 | `config.yaml`, `configurator/server.mjs` |
| **B17** | ~~**The printed case rim stands ~3.6 mm proud of the plate.**~~ **FIXED 2026-11-16**, author chose to lower the rim rather than raise the pedestal (keeps the 6 mm standoff already in the BOM, shorter case, no wall around the caps). `case_border_height` is now **derived**: `case_bottom_thickness + standoff_length + pcb_thickness + plate_top_above_pcb_top` = 3 + 6 + 1.2 + 2.2 = **12.4**. Verified: case STL 140.61 × 142.80 × **12.4** (was 16.00), 5 floor holes, wall closed at z=12.0. The USB-C cut was reduced `extrude: 10 → 8` because 10 mm from z=3 reached z=13, above the new rim. `schema.mjs` and all three presets were also carrying a literal 16 and now derive; `standoffs.length` reads the unit. ⚠️ ergogen evaluates units top-down. | ✅ fixed 2026-11-16 | `config.yaml` units, `configurator/lib/*`, presets |
| **B18** | **Controller bay is open-topped; reset/power/JST sit outside the roof** — **ACCEPTED BY THE AUTHOR (2026-11-16)** as a deliberate tradeoff: dust/water ingress matters more than reachability, and the switches are only needed during initial setup and testing. Not a blocker. Roofed area = the `l_controller_area` rectangle (50 × 30 mm at the MCU, x ≤ 106.75); reset (112.0, 47.8), power (108.0, 39.8) and JST (107.0, 58.0) all fall outside it but are on the board and finger-reachable from above. **Optional later improvement:** a small recessed cut-out per switch. **Still open:** the USB-C plug path (15 × 15 mm rim tunnel at z 3…13 vs the connector at PCB level z ≈ 9–10) — see ❓-13. | 🟡 by design | `config.yaml` → `l_cover`, ❓-13 |
| **B19** | ~~**The two FR4 plates are different parts.**~~ **FIXED 2026-11-16.** `plate_right` referenced `r_cover_outline` (132.622 × 134.808) instead of `r_coverpart_switch_plate_outline` (132.622 × 117.048). The **117 mm one is correct**: it is *key cluster − key holes − screw holes* (a switch plate) and it is what the printed `l_cover` plate uses; `r_cover_outline` is the *full PCB outline* (controller + JST bays) and would lay plate over the MCU. After the fix both plates measure **132.22 × 116.65** ⇒ the two files are genuine mirrors. Promoted from §5.2. | ✅ fixed 2026-11-16 | `config.yaml` → `pcbs.plate_right` |
| **B20** | **The cover/plate has no ledge to sit on.** The case's top opening is `l_case_border_do_not_ocupy` = **135.95 × 138.14 mm** (PCB outline + 2), while the switch plate is `l_coverpart_switch_plate_outline` = **132.22 × 116.65 mm** (key cluster − keys − screws). The plate is therefore smaller than the hole it covers, so its height and lateral position are set **only by the 5 screws through the standoffs** — nothing supports it, and it can shift ~1.9 mm per side. With B17 fixed the rim top now coincides with the plate top, so a shelf is cheap: shrink the opening to ≈ PCB outline + 0.2 so the 1.7 mm-wide rim top becomes a seat. Found 2026-11-16 by comparing outline extents (not visible in any render). | 🟠 before printing | `config.yaml` → `l_case_border_do_not_ocupy` / `l_case_border` |
| **B21** | ~~**The screws cannot reach the standoffs.**~~ **FIXED 2026-11-16.** The top screw (4 mm) had to cross plate 1.2 + air 1.0 + PCB 1.2 = 3.4 mm before meeting a standoff that sits below the PCB, leaving 0.6 mm of bite; the bottom screw left 1.0 mm. Now derived: `screw_top_length: 6` (min 5.9 = 3.4 + `screw_engagement` 2.5) and `screw_bottom_length: 6` (min 5.5 = 3.0 floor + 2.5). Budget check: 2.5 + 2.5 engagement ≤ `standoff_length` 6 ✓. `screws_top.standoff_height` now reads `standoff_length` instead of a literal 4. **BOM change: both screws become M2 × 6 mm.** | ✅ fixed 2026-11-16 | `config.yaml` → `screws_top`/`screws_bottom` |

## 5. Non-blocking defects found during this review

1. **Choc V1/V2 plate mismatch** — PCB supports V2 (5 mm centre hole, wider pads) but the plate
   cutout is `plate_kx = 13.8` (V1 correct, V2 needs 13.95). Wanting both ⇒ cut 14.0.
   Verified: V1 = 13.8, V2 = 13.95 (`KEYBOARD-REFERENCE.md` §2, `DECISIONS.md` ❓-1).
2. **`plate_left` ≠ `plate_right`** — **promoted to B19 and FIXED in the 2026-11-16 pass.** left used
   `l_coverpart_switch_plate_outline` (keys only, 116.9 mm tall), right used `r_cover_outline` (full
   PCB outline incl. controller area, 134.7 mm). `r_coverpart_switch_plate_outline` was the correct,
   unused one; both plates now measure 132.22 × 116.65.
3. **`keycap_x_space` is undefined** in the `choc_space` footprint params (latent `NaN`; harmless
   only because no key carries the `space` tag, i.e. **there is currently no space key**).
4. **`r_tenting_base_bottom_outline` copies `l_case_bottom`** (should be `r_case_bottom`) — and
   only the left tenting base is ever generated anyway. **FIXED in the 2026-11-16 pass** (B16): the
   original resolved to **completely empty geometry** — a 210-byte DXF with **0 entities** — so it was
   not a cosmetic mislabel.
5. **`screws_top.standoff_height: 4` vs `standoffs.length: 6`** — the two numbers describing the
   same gap disagree (`HARDWARE-STACK.md` §4). **Quantified in the 2026-11-16 pass:** with
   `case_border_height: 16` they put the plate top at 12.4 mm, so the rim stands 3.6 mm proud of the
   plate and CFX caps end up flush with the case wall. See B17.
6. **`internal_distance_between_plates: 4` and `bottom_plate_thickness: 1.0` are unused units.**
7. **The POS regression is attributable.** `manualboms/manualpos 2026-02-01/*.pos` were produced
   by **KiCad itself** ("Printed by KiCad version 9.0.2") and contain diodes (top) + switches
   (bottom) + reset/power. The CI files are produced by **KiBot** ("Printed by KiBot") with
   `only_smd: true`, and contain only the two `smd`-attributed footprints. So the difference is the
   `smd` attribute, not the pipeline: add `(attr smd)` where a part should be placed.
   **Closed 2026-11-16 (B3).** One correction, from re-running KiCad 9.0.7 on the unfixed board:
   `kicad-cli pcb export pos --smd-only` produced **`PWR1` + `RST1` only** — the Feb-2026 manual
   files were exported *without* `--smd-only`, which is why they "contain the diodes": they also
   contain all 86 preview/hole footprints. KiCad and KiBot never disagreed; both were reading the
   same missing `attr`. See `JLC-ASSEMBLY.md` §2.
8. ~~**`fix_pos_package_name.py` maps `switch_choc_v1_v2 → CPG135001S30`**~~ — **deleted 2026-11-16**
   with its workflow step: JLC reads the part from the BoM, so a part number in the CPL's `Package`
   column was never the mechanism, and the number it wrote was the *switch*'s, not the socket's
   (`JLC-ASSEMBLY.md` §3, §4). The finding itself stands: `CPG135001S30` is the *Kailh Choc
   V1 switch* part number, not a hotswap-socket part number. It encodes the older intent
   "JLC places switches", which conflicts with the current intent "hotswap" (`DECISIONS.md` D-6).

## 6. Suggested next steps (in order)

> The scripts referenced below already exist and were used to produce this document:
> `scripts/regen.sh`, `scripts/check_matrix.py`, `scripts/check_print_files.py`.
> `./scripts/check_matrix.py` currently **FAILS** on both halves — that failure list *is* B1+B4.

1. **Fix B1** (~2 min): remap rows to `P3,P4,P5,P6,P7 → R1..R5`, leave `P8,P9,P10` free. Re-run
   `scripts/regen.sh && scripts/check_matrix.py`.
2. **Fix B2**: make the `kibot` action accept a board *file*, or add `suffix: _autorouted` for the
   `boards` config; then make the workflow fail loudly if no `*.ses` was produced, so a silent
   freerouting failure can never publish a bare board again.
3. **Push a branch, confirm in CI** that `filtered-output/pcbs/cad/left_pcb_autorouted.kicad_pcb`
   exists and `scripts/check_matrix.py --routing` passes on it.
4. **B4 + B5**: add `right_screw` points (mirror of `l_screw_*`), register the same
   screws/standoffs in `right_pcb`, add `r_case_3d` / `r_cover` cases from `r_case_bottom` /
   `r_case_border`.
5. **B6**: repair or re-export the STLs (fix normals for the tenting base, weld the case shell),
   then `scripts/check_print_files.py` must pass.
6. **B3/B7**: decide assembly scope (`DECISIONS.md` D-6), then produce a real POS + BOM.
7. Then: mechanical attachments, firmware, order.

## 7. ❓ Open questions (need the author)

Consolidated; each is also referenced from `DECISIONS.md`.

| ID | Question | Blocks |
|---|---|---|
| ❓-1 | ~~Plate cutout 13.8 (V1) vs 14.0 (V1+V2)?~~ **Resolved:** 14.0, applied (V1 = 13.8, V2 = 13.95). | — |
| ❓-2 | PCB thickness: author asked for **0.8 mm**; I recommend **1.2 mm** and a cheap 0.8 test board (no choc-hotswap build found at 0.8; switch pegs protrude 1.85 mm below the board; 132 × 135 panel flex). **Needs a yes/no.** | ordering PCB |
| ❓-3 | Surface finish / mask colour. Recommendation: lead-free HASL + black for the prototype, ENIG if boards will sit unassembled. | ordering PCB |
| ❓-4 | How does the case attach to the tenting base? (insert-from-below tabs / screw through base / basket / magnet) — four ideas exist in the notes. | 3D printing |
| ❓-5 | Does the palm rest attach to the case, or is it a separate slab? ("tongues with screw holes" idea) | 3D printing |
| ❓-6 | Assembly scope at JLCPCB: diodes only / diodes + hotswap sockets + JST + reset + power / switches placed instead of hotswap | assembly order, POS |
| ❓-7 | MCU mounting: 12-pin pin headers (2 × 12 per half) vs no-solder spring headers vs pins pre-soldered by JLC | BOM, case height |
| ❓-8 | ~~3D printing material~~ **Resolved: PLA for v1** (D-12), ASA/PA12-CF/3301PA only if heat/durability demands it, never SLA resin. | — |
| ❓-9 | Screw scheme: keep M2 everywhere or move the plate screws to M1.6 ("probably want smaller screws" note) | BOM, plate holes |
| ❓-10 | Is the 6.5° tenting base final for v1 (fixed, print two), or should it be stackable/multi-angle? | 3D printing |
| ❓-11 | Firmware: generate a ZMK shield in this repo, or keep it elsewhere? | usability |
| ❓-12 | Row-stagger variant. **Unblocked:** row-level `shift` works (`rows.<r>.shift`), no transposing needed — see `ERGOGEN-GUIDE.md` §4.7. Only the "when" is open. | `ROADMAP.md` |
| ❓-14 | **Reversible parts** — one design for both hands, to halve iteration cost at JLCPCB's 5-board minimum. See [`REVERSIBLE.md`](REVERSIBLE.md). Recommendation: plate = already free (just order one design), printed case/tenting/palm = free once we accept flipping in the slicer, **PCB = defer to v0.3** (footprints all support `reversible: true`, but it changes pad geometry and mirrors the firmware matrix). | ordering strategy |
| ❓-13 | **Controller bay access — ANSWERED 2026-11-16.** The open bay is *intentional*: water/dust safety is worth more than button reachability, and the switches are only used during setup/testing (author). An access hole per switch is a possible later option, not a v1 requirement. **Still open: the USB-C plug path** — 15 × 15 mm tunnel through the case rim at z 3…13 vs the connector at PCB level z ≈ 9–10. Cheapest settlement: one assembly render of `l_3d_preview` + the MCU/switch 3D previews. | case, USB-C only |

## 8. Repo hygiene notes

- Working tree is dirty: **~257 files differ only by CRLF line endings** (Windows checkout).
  `git diff --stat` is meaningless; use `git diff -w`. `.gitattributes` has been added to stop
  this, but the existing churn needs one deliberate normalization commit.
- Three files are deleted-but-uncommitted in the working tree
  (`analyze_pcb_glb_structure.py`, `plans/3d-model-footprint-analysis.md`,
  `plans/add-3d-model-to-jst-connector.md`) — decide whether to commit the deletions.
- `filtered-output/` (93 tracked files, incl. a 13 MB `combined_scene.glb`) is committed CI
  output. It will keep producing churn; consider publishing it via Pages only.

## 9. Documentation added in this pass (2026-11-15)

| File | What it is |
|---|---|
| `AGENTS.md` | agent/human contract: golden rules, local commands, verification loop |
| `docs/README.md` | documentation index + the ⚠️/🟡/❓ uncertainty convention |
| `docs/STATUS.md` | this file |
| `docs/DECISIONS.md` | 10 locked decisions + 12 open questions, with evidence |
| `docs/HARDWARE-STACK.md` | heights/gaps/fasteners; measured 3D-model table; the conflicts |
| `docs/BOM.md` | quantities per half and total, with sourcing notes |
| `docs/ORDER-CHECKLIST.md` | what to upload to JLCPCB / print service / parts vendors |
| `docs/KEYBOARD-REFERENCE.md` | domain + part facts (choc v1/v2, CFX/MBK, nice!nano pins, vendor limits) |
| `docs/ERGOGEN-GUIDE.md` | config map, mirroring, filter syntax, recipes (add key, fix screws, row stagger…) |
| `docs/PIPELINE.md` | build graph, artifacts, and the 6 known pipeline bugs |
| `docs/TROUBLESHOOTING-3D.md` | distilled 3D-export state + the v1–v11 variant results |
| `docs/ROADMAP.md` | phased plan + the configurator-website recommendation |
| `docs/BUILD-REFERENCE.md` | Lily58 Pro build guide audit: parts, assembly order, assumption table |
| `scripts/regen.sh` | local ergogen run (works with `node.exe` from WSL) |
| `scripts/check_matrix.py` | matrix↔MCU validation, routing check, left/right parity |
| `scripts/check_print_files.py` | STL watertightness / normals / scale check |
| `scripts/inspect_print_model.py` | shape check by sectioning (loop counts per height), body count, centroid offset |
| `scripts/render_stl.py` | headless orthographic PNG renders (matplotlib; VTK/vedo rejected - it re-aims the camera) |
| `scripts/check_render.py` | measures a render: fill, islands, see-through holes, symmetry; validates itself by aspect ratio |
| `.gitattributes`, `.env.example` | line-ending policy, KiCad 3D-model env vars |

## 10. Change log

### 2026-11-15 — documentation + first verification pass
- Added the doc set (`docs/`), `AGENTS.md`, `.gitattributes`, `.env.example` and three check
  scripts (`scripts/regen.sh`, `check_matrix.py`, `check_print_files.py`).
- **Found and fixed B10**: plate cutouts were half size (7 mm) because `rectangle.size` is the
  full extent. Both plates and the printed cover now have 14 × 14 mm holes.
- **Found and fixed B9**: plate thickness 1.6 → 1.2 mm (choc requires ≤1.5 FR4, 1.2 nominal).
- Plate cutout 13.8 → 14.0 for V1+V2 compatibility (❓-1 closed).
- Verified externally (with sources in `KEYBOARD-REFERENCE.md`): choc V1/V2 cutouts, plate
  thickness and plate-top height, CFX/MBK dimensions, hotswap-vs-thickness, JLC thickness and
  finish options, JLC3DP materials (incl. "9600" = SLA resin).
- Verified ergogen row/column override semantics against `points.js`; row stagger **is**
  expressible (`ERGOGEN-GUIDE.md` §4.7).
- Decided D-12: PLA for v1 printing.
- Added a web search tool (`C:/a/d/dev_agents/tools/websearch`) so external facts can be checked
  instead of guessed.

### 2026-11-15 (later) — configurator + print-file repairs
- **Built the local configurator** (`configurator/`, docs in `docs/CONFIGURATOR.md`): JSON config →
  `config.yaml` → Ergogen → checks → OpenJSCAD/trimesh print files → three.js viewer.
  Validated by equivalence: the `sweepyway` preset reproduces **38/38** key points of the repo
  build; the only additions are the 5 right-hand screw points (fixes B4 in generated configs).
- Generated configs auto-assign MCU pins from the row/column lists, so they cannot reproduce the
  B1 off-by-one. A second preset (`minimal-3x5`) proves the generator is layout-agnostic.
- `create_palmrest.py` / `create_tenting_system.py` now accept CLI args (`--height`, `--curve`,
  `--angle`, `--z-min`, `--hollow`, `--out`, `--dxf`) and produce watertight, positive-volume
  meshes. The palm rest mesh was rebuilt on a constrained triangulation (it used to have 64
  boundary edges).
- `scripts/repair_stl.py` (new) welds/orients any STL; wired into the configurator's case stage.
- `scripts/check_matrix.py` gained `--plates`, `--pcbs-dir`, `--json`; `check_print_files.py`
  gained `--json` and now separates *blocking* defects (open surface, inverted/none volume, metre
  scale) from *warnings* (non-manifold T-junctions).

### 2026-11-15 (third pass) — Lily58 audit, shape verification, 1u variant
- **Added [`BUILD-REFERENCE.md`](BUILD-REFERENCE.md)**: the Lily58 Pro build guide (fetched, 190
  lines) as a manual-build oracle. Confirms 1.2 mm FR4 plates for choc, sockets + diodes on the same
  side, and that 1.5u thumb caps are explicitly optional ("can also be 1U"). Its 4 mm choc
  PCB→plate spacer is *not* comparable to our 6 mm floor→PCB clearance.
- **Verified the printed parts by sectioning** (`scripts/inspect_print_model.py`, new): loop counts
  at fixed z confirm 5 screw holes in the case floor, an open USB-C slot, 32 switch cutouts + the
  controller bay in the cover, a hollow tenting shell and a solid palm rest. Found **B11** (cover
  floating at z=25) and **B12** (`check_matrix.py` false green on empty input); both fixed.
- **`layout.rowStagger` now takes absolute offsets** (ergogen's `shift` is cumulative — authoring
  `[0, 4.25, 8.5]` silently produced 0/4.25/12.75). New preset `row-stagger-1u.json`: standard 0.25u
  row stagger, all 1u, no thumb fan, 34 keys/half, matrix check PASS.
- BOM/CPL/routing gaps for the specific "everything except MCU + switches" order are now itemised in
  [`ORDER-CHECKLIST.md`](ORDER-CHECKLIST.md) §0.1.

### 2026-11-16 (fourth pass) — the visual audit
- **The vision channel works.** pi had been stripping images because `"input"` was absent from the
  model entry in `~/.pi/agent/models.json`; it is now `["text","image"]` and a fresh session reads
  PNGs. 20 images were inspected this pass (12 part renders, KiCad plots, and zoom crops).
- **Added [`VISUAL-AUDIT.md`](VISUAL-AUDIT.md)**: what sight confirmed, what it corrected, and what
  it newly found. Read it before editing `config.yaml`.
- **Confirmed visually:** B13 (the plate shows *semicircular bites* instead of screw holes —
  `check_render.py` reports `holes=32` and there is no region smaller than 500 px, so zero Ø2.2
  holes), B4 (right board has **0** standoff previews vs the left's **5**), B2 (published top copper
  is bare — pads only, no traces), B8 (the tenting base is a plain ring with **no** fastener/lip/
  pocket features).
- **Corrected:** **B1 is in both halves and the halves differ** (left shorts `R5` on P5+P9, right on
  P6+P7; `R1` missing in both). Measured impact: rows hold 6/7/7/7/5 keys, so a missing `R1` pin
  kills **6 keys per half = 12 of 64**. The silkscreen on the published board reads exactly the
  repo config's left map, independently dating the stale artifacts (B14).
- **New blockers:** **B16** (right tenting bottom outline resolves to an empty SVG), **B17** (case
  rim 3.6 mm proud of the plate; CFX caps flush with the wall), **B18** (controller bay open-topped,
  reset/power/JST outside the roof), **B19** (§5.2 promoted: the two FR4 plates are different
  parts). **New question:** ❓-13 (bay access + USB-C path).
- **Verified pad layers** (no longer inferred): switch pads are **B.Cu** smd 2.6×2.6, diode pads are
  **F.Cu** smd 0.9×1.2, socket footprint has **zero** pads. Also noted the 5 mm plate↔PCB gap in
  `l_3d_preview` is a *preview* offset, not a design value.

### 2026-11-16 (fifth pass) — fixes from the audit + publication gate
- **B19 FIXED**: `plate_right` now references `r_coverpart_switch_plate_outline` (the correct one — a
  switch plate is *key cluster − key holes − screw holes*; `r_cover_outline` is the full PCB outline
  and would have laid FR4 over the MCU). Both plates now measure **132.22 × 116.65**.
- **B16 FIXED**: `r_tenting_base_bottom_outline` rewritten as a true mirror of the left
  (`r_case_bottom` expand 2 − `r_pcb_outline`). Verified: the original emitted a **210-byte DXF with
  0 entities**; it now emits **132 entities, 143.42 × 145.60 mm** at x0 = 178.58 (left size +160.58).
  ⚠️ Its **SVG preview stays empty** even when correct — judge outlines by DXF entity count.
- **B18 accepted by the author** as a deliberate tradeoff (dust/water ingress over button
  reachability); an optional access cut-out is noted for later. ❓-13 reduced to the USB-C path.
- **New publication gate**: `scripts/check_published.py` (build stamp + config sha1 + cross-artifact
  checks + 14 mm cutout signature). It reproduces B14 exactly on the current folder (21.770 mm, and
  128–129 half-size segments = the pre-B10 6.9 mm cutouts). The workflow now wipes `filtered-output/`,
  rsyncs with `--delete`, writes `BUILD-STAMP.txt` and runs the gate before Pages/artifact upload.
- **New [`REVERSIBLE.md`](REVERSIBLE.md)** (+ ❓-14): the FR4 plate is *already* reversible for free
  (flip it), the printed parts are free too, and a reversible **PCB** is natively supported by every
  ceoloide footprint but recommended for v0.3 because it changes pad geometry and mirrors the
  firmware matrix.
- **B17 diagram added** (`docs/img/B17-stackup.png`, regenerable from this document's arithmetic):
  section showing the rim standing 3.6 mm above the plate, and the 9.6 mm pedestal that fixes it.

### 2026-11-16 (sixth pass) — B16 finished, B17 fixed by lowering the rim
- **B16 FULLY fixed**: outline mirror (DXF 0 → 132 entities) **plus** the configurator's print stage is now side-aware
  (`cfg.printSides`), with an explicit "outline is EMPTY" error. Verified end-to-end: right tenting base watertight
  **59.29 cm³** (left 59.99) and right palm rest both generate.
- **B17 fixed by lowering the rim** (author's call): `case_border_height` is now a **derived unit**
  (`floor + standoff + PCB + plate band` = 3 + 6 + 1.2 + 2.2 = **12.4**, was a literal 16). Case STL verified
  **140.61 × 142.80 × 12.4**; 5 floor holes intact; wall still closed at z=12.0. Consequences handled: USB-C cut
  `10 → 8` (it reached z=13, past the new rim); `schema.mjs` + all 3 presets also carried the literal 16 and now
  derive; `standoffs.length` reads `standoff_length`. **Why lowering beats raising the pedestal:** keeps the 6 mm
  press-fit standoff already in the BOM, shorter case, less filament, and no wall standing around the caps.
- **New B20**: the cover has **no ledge** — case opening 135.95 × 138.14 vs plate 132.22 × 116.65, so the plate's
  height/position come only from the 5 screws. Cheap fix now that the rim top == plate top.
- **New asymmetry to investigate**: `l_hand_rest_polygon.dxf` is **205.97 × 72.71** but `r_hand_rest_polygon.dxf` is
  **120.92 × 71.12**. The left palm-rest STL still comes out correct (119.64 wide), so a script step must be clipping
  it — but the two outlines should not differ in the first place.
- **ergogen gotcha**: units are evaluated **top-down** (mathjs scope), so a derived unit must be declared *after*
  every symbol it references (`case_border_height` before `case_bottom_thickness` fails with
  "Undefined symbol").

### 2026-11-16 (seventh pass) — B13 fixed: the plate can be screwed down
- **B13 closed.** Screw points moved to (43.80, 86.15) (43.80, 137.15) (128.80, 80.13) (128.80, 132.63) (131.70, 160.30).
  `check_assembly.py` passes for the first time; tightest clearance +1.769 mm (needed 1.7).
- **Symptom gone:** FR4 plate has 5 real Ø2.2 holes per side (was: 4 swallowed + 1 clipped), printed cover plate level
  shows 32 keys + 5 screw holes, case floor 5 holes, and the stray 197.6 mm² plate cutout is back to 196.0.
- **Traps recorded:** ergogen's point y is inverted vs PCB y (delta = −dy); the thumb point sits in a ~25° rotated frame
  so its shift is rotated (calibrated basis: `L(1,0)=(0.9063,0.4226)`, `L(0,1)=(0.42667,-0.90667)`); and the binding
  clearance constraint is the **plate outline**, not the PCB edge — the first attempt satisfied the PCB edge and still
  produced a notch at the thumb.
- Still open on the mechanical side: B4 (no right-half screws), B20 (no ledge under the cover), and the fastener topology
  decision. The B17/USB-C slot path (❓-13) is unchanged.

### 2026-11-16 (eighth pass) — hot-swap insight: the top fastener is redundant
- **New mechanical finding (§FASTENERS §1).** The choc hot-swap socket is anchored to the PCB by
  **two Ø3 press-fit pegs** (plus 2 SMD pads) and grips the switch's two pins; the switch latches
  into the 14 mm plate cutout and press-fits its two Ø1.9 pegs into the PCB. Net effect:
  **plate + switches + sockets + PCB are one rigid, self-clamping unit.** Verified against the
  generated `choc_v1_v2` footprint pads.
- **Consequences:** (a) the top screw is redundant — nothing left to clamp; (b) the 1.0 mm choc air
  gap is set by the *switch body*, so it is no longer a precision *case* dimension (the switches
  would simply refuse to seat); (c) the plate's 5 screw holes become optional; (d) the
  "two screws through one bore" constraint — the hardest one in the fastener search — disappears.
- **New doc:** [`FASTENERS.md`](FASTENERS.md) — full option space, measured numbers, the JLCPCB
  declaration rules (Q-16), and the recommended route (**F3: threaded standoff soldered by JLCPCB**,
  the author's idea). Six follow-up questions in §7.
- Still gated by **B3** before any fab-side option can ship.

### 2026-11-16 (ninth pass) — F3 parts verified against JLC's live API
- Queried JLCPCB's SMT parts API directly (no catalogue guessing). **Confirmed a solderable M2
  standoff exists, in stock, and JLC will place it:** XHHD `M2*3+3` = **C192879**, **5 333 pcs**,
  $0.0126, `assemblyComponentFlag: true`, LCSC category *knurled studs*, Chinese description marks
  it **焊接辅料** (soldering auxiliary). `M2*5+3` = **C193469** is the right height but has only
  **27** left; `M2*10+3` = C193465 (2 840) is too tall.
- **Negative results (checked, not assumed):** no M2 female-female standoff in stock; M2 nuts
  catalogued at **stock 0**; PEM `SMTSO` type parts only under `C9900xxxxx` private codes at
  **stock 0**; M3 hardware is plentiful (hex nuts `C133377` = **14 510**) but Ø5.5 and too fat for
  our webs (needs ~9.95 mm, we have 8.83 min).
- **The "can a nut substitute?" question now has an empirical answer:** JLC *does* place nuts
  (`C133377`, 14 510 in stock) — nuts are a real placement line item. M2 simply isn't among them.
- Two live caveats recorded in `FASTENERS.md` §4.5: the **3 mm stud vs the 1.0 mm air gap**
  (protrudes 1.8 mm above the PCB; the plate hole absorbs 1.2 mm, leaving ~0.6 mm — needs checking),
  and the **5 mm body being out of stock**. F2d (press-fit, already `BOM.md` item 12) remains the
  default until JLC answers.

### 2026-11-16 (tenth pass) — F3b: a printed boss covers the height difference
- Author's question: *"can't we have a boss to cover the height difference, for example for
  C192879?"* — **yes, and it makes the 3 mm part the correct one.** Boss height =
  `standoff_length − 3.0`; the metal body supplies only the thread. Both objections from the ninth
  pass dissolve:
  - **stud vs plate:** 3.0 stud − 1.2 PCB = 1.8 mm above the PCB top, plate band is 2.2 mm, so the
    tip stops **0.4 mm below the plate's top face, inside the Ø2.2 hole B13 already provides** →
    no interference at all (B13 and F3b turn out to be mutually dependent).
  - **body too short:** it no longer needs to span the gap. 3 mm in stock (5 333) is enough; the
    5 mm variant (27 left) is unnecessary.
- **Load path improves:** PCB → body top face → boss → floor, i.e. metal in compression under
  typing force; the screw only retains. Better than F1, where the thread is in plastic and takes
  the load.
- **Bonus the author wanted: the case gets shorter.** The 6.1 mm floor existed only because two
  screws share each bore (`MOUNT_GAP_IDEAL`). With one screw per point, the limit drops to socket
  clearance (3.5) → **`s = 4.5` is reachable: boss 1.5 mm, M2×8, case 10.9 mm** (from 12.4).
- New figure `docs/img/f3b-boss.png` (to scale). `FASTENERS.md` gains §3 F3b + a table of
  s/boss/screw/case-height; §4.5's two caveats are marked RESOLVED.
- Remaining: one process question to JLC ("do you reflow this part or only place it?") and B3.

### 2026-11-16 (eleventh pass) — F3b implemented and configurable; PCB Assembly question closed
- **Configurability shipped.** `ergogen/config.yaml` now has `standoff_body_length` (the metal part
  hanging below the PCB) with `standoff_boss_height = standoff_length - standoff_body_length`
  derived from it. 3 = F3b (default), 6 = press-fit standoff (old design, boss 0), 0 = printed post.
  Changing this one number switches topology; the case boss, the BOM and the screw length follow.
- **Case geometry:** `l_standoff_bosses` (Ø4.2 annulus, Ø2.2 bore) extruded on the floor. STL
  verified: 6 outlines at z>3.0 (5 bosses + wall), 1 at z=2.9, top exactly 6.00 mm, bbox and
  12.4 mm height unchanged; `check_assembly.py` still **PASS**.
- **`hardware_bom.py`** auto-detects topology and emits F3b (C192879 + M2×10 + printed boss), with
  gates. `--topology standoff` reproduces the old BOM exactly → no regression.
- **Configurator:** new "Metal part below PCB" field (`case.standoffBodyLength`), range-validated
  (0..standoffLength), written by `generate.mjs`; defaults round-trip cleanly.
- **The JLC process question is closed** (docs/FASTENERS.md §5.0): their PCB Assembly service
  covers **SMT + THT + mixed, single- and double-sided**, so the standoff simply joins the same
  assembly BOM as the sockets and diodes. My "reflow vs placed / wicking hole" worry was
  over-thinking a service that already does through-hole.
- **Deferred on purpose:** a button that queries LCSC stock and auto-selects the nearest available
  body length (the user asked for it as a follow-up; availability stays a manual check for now).
- Known cosmetic follow-ups: `l_3d_preview` does not show the new bosses, and the
  `ceoloide/standoff-preview` model still draws a full `standoff_length` column instead of
  `standoff_body_length` + boss.

### 2026-11-16 — SESSION CLOSE (state is consistent; pick up at HANDOFF §0)

**Done and verified this session:** B13 (screw move, `check_assembly` PASS), B16, B17, B19, B21,
B2 root cause (action rewritten, not yet run in CI), the F3b anchoring architecture (decided AND
implemented, with `standoff_body_length` as a single configurable knob), the LCSC part
verification (`C192879`), and the JLC service answer (PCB Assembly = SMT+THT+mixed).

**Gates at close:** `scripts/check_assembly.py` **PASS** · `scripts/hardware_bom.py` **PASS**
(topology auto-detected = soldered) · ergogen regen with `--clear` **stable** (config byte-identical
after regeneration) · `scripts/check_published.py` still reproduces B14 on an unstamped folder ·
`scripts/check_matrix.py` fails on B1/B4 only (known, documented).

**First task next session: B4** — mirror the 5 screw points to the right half. It is the last
mechanical blocker: without mounting holes the right PCB cannot take the soldered standoffs, and
without standoffs the right half has no anchoring at all.

**Session deliverables:** `docs/FASTENERS.md` (new, 500 lines, read §0 first) · `docs/img/f3b-boss.png`
· `docs/img/plate-holes.png` · `docs/HARDWARE-BOM.md` (regenerated, F3b) · updated `HANDOFF.md` §0/§5/§15,
`STATUS.md`, `BOM.md`, `DECISIONS.md` (Q-15/Q-16), `HARDWARE-STACK.md` §4.0a.

### 2026-11-16 (session 3) — B4 fixed by subagent, B1 fixed, B2 router re-proven
- **B4 fixed** (codex worker, verified by me independently): 5 right-hand mounting holes + 5 plate
  circles, mirror axis x=170 mm. The worker disproved my hypothesis with source citations — there is
  **no `points.mirror`**, and `points.key.mirror` is *clone metadata*, so no `mirror_l_screw_*` points
  ever existed (`node_modules/ergogen/src/points.js:349-380`). The real second half of the bug was the
  missing `right_pcb.footprints.screws` NPTH declaration.
- **B1 fixed**: both pin blocks now `P3..P7 → R5,R4,R3,R2,R1`, `P8`/`P9` free. `check_matrix.py`
  went from **15 failures to 0** — the matrix is now electrically correct on both halves (no dead
  rows, no shorted GPIOs, no wasted pins).
- **Precision note:** the exact thumb screw coordinate is **(131.7104269, 160.2956003)**, not the
  rounded (131.70, 160.30) written in earlier docs. The shift always produced the exact value; only
  my documentation rounded it. Right-hand counterpart is 208.2895731.
- **B2 re-proven locally** on an isolated snapshot with the rewritten action's exact parameters
  (`-mp 6 -mt 8`): left went from **105 unrouted nets to 0 unrouted / 0 violations** (auto-route
  stage 280 s, score 1000.00), right reached 0 with a 66 KB `.ses`. Confirms the tail is the
  **optimizer**, not routing (`-mp` does not cap it), as documented in the action.
- **New blocker B22** (`docs/CONFIGURATOR-DRIFT.md`): the configurator generator still emits plain
  `[screw_offset_x, screw_offset_y]`, so **running it would revert B13**. Not fixed; it is the reason
  B1 was patched surgically instead of by regeneration.
- Gates at close of this block: `check_assembly` **PASS**, `hardware_bom` **PASS**,
  `check_matrix` **0 failures**.
