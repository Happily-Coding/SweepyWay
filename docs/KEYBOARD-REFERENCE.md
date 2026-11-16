# KEYBOARD-REFERENCE — facts, specs and vocabulary

The "cite this instead of re-deriving it" file. Split into domain concepts (what a keyboard is
made of) and project specifics (what *this* keyboard is made of).

---

## 1. Vocabulary

| Term | Meaning here |
|---|---|
| **Matrix** | The switch grid. Each key connects one **column** net to one **row** net when pressed. 7 columns × 5 rows here (with skips). |
| **COL2ROW** | Diode orientation: anode on the column side, cathode (band) on the row side. Firmware (`col2row`) drives columns and reads rows. ZMK's default. |
| **Stagger** | Vertical offset per column (`key.stagger`) — this keyboard is *column*-staggered like the Ferris Sweep. A *row*-staggered variant (standard 0.25u/row) is available via `layout.rowStagger` in the configurator; see `docs/CONFIGURATOR.md` §8. |
| **Splay** | Rotation of keys within a cluster (`key.splay`), used on the thumb fan (±5°, ±15°). |
| **Hotswap** | Sockets soldered to the PCB so switches can be pushed in without soldering. |
| **Plate / switch plate** | The sheet above the PCB that holds the switches square and at the right height. Has 13.8/14.0 mm square cutouts. |
| **Case border / wall** | Printed wall around the PCB. |
| **Tenting** | Tilting the halves inward (and/or raising the inner edge); here a 6.5° sloped base under each half. |
| **Negative tilt** | Raising the *front* edge so the wrists angle down — discussed in `../notas teclado.txt` as future work. |
| **Tongue / jsph area** | The small PCB island next to the MCU holding the JST battery connector. |
| **`l_` / `r_` prefix** | Left / right half in `config.yaml` (`l_pcb_outline`, `r_case_bottom`, …). |
| **`leftkey` / `rightkey`** | Ergogen tags: real keys of the left cluster / their mirrored copies. |
| **Ergogen "point"** | A named `[x, y, r]` position; outlines and footprints are anchored to points. |
| **`mirror_mcu`, `mirror_matrix_col6_row4`** | Auto-generated names for mirrored points — the right half is literally the mirrored copy of the left on the same sheet. |

## 2. Switch: Kailh Choc V1 / V2

Verified 2026-11-15 (sources at the end of this section).

| | Choc V1 (PG1350) | Choc V2 (PG1353) |
|---|---|---|
| Used here | ✅ Choc Ambient (nocturnal / twilight) | supported by the PCB, not used |
| Plate cutout | **13.8 × 13.8 mm** | **13.95 × 13.95 mm** (often rounded to 14.0) |
| Plate thickness | **1.2 mm steel-equivalent / 1.5 mm FR4 max** | same |
| Plate top → PCB top | **2.2 mm** | same |
| PCB centre hole | 3.4 mm | 5.0 mm |
| Pin pitch | 5.5 mm (2 pins) | 5.5 mm |
| Switch body | 15 × 15 mm outer rim, 0.8 mm tall | same family |
| Pins below plate top | 4.85 mm (2.2 body + 2.65 pin) | same |
| Keycap mount | Choc (2 posts) | MX-style cross |
| Hotswap socket | Choc V1 socket (~3 mm deep) | Choc V2 socket (different part) |

- `choc_v2_support: true` in the footprint widens the pads and the centre hole so both fit
  (5.3 mm plated pad / 5 mm drill). A V1 switch then has ~0.8 mm radial play at the centre post;
  it is held by the plate, not by the PCB hole.
- **One plate cutout cannot make both versions clip properly.** 13.8 is V1-correct; V2 needs
  ~13.95. A 14.0 cutout is the compromise: V2 clips, V1 has 0.1 mm play per side and is still
  held by the plate (this is what most "universal" choc plates do).
