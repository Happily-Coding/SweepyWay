# VISUAL AUDIT — 2026-11-16 (session 2)

The first pass in which the agent could **actually see images**. `HANDOFF.md` §10 recorded that pi
was stripping images and that the vision channel was unproven. That is now **resolved**: images
arrive, and 20 of them were inspected in this pass.

Purpose of this document: record what sight confirmed, what sight *corrected*, and what sight newly
found — so no later session re-derives it, and so the blockers in `STATUS.md` §4 carry the right
severity.

---

## 1. The vision channel — CONFIRMED WORKING

`~/.pi/agent/models.json` now carries `"input": ["text","image"]` for the active model, and a fresh
session reads PNGs normally (first image read this session:
`configurator/builds/sweepyway-2f79aca4/assets/renders/l_cover-top.png`).

Consequences for the workflow:

- `HANDOFF.md` §10's three fallbacks (pixel measurement / `ask-model` / geometry sections) are now
  **secondary**, not the default. Look at the picture first, measure second.
- Renders do **not** need `--title off` for human/agent viewing, only for `check_render.py`
  measurement (trap 6 in `HANDOFF.md` §8 still applies to the measuring tool).
- The painter's-algorithm renderer in `scripts/render_stl.py` draws **false internal seams**
  (faint diagonal lines/creases across flat faces, and vertical "striping" on walls). Those are
  *not* geometry. Do not report them as defects.

## 2. Images inspected

| Group | Files | Verdict |
|---|---|---|
| Fresh build, 4 parts × 3 views | `configurator/builds/sweepyway-2f79aca4/assets/renders/*.png` (12) | all read; shape matches the numbers |
| Published board plots | `filtered-output/pcbs/images/{left,right}_pcb-{top,bottom,3d-top}.png` (6) | read 3; stale, see §4 |
| Zoom crops | MCU header, single-key pad detail, standoff area | read; used to read the silkscreen pin map |

## 3. Confirmed by eye (previously only measured)

1. **B13 is real and has a visible signature.** The FR4/printed plate renders show **no round screw
   holes** and instead show **semicircular "bites" interrupting the plate outline** (left edge at
   mid-height, right edge at mid-height, and beside the thumb cluster). That is exactly the
   predicted failure: a Ø2.2 hole centred 0.200 mm inside a 14 mm cutout is swallowed by the
   boolean, leaving notches. `check_render.py` agrees: `holes=32`, i.e. 32 key openings and nothing
   else. Pixel count confirms it: no region smaller than 500 px exists (a Ø2.2 hole would be ~290 px).
2. **B4 is visible on the board art.** `right_pcb-3d-top.png` shows **zero** standoff previews;
   `left_pcb-3d-top.png` shows **five** white hexagonal standoffs. Right half genuinely has none.
3. **B2 is visible.** The top-copper plot of the published board is bare: pads only, no traces, no
   zones. Nothing has ever routed this board.
4. **Case shell** is a hollow tub: 3 mm floor + wall, 5 screw through-holes in the floor, and the
   USB-C notch fully interrupts the wall band (matches `inspect_print_model.py` expectations).
5. **Tenting base** is an open **ring** whose top edge undulates because the 6.5° plane slices the
   case silhouette; it has **no fastener, lip, pocket or clip features anywhere** — B8 confirmed
   structurally, not just "undefined in prose".
6. **Palm rest** is a solid wedge, ~10 mm at the high edge, feathered to a thin edge at the front,
   with a coarsely triangulated top surface (a fan of large triangles sharing few vertices). The
   facet creases are real geometry, unlike the renderer seams.

## 4. What sight corrected (docs were wrong or imprecise)

### 4.1 B1 — it is in **both** halves, and the two halves differ

`HANDOFF.md` §5 states one map (`P3..P9 → R2,R3,R5,R4,R7,R6,R5`). That is the **left** map only.
The right half is different:

