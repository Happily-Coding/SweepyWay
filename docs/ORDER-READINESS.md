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
| **B4** | **Consigned sockets are a physical process step, not a file.** `C9900248317` (Kailh choc hotswap) is mail-in only: 64 sockets must be sent to JLCPCB (their consignment minimum is 10). No in-stock alternative exists - every choc socket code in their catalogue is `stock 0`, and `CPG135001S30` reads *"no longer manufactured"*. | JLC API, queried 2026-xx: `C9900009224`, `C5333465`, `C9900248317`, `C9900180604`, `C7499820` all zero | **mandatory** if the sockets are to be factory-fitted (no hand-soldering by the buyer) |
| **B5** | **The MCU is never placed by JLCPCB - by design, and without the buyer soldering.** Two supported routes (details in `docs/MCU-MOUNTING.md`): (A) solderless spring headers from Typeractive pressed into the 2 × 12 holes, factory fits nothing, or (B) JLCPCB fits the headers and the buyer plugs the module in - **not** an SMT job, so THT service must be confirmed per order. Measured on the published board: 27 through-hole pads, **⌀1.0 mm drill / ⌀1.7 mm pad**, rows at x ±7.62. | `kicad_footprints()` on the published `left_pcb.kicad_pcb`; `Assemble=no` in the BoM | none for the buyer either way; only route B needs a THT question asked of JLC |

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

## The plate is a flat 1.2 mm sheet — three ways to get one

Measured on `export3d/plate_right_full.stl`: **two** distinct z values (11.2 and 12.4), i.e. constant
1.20 mm, every feature a through-cut. The roof and the 8.88 mm hood belong to the **printed case**
(`l_case_3d`), not to the plate. So any 2D process can make it:

| route | file it needs | process | material | status |
|---|---|---|---|---|
| (a) **PCB** | Gerbers (Edge.Cuts + drill) | PCB fabrication: panel, router-cut with a 1.6–2 mm bit, tolerances like a board | **1.2 mm FR4 only** | **missing** (B1) |
| (b) **Sheet cut** ("mechanical cut") | DXF | laser (acrylic/PC) or CNC router (FR4) cuts the outline from a sheet — no copper, no mask, no PCB process | FR4 sheet, acrylic, polycarbonate, aluminium | ready (`outlines/plate_*_on_wall.dxf`) |
| (c) **3D print** (JLC3DP) | STL | resin (SLA) or nylon (SLS) | resin / nylon | exists but **stale** (pre-hood: 9.40 cm³ vs 8.07 cm³ now) + needs `repair_stl.py` |

(a) and (b) are the **same shape**, different process and material choice: (a) is FR4 made by a PCB
house, (b) is any sheet cut by a fabrication shop. The DXF and the Edge.Cuts describe the same plate.

**Acrylic is the wrong pick here** specifically because this plate is clamped by 5 screws through
⌀2.2 mm self-tapping holes in 1.2 mm sheet: acrylic crazes and cracks at those holes under screw load,
and a cracked plate drops switches. Polycarbonate if a clear plate is wanted; FR4 is the standard for
exactly this reason.

**3D printing a 1.2 mm plate is worse than either**: SLA resin at 1.2 mm is brittle, SLS nylon is
springy, and the plate's job is to hold 32 switches at a fixed 14.00 mm and take the screw clamping.
Recommendation: **(a) PCB route**, which is what the repo already models - it just needs the plot job.

## Decisions still open## Order sheet (once B1/B3 are settled)

* PCB: 2 layers, 1.6 mm, 132.27 × 134.46 mm, quantity 2 (or 2 × mirrored design), HASL, no impedance
  control, no panel.
* Plate: 2 layers, **1.2 mm**, quantity 2, no copper needed.
* Assembly: top side only unless the sockets are consigned; MCU excluded, hand-solder.
* The plate files now declare 1.2 mm, so the order form must not be used to "correct" it to 1.6.
