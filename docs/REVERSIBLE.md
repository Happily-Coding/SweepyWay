# Reversible parts — feasibility, cost, and risk

**Question (author, 2026-11-16):** JLCPCB's minimum is 5 boards per design. Can we make a
**reversible plate** (and by extension PCB) so one design serves both hands, halving what we order
per iteration? Acknowledged constraint: some setups won't allow it.

This document separates **three** different things people mean by "reversible", because they cost
very different amounts. Short version: **the plate is already reversible and free; the PCB is
possible but is a real redesign with a re-verification bill attached.**

---

## 1. Three distinct meanings

| # | Meaning | Applies to | Verdict |
|---|---|---|---|
| **R-PLATE** | One flat part; **flip it over** to become the other hand | FR4 switch plate | **Already true. Zero work.** |
| **R-PCB** | One copper design; flip the whole board to become the other hand | `left_pcb` / `right_pcb` | Possible; medium effort, real risk |
| **R-FOOTPRINT** | A footprint parameter `reversible: true` that duplicates its pads on both faces | ceoloide library | Supported everywhere we need it |

R-FOOTPRINT is the *mechanism*; R-PCB is the *decision*. R-PLATE needs neither.

## 2. R-PLATE — the plate is already reversible (free)

A switch plate has **no copper, no components and no sided features**. Flipping a chiral flat part

> **CORRECTION 2026-11-17 (B5).** The claim that the right half is an exact mirror of the left holds
> for the **FR4 plate** and for the switch/screw geometry, but **not for the controller bay**. The MCU
> zone mirrors about **x = 168.5** (`points.zones.mcu.mirror.distance: 165`) while the keys mirror
> about **x = 170**, so the right PCB's MCU / controller-bay / JST / USB-C block sits **3.0 mm closer
> to the seam** than a mirrored left does. Consequences:
>
> - **Do not print the case by slicer-mirroring the left one** — it is 3 mm out around the bay. B5 now
>   generates real `r_case_3d` / `r_cover` / `r_3d_preview` from the right-side outlines; print those.
> - The **plate** is still free to mirror (it is symmetric through its thickness and has no bay).
> - `r_hand_rest_polygon` and `r_thumb_suplementary_outline` are **not true mirrors** either, so no
>   right palm rest or tenting base is generated yet; those builders are left-only Python scripts
>   (`palmrest_and_tenting_creation/`). Tracked in `docs/B5-RIGHT-3D.md`.
>
> Open decision: whether the 3 mm MCU offset is intentional (leave the PCB, keep per-side parts) or a
> slip to be corrected by setting `mcu mirror.distance` to 170 (which would change the verified and
> routed right PCB). Until decided, the per-side generated parts are the source of truth.

produces its mirror image by definition, and the right half *is* the mirror of the left half. So:

- `plate_left` (132.22 × 116.65) flipped over **is** `plate_right` — the two files are bit-for-bit
  equivalent in geometry after the B19 fix (measured: both 132.22 × 116.65, identical cutout set).
- The thumb cutouts rotate −10° / −25° / −30° on the left; mirrored they become **+10° / +25° /
  +30°**, which is exactly what the right hand needs. No config change required.
- The 5 screw holes mirror with the rest of the outline (once B13 moves the points, they stay
  mirror-consistent automatically because they come from `left_screw` / `right_screw` point zones).

**Consequence for ordering:** order **one** plate design at quantity 5 ⇒ 2 complete keyboards
(one flipped) + 1 spare, instead of 5 left + 5 right. That is the full saving the author asked for,
on the plate side, for free.

**Two caveats, both cosmetic:**
1. The plate footprints carry silk `utility_text` (`JLCJLCJLCJLC`, the repo URL). A flipped plate
   shows them mirrored. Irrelevant mechanically; the JLC order-number silkscreen still serves its
   purpose.
2. This only works because the plate is **symmetric through its thickness**. If a future revision
   adds anything sided (a recessed counterbore, a one-sided texture, a printed-in legend), the trick
   breaks. Keep the plate side-agnostic as a design rule — worth writing down as a decision.

## 3. R-FOOTPRINT — already supported by the whole library

Grepped `ergogen/footprints/ceoloide` for the parameter:

| footprint | `reversible` support | note |
|---|---|---|
| `switch_choc_v1_v2.js` | ✅ | "if true, the footprint will be placed on both sides so that the PCB can be reversible" |
| `diode_tht_sod123.js` | ✅ | also has a **THT variant** (pads at ±3.81 mm, 1.778 mm annular) which is inherently double-sided |
| `mcu_nice_nano.js` | ✅ | "a single-side **or reversible** footprint for the nice!nano" (38 references) |
| `reset_switch_smd_side.js` | ✅ | |
| `power_switch_smd_side.js` | ✅ | |
| `battery_connector_jst_ph_2.js` | ✅ | |
| `mounting_hole_npth.js` | n/a | NPTH is symmetric anyway |