| half | P3..P9 row map | duplicated net | missing row |
|---|---|---|---|
| left (`config.yaml` L866-894) | R2, R3, **R5**, R4, R7, R6, **R5** | R5 on P5 **and** P9 | R1 |
| right (`config.yaml` L1181-1206) | R2, R3, R4, **R5**, **R5**, R6, R7 | R5 on P6 **and** P7 | R1 |

**Impact, measured on the generated board:** keys per row are
`R1=6, R2=7, R3=7, R4=7, R5=5` = 32 ✓ (`R1` is a pure grid row: `col1_row1`…`col6_row1`, no thumbs;
`R5` is 2 grid keys `col2_row5`/`col3_row5` + the 3 thumbs, which are *named* `col{1,2,3}_thumb_row_1`
while wired to column nets `C5`/`C6`/`C7`). So a missing R1 pin kills **6 keys per half = 12 of 64
keys**, and the duplicated R5 shorts two GPIOs onto the net carrying the 3 thumbs + 2 grid keys.

**The generated config is clean.** `configurator/builds/sweepyway-2f79aca4/config.yaml` maps
`P3→R5, P4→R4, P5→R3, P6→R2, P7→R1` (P8/P9/P10 free), and the built PCBs verify it: each half has
`R1..R5` on five distinct pins and `C1..C7` on seven distinct pins. Adopting the generated config
(already recommended in `HANDOFF.md` §11.5) closes B1.

### 4.2 The silkscreen pin map is readable — and it dates the published board

Zooming `filtered-output/pcbs/images/left_pcb-top.png` the labels read
`DPC DPD GND GND DPE R2 R3 R5 R4 R7 R6 R5` and `RAW GND RST VCC C1 C2 C3 C4 C5 C6 C7 P10`.

`R2 R3 R5 R4 R7 R6 R5` is **exactly the left map in `ergogen/config.yaml`** — and *not* the generated
config's map. So the published artifacts were built from the repo config, independently confirming
B14 (the published folder is not the fixed build).

### 4.3 The switch pads are on the **bottom**; the diodes are on the **top**

Parsed from the generated `left_pcb.kicad_pcb`:

| footprint | pads |
|---|---|
| `ceoloide:choc_v1_v2` | `pad 1` smd rect 2.6×2.6 **B.Cu** @ (−3.275, −5.95) → `col1_row4`; `pad 2` smd rect 2.6×2.6 **B.Cu** @ (8.275, −3.75) → `C1`; centre Ø5 NPTH, stabs Ø1.9 NPTH, side holes Ø3 NPTH, one un-netted plated Ø1.9 |
| `ceoloide:diode_tht_sod123` | `pad 1` smd rect 0.9×1.2 **F.Cu** @ (−1.65, 0) → `R4`; `pad 2` smd rect 0.9×1.2 **F.Cu** @ (1.65, 0) → `col1_row4` |
| `ceoloide:hs-socket-fab-preview_choc_v1_v2` | **no pads at all** (confirms B3) |

So the top-copper plot legitimately shows no switch pads, and the hotswap socket is soldered to
B.Cu — i.e. switch pins enter from the plate side, sockets on the underside. Topology confirmed:
`C1 → switch pad 2 → switch pad 1 (col1_row4) → diode pad 2 → diode pad 1 (R4) → row net`. 🟡 Note
the diode land pattern is narrower than typical SOD-123 practice (0.9 × 1.2 mm at 3.3 mm pitch vs
~1.2 × 1.4 at 3.6); hand-solderable, marginal for reflow.

### 4.4 The 5 mm plate↔PCB gap in `l_3d_preview` is a preview offset, not a design value

`l_cover` puts the plate at `z=25` and `l_3d_preview` puts the PCB outline at `z=20`; the 5 mm
difference is the *preview stacking offset* that `HARDWARE-STACK.md` §4.1 already warns about. Do
not treat it as the real air gap. The real target is §4.0's **1.0 mm**.

## 5. New findings (not in any prior doc)

### B16 — `r_tenting_base_bottom_outline` resolves to **empty geometry** 🔴

