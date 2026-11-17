# Published outputs — index

Site: <https://happily-coding.github.io/SweepyWay/> · source tree: `filtered-output/` (tracked in git,
93 files) · produced by `.github/workflows/build.yaml`.

**How to open the 3D ones:** drag the file onto **<https://3dviewer.net/>** in a browser. It renders
GLB (with materials/colours and part names) and STL, and it can load several files at once to
compare variants. Prefer GLB when both exist — plain STL carries no colours and no part names.
`export3d/` in this repo is already in assembly frame (plate bottom = case top = 11.2), so a case
and a plate load together and line up.

**Read this first — the snapshot is stale and mixed.** `filtered-output/` has **no
`BUILD-STAMP.txt`** (that is why `check_published.py` blocks), some files were refreshed by the
B20-D merge while others were not, and the measured staleness is:

| artifact | measured | today's design |
|---|---|---|
| `cases/case.stl`, `cases/l_case_3d.stl` | **16.00 mm** tall | **11.20** (B17 + B20-D) |
| `pcbs/cad/plate_left.kicad_pcb` | 132.22 mm wide, 165 lines / 34 arcs | 140.62 wide, D2 = 160/32, D1 = 166/36 |
| `pcbs/outlines/` | no `l_plate_on_wall*` files at all | D era emits them |
| `pcbs/gerbers/left_pcb.zip` | mtime Nov 16 | — |

So: **nothing on that site reflects B17/B19/B20.** Do not quote it as current.

---

## Root

| path | what it contains | producer | notes |
|---|---|---|---|
| `combined_scene.glb` | everything merged for viewing: cases + FR4 plates + PCBs-with-components + palm rest + tenting system, in one scene | **`scripts/build_combined_scene.py`** (replaces `create_full_3d_visual.py`) | Now coherent: case 0…11.20, plate 11.20…12.40 (sitting on the wall), PCB lifted to 9.00…10.20 from `config.yaml`, both halves side by side. It **fails** if the stack is incoherent. Caveat: the PCB export's fastener *preview* models hang ~2 mm below the floor, so component z-extents are indicative. The old script read `cases/case.stl` + `cover.stl` (legacy committed files nothing regenerates — the committed cover was dated March 2026) and applied a −90° rotation plus "PCB up 7", which is why the published scene showed a 16 mm case. |
| `temp_stl_models_no_tenting.glb` | scratch: STL parts only, pre-merge | same script | **build junk — should not be published** |
| `temp_stl_models_tenting.glb` | scratch: STL parts with tenting applied | same script | build junk |
| `pcb_plus_stl_no_tenting.glb` | scratch: PCB + STL parts, before tenting | same script | build junk |
| `pcb_plus_stl_no_tenting_tented.glb` | scratch: previous + tenting rotation | same script | build junk |
| `readme.md` | page text for the site | repo | — |

## `cases/` — printed parts

| path | contents | frame | notes |
|---|---|---|---|
| `case.stl`, `l_case_3d.stl` | printed case: walls, floor, screw bosses, USB-C cut, screw holes — **left** half | ergogen outline frame, x 20…160.6, y −176.6…−33.8, z 0…16 | stale (16 mm). The two files are *not* byte-identical (179 484 vs 179 684) even though they render the same volume — the docker `convert-all.sh` and the local jscad path disagree on tessellation. |
| `cover.stl`, `l_cover.stl` | printed cover: 32 key openings + frame | same frame | 132.62 × 134.80 × 7.00 — a **pre-plate** cover; today's `l_cover` is a different part |
| `l_3d_preview.stl` | case + cover + PCB assembly preview for eyeballing | same frame | stale |
| `tenting_system.stl` | tenting wedge/legs | own frame | **volume = −60.0 cm³ → inverted normals / not watertight.** Will confuse slicers. |
| `l_3d_preview.jscad`, `l_case_3d.jscad`, `l_cover.jscad` | the parametric sources (OpenJSCAD) | — | these are the files to open at <https://openjscad.xyz/> |

There is **no right-half case/cover** in the published set (`case_right`, `r_case_3d` are generated
locally but not shipped) — worth confirming whether that is intentional.

## `pcbs/3d/` — PCB with components

| path | contents | notes |
|---|---|---|
| `left_pcb-3d.glb` / `right_pcb-3d.glb` | board + every placed component with its 3D model (switches, keycaps, hotswap, pins, sockets, diodes, screws) | **the most useful file for geometry questions.** Axes are rotated by the exporter: in this file the PCB slab is 0…1.51 on **y**, and keycaps are the +y side (so +y = up, the keycap face). Always apply per-node transforms (`scene.graph[node]`); `scene.geometry[name].bounds` are model-local and will mislead you. |
| `*-3d-misscaled.glb` | same, **before** `fix_glb_scale.py` (metres→mm) | known-broken; kept because KiBot emits it first |
| `*-3d.step` | CAD export | different tessellation/materials from the GLB — not interchangeable evidence |
| `*-3d.stl` | geometry-only export | no colours/names |

