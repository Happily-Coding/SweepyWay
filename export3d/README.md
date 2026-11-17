# 3D exports (open these, don't trust prose)

All files are in **assembly coordinates**: x 20…160.6, y −176.6…−33.8, z up from 0.
Two halves sit side by side in the same frame (left at x 20…160, right at x 179…320),
so you can load a left and a right part together and they line up.

## Fastest: the two coloured assemblies

| file | what you see |
|---|---|
| `assembly_left_D1.glb` | grey case + **green** plate `plate_left_bay` |
| `assembly_left_D2.glb` | grey case + **purple** plate `plate_left_full` |

Load one in <https://3dviewer.net/> (File → open, or drag it in). That site is alive and
handles GLB colour; the old `openjscad.azurewebsites.net` link is dead — the live JSCAD
editor is <https://openjscad.xyz/> and it opens the `*_case_3d.jscad` **sources** directly.

Other viewers that work: Windows **3D Viewer** (STL only, no colour), Blender, Fusion.

## Single parts (STL)

| file | z range | notes |
|---|---|---|
| `case_left.stl`, `case_right.stl` | 0 … 11.2 | wall, floor, screw bosses, USB-C cut |
| `plate_left_bay.stl` | 11.2 … 12.4 | **D1** — bay notched out, **28 switch cutouts** |
| `plate_left_full.stl` | 11.2 … 12.4 | **D2** — bay covered, **32 switch cutouts** |
| `plate_right_bay.stl`, `plate_right_full.stl` | 11.2 … 12.4 | mirrors of the above |

The plate bottom plane (11.2) is exactly the case's top plane, which is the whole point of
option D: the plate overhangs the wall and is the lid. Nothing else holds it up.

## What to look at

Load `assembly_left_D1.glb` and `assembly_left_D2.glb` and compare the **controller-bay
corner** (the end with the two big bay windows in the wall):

- **D2** has plate material there, with four switch cutouts in it.
- **D1** has a hole there — those four cutouts are gone. Count the switch openings: 32 vs 28.

That is the actual defect being discussed, and it is visible without measuring anything.

## How these were produced

- case STL: `node node_modules/@jscad/cli/cli.js ergogen/output/cases/l_case_3d.jscad -of stla`
- plate STL: Edge.Cuts of `ergogen/output/pcbs/plate_<side>_<variant>.kicad_pcb`, extruded
  1.2 mm, lifted to z 11.2. The plate PCB files are in the **PCB frame**, which is y-flipped
  relative to the case frame (`y_case ≈ −y_pcb`), so the export flips them back before lifting.
  The left plates are mirrored from the right ones (`x → 340 − x`, mirror axis x = 170)
  because the left outline chain doesn't close cleanly in the DXF.

## Not included, on purpose

No MCU, no switches, no keycaps: the nice!nano's mounted height is still unresolved in this
repo (`mcu_3dmodel_xyz_offset: [0,0,2.5]`, and the KiCad GLB export of the MCU is mis-oriented),
so any block I drew there would be a guess dressed up as a measurement.
