# B20 — the plate sits ON the wall (option **D**), with two plate variants

Decision note, 2026-11-17. Implements **panel D** of `docs/img/B20-options.png` for the author.
Everything below was executed and measured, not recalled. Markers follow `docs/README.md` §2:
⚠️ UNVERIFIED, 🟡 BEST-GUESS, ❓ OPEN.

---

## 1. What D is, and why

B20 is "the cover/plate has no ledge": the FR4 plate was the **key cluster**
(132.62 × 117.05), i.e. 2–4 mm *smaller* than the cavity (135.95 × 138.14), so it hung from the
32 switch latches with nothing under its edge (measured knock-on: it could shift ~1.9 mm per side).

Four ways to seat the edge were drawn (`docs/img/B20-options.png`). The author picked **D**:

```
                    before (A)                 after (D)
wall top ............ 12.4  (= plate top)      11.2  (= plate UNDERSIDE)
plate ............... 132.62 x 117.05           140.61 x 142.80  (= the case footprint)
plate edge support .. none (switch latches)    full perimeter, the plate overhangs the wall
extra parts ......... —                         nothing
reveal .............. —                         none: the plate edge IS the case edge
```

The stack is unchanged, only the *division* of it:

```
floor 3.0 + standoff 6.0 + PCB 1.2 + air 1.0 = 11.2  = wall top  = plate bottom   <- new
                                        plate 1.2 = 12.4  = plate top (= old rim) <- unchanged
```

Because the plate **top** stays at 12.4, keycaps, the USB-C cut and the screw stack do not move;
only the wall got 1.2 mm shorter and the plate got the case footprint.

## 2. What changed

| File | Change |
|---|---|
| `ergogen/config.yaml` | new unit `plate_sits_on_wall: 1`; `case_border_height` = `case_bottom_thickness + standoff_length + pcb_thickness + plate_top_above_pcb_top - plate_sits_on_wall * top_plate_thickness` = **11.2**; `usbc_slot_height` still derived from it (**7.2**); new outlines `l_/r_plate_on_wall_bay` (D1) and `l_/r_plate_on_wall` (D2); 4 new PCBs `plate_{left,right}_{bay,full}`; `plate_left` / `plate_right` repointed at the **D1** outline |
| `scripts/hardware_bom.py` | carries `wall_top` and `plate_top` separately; `--case-stl` now asserts the **case** height (11.2) and the report prints both rows; new check "plate top − wall top == plate thickness"; `plate_sits_on_wall` is optional (a config without it is the pre-D stack) |
| `configurator/lib/schema.mjs` | `PLATE_SITS_ON_WALL = 1` (same treatment as `MCU_MIRROR_DISTANCE`) |
| `configurator/lib/generate.mjs` | emits the new scalar and the new `case_border_height` formula, and its "derived vs override" comparison now subtracts the plate thickness |
| `scripts/check_assembly.py` | +15 checks (8 in the new B20-D block, 7 replacing the old orderable-plate block): plate outline == case footprint, D1−D2 == the bay area, wall ring untouched, wall top == STL height, a hole at every switch, screw bores, right = left; the old "count 32 closed cutouts" test was replaced (the bay notch merges cutouts, so counting stopped being meaningful) |
| `docs/HARDWARE-BOM.md` | regenerated (it is generated — never hand-edit) |

Not touched: the left screw coordinates, pin maps, `standoff_*`, `MCU_MIRROR_DISTANCE = 168`,
`kibot/`, `filtered-output/`, the `ceoloide` submodule. Nothing was committed.

## 3. The two plates (both are generated, both are orderable)

Both are `l_case_bottom` (= `l_pcb_outline` + 4 mm, **already minus the 5 screw bores**) minus the
key cutouts; they differ only in the controller bay.

| Variant | outline | PCB file | NET area | outer bbox | what it is |
|---|---|---|---:|---|---|
| **D1 — bay open** (default) | `l_plate_on_wall_bay` | `plate_left` = `plate_left_bay` | **6 416.03 mm²** | 140.61 × 142.80 | footprint − 32 keys − 5 screws − controller bay − JSPh bay |
| **D2 — bay covered** | `l_plate_on_wall` | `plate_left_full` | **7 808.44 mm²** | 140.61 × 142.80 | footprint − 32 keys − 5 screws |
| right twin of D1 | `r_plate_on_wall_bay` | `plate_right` = `plate_right_bay` | 6 416.14 mm² | | |
| right twin of D2 | `r_plate_on_wall` | `plate_right_full` | 7 808.54 mm² | | |

