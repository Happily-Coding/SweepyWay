# BUILD-REFERENCE — what a proven manual build of this exact part mix looks like

The repo contains a lot of geometry and no photograph of a finished keyboard. The Lily58 Pro build
guide is the closest published, photographed, thousands-of-times-followed manual for **the same part
mix as ours**: Kailh choc switches, hotswap sockets, 1N4148 diodes in a column-to-row matrix, an FR4
plate, M2 screws and a two-piece split. Reading it is the cheapest way to audit our assumptions
about assembly order, clearances and screw lengths.

- **Source**: <https://github.com/kata0510/Lily58/blob/master/Pro/Doc/buildguide_en.md>
- **Fetched**: 2026-11-15 (full text, 190 lines). Canonical: `kata0510/Lily58`, `Pro/Doc/buildguide_en.md`.
- **What it does *not* cover**: wireless (it uses two ProMicros + TRRS + OLED), printed cases,
  palm rests, tenting. Those parts of SweepyWay have no counterpart and stay `⚠️ UNVERIFIED` by
  this source.

---

## 1. Its parts list, verbatim

| Part | Qty | Note in guide |
|---|---|---|
| PCB | 2 | Reversible: "parts on each side" — mark front/back with masking tape |
| Case | 1 set (4 pcs) | 2 solid panels + 2 panels with switch holes (i.e. plate = case layer) |
| Switch | 58 | MX and choc use **separate** socket footprints |
| Switch socket | 58 | hotswap |
| Diode | 58 | 1N4148W (SOD-123), **back side**, wire toward the arrow on the silkscreen |
| Keycaps | 58 | "1.5U caps, can also be 1U" |
| OLED / TRRS / tact switch | 2 each | | 
| M2 spacer | 10 pcs (4/half near MCU) + 4 pcs (plate alignment) | **choc: 4 mm**, MX: 7 mm |
| M2 screw | 28 | |
| TRRS cable, USB cable | 1 each | magnetic USB recommended ("low durability of the ProMicro socket") |

## 2. Its assembly order (the useful part)

1. Mark front/back of both boards (masking tape) — the PCB is reversible and it is easy to lose track.
2. **Diodes** on the back: pre-tin one pad → place → solder the other side. Orientation is
   load-bearing: "if the orientation is incorrect, the key will not respond". Verify with a
   multimeter from the front before moving on.
3. **Hotswap sockets** on the back, same pre-tin-one-pad technique. "For parts that require force,
   firmly solder both pads and check for looseness/wiggling."
4. **Jack + reset** on the front (the side with the sticker): tape down, solder from behind, make sure
   the part sits flush with the board.
5. OLED (4 jumper pads bridged), then 10 mm spacers near the MCU (screw from the back, spacer on top).
6. Plate spacers: **4 mm for choc**.
7. Switches into the plate **four at a time**, starting at the middle row and working outward; choc
   "require some power for installation" — check no pin is bent first.
8. Re-push every switch after the plate is on ("make sure that installation is complete").
9. Flash the keymap, then test each key.

## 3. Assumption audit against our design

| Our assumption | Lily58 evidence | Verdict |
|---|---|---|
| Plate **1.2 mm** (D-11), choc 13.8–14.0 cutout | The plate *is* an FR4 case layer (same 1.2–1.5 mm family); a 4 mm spacer separates it from the PCB | ✅ consistent — no counter-evidence for 1.2 mm |
| Sockets and diodes on the **same side** | Both on the back, switches/sockets/diodes all one side, MCU/jack/reset the other | ✅ matches our F-side (diodes + socket) / B-side (switch) split |
| **1u only** is a legitimate layout | Ship 1.5u thumb caps, explicitly "can also be 1U" | ✅ your 1u-only variant is not a compromise, it is an option they document |
| M2 screws, **5 standoffs per half** | 28 screws / 14 per half across 4 layers | ✅ same hardware class; we use fewer parts because the case is printed, not stacked FR4 |
| **6 mm** standoff, 3 mm floor | 4 mm PCB→plate spacer for choc | 🟡 not equivalent: theirs is plate-to-PCB, ours is floor-to-PCB. What actually binds is socket depth (~3.5 mm) + switch pin travel below the PCB; 6 mm clears it, 4 mm would be marginal for hotswap |
| Reset reachable with a pin | Tact switch on the front, pressed through a case hole | ✅ same idea as our EVQ-PUC02K + pin hole |
| Wireless, no TRRS/OLED | n/a | ❓ no external validation available; own risk |
| Printed case + palm rest + tenting | n/a (their case is 4 FR4 panels) | ⚠️ UNVERIFIED — nothing in the wild to copy; validated only by the numeric checks in `PIPELINE.md` §5 |

## 4. Who does what for our JLC order

The point of the Lily58 list is that it separates *soldering* from *assembly*. Our split:

| Step | Who | Notes |
|---|---|---|
| Diodes + hotswap sockets + JST + reset + power switch | **JLCPCB assembly** | SMD; needs the BOM/CPL work in `ORDER-CHECKLIST.md` §3 |
| MCU (nice!nano) + headers | you | do **not** ask JLC to place it; sockets/pins hand-soldered or press-fit |
| Switches into the sockets | you | Lily58 step 7: check pins, start at the middle, "some power required" |
| Keycaps (CFX) | you | 1u everywhere in the row-stagger preset |
| Battery, firmware, keymap | you | |
| Plate, case, palm rest, tenting base | 3D print / FR4 order | `ORDER-CHECKLIST.md` §4 |

## 5. Failure modes it warns about → our test procedure

| Their warning | Our check |
|---|---|
| Diode orientation → key dead | `scripts/check_matrix.py` verifies one diode per matrix position and its net orientation; still spot-check with a multimeter on the first build |
| Loose socket ("wiggling") | after JLC returns the board, push a switch into each socket and tug |
| Bent switch pin before insertion | eyeball all 64 pins; choc pins bend easily |
| Reversible PCB confusion | label both halves' component side before anything is soldered |
| "Connector durability" | magnetic/angled USB-C cable for the MCU |

## 6. Numbers worth copying

- **4 mm** is the choc PCB→plate gap in a mature design (our case gives 6 mm of floor clearance; the
  plate sits at PCB top + 2.2 mm per `KEYBOARD-REFERENCE.md` §2).
- **28 M2 screws** for 4 layers ⇒ ~7 screws per layer interface. Our 5 per half is on the light side
  for a 132×135 mm board; if the case creaks, add screw points (`r_screw_*`/`l_screw_*` twins).
- Pre-tin one pad, place, solder the rest: the technique that makes 58 hand-soldered joints survivable
  (relevant if you ever assemble a half yourself).