So the library does not block us. That is the single most important fact for the difficulty estimate.

## 4. R-PCB — what it actually takes

### 4.1 The mechanism, stated precisely

A flipped board's top view is the **mirror** of the file's original top view. Since the right half
*is* the mirror of the left half, one physical board flipped = the other hand. **No layout symmetry
is required** — the trick is not "make the layout symmetric", it is "make every footprint legal from
either face". Everything (outline, switch positions, MCU position, thumb cluster) mirrors together
and lands where the other hand needs it.

### 4.2 The change list

1. `choc`, `diode`, `promicro` (MCU), `reset`, `power`, `pads_bat` → `reversible: true`.
2. **Delete `right_pcb`** (or keep it as a mirror-sanity export only). One PCB file becomes the
   product.
3. Duplicate or mirror-tolerant silkscreen (key names, `url`, `JLCJLC…`, refdes).
4. Firmware: the right hand's **matrix is mirrored**. ZMK needs a per-hand matrix transform (or two
   shield variants). This is the part with no tooling support in this repo today.
5. Re-derive the pos/BOM/CPL story for a two-sided board (B3 is already open there).
6. Case: the printed case must exist in **both chiralities** — but that is free, exactly like the
   plate (flip in the slicer). It does *not* need PCB reversibility, so this is a parallel win.

### 4.3 Risk register (ranked by how expensive the failure is to discover)

| # | Risk | Severity | Why |
|---|---|---|---|
| **R1** | **Silent pin/matrix mistakes** | 🔴 high | A flipped board means the *physical* matrix is mirrored. Getting C1..C7/R1..R5 right per hand is exactly the class of bug B1 already is — and it would only show up after soldering, as dead or transposed keys. Needs a checker (e.g. `check_matrix.py --expect-mirror`) before any order. |
| **R2** | **Invalidates the verified wiring baseline** | 🟠 medium | `reversible: true` changes pad **positions and layers** (the `_reversible` variants put pads at mirrored offsets). Every wiring/fit assertion in `check_assembly.py` was computed against the current pad geometry and must be re-baselined. |
| **R3** | **Sided hardware ends up on the wrong face** | 🟠 medium | nice!nano USB-C, the JST, and the side-actuated reset/power switches all have a "correct" orientation relative to the case. Flipping moves them to the opposite face; the case openings (❓-13 / USB-C path) must tolerate both. |
| **R4** | **Hotswap pad/edge-cut clearance** | 🟡 low-medium | ceoloide warns the outer pad must not go below 1.6 mm width to stay solderable; duplicating pads on both faces plus 2.6 → the `outer_pad_width_*` knobs may need retuning near the edge. |
| **R5** | **Paste apertures on both faces** | 🟡 low | `reversible` emits `F.Paste` *and* `B.Paste`. Harmless for hand soldering; affects a reflow stencil if JLC ever places sockets. |
| **R6** | **No left/right error detection at assembly** | 🟡 low | With one design, a builder can populate two boards both as "left". Physical keying (a mark on the bottom silk) is worth adding. |

### 4.4 Cost arithmetic — what the 5-board minimum actually buys

| Strategy | Boards ordered | Complete keyboards | Iteration cost |
|---|---|---|---|
| Two designs today | 5 left + 5 right = 10 | **5** | 2 setups |
| **Reversible** | 5 (one design) | **2** (+1 spare) | **1 setup** |

So reversible does **not** produce more keyboards — it halves the **setup cost and the waste per
iteration**, which is exactly the author's stated goal ("that allows us to halve the number of pcbs
we need for each iteration"). If you want 5 keyboards, reversible needs 10 boards of one design.

## 5. Recommendation

1. **Do R-PLATE now** (free): treat the FR4 plate as ONE design, order 5, flip for the right hand.
   Also write the rule down: *the switch plate must stay symmetric through its thickness.*
2. **Do the printed parts the same way**: case, cover, tenting base and palm rest are all
   flip-able, so they too are one design each. This is already half of B5's work — it removes the
   need for `r_case_3d` / `r_cover` **if** we accept flipping printed parts (and we should).
3. **Defer R-PCB to v0.3.** Reasoning: v0.2 still has B13 (screw points) and B17 (stack-up)
   shaping the physical design; adding a pad-geometry change now would invalidate the one good
   verification baseline we have, and R1 (mirrored matrix) is invisible until assembly. The library
   support means it will not get harder later.
4. **If we do R-PCB, gate it:** a new `check_matrix.py --expect-mirror` that compares the two hands'
   net→pin maps, plus re-running `check_assembly.py` against a re-baselined pad set, before ordering.

**Difficulty summary:** plate = **trivial (done)**; printed case = **free once we accept flipping**;
reversible PCB = **moderate config work + a firmware change + a re-verification bill**, roughly a
day of careful work plus one full checker pass — not exotic (Corne/Sofle are built exactly this
way), but it should not be bundled with the mechanical fixes still in flight.