`plate_left_bay` / `plate_left_full` / `plate_right_bay` / `plate_right_full` are the explicit
names; `plate_left` / `plate_right` still work and are the **D1** part, since D1 is the
recommendation.

> Note on the two ways to measure the same outline: the DXF numbers above are the true areas (they are
> the shapes the case is built from, and the case STL's bbox 140.61 x 142.80 matches them exactly).
> Parsed out of the `.kicad_pcb` Edge.Cuts with an 8-chord arc approximation, the same plates measure
> **6 313.46 / 7 701.88 mm2** (left) and 6 313.51 / 7 701.92 mm2 (right) — 1.4 % less, which is chord
> error on the rounded corners, not a different part. `check_assembly.py` quotes the PCB-file numbers
> because the PCB file is what gets fabricated; left and right agree to 0.05 mm2.

**The difference is exactly the bay's area** (the number the task asked for):

```
D2 - D1                                    = 1 392.41 mm²
controller bay 1 492.02 + JSPh bay 244.02  = 1 578.78 mm²   (the bay region)
minus the 186.39 mm² of it already cut as key cutouts
                                           = 1 392.39 mm²   <- matches to 0.02 mm²
```

**Both bay rectangles are needed.** The JSPh (`l_jsph_area`) sticks out of the controller
rectangle by **86.76 mm²**, so subtracting only `l_controller_area` would leave FR4 over part of the
JST connector — and the JST body is **7.60 mm** tall while the gap under the plate is 1.0 mm.
Same for the MCU itself (**3.34 mm**) and the power switch (**5.00 mm**). Those bodies, measured from
`component_3d_models/*.step`, are why D1 must have a notch at all:

| body | height | plate bottom is `PCB top + 1.0` → protrudes through a covered plate by |
|---|---:|---:|
| `Nice_Nano_V2` (incl. USB-C) | 3.34 mm | 2.34 mm |
| `JSTPH2-S2B-PH-K-S` | 7.60 mm | 6.60 mm |
| power switch `SSSS811101` | 5.00 mm | 4.00 mm |
| reset `EVQ-PUC02K` | 2.44 mm | 1.44 mm |

**D2 is inspectable but not buildable as-is**: it lays FR4 across all four of those bodies. It is
generated so the author can *see* panel D as drawn; ordering it would mean an MCU on a cut-down
header stack that does not exist.

## 4. Geometry verified on the artifacts

Generated with `./scripts/regen.sh`, `.jscad → STL` with openjscad + `scripts/repair_stl.py
--drop-to-bed` (the configurator does exactly this), measured with
`scripts/check_assembly.py`, `scripts/inspect_print_model.py` and a shapely area pass over the
outlines.

```
case STL      l_case_3d.stl   140.61 x 142.80 x 11.20   z 0.00..11.20   volume 51.503 cm³
              r_case_3d.stl   140.61 x 142.80 x 11.20                    (was 12.40 / 52.832 cm³)
plate         D1 6 416.03 mm²  D2 7 808.44 mm²  both 140.61 x 142.80 = the case footprint
plate top     wall 11.20 + plate 1.20 = 12.40  (unchanged: caps and screws do not move)
wall ring     (footprint - (pcb+2)) = 1 141.80 mm²; uncovered by D1 0.000 mm², by D2 0.000 mm²
sections      z=1.5  1 loop + 5 screw holes      (case floor)
              z=3.2  6 loops + 5 holes           (wall band cut open by the USB-C slot)
              z=10.8 1 loop                      (wall closed just under the plate)
              z=10.15 open · z=10.20 closed      <- the USB-C window's top edge, to 0.05 mm
```

`check_assembly.py --cases` **PASS** (47 checks). Notably: *"D1 plate removes exactly the
controller + JSPh bay area"* (1 392.41 vs 1 392.39 mm²), *"neither plate variant cuts the wall ring"*
(0.000 mm²), *"plate outline == case outer footprint"* (140.61 × 142.80 both), *"case STL height ==
wall top (11.20)"*. The full gate output is in §6.

**D1 keeps full-perimeter support.** The bay notch stops at the PCB edge, 2 mm short of the wall, so
even the "bay open" plate presses on the whole wall ring. That is the whole point of D, and it is the
one thing A/B/C could not give.

## 5. The USB-C consequence (open question B18 / ❓-13) — the honest answer

Lowering the wall shortens the USB-C window, and this is where D could bite:

```
                    before            after D
window z ............ 3.0 .. 11.40     3.0 .. 10.20      (usbc_slot_height 8.4 → 7.2)
window top edge ..... 11.40            10.20  = PCB top face exactly (3.0 + 6.0 + 1.2)
height .............. 8.40 mm          7.20 mm
```

Measured on the case STL: the wall band is **open at z = 10.15 and closed at z = 10.20** — i.e. the
window really does stop at 10.2, and above it there is 1.0 mm of wall plus the 1.2 mm plate.

**The connector, measured from the 3D model** (`component_3d_models/Nice_Nano_V2.step`, solid
`User Library-TYPE-C-31-M-14.step`):

| quantity | value |
|---|---|
| body | **11.47 × 8.43 × 3.34 mm** |
| vertical extent in the nice!nano's own frame | **z −1.581 … +1.757** (3.34 mm) |
| the nice!nano PCB it is mounted on | **z 0.000 … 1.600** (the two dominant horizontal planes of the `COMPOUND` solid, 557 / 499 mm²) |
| overhang past the nice!nano board edge | **0.80 mm** (y 8.87…17.30 vs board −16.50…+16.50) |

So the receptacle **straddles its own board** (1.58 mm below the board's bottom face, 1.76 mm above
its top face): it is a mid/sink-mount part, and its mouth is a 3.34 mm tall slot whose centre sits at
the nice!nano PCB's **mid-plane ± 1.67 mm**.

**Verdict — and the reason it is not a clean yes/no:** a plug enters horizontally, so what matters is
whether the window contains the mouth. With the mouth centred on the nice!nano's mid-plane `m` (so it
spans `m − 1.67 … m + 1.67`), how much of it each window hides is pure arithmetic:

| nice!nano mid-plane `m` | mouth spans | hidden by the OLD window (top 11.40) | hidden by the NEW window (top 10.20) | D costs |
|---|---|---|---|---|
| 8.00 mm | 6.33 … 9.67 | 0.00 | 0.00 | 0 |
| **8.53 mm** | 6.86 … 10.20 | 0.00 | 0.00 | **0 (the break-even point)** |
| 9.00 mm | 7.33 … 10.67 | 0.00 | 0.47 | 0.47 |
| 9.73 mm | 8.06 … 11.40 | 0.00 | 1.20 | 1.20 |
| 10.20 mm (= PCB top face) | 8.53 … 11.87 | 0.47 | 1.67 | 1.20 |
| 11.00 mm | 9.33 … 12.67 | 1.27 | 2.47 | 1.20 |

So **D costs at most 1.2 mm of the connector's 3.34 mm, and costs nothing at all if `m ≤ 8.53 mm`** —
i.e. if the nice!nano PCB's mid-plane is at least 1.67 mm below the main PCB's top face. Where `m`
actually is **is not resolved anywhere in this repo**:

- the MCU's 3D preview is demonstrably mis-oriented — exporting the PCB with `kicad-cli pcb export
  glb` shows KiCad's transform putting the nice!nano's 33.8 mm model axis **along the vertical**, and
  the exporter emits no mesh for it at all — which is consistent with the hand-fudged
  `mcu_3dmodel_xyz_offset: 2.5` (left) / `5` (right);
- ❓-13 itself was written as "connector at PCB level z ≈ 9–10" 🟡, which is `m ≈ 9.7 … 10.7` — i.e.
  right at the worst case for D;
- the header stack is not modelled: `PinHeader_1x12_P2.54mm_Vertical` measures **11.54 mm**
  (z −3.00 … +8.54) and the cavity under the PCB is only 6.0 mm, so the nice!nano cannot be under the
  PCB by 8.54 mm — it must be above it, which puts `m` **higher**, not lower.

🟡 **BEST-GUESS: `m ≈ 10 mm` (the ❓-13 reading) → D hides ~1.2 mm of the mouth's top**, i.e. the plug
still centres within the window but its upper shell edge is 1.2 mm behind FR4. That is a real, if
mild, interference (a 2.5 mm tall plug shell centred at 10.0 would have its top 0.4 mm behind the
plate) — **so treat the new window as marginal and settle it with one measurement before printing the
case.** ⚠️ UNVERIFIED: no physical plug was inserted.

**Recommended fixes, cheapest first** (do not implement blindly — settle the mounting first):

1. **Nothing** — if the nice!nano's mid-plane measures `m ≤ 8.53 mm` (the mouth then clears 10.20 in
   full). **The measurement to take:** plug the MCU into the PCB, lay a straight edge across the PCB
   *top face*, and measure from it to the centre of the receptacle's mouth. Cost: 0. Until then the
   window is 🟡 marginal, not proven.
2. **Window top = wall top** (`usbc_slot_height: case_border_height - case_bottom_thickness` = 8.2,
   window 3.0…11.2). Free, no plate change: the 1 mm "1 mm below the rim" margin only existed to
   stop the cut breaking through the rim, and the rim is now capped by the plate, so the plate's
   underside becomes the top of the opening. Recovers 1.0 of the 1.2 mm lost (window 11.2 vs 11.4).
   ⚠️ UNVERIFIED visually: it interrupts the wall's top face over the 15 mm window, so the plate
   seats on the wall only either side of it there.
3. **Full 11.4 back** — needs the opening raised to 12.4 *and* a matching notch in the plate, because
   under D the plate is what caps the window. Cheapest form: subtract `l_usbc_border_outline` from
   `l_plate_on_wall*`, i.e. a **15 × 2 mm notch in the plate's bay edge = 30 mm² of FR4** (2.6 % of the
   1 141.80 mm² wall ring) plus a re-order of the plate. Note there is no free "tower": a wall boss
   above 11.2 would collide with the plate, so a tower *always* brings the plate notch with it and
   costs strictly more than option 2 while gaining only 0.2 mm over it.
4. **Right-angle / angled USB-C cable** — the usual mitigation; no geometry at all.

## 6. Gates (all green, output as run)

```
$ ./.venv/Scripts/python.exe scripts/check_assembly.py --cases <build>/assets
  ...  cover plate level: 32 key openings, 1 controller bay, 5 screw holes
  ok    plate cutouts land on switches                 32 cutouts, worst 0.000 mm
  ok    plate_left.kicad_pcb: every switch has an opening 32/32 openings, plate over: []
  ok    plate_left.kicad_pcb: key cutouts land on switches 28 key-sized cutouts, worst 0.000 mm
  ok    plate_left.kicad_pcb: has the 5 screw bores    5 openings smaller than 10 mm2
  ok    D1 (`plate_left`, default) leaves the bay open, D2 (`plate_left_full`) covers it
  ok    the right plate is the mirror of the left (same net area) 6313.46 / 6313.51 mm2
  ok    wall top + plate thickness == the old rim       wall 11.20 + plate 1.20 = 12.40
  ok    B20-D plate outlines exist and are closed       7 outlines
  ok    D2 plate (bay covered) == case footprint - keys - screws  symmetric difference 0.000 mm2
  ok    D1 plate (bay open) removes exactly the controller + JSPh bay area  1392.41 vs 1392.39 mm2
  ok    neither plate variant cuts the wall ring        wall ring 1141.80 mm2; uncovered 0.000
  ok    plate outline == case outer footprint           case 140.61 x 142.80 = D1 plate outline
  ok    case STL height == wall top (11.20 mm = plate underside)
  ok    the wall is closed 0.4 mm below its top        1 closed loop at z=10.80