`STATUS.md` §5.4 notes it "copies `l_case_bottom` (should be `r_case_bottom`)". The consequence is
worse than a mislabel:

```
configurator/builds/sweepyway-2f79aca4/out/outlines/l_tenting_base_bottom_outline.svg   2706 bytes, has <path>
configurator/builds/sweepyway-2f79aca4/out/outlines/r_tenting_base_bottom_outline.svg    224 bytes, <path> ABSENT
```

224 bytes is an empty `<g>` with no `width`/`height` on the `<svg>`. The boolean
(`l_case_bottom` expand +2) − (`l_case_bottom` expand −5) collapses to nothing. So no right tenting
base can be generated at all, and the left/right definitions are also **structurally different**
(left subtracts `l_pcb_outline`, i.e. it reaches in to the PCB edge; right subtracts an eroded case
outline) — fixing the name alone leaves two non-mirror-image standoffs. Note also
`r_tenting_base_border_outline` **is** fine (3817 bytes), so only the bottom is broken.

### B17 — the printed case rim stands ~3.6 mm proud of the plate ⚠️ needs author confirmation

No config value defines the plate height (`HARDWARE-STACK.md` §4.1). The only numbers that imply it
are the **preview** footprints `standoffs.length: 6` and `screws_top.standoff_height: 4`, and the
case wall `case_border_height: 16` (from `z=0`, floor top at `case_bottom_thickness: 3`).

Arithmetic via the verified choc rule (plate **top** = PCB **top** + 2.2 mm ⇒ 1.2 mm plate + **1.0 mm
air gap**), with the PCB resting on the press-fit standoffs:

```
floor top            3.0      (case_bottom_thickness)
+ standoff           6.0      (standoffs.length)          -> PCB bottom 9.0
+ PCB                1.2                                 -> PCB top   10.2
+ air gap            1.0      (HARDWARE-STACK §4.0)
+ plate              1.2                                 -> plate top 12.4
case rim top        16.0      (case_border_height)
                     ----
rim above plate top  3.6 mm   <-- should be ~0
```

Equivalently, if the plate is meant to sit flush on the rim, the pedestal must be **9.6 mm**, not
6 mm. With CFX keycaps (3.7 mm tall) the cap tops would land ~0.1 mm **above** the case wall — the
outer keys would look and feel flush with the rim. MBK (5.5 mm) would survive. This is the concrete
consequence of the flag already in `HARDWARE-STACK.md` §4.5 / `STATUS.md` §5.5; it is the number
that decides whether the case can be printed.

> ⚠️ Depends on the assumed topology (PCB on top of floor-pressed standoffs). If the intent is a
> standoff *between* PCB and plate instead, then 6 mm is the wrong number by ~5 mm. Either way the
> two numbers cannot both be right, and the required value is 1.0/9.6.

### B18 — the controller bay is open-topped, and reset/power sit outside the roof ❓

`l_cover` is: plate (key cluster only) + `l_controller_area_to_cover_outline` extruded 5 mm and
hollowed by `l_controler_area_to_not_fill` + a **solid 2 mm roof** on top of the same outline
(`controller_area_roof_z_thickness: 2`, total cover height 7.00 mm ✓).

The roofed area is the `l_controller_area` rectangle = `controller_sorrounding_x/y` = **50 × 30 mm**
centred on the MCU at **(81.75, 47.77)**, i.e. x 56.75…106.75, y 32.77…62.77. The three parts that
need human access all land **outside** it:

| part | centre | vs roofed box |
|---|---|---|
| reset `reset_switch_smd_side` | (112.0, 47.8) | **5.25 mm outside** in +x |
| power `power_switch_smd_side` | (108.0, 39.8) | **1.25 mm outside** in +x |
| JST battery `battery_connector_jst_ph_2` | (107.0, 58.0) | **0.25 mm outside** in +x |