## `pcbs/cad/`

| path | contents | notes |
|---|---|---|
| `left_pcb.kicad_pcb/.kicad_pro/.kicad_prl`, `right_*` | the routed boards, openable in KiCad | stale here (pre-B17 stack) |
| `plate_left.kicad_pcb`, `plate_right.kicad_pcb` | the FR4 switch plates (Edge.Cuts only, no copper) | in the published set these are **pre-D**. In today's repo they are aliases: `plate_*` → `plate_*_bay` (**D1**), and D1 currently **deletes 4 switch cutouts per half** — see `docs/HANDOFF-NEXT.md` §2. D2 (`plate_*_full`) is the variant the author wants. |

## `pcbs/gerbers/`

`left_pcb.zip` / `right_pcb.zip` and the same content unzipped (`left_pcb/`, `right_pcb/`, 12 files
each: copper, mask, silk, paste, edge cuts, drill). **These are what a fab order actually uses.**
Produced by KiBot `boards`. Stale in the snapshot.

## `pcbs/pdfs/`

One multi-layer PDF per board — a single flat render of every layer combined (name lists them:
F_Cu+F_Mask+B_Cu+B_Mask+F_Silkscreen+B_Silkscreen+… +Edge_Cuts+…. Useful for a quick visual check,
useless for fab.

## `pcbs/pos/` — pick & place

`left_pcb-top_pos.pos`, `left_pcb-bottom_pos.pos` (raw KiBot POS) and `*-jlcpcb.pos`
(rotation-corrected, JLC column order). `scripts/jlc_assembly.py` consumes the latter.

## `pcbs/outlines/` — the 2D sources of truth (49 DXFs)

Ergogen's outline exports: `l_case_bottom`, `l_case_border`, `l_case_border_do_not_ocupy`,
`l_controller_area`, `l_all_key_clusters_outline`, per-key outlines, plate outlines, etc.
These are what the case, plate and cavity are built from — when a dimension is in question, measure
here (judge by **entity/contour counts**, never by SVG bytes). Frame: y is negative-ish
(x 20…160.6, y −176.6…−33.8); **the PCB frame is y-flipped relative to this one** (`y_case ≈ −y_pcb`).

## `pcbs/images/`

`left_pcb-top.png`, `left_pcb-bottom.png`, `right_*` (2D layer renders) and `*-3d-top.png`
(KiCad 3D render from the top). Good for a fast visual diff of copper/silk.

## `palmrest/`

`palm_rest.stl` — parametric palm rest, 119.64 × 70.67 × 10.00, from
`palmrest_and_tenting_creation/create_palmrest.py`. **Left only** — the right palm rest does not
exist because `r_hand_rest_polygon` is not a true mirror of the left.

---

## Gaps and traps found while indexing

1. **The JLCPCB order files are not published.** `filtered-output/pcbs/bom/{left,right}_pcb/`
   (`*_bom_jlc.csv`, `*_bom_audit.csv`) exists locally but the site serves no `pcbs/bom/` at all.
   Those plus `pcbs/pos/*.pos-jlcpcb.pos` are exactly what an order needs.
2. **Build intermediates are published** (`temp_stl_models_*.glb`, `pcb_plus_stl_*.glb`).
3. **Same content, different extension, different result** — treat these as separate evidence:
   `*-3d.glb` vs `*-3d-misscaled.glb` vs `*-3d.step` vs `*-3d.stl`; `case.stl` vs `l_case_3d.stl`;
   `cover.stl` vs `l_cover.stl`. The repo needs `fix_glb_scale.py` precisely because the GLB export
   gets units wrong, so the GLB is only correct *after* that step.
4. ~~`tenting_system.stl` has negative volume~~ — **fixed by regeneration**: the pipeline's own
   output is +60.0 cm³; only the committed snapshot was inverted. Rebuild before printing.
5. **`combined_scene.glb` is not a valid clearance check** (parts stacked incoherently).
6. **No build stamp**, so nothing here can be proven to match any commit — hence
   `scripts/check_published.py` refuses to publish, correctly.

## What to check, in this order, whenever an artifact is questioned

1. Is it stamped? (`filtered-output/BUILD-STAMP.txt` — absent today.)
2. Measure a *known* dimension in it (case height 11.2, plate footprint 140.6 × 142.8, PCB
   thickness 1.51) instead of trusting the name or the picture.
3. Cross-check the number against `ergogen/output/outlines/*.dxf` (2D truth) — not against another
   render.
4. Only then look at the picture, and remember the PCB frame is y-flipped vs the outline frame.
