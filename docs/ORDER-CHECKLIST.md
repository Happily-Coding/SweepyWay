# ORDER-CHECKLIST

Everything you need to upload, and to which vendor. Written to be usable as a literal
check-list on order day.

> **GATE: do not order the PCB until B1, B2, B3, B4 and B5 in [`STATUS.md`](STATUS.md) §4 are closed.**
> §0.1 below is the one-screen version of what is missing for the specific order you described.
> Ordering today would deliver a board with no copper, one dead row, and no way to screw the right
> half together.

---

## 0. Pre-flight (5 minutes, every time)

```bash
./scripts/regen.sh                     # config → PCB/plate/outlines/cases
./scripts/check_matrix.py              # matrix ↔ MCU map, dangling nets
./scripts/check_print_files.py         # STL sanity
```

Then confirm the *published* artifacts are newer than the last commit you care about:

- CI run list: `https://github.com/Happily-Coding/SweepyWay/actions`
- Only trust `filtered-output/` if the newest file date is after your last config change.

## 0.1 Readiness for *this* order (palm rest + tenting + PCB, everything soldered except MCU + switches)

Scope assumed: JLCPCB fabricates + assembles the PCB (diodes, hotswap sockets, JST, reset, power
switch), you keep the MCU, switches, keycaps and battery for yourself; the printed parts come from
JLC3DP or a local printer. Status as of 2026-11-15:

