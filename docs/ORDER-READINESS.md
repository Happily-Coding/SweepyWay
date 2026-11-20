# Order readiness — what stands between v0.2 and a JLCPCB cart

Audited against the published snapshot (`filtered-output/`, stamped, commit `afcfbe4`+). Every number
below is measured from the files, not remembered.

## Verdict

| part | orderable today? | why |
|---|---|---|
| **PCB × 2** (132.27 × 134.46 mm, 2-layer, 1.6 mm) | **almost** — 1 fix, 1 confirmation | see B2, B3 |
| **FR4 plate × 2** (1.2 mm, cutouts) | **no** | **no plate gerbers are produced at all** (B1) |
| **Case / hood / palm rest** | not a fab order | prints at home |

## Blockers

| # | blocker | evidence | fix |
|---|---|---|---|
| **B1** | **No gerbers exist for the plates.** `pcbs/gerbers/` holds only `left_pcb/` and `right_pcb/`. The plates exist as `kicad_pcb` (cad/) and as DXFs (outlines/), and **no kibot job plots them**. | `ls filtered-output/pcbs/gerbers/` → 2 boards only | add a kibot plot job for `plate_left/plate_right`: Edge.Cuts + drill, no copper. Or order the plates from the DXF as a mechanical cut |
| **B2** | **Plate thickness was 1.6 mm in the file** while the stack needs **1.2 mm** (`top_plate_thickness`, and config's own comment: *"choc switches need a 1.2 mm plate (1.5 mm FR4 absolute max) or they do not seat"*). ergogen stamps every kicad_pcb with a 1.6 default. | `grep thickness plate_left.kicad_pcb` → `(thickness 1.6)` | **FIXED**: `scripts/fix_plate_thickness.py` runs right after ergogen; `check_assembly` now asserts the file says 1.2. Verified: all 6 plate files read `(thickness 1.2)` |
| **B3** | **The right PCB is a translated copy of the left, not a mirrored design.** left `x 24.00…156.27`, right `x 183.73…316.00`, identical 132.27 × 134.46. A mirror about x=170 would put the right at `x −146.00…−13.73`. So the artefacts are the *same artwork*. | measured from `pcb_net_shape()` on both boards | **needs the author's confirmation**: either order 2× one design and flip one physically (works, but the sockets end up on the opposite face and silkscreen reads mirrored), or the right half was meant to be a true mirror and the artwork is wrong |
| **B4** | **Consigned sockets are a physical process step, not a file.** `C9900248317` (Kailh choc hotswap) is mail-in only: 64 sockets must be sent to JLCPCB (their consignment minimum is 10). | `jlc_assembly check` → 32 sockets per half on LCSC `C9900248317` | buy the sockets and ship them before/with the order, or set `assemble=no` and hand-solder 64 sockets + 64 diodes |

## Verified good (with the number it was verified at)

| check | result |
|---|---|
| board outline | 132.27 × 134.46 mm; case pocket is PCB+4 → 2.2 mm walls, matches the 140.61 × 142.80 case |
| layers / thickness | 2 copper (F.Cu, B.Cu), 1.6 mm — correct for the PCB (1.2 mm only for the plates) |
| copper within outline | F.Cu `x 27.15…149.60`, `y −156.69…−38.65` vs Edge.Cuts `x 24.00…156.22`, `y −172.18…−37.77` |
| CPL ↔ gerber frame | both Y-up with negative values, **same origin** → no mirror, parts land where the copper is. Normalising to a bottom-left origin is cosmetic, not required |
| CPL rows | 67 placements (66 SMT) per half: 32 Bottom + 35 Top |
| BOM | 5 lines, 6 unique parts, **0 LCSC gaps**; only the nice!nano is excluded (`Assemble=no`, hand-solder) |
| drills | PTH 0.75 / 1.0 / 1.6 mm; NPTH 0.9 / 1.9 / 2.2 / 3.0 / 5.0 mm |
| plate holes | 38 per half: 32 key cutouts (14.00 × 14.00, rotated for the thumb cluster — bbox 16.22 / 18.60 is a rotated square, not a bigger hole), 5 × ⌀2.2 screw holes, 1 hood cutout 50.00 × 27.96 |
| plate clearance | nearest hole-to-edge 3.40 mm; hood cutout is fully interior (not a notch) |
| plate copper | 0 pads, 0 segments, 0 zones — a pure cutout board (`(viasonmask no)` is a setting, not a hole) |
| hood ↔ keys | hood footprint hits **0.00 mm²** of switch cutouts; plate/hood overlap **0.000 mm²** |

## Decisions still open

1. **Key cutout 14.0 vs 13.8 mm.** Kailh's choc drawing is 13.8 × 13.8; ours is 14.0 × 14.0 square, so
   each switch has ~0.1 mm play per side. JLCPCB will also round the internal corners with their router
   bit (r ≈ 0.8–1.0 mm), which is normal for choc plates.
2. **Bottom-side assembly.** The 32 hotswap sockets are on **Bottom**. JLC charges per side, so this is
   a two-pass assembly. Hand-soldering the sockets instead drops the SMT order to one side.
3. **Plate supply.** Plates as PCB gerbers from JLC, or as a DXF mechanical cut from a plate service —
   B1 has to be decided one way or the other before the cart is complete.

## Order sheet (once B1/B3 are settled)

* PCB: 2 layers, 1.6 mm, 132.27 × 134.46 mm, quantity 2 (or 2 × mirrored design), HASL, no impedance
  control, no panel.
* Plate: 2 layers, **1.2 mm**, quantity 2, no copper needed.
* Assembly: top side only unless the sockets are consigned; MCU excluded, hand-solder.
* The plate files now declare 1.2 mm, so the order form must not be used to "correct" it to 1.6.