- **Plate thickness is a hard constraint**: thicker than ~1.5 mm FR4 and the housing shoulders
  refuse to seat — the switch perches above the PCB and never registers. The repo currently says
  `top_plate_thickness: 1.6` → **too thick** (`STATUS.md` D-3).

Sources: `raw.githubusercontent.com/daprice/keyboard_parts/master/parts.scad` (PG1350 plate
footprint 13.8, `pcbHeight` = 2.2, pin/body geometry from the Kailh drawing it cites);
`github.com/cyril279/keyboards/blob/main/revlp/41_1353/README.md` ("13.95 mm for v2's that are
expected to clip into the plate, 13.8 mm for ... choc v1"); Sofle Choc build guide,
`sonalpinto/mt-choc` build.md and r/olkb for the 1.2 mm FR4 plate consensus; low-profile switch
comparison article (botmonster) for the 1.2 mm steel / 1.5 mm FR4 ceiling.

## 3. Keycaps

Verified 2026-11-15.

| | CFX (Chosfox) — **target** | MBK 1u | MX |
|---|---|---|---|
| Cap size | **16.50 × 16.50 mm ±0.07** | **17.5 × 16.5 mm** | 18.2 × 18.2 mm |
| Cap height | **3.70 mm ±0.05** | ~5.5 mm (measured 5.52) | varies by row |
| Minimum pitch | 17 mm | 17.5–18 mm | 19.05 mm |
| Mount | Choc | Choc (V1 only) | MX |
| Profile | flat/low | scooped | varies |

This keyboard: `kx = ky = 17`, cap assumption 16.5 → **CFX at 17 mm** (D-2).
CFX being 3.7 mm tall (vs MBK ~5.5) is a *feature* for this build: less total height, so the
keyboard is usable without a palm rest — which is one of the stated design goals.
The 3D preview uses the MBK model, so it *overstates* both the footprint (+~1 mm) and the
height (+~1.8 mm) of the real keycaps. 🟡 Cosmetic only, but do not read keycap height off it.

Sources: `chosfox.com/products/chocfox-cfx-choc-keycaps` (16.50 × 16.50 ±0.07, height
3.70 ±0.05); beekeeb MBK product pages (17.5 × 16.5 mm).

## 4. MCU: nice!nano v2

- 17.78 × 33.80 × 3.34 mm (measured). nRF52840, BLE, ZMK, USB-C.
- Pads numbered 1–24 in `mcu_nice_nano.js`; the label↔pad mapping used by this config:

| config label | pad | net | use |
|---|---|---|---|
| P0 / P1 / P2 | 1 / 2 / 5 | DPD / DPC / DPE | reserved for nice!view (data/clock/CS) |
| P3 | 6 | R2 | row |
| P4 | 7 | R3 | row |
| P5 | 8 | R5 | row |
| P6 | 9 | R4 | row |
| P7 | 12 | **R5 (duplicate!)** | row — wrong, see B1 |
| P8 | 11 | **R6 (no such row)** | row — wrong, see B1 |
| P9 | 10 | **R7 (no such row)** | row — wrong, see B1 |
| P10 | 13 | P10 | free (the pin R1 should probably come here) |
| P21 | 20 | C1 | column |
| P20 | 19 | C2 | column |
| P19 | 18 | C3 | column |
| P18 | 17 | C4 | column |
| P15 | 16 | C5 | column |
| P14 | 15 | C6 | column |
| P16 | 14 | C7 | column |
| RAW | 24 | RAW | battery + |
| GND | 3, 4, 23 | GND | |
| RST | 22 | RST | reset switch |
| VCC | 21 | VCC | |
| P101/P102/P107 | 25, 26, 27 | — | extra pins (`include_extra_pins: true`) |

The **right** half is the same footprint with a different (also wrong) map:
`P3..P9 → R2, R3, R4, R5, R5, R6, R7`. Both halves are missing `R1`, i.e. the 6 keys of the
first row per half are dead until B1 is fixed.

`reverse_mount: true` = the MCU is mounted on the opposite side of the PCB from the keys (the
board is used with the B side facing up), which is why the case has a raised bay for it.

## 5. Diode

- `SOD-123` (3.8 × 1.6 × 1.25 mm). One per key, SMD, on the F side, `COL2ROW`.
- Placement: `shift: [-0.5·plate_kx − 0.85, +1.5]` = `[-7.75, +1.5]` mm from the key centre,
  rotated 90°. The offset is "how much to shift so the diodes don't overlap each other".

## 6. Fasteners

M2, low-profile socket head screws, splined press-fit standoffs, ⌀2.2 mm holes. Details and the
contradictions in the current config: [`HARDWARE-STACK.md`](HARDWARE-STACK.md) §5.

## 7. Vendor limits (JLCPCB)

| Constraint | Value | Where it bites |
|---|---|---|
| Min trace / space | 0.127 mm (0.1 with extra cost) | `via_size 0.56 / via_drill 0.3` are above the minimum ✅ |
| Min drill | 0.3 mm | vias are exactly at the minimum |
| Board size | 10 × 10 … 500 × 500 mm | 132.5 × 134.7 mm ✅ |
| Assembly MOQ | 2 boards | 5 PCBs, assemble 2 ✅ (confirmed in chat) |
| Assembly parts | must come from their library; library parts **cannot** be shipped loose | screws/standoffs must be a separate order |
| BOM/CPL | must be one CSV each, with LCSC codes | currently missing (B3/B7) |
| PCB thickness | 0.8 / 1.0 / 1.2 / 1.6 mm available, from ~$2 (0.8–1.0 mm capped at 300 × 300 mm) | ❓-2: 1.2 mm is the recommendation |
| Surface finish | lead-free HASL (cheap) / ENIG (RoHS, flat, better for fine pitch and thin boards); HASL is restricted on very thin (0.4 mm) boards only | ❓-3 |
| 3D printing FDM infill | default 50%, range 20–100% (≥20% recommended) | case should be fine at 50% |
| 3D printing SLS/resin | infill fixed at 100% | |
| 3D printing file | one solid per part, watertight, mm | B6 |
| 3D printing materials (JLC3DP) | SLS **3301PA nylon**, MJF **PA11**, SLA **9600** / 8228 / black resin, FDM **PA12-CF** | see ❓-8 |

The material names above resolve the "9600" MSDS mystery: **9600 is JLC3DP's SLA resin**
(cheapest option, matte white, described as tough). The three MSDS files in the project root are
therefore ABS (conductive, FDM), ASA (INTAMSYS, FDM) and 9600 (SLA) — i.e. the author was
comparing FDM-vs-resin options, not picking a nylon.

⚠️ Still open: current prices, stock, and whether they still offer "consigned components".
I could not confirm from search whether LCSC/JLC stock a choc hotswap socket; the socket is
commonly bought from keyboard vendors (splitkb, typeractive, beekeeb, KEEBD). Verify in the JLC
parts search before promising assembly scope.

## 8. Design rationale (why it looks like this)

Written by the author in `../Design journey/design-journey.md` and `../README.md`:

- **Column stagger** matches actual finger lengths (Ferris Sweep philosophy); aggressive.
- **Choc** for low actuation force, low height (usable without a palm rest), and 17 mm-class
  spacing so the outer columns are reachable without over-stretching.
- **Controller placement priorities**, in the author's own words: must not push the mouse
  further out, must not force a palm position, must not interfere with tenting, must not add
  height, must be far from spill zones, must not add much space. Result: a bay below/behind the
  matrix, reachable by USB-C only through a slot in the wall.
- **Accident-prepared**: controller away from spills, power switch for transport, no metal
  plates (static discharge), everything hotswappable.
- **Beginner friendly**: printable PDFs to try the layout on paper, abundant keys, no soldering
  required (goal).
