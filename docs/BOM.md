# BOM — what to buy, how many

Canonical bill of materials for **one keyboard = 2 halves**. Quantities were derived from the
generated PCBs (footprint counts per type, cross-checked with `scripts/check_matrix.py --counts`)
and from `ergogen/config.yaml`.

> ⚠️ Every line marked `❓` depends on an open decision in [`DECISIONS.md`](DECISIONS.md).
> ⚠️ Prices/suppliers are not tracked here — they live in `../shopping links/*.url` and
> `../component_3d_models/readme.md`. Marketplace links in those files may be dead.

---

## 1. Electronics

| # | Part | Spec / MPN | Per half | Total | Fitment notes |
|---|---|---|---|---|---|
| 1 | Switch | Kailh **Choc V1** (author uses Choc Ambient: nocturnal / twilight) | 32 | **64** | hotswap, hand-inserted. ⚠️ UNVERIFIED switch force/MPN per batch |
| 2 | Hotswap socket | Kailh Choc V1 hotswap socket | 32 | **64** | ⚠️ UNVERIFIED whether LCSC/JLC stock it (❓-6); footprint work required for JLC placement |
| 3 | Diode | **SOD-123** (e.g. 1N4148W) | 32 | **64** | SMD, F side, COL2ROW. Footprint currently has **no `attr`** → excluded from the CPL (B3) |
| 4 | MCU | **nice!nano v2** | 1 | **2** | not stockable at JLC → buy separately |
| 5 | Battery connector | **JST PH 2-pin** `S2B-PH-K-S(LF)(SN)` | 1 | **2** | SMD, on the 18 × 14 mm tongue |
| 6 | Reset switch | Panasonic **EVQ-PUC02K** | 1 | **2** | SMD side switch |
| 7 | Power switch | Alps **SSSS811101** | 1 | **2** | SMD side switch |
| 8 | MCU headers | **2 × 12-pin**, 2.54 mm (e.g. `PPTC121LFMS-RC`) | 2 | **4** | ❓-7: headers vs spring headers vs JLC-soldered |
| 9 | Battery | LiPo 3.7 V, single cell | 1 | **2** | ⚠️ not modelled yet (`component_3d_models/todo.md`: "Sumar modelo de la batería?"). Size must fit under the plate / in the tenting base — measure before buying |
| 10 | Keycaps | **CFX 1u** (Chosfox) ×64 | 32 | **64** | 16.50 × 16.50 ±0.07 mm, 3.70 mm tall (verified) @ 17 mm pitch. MBK (17.5 × 16.5 mm) does **not** fit this spacing |
| 11 | Optional | nice!view display | 0 | 0–2 | P0/P1/P2 are reserved for it; not in the current BOM |

Reference part numbers already used in the repo: switch `CPG135001S30` (Kailh Choc V1, the number
JLC uses), header `PPTC121LFMS-RC`.

## 2. Mechanical

| # | Part | Spec | Per half | Total | Notes |
|---|---|---|---|---|---|
| 12 | Standoff (**default, F3b**) | Soldered M2×3+3, LCSC **C192879** — JLC's PCB Assembly places AND solders it (SMT+THT+mixed is one service, `assemblyComponentFlag: true`, 焊接辅料) | 5 | **10** | **verified 2026-11-16**: 5 333 in stock, $0.0126, `leastPatchNumber` 2 — see `FASTENERS.md` §4.5/§5.0. Supplies the only thread; printed boss `standoff_length − 3` fills the rest; screw from below. Alternative topologies: `standoff_body_length: 6` = press-fit (old), `0` = thread in plastic |
| 13 | Top screw | **not used under F3b** — the 32 switches hold the plate. Only needed for the press-fit topology (`standoff_body_length: 6`) | 0 | 0 | F3b leans on the hotswap socket grip (FASTENERS §1) |
| 14 | Bottom screw | M2 × **10 mm** low-profile socket head (`93070A278`), derived: `standoff_length + 2.5` | 5 | **10** | through floor + boss into the soldered standoff |
| 15 | Optional | M2 coupling nut 6 mm (`93020A101`), M1.4/M1.6 screws and nuts | — | — | already in `component_3d_models/`; purpose 🟡 (probably for the palm rest / tenting anchoring) |

## 3. Printed / fabricated parts

| # | Part | Source | Qty | Status |
|---|---|---|---|---|
| 16 | PCB, left | `filtered-output/pcbs/gerbers/left_pcb.zip` | 1 (order 5) | 🔴 **currently unrouted — do not order** |
| 17 | PCB, right | `filtered-output/pcbs/gerbers/right_pcb.zip` | 1 (order 5) | 🔴 same |
| 18 | Switch plate ×2 | FR-4 (from `plate_left/right.kicad_pcb`) **or** printed (from `l_cover`) | 2 | 🟠 right plate has no screw holes; left/right shapes differ |
| 19 | Case bottom+wall ×2 | printed, `l_case_3d.stl` | 2 | 🔴 only the left exists (`r_case_3d` missing) |
| 20 | Cover/plate with controller housing ×2 | printed, `l_cover.stl` | 2 | 🔴 only the left exists |
| 21 | Tenting base ×2 | printed, `tenting_system.stl` | 2 | 🟠 file has inverted normals; only the left outline is generated |
| 22 | Palm rest ×2 | printed, `palm_rest.stl` | 2 | 🟡 generated; attachment undecided; not watertight |

JLC assembly would place, in the best case: 64 diodes (F) + 64 hotswap sockets + 2 JST + 2 reset
+ 2 power (B) — everything except switches, keycaps, MCU and battery. See ❓-6.

## 4. Consumables / tools implied by the design

- 1.2 mm or 1.6 mm PCB coupon for the socket test-fit (`HARDWARE-STACK.md` §7)
- Flux + iron for hand-soldering sockets if JLC cannot place them
- Superglue/epoxy for press-fit standoffs if they spin
- ZMK flashing: USB-C data cable (nice!nano is USB-C), and access to the reset button
  (the case must keep it reachable — `README.md` TODO)

## 5. Quantities to double-check after each config change

`scripts/check_matrix.py --counts` prints the footprint count per type per half straight from the
generated `.kicad_pcb`. If those numbers stop matching this table, this table is stale — update
it in the same commit.