PASS

$ ./.venv/Scripts/python.exe scripts/hardware_bom.py --case-stl <build>/assets/l_case_3d.stl
  -> exit 0   (wall top 11.2 asserted against the STL, plate top 12.4 reported)

$ ./.venv/Scripts/python.exe scripts/check_matrix.py --counts      -> PASS (0 failures)
$ node.exe scripts/check_config_drift.mjs                          -> B22 gate: PASS
$ bash scripts/pre-push.sh                                         -> 1/4 ok 2/4 ok 3/4 ok 4/4 ok, pre-push: ok
```

`scripts/hardware_bom.py` and `check_assembly.py` use different code paths on purpose: the BOM asks
the *config* for the wall height, the assembly check asks the *STL*. Both agree at 11.20.

## 7. Deliberately not done

- **No commit** (per the task), and `filtered-output/` is untouched (it is replaced by CI).
- **The printed `l_cover` is unchanged.** It still contains a 32-key printed plate; with FR4 as the
  lid that plate is redundant (and would raise the keycaps by 1.2 mm if printed). Only its controller
  housing is still wanted. Out of scope here — `check_assembly.py`'s cover checks still pass, so this
  is a print-file decision for the author, not a gate failure.
- **No USB-C geometry change**: the window stays at the `case_border_height - floor - 1` rule the task
  specified (7.2 mm, top at 10.2). §5 gives the three fixes with costs; picking one needs the mounting
  measurement first.
- **The MCU 3D preview stays broken** (model stands on edge, `mcu_3dmodel_xyz_offset` 2.5 vs 5). It is
  a preview-only defect, it predates this work, and touching those offsets would have changed the left
  half silently (the B22 note in `generate.mjs` says exactly this).