| Need | State | Missing |
|---|---|---|
| **2× PCB, routed** | ❌ | B2: the published gerbers contain **0 tracks / 0 vias**. Nothing has ever run the autorouter end-to-end; the CI KiBot step exports `${board}.kicad_pcb` instead of `${board}_autorouted.kicad_pcb`. Fix = one line in `.github/actions/kibot/action.yaml` + fail the job if the routed file has no copper. |
| **2× PCB, electrically correct** | ⚠️ repo config only | B1: row `R1` has no MCU pin (2 GPIOs shorted on R5, R6/R7 don't exist). The **configurator-generated** config fixes this by auto-assigning `P3..P7`; the repo's hand-written `config.yaml` does **not** yet. |
| **Plate / cover held by screws** | ❌ | B13: 4 of the 5 M2 holes are 0.2 mm **inside** the 14 mm switch cutouts, so the cover has no screw holes at all and the FR4 plate has a 0.9 mm sliver at those four corners. Move the screw points (B13) before ordering anything. |
| **2× PCB, right half complete** | ❌ | B4/B5: right half has no screws/standoffs/mounting holes and **no `r_case_3d`/`r_cover` at all**. You cannot print a right case today. |
| **Trustworthy published artifacts** | ❌ | B14: `filtered-output/` mixes two builds — the plate PCB still has 6.9 mm cutouts and the cover's key openings are 21.8 mm off the switches. Regenerate from the current config and re-verify with `scripts/check_assembly.py` before uploading anything from it. |
| **Assembly data (CPL/POS)** | ✅ (data) | B3 **fixed 2026-11-16**: per half the CPL lists **67 placements** (32 diodes, 32 hotswap sockets at the `S*` designators, JST, reset, power). The nice!nano is hand-soldered by design; the 86 preview/hole footprints cannot be placed. `scripts/jlc_assembly.py check` gates it. |
| **BOM with LCSC part numbers** | ⚠️ | B7: the JLC BoM is now generated with the LCSC column (`scripts/jlc_assembly.py bom`), but **5 parts still have no code** (diode, hotswap socket, JST, reset, power) — data entry in `kibot/jlc_parts.csv`, see `JLC-ASSEMBLY.md` §6. Until then JLC places nothing. |
| **PCB thickness decided** | ❓ | ❓-2: 0.8 mm requested vs 1.2 mm recommended — and the board file says **1.6 mm with no config parameter** (B15), so this needs a `.kicad_pcb` patch or the order form set to 1.6. |
| **Palm rest STL** | ✅ | watertight, +26 cm³, 119.6 × 70.7 × 10 mm, sits on z=0. Verified by sectioning (1 loop = solid ramp). |
| **Tenting base STL** | ✅ | watertight, +60 cm³, 144.6 × 146.8 × 19.5 mm, hollow (2 loops at low z), sits on z=0. **One only** — it is not mirrored, so check it fits the *right* half too (it is a symmetric wedge in X; the halves are mirror images, so verify before printing two). |
| **Left case + cover STL** | ✅ (with caveat) | watertight; the cover was exported **floating 25 mm above the bed** — `repair_stl.py --drop-to-bed` now fixes it automatically. The case is `closed` with 3 coplanar T-junctions (slicers repair, reported as a warning). |
| **Right case + cover STL** | ❌ | B5. |
| **Screws / standoffs / plate** | ❌ | M2 hardware is not a JLC item (see `BOM.md`); plate is an FR4 order only if you don't print the cover's plate layer. |

**So: what is actually sendable today is the palm rest and the tenting base** (plus the left case if
you accept the T-junction warning and print a mirrored right case by hand — which is *not*
equivalent: the USB-C slot and controller bay are asymmetric).

The shortest path to a sendable order:
1. B2 (routing) — mechanical, one CI fix + one gate.
2. B1/B4/B5 — easiest by adopting the configurator's generated `config.yaml`, which already has the
   auto-assigned pins and the `r_screw_*` twins, then adding `r_case_3d`/`r_cover`.
3. ~~B3/B7 (CPL + BOM)~~ — **B3 done 2026-11-16** (declarations fixed; 2 → 67 placements/side).
   B7 is now purely data entry: the 5 LCSC codes in `kibot/jlc_parts.csv` (`JLC-ASSEMBLY.md` §6).
4. ❓-2 thickness, then order.

---

## 1. JLCPCB — PCB fabrication

Upload `filtered-output/pcbs/gerbers/left_pcb.zip` and `right_pcb.zip` (each contains
`F_Cu, B_Cu, F_Mask, B_Mask, F_SilkS, B_SilkS, Edge_Cuts` + `PTH/NPTH` drill + drill maps).

| Option | Value | Why |
|---|---|---|
| Layers | 2 | design is 2-layer |
| Dimensions | 132.5 × 134.7 mm per half | from the Edge.Cuts bbox (`scripts/check_matrix.py` prints it) |
| Qty | 5 (minimum 5) | 1 needed per half, spares for the inevitable |
| **Thickness** | **1.2 mm** (❓-2, recommended) or 1.6 mm | 1.2 matches the author's 1.3 mm measurement and is friendlier to choc hotswap sockets |
| Surface finish | lead-free HASL (❓-3) ; ENIG if budget allows | HASL is fine for these pad sizes |
| Solder mask | black (cosmetic) | 🟡 author preference, unconfirmed |
| Silkscreen | white | |
| Copper weight | 1 oz | nothing high-current here |
| Via covering | tented (already set in `kibot/default.kibot.yaml`) | |
| Gold fingers / castellated / impedance | none | |
| "Remove order number" | **Yes** (or keep — it is printed as `JLCJLCJLCJLC` silk text, which is the standard trick) | silk text exists for this purpose |

## 2. JLCPCB — SMT assembly (optional, ❓-6)

Needs three files. **None of them is currently valid** — this section is the target state.

| File | Where it comes from | Current state |
|---|---|---|
| Gerbers | as above | ok once B2 is fixed |
| BOM (CSV, with LCSC part numbers) | `scripts/jlc_assembly.py bom` → `filtered-output/pcbs/bom/<board>/<board>_bom_jlc.csv` | 🟡 column present and published, **5 LCSC codes missing** |
| CPL / POS | `kibot/jlpcb_pos.kibot.yaml` (raw) → `scripts/jlc_assembly.py cpl` → `filtered-output/pcbs/pos/<board>/<board>_cpl_jlc.csv` | ✅ **67 placements/side** (66 SMD + 1 THT) |

Notes that cost money if forgotten:

- **MOQ for assembly is 2 boards** (confirmed in the JLC chat transcript in
  `../3d printing jlpcb.txt`). You can order 5 PCBs and assemble only 2 — also confirmed there.
- **Parts from the JLC library cannot be shipped loose** (same transcript): if you want the M2
  screws/standoffs in the same parcel, they must be ordered as a separate item/order.
- B-side assembly means the hotswap sockets, JST, reset and power switch; F side is the diodes.
- Switches/keycaps/MCU/battery/headers are **not** assembled (D-6, ❓-6, ❓-7).

## 3. 3D printing (JLCPCB 3D, or local FDM)

Files and quantity (per keyboard):

| File | Qty | Notes |
|---|---|---|
| `filtered-output/cases/l_case_3d.stl` (case bottom + wall) | 1 | B5: right-case equivalent does not exist yet |
| `filtered-output/cases/l_cover.stl` (plate + controller housing) | 1 | |
| `filtered-output/cases/tenting_system.stl` | 1 | mirrored copy for the other half; file needs normal repair (B6) |
| `filtered-output/palmrest/palm_rest.stl` | 1 | mirrored copy; not watertight (B6) |

Settings discussed with JLC (`../3d printing jlpcb.txt`):

- FDM: default infill 50%, adjustable 20–100% (they warn below 20% is weak). Leave a note in the
  "3D remark" box for a different infill.
- SLS nylon / resin: infill fixed at 100%, not adjustable.
- Multicolour is only available for PAC-nylon and WJP full-colour resin.
- Material shortlist evidence: MSDS on file for **ABS (conductive)**, **ASA (INTAMSYS)** and
  **"9600"** (unreadable scan — probably the nylon/resin family, ⚠️ UNVERIFIED).
  Recommendation: ASA or PA for the case, PLA for fast iterations (❓-8).
- Print orientation: case bottom flat on the bed, wall up (no supports needed except the USB-C
  slot bridge). Palm rest on its flat underside. Tenting base flat on its base, slope up.

Before uploading: `./scripts/check_print_files.py` must report watertight + positive volume.

## 4. Parts (LCSC with the PCBs, or AliExpress/other)

See [`BOM.md`](BOM.md) for the full table. The pieces that are *not* buyable at JLC:

- 2 × nice!nano v2 (with or without pre-soldered pins — ❓-7)
- 64 × Choc V1 switches (Ambient nocturnal/twilight)
- 64 × CFX 1u keycaps
- 2 × LiPo cells (size to be chosen, must fit the case/tenting base)
- M2 standoffs/screws if you don't buy them from JLC's library — links in `../shopping links/*.url`
- 4 × 12-pin headers or spring headers

## 5. After the parts arrive (assembly order)

1. Receive PCBs → **inspect the copper** under a light before anything else (this is where an
   unrouted board gets caught).
2. Test-fit one hotswap socket in a spare PCB (click, no rocking, contacts not bridged).
3. Solder/verify sockets → diodes → JST → reset → power → headers.
4. Flash the MCU with the ZMK shield (❓-11, not written yet) *before* final assembly — debugging
   with the case closed is miserable.
5. Continuity-test the matrix: every key should short exactly one row net to one column net.
6. Print the plate → test-fit switches through the plate → then the case.
7. Only then: keycaps, battery, tenting base, palm rest.