All three are inside the board edge (verified by drawing the Edge.Cuts with the footprint centres;
the bay spans x 65…118, y 38…65), and the plate does not cover the bay (the plate is the key
cluster only). So the bay **is open from above** and the switches are reachable with a finger — but
**nothing** in the config subtracts a deliberate access hole, and the open bay also means the
interior is not sealed and the MCU's USB-C plug path is geometry nobody has checked: the case slot
is a 15 × 15 mm tunnel through the rim at z 3…13, while the connector sits at PCB level (z ≈ 9–10),
i.e. inside/above that tunnel rather than in line with it.

Needs a decision (new ❓-13), and the cheapest way to settle it is one assembly render of
`l_3d_preview` + the MCU/socket/switch 3D models, which the config already has as preview
footprints.

### B19 — the two FR4 plates are different parts (promote `STATUS.md` §5.2 to a blocker)

`STATUS.md` §5.2 has this as *non-blocking*. Measured on the generated boards:

| file | outline canvas | key cutouts | screw holes | slivers |
|---|---|---|---|---|
| `plate_left.kicad_pcb` | 132.62 × **116.95** | 32 × ~196 mm² | **0** | 0 |
| `plate_right.kicad_pcb` | 132.62 × **134.71** | 32 × ~196 mm² | **0** | 0 |

The root cause is one line: `pcbs.plate_right.outlines.right.outline: r_cover_outline`
(132.622 × 134.808) instead of `r_coverpart_switch_plate_outline` (132.622 × 117.048 — it exists,
both halves, and is what `plate_left` uses). The right plate therefore carries **17.76 mm of extra
material** reaching over the MCU/JST bay. Since both plates must go to the same fab order and be
mirror images, this should be **promoted to a blocker, not a §5 note**. Both plates also confirm B13
(0 screw holes, and no leftover sliver polygons at all).

## 6. Reproduction

```bash
cd "/mnt/c/a/IRL Products/Keyboard design/SweepyWay"

# the 12 part renders
./.venv/Scripts/python.exe scripts/check_render.py \
  configurator/builds/sweepyway-2f79aca4/assets/renders/*.png

# empty right tenting outline (B16)
wc -c configurator/builds/sweepyway-2f79aca4/out/outlines/{l,r}_tenting_base_bottom_outline.svg
grep -c "<path" configurator/builds/sweepyway-2f79aca4/out/outlines/r_tenting_base_bottom_outline.svg

# plate L/R divergence + B13 on both plates
./.venv/Scripts/python.exe -c "
import sys; sys.path.insert(0,'scripts')
from check_assembly import plate_polys
from pathlib import Path
for s in ('left','right'):
    p=plate_polys(Path(f'configurator/builds/sweepyway-2f79aca4/out/pcbs/plate_{s}.kicad_pcb'))
    print(s, len(p), [round(x['area']) for x in p])"

# pin maps: repo (broken, both halves) vs generated (fixed)
grep -n 'P[0-9]\+: *"' ergogen/config.yaml
grep -n 'P[0-9]\+: *"' configurator/builds/sweepyway-2f79aca4/config.yaml

# keys per row (B1 impact)
grep -c 'fp_text reference "D' configurator/builds/sweepyway-2f79aca4/out/pcbs/left_pcb.kicad_pcb
```

## 7. How to use vision from now on

1. **Before claiming a shape is wrong, render it and look.** `scripts/render_stl.py OUT *.stl
   --views top,front,iso` produces title-free PNGs that `read` accepts.
2. **Never trust the renderer's internal seams** (§1) — cross-check any suspicious crease against
   `inspect_print_model.py` sections or the source `.jscad`.
3. **Zoom before concluding.** `check_render.py` said "holes=32"; reading the numbers behind it
   (`holes` = background regions enclosed by material) needed the actual crop to see that the 32
   are key openings and not screw holes.
4. **Plot footprints, not just shapes.** Drawing Edge.Cuts with `choc`/`diode`/`reset`/`power`/
   `mounting_hole` markers (see §5 B18) is what exposed the controller-bay question; the STL alone
   hides it.
