# Fasteners, bosses and hot-swap sockets — decision record

**Last updated:** 2026-11-16 (end of session 2)
**Status:** analysis complete, **decision MADE and IMPLEMENTED — F3b (§3), default since 2026-11-16.**
One knob (`standoff_body_length`) switches topology; the case boss, the BOM and the screw lengths
derive from it (§4.6). B13 (screw move) is also done. Everything else in this file is analysis.

This document exists so the reasoning survives a pause of weeks. Read §0 first.

---

## 0. Read this first

**The question:** how do the case, PCB, plate and cover hold together, using only a screwdriver
(no soldering iron, no tapping, no glue), in a way we can actually order from JLCPCB?

**The answer so far, in one paragraph.** Hot-swap sockets change the problem completely: the
switch latches into the plate *and* its pins are gripped by the socket that is soldered *and*
peg-anchored to the PCB, so plate + switches + sockets + PCB form **one rigid, self-clamping
unit**. Nothing has to bolt the plate to the PCB. That deletes the top screw, deletes the
"two screws through one bore" problem, and leaves only one real question: **how to anchor that
unit inside the case.** Four viable answers are analysed in §3; the most promising — and the
one the author proposed — is **§3 option F3: a threaded standoff soldered onto the PCB by JLCPCB
as a placement**, so the builder receives a PCB that already has its own threads and the printed
parts get simpler, not more complex.

**What is left:** nothing to decide — F3b is implemented and the service question is closed
(§5.0: PCB Assembly does SMT+THT+mixed, double-sided). What remains is *plumbing and mirroring*:
**B4** (the right-hand PCB still has no screw holes at all, so the right half cannot be anchored),
**B3** (CPL exports 2 of 98 placements), and the cosmetic preview gaps noted in §4.6. See §7.

**Do not redo:** the screw move (B13, done — positions in §4.1). The numbers in §4 are measured,
not estimated; each says where it came from in §9.

---

## 1. What actually holds the keyboard together

### 1.1 The mechanical chain

```
keycap
  └─ press-fit on switch stem
switch ──latches──> plate            (14 mm cutout, 1.2 mm plate)
  │
  ├── 2 × Ø1.9 pegs ──press-fit──> PCB      (switch body locates in the PCB)
  └── 2 pins ──gripped by──> hot-swap socket
                                  │
                                  ├── 2 × Ø3 pegs ──press-fit──> PCB
                                  └── 2 × SMD pads ──soldered──> PCB
```

Verified against the generated footprint (`ergogen/footprints/ceoloide/switch_choc_v1_v2.js` →
`ergogen/output/pcbs/left_pcb.kicad_pcb`):

| feature | size | role |
|---|---|---|
| centre hole | Ø5.0 NPTH | switch centre post |
| two side holes | Ø1.9 NPTH at ±5.5 mm | switch locating pegs |
| two socket holes | Ø3.0 NPTH at (0,−5.95), (5,−3.75) | **hot-swap socket pegs — takes the load** |
| two socket pads | 2.6 × 2.6 SMD | socket solder joints |

The Ø3 socket pegs matter more than the solder: they carry the mechanical load, and the solder
only retains them. That is why every hot-swap sandwich board in the hobby works without screws
between plate and PCB.

### 1.2 What that insight removes

1. **The top screw is redundant.** Its only job was clamping the plate to the standoff. The
   switches already do that, 32 times over, with a spring latch each.
2. **The 1.0 mm air gap stops being a precision case dimension.** The gap is set by the switch
   body: if the plate and PCB are the wrong distance apart, the switches physically cannot seat.
   The switch is the gauge. The case only has to put the assembled unit at a sensible height.
3. **The plate does not strictly need screw holes.** (B13's fix stays valid and harmless — it
   also fixed the case and PCB holes — but the *requirement* on the plate relaxes if the plate is
   no longer clamped. See §7 Q3.)
4. **The "two screws through one bore" problem disappears.** That problem only existed because
   the plate and the PCB were treated as two parts needing two independent clamps. They are one
   part. This was the single hardest constraint in the whole fastener search, and it was
   self-inflicted.

### 1.3 What it does *not* remove

- The PCB still has to be held **in** the case (it can't float; the caps must clear the rim and
  the USB-C port must line up).
- The PCB bottom is crowded: sockets (≈3.5 mm tall), diodes, the MCU. The anchoring hardware
  must live in the webs between switches — which is exactly where the 5 screw points are (§4.1).
- Someone still has to buy *something* and drive *some* screws. The options differ in how much.

---

## 2. The revised problem statement

> Hold the PCB (with its self-clamped switch/plate unit) at a fixed height inside the case, so
> the keycaps clear the rim and the USB-C cut-out lines up, using only a screwdriver, with
> hardware that can be bought or that JLCPCB can place.

That is one job, not two. Everything in §3 is an answer to it.

---

## 3. Option space

All five anchor the same 5 points (± mirror). They differ in **who supplies the thread**.

| | thread lives in | builder buys | tools | printed parts | exits case floor? |
|---|---|---|---|---|---|
| **F1** | printed pedestal (screw threads into plastic) | 10 × M2×6 | screwdriver | pedestals + bosses | **yes** → needs counterbore or feet |
| **F2a** | printed boss, self-tapping | 5 × M2 thread-forming | screwdriver | bosses | no |
| **F2b** | heat-set insert in printed boss | 5 inserts + 5 screws | **soldering iron** | bosses | no |
| **F2c** | M2 nut pocket in printed boss | 5 nuts + 5 screws | screwdriver | bosses + pockets | no |
| **F2d** | splined **press-fit** standoff in printed boss | 5 standoffs + 5 screws | pliers/vice | bosses | no |
| **F3** | **threaded standoff soldered to the PCB** | 5 screws only | screwdriver | **floor only** | no |
| **F4** | clips/snap-fit for the cover | 0–5 screws | none | clips | no |

### F1 — bottom screws into printed pedestals (current design)

Screws enter through the case floor, into the pedestal that also supports the PCB. This is what
the repo does today (`standoff_length: 6`, BOM `93070A276` M2×6).

*For:* zero new hardware, no special parts, already modelled and gated by `hardware_bom.py`.

*Hidden cost (found while writing this):* F1 has **two independent things trying to set the same
dimension.** The standoff fixes the plate↔PCB distance, and the switches also fix it (they are the
gauge). Printed ±0.2 mm plus PCB ±0.1 mm against a switch that wants 1.0 mm means the case can
fight the switches: too short and the sockets lift off their pins (intermittent keys), too long and
the switches never latch. Every topology where the case clamps the *plate* has this fight. F2/F3
clamp only the PCB and let the switches own the gap — mechanically the more honest design.
*Against:* the head protrudes **1.0 mm below the floor** (measured), so the case needs either a
counterbore in 3 mm of plastic or 1 mm feet; and the tenting base needs **1.0 mm-deep Ø5 pockets**
at the 5 points to sit flat. Also: the thread is in FDM plastic, and the user's stated worry is
pilot-hole reliability.

### F2 — screws from above, through the PCB, into case bosses

Because the plate is no longer clamped, the screw can drop **through the PCB only** (not the
plate) and thread into a boss standing on the case floor. The head sits on the PCB top, hidden
under the plate, inside the 1.0 mm air gap — a low-profile head is flush with the plate underside,
which is harmless (it just kisses it).

Assembly order: PCB in → 5 screws → plate on → 32 switches in. Reversible in reverse.

*For:* **nothing exits the case floor** — no counterbore, no feet, no pockets in the tenting base.
The case floor becomes a plain 3 mm slab. Plate keeps its 5 holes as clearance, or loses them.
*Against:* still a printed thread (F2a), or an iron (F2b), or nut pockets (F2c); and the screw is
only reachable after removing the switches.

Thread choice within F2 (see §4.3 for the strength numbers):

- **F2a self-tapping**: needs a thread-forming screw in M2 — the user's worry, and the part is
  harder to source in M2 than in M3. **Low priority, not discarded.**
- **F2b heat-set insert**: best mechanical result, but needs a soldering iron. **Rejected by the
  author** as "not a normal person" step. Kept here only for completeness.
- **F2c nut pocket**: an M2 nut dropped into a hex pocket in the boss. Screwdriver only, no iron,
  and a nut is the cheapest thread in the world. Boss envelope Ø5.9 (M1.4) / Ø6.1 (M1.6) /
  Ø7.0 (M2) — §4.2 shows the room exists, sometimes only after moving the screw.
- **F2d splined press-fit standoff** *(already modelled in this repo — `component_3d_models/
  92985A817*` M2 open-end 2 mm, `92985A818*` 3 mm, plus `93020A101` a 6 mm M2 coupling nut)*:
  a knurled/splined metal standoff is pressed into a printed hole; the splines bite into the
  plastic and it is held by friction plus the screw preload. No iron, no solder, no tapping, and
  the thread is factory-cut. The usual trick is to screw it onto a long screw from the far side
  and draw it in, which avoids needing a press. **This is the best "normal person" option that
  keeps the thread out of the printing** — stronger than a self-tap, friendlier than an insert.
  It was apparently considered in an earlier session and then dropped; worth reviving as the
  fallback if F3's LCSC part does not exist.

### F3 — SMT threaded standoff, placed by JLCPCB (**the author's idea**)

Instead of printing the thread, **buy it and let the assembler solder it on**. A solderable
threaded standoff/spacer (the PEM `SMTSO` family, Würth SMT spacers, and generics) is an SMT
part: flat solderable base, tape-and-reel, reflow-compatible, female thread through the middle.

The PCB arrives with 5 threaded posts already on it. The case floor becomes a plain slab with 5
clearance holes (or none, if the screws come from above). The printed part count goes **down**,
not up: no pedestals, no bosses, no nut pockets.

*For:*
- **Thread quality is factory-grade**, not FDM. No inserts, no tapping, no pilot-hole risk.
- The builder buys **only screws** — the thing the author asked for ("save the person from having
  to individually buy parts").
- It removes the tallest printed feature (the 6 mm pedestal) and, with it, a lot of printed
  volume and print time.
- Height tolerance is machined (±0.1 mm) instead of layered.
- It kills the "two screws per bore" problem *and* B20's ledge problem at the same time, because
  the PCB becomes the structural datum.

*Against / must verify:*
- **Sourcing is unverified.** I have not confirmed that any specific threaded SMT standoff is in
  LCSC stock with an LCSC part number. If it is not, JLC will not place it under the standard
  service. **This is the first thing to check next session (§7 Q1).**
- It must fit the available web: pad footprint plus body diameter vs the same Ø envelope that
  limits the bosses (§4.2).
- Perfectly-sized heights are a catalog choice, not a design variable — so `standoff_length`
  becomes "pick the nearest catalog height" (typically 4/5/6/8 mm).
- Adds an extended-part fee per unique part (small).

**This is the option I would pursue first.** It is the only one where the answer to "where does
the thread come from?" is "the factory", and the only one that makes the printed parts *simpler*.

### F3b — F3 + a printed boss to cover the height difference (**the answer to "the 3 mm body is too short"**)

The 3 mm body (`C192879`) is only too short if it has to span the whole gap. It doesn't have to:
**a printed boss under each standoff supplies the missing height, and the metal part supplies only
the thread.** That is the whole trick — the height comes from plastic (cheap, printable, no
tolerance risk) and the thread comes from the factory (the one thing you cannot print reliably).

See `docs/img/f3b-boss.png` — a to-scale cross-section at `standoff_length = 6`.

- **Boss height = `standoff_length` − 3.0** (the body length), plain Ø4.2 post, no thread, no
  pocket, no insert. It is the shortest printed feature in the whole design.
- **Screw length ≈ 3.0 (floor) + boss + 2.5 (engagement)**, i.e. `standoff_length + 2.5`.
- **Load path is metal-in-compression:** PCB bottom → the body's top face → the boss → the floor.
  Typing force never loads the solder joint; the screw only retains the stack. This is strictly
  better than F1, where the thread is in plastic and carries the load.
- **The stud clears the plate for free.** 3.0 stud − 1.2 PCB = 1.8 mm above the PCB top, and the
  plate top is 2.2 mm above it, so the tip stops **0.4 mm below the plate's top face**, inside the
  Ø2.2 hole **that B13 already gave us**. No clearance problem, nothing pokes out. (B13 and F3b
  turn out to depend on each other.)

| `standoff_length` | printed boss | screw | case height | socket clearance |
|---|---|---|---|---|
| 4.5 | 1.5 mm | M2×8 | **10.9 mm** | 1.0 mm |
| 5.0 | 2.0 mm | M2×8 | 11.4 mm | 1.5 mm |
| 6.0 (today) | 3.0 mm | M2×10 | 12.4 mm | 2.5 mm |

**And here is the bonus the author has wanted all along: `S` can finally shrink.** The current
floor of 6.1 mm exists only because two screws share each bore and their tips must not meet in the
middle (B21, `MOUNT_GAP_IDEAL`). With **one** screw per point that constraint evaporates; the only
remaining limit is socket clearance (3.5 mm) plus a printable boss. **s = 4.5 is reachable, which is
a 1.5 mm shorter case** — and a shorter, cheaper screw.

*Against:* one more print feature per point (trivial), and it depends on JLC placing the part. But
it is the only topology where the builder buys **nothing but screws**.

### F4 — clip or snap-fit cover, no screws at all

The plate/cover unit is held by the switches, so in principle the case only needs to stop it
sliding. A pair of printed hooks or a snap lip would do it.

*For:* zero hardware, zero assembly steps, nothing to lose.
*Against:* printed clips fatigue and are the classic failure of FDM enclosures; and the author
wants a solid keyboard, which argues for metal threads. Keep as a *fallback* for the cover, not
for the PCB.

### F5 — press-fit / friction, nothing at all

Rejected: FDM tolerances are ±0.2 mm, the PCB is 1.2 mm FR4, and a keyboard gets picked up by the
plate. Not worth analysis.

---

## 4. Numbers

### 4.1 The 5 screw points (B13, **done and verified**)

| point | position (PCB coords) | cutout clearance | plate-outline | nearest key |
|---|---|---|---|---|
| left_top | (43.80, 86.15) | +1.80 | 1.80 | 9.9 |
| left_bottom | (43.80, 137.15) | +1.80 | 1.80 | 9.9 |
| right_top | (128.80, 80.13) | +1.85 | 1.80 | 10.1 |
| right_bottom | (128.80, 132.63) | **+1.769** (tightest) | 1.77 | 8.8 |
| thumb | (131.710, 160.296) | +3.34 | 1.30 | 10.9 |

Gate: `scripts/check_assembly.py` → **PASS** (needs ≥1.7 mm to any 14 mm cutout).
Moved from the old points by 2.0–2.5 mm (grid) and 3.9 mm (thumb). See `docs/img/screw-move.png`.

### 4.2 Room available for a boss or standoff body

A boss must clear the neighbouring key cutouts by the same 1.7 mm rule. Measured thresholds — the
**minimum key-to-screw distance** each body diameter needs:

| body diameter | needs key-distance ≥ | note |
|---|---|---|
| Ø4.2 | **8.55 mm** | M1.4 nut pocket / small standoff |
| Ø6.0 | 9.45 mm | M1.6 nut pocket |
| Ø7.0 | 9.95 mm | M2 nut pocket |

The B13 screw set reaches **8.83–10.07 mm**, so all three fit; the Ø7.0 case needs the set as
moved (it did not fit before B13). If the right_bottom point at 8.8 mm turns out to be the binding
one for Ø6.0/Ø7.0, moving it costs another ~1 mm — cheap, the plate has room.

### 4.3 Thread sizes and strength

Load per screw is tiny: a 500 g half-keyboard on 5 screws needs **~4.3 N per screw** in the worst
case (one screw carrying everything is still <5 N).

| thread | tensile area | breaking load @400 MPa | margin |
|---|---|---|---|
| M1.4 | 0.983 mm² | 393 N | **91×** |
| M1.6 | 1.270 mm² | 508 N | 117× |
| M2 | 2.073 mm² | 829 N | 191× |

So **strength does not choose the screw; availability does.** M2 wins because it is the most
common, cheapest, and the repo already ships it (B21: M2×6, `93070A276`). M1.6 would buy ~30 %
more room for bosses at the cost of sourcing. M1.4 is only interesting for a nut pocket in the
tightest web.

Engagement: `screw_engagement: 2.5` mm, `screw_top_length` 6 (min 5.9), `screw_bottom_length` 6
(min 5.5) — B21 verified these against the actual stack.

### 4.4 Stack constants (the case height is derived from these)

```
screw_radius            1.1      # M2
case_bottom_thickness   3.0
standoff_length         6.0      # B17
pcb_thickness           1.2      # B15: measured, was implicitly 1.6
top_plate_thickness     1.2      # choc need exactly 1.2; 1.5 is FR4's max for seating
plate_top_above_pcb_top 2.2      # ⇒ 1.0 mm air gap between PCB top and plate bottom
plate_sits_on_wall      1        # B20 option D (2026-11-17)
case_border_height      = 3.0 + 6.0 + 1.2 + 2.2 − 1.2 = 11.2   # verified on the case STL
                                  # ... but the PLATE TOP is still 3.0 + 6.0 + 1.2 + 2.2 = 12.4
```

**B20 option D (2026-11-17) split the top of this stack in two** — `case_border_height` is no longer
the plate top. The wall stops at the plate's **underside** (11.2) and the FR4 plate overhangs it and
is the lid; the plate top is unchanged at 12.4, so nothing above it moved. A case STL must therefore
measure **11.2**, not 12.4 (`scripts/hardware_bom.py --case-stl` asserts exactly that, and it now
carries the two numbers separately). The plate outlines are the case footprint, in two variants:
`plate_left_bay` (controller + JSPh bays open, default) and `plate_left_full` (bays covered).
Full record, numbers and the USB-C consequence: `docs/B20-PLATE-ON-WALL.md`.

The 1.0 mm air gap is the space the switch body's lower half occupies. **Under §1.2 it is no
longer a case dimension** — it is a property of the switch, and the case cannot violate it: the
switches would refuse to seat. `standoff_length` therefore only controls *how high the whole unit
floats above the floor* (needs ≥4.5 mm for socket clearance) and *where the caps sit relative to
the rim*.

### 4.5 F3 parts — **VERIFIED against JLC's live parts API (2026-11-16)**

I queried JLCPCB's SMT component API (`POST /api/overseas-pcb-order/v1/shoppingCart/smtGood/
selectSmtComponentList`) rather than trusting a catalogue page. Results:

**Solderable M2 standoffs that exist, in stock, and JLC will place** — brand XHHD (新宏辉达), LCSC
category *knurled studs*, Chinese description ending in **【焊接辅料】** ("soldering auxiliary"),
`assemblyComponentFlag: true`:

| LCSC | model | body + stud | stock | unit price | verdict |
|---|---|---|---|---|---|
| **C192879** | M2*3+3 | 3 mm + 3 mm stud | **5 333** | $0.0126 | ✅ orderable today; body too short (§ below) |
| C193469 | M2*5+3 | **5 mm** + 3 mm stud | **27** | $0.0107 | ⚠️ right length, essentially out of stock |
| C193465 | M2*10+3 | 10 mm + 3 mm stud | 2 840 | — | ✅ in stock but too tall |

All three are "单通头" = **male-female**: a 3 mm male stud (goes through the PCB and is soldered)
plus a body with an M2 female thread (receives the screw from the case). Attrition allowances are
declared (`lossNumber` 4–10), and reels are 4 000–10 000 pcs, so 5–50 pcs is a trivial order.

**What does NOT exist in stock (checked, not assumed):**

| what | result |
|---|---|
| M2 **female-female** (双通头) standoff | **none in stock** — only M3 versions (thousands) |
| M2 **nuts** as placement parts (`Nut`, `Through hole embedded round nuts`) | catalogued, **stock 0** |
| M3 **nuts** as placement parts — `C133377`, *Hexagonal nuts* | **stock 14 510** ⇒ JLC demonstrably *places nuts* |
| PEM `SMTSO`-style true SMD standoffs | only under `C9900xxxxx` private codes, **stock 0** — not orderable |
| M3 **female-female** hex standoffs (e.g. `C50377307` STTZ3003, `C551326` M3*6) | plentiful stock, but M3 hex is Ø5.5 and needs ~9.95 mm key clearance (§4.2); our min is 8.83 mm |

**Consequences for F3 — three real findings:**

1. **The idea works.** JLC sells, stocks and places M2 threaded standoffs explicitly intended to be
   soldered to a PCBA. It is not a naming trick: these are real line items with a price, a reel
   quantity and an assembly flag. (This also answers "can a nut substitute?" empirically — yes, JLC
   *does* place nuts, `C133377` in 14 510 stock; M2 nuts simply are not among them.)
2. **The stud length is a problem.** 3 mm of stud through a 1.2 mm PCB leaves **1.8 mm protruding
   above the PCB top**, and the choc air gap is only **1.0 mm** (§4.4). The plate's existing Ø2.2
   screw hole would swallow 1.2 mm of that, leaving ~0.6 mm standing proud of the plate top — which
   is inside the gap between plate and keycap, so probably harmless, but **it must be checked
   before committing**. A 1.2 mm-stud variant (or filing the stud) would remove the question.
3. ~~**The body length is the other problem.**~~ **RESOLVED by §3 F3b:** the body does **not** need
   to span the gap — a printed boss covers the difference. The 3 mm body with 5 333 pcs in stock is
   therefore the *right* part, and the 5 mm one (`C193469`, 27 left) is no longer needed at all.

**Net: F3b is now both verified-feasible and verified-suitable.** The 3 mm part (5 333 in stock,
1.3 ¢) plus a 3 mm printed boss reproduces the current 12.4 mm stack exactly, and at `s = 4.5` makes
it 10.9 mm. The only thing left to confirm is the *process*, not the geometry: **does JLC reflow-solder
this part or only place it, and does the stud need a specific hole size for wicking?** (One question
to JLC support.) **F3b is the recommendation; `F2d` press-fit stays the fallback if that answer is
unfavourable.**

### 4.6 Configurability — one number now drives the whole topology (**implemented**)

`ergogen/config.yaml` gained:

```yaml
standoff_body_length: 3                                    # the knob
standoff_boss_height: standoff_length - standoff_body_length   # derived, never authored
```

That is the whole mechanism. Changing this one number switches topology and *nothing else needs
editing* — the boss is extruded in the case, the BOM, the screw length and the validation all
follow:

| `standoff_body_length` | topology | printed boss | screw | top screws |
|---|---|---|---|---|
| **3** (default) | **F3b** | `s − 3` | `s + 2.5` → M2×10 fan s=6 | **none** |
| 6 | press-fit standoff (the old design) | 0 (no boss) | M2×6 | 5 per half |
| 0 | printed post, thread in plastic (F1) | `s` (full height) | `s + 3 + 2.5` | none |

Wired end to end:
- **Case geometry:** `l_standoff_bosses` (annulus Ø4.2 / Ø2.2) extruded `standoff_boss_height` on
  the floor. Verified on the STL: 6 outlines above z=3.0 (5 bosses + wall), 1 below, top at exactly
  6.00 mm, bbox and 12.4 mm height unchanged.
- **`scripts/hardware_bom.py`** auto-detects the topology, emits the right BOM, and gates it
  (boss ≥ 1.0 mm printable, screw bite ≥ engagement, metal part ≤ standoff). `--topology standoff`
  reproduces the old BOM byte-for-byte, so the change is a superset, not a break.
- **Configurator:** new **"Metal part below PCB"** field (`case.standoffBodyLength`), validated as
  `0 ≤ body ≤ standoffLength`, written back to `config.yaml` by `generate.mjs`.
- **Follow-up deliberately not built:** *querying LCSC stock and auto-picking the nearest available
  body length*. The user asked for it as a later button, so availability is still a manual check.
  Everything needed for it exists (§4.5 was generated by exactly that API call).

---

## 5. JLCPCB: naming, attributes, and "can a nut substitute?"

This section answers the question the author asked twice and that never got a proper answer.

### 5.0 Which service does this — **PCB Assembly covers all of it** (verified on jlcpcb.com)

Their PCB Assembly page states: *"SMT, THT & Mixed PCB Assembly — Supports Surface Mount
Technology (SMT), Through-Hole Technology (THT), and mixed-technology PCB assembly. Single-Sided
and Double-Sided Assembly."*

So there is **no separate service to buy and no process question to resolve**. Hot-swap sockets and
diodes are SMT; the standoff's stud is through-hole; their *mixed* service does both on the same
board, and double-sided means parts may sit on the bottom face. The part is already in their
assembly catalogue (`componentSource: shop`, `assemblyComponentFlag: true`), priced and reeled, so
it is added to the same assembly BOM as everything else.

The page also lists the sourcing fallbacks if a part is not in the library: in-stock components,
global distributor sourcing, pre-order, **customer-consigned components**, and new-part requests.
`C192879` is stocked, so none of that is needed — but it means a jlc-specific part is never a dead
end either.

*Earlier framing, now withdrawn:* I had asked whether the standoff is "reflow-soldered or merely
placed" and what hole size "solder wicking" needs. Both were over-thinking a service that already
handles through-hole: the stud is inserted and soldered, and the PCB hole only has to match the
stud (Ø2.2 for an M2 stud, which is what `screw_radius` already gives us).

### 5.1 What JLC actually reads

JLC's assembly service consumes, and checks against, **five** declarations — not one:

1. **BOM** — comment/value, designator, footprint, **LCSC part number**.
2. **CPL/POS** — X, Y, rotation, layer, for every designator in the BOM.
3. **Footprint** — must contain real pads (a footprint with 0 pads cannot be placed).
4. **KiCad `attr`** on the footprint — `smd` / `through_hole` / `exclude_from_pos_files`.
5. **Part height / package** — used for their stencil and clearance checks.

Miss any one and the part silently disappears from the order.

### 5.2 "Is option 1 just a matter of naming?"

**For the parts we already have: yes, essentially.** The repo already proved this the hard way
(`docs/STATUS.md` §5.7): a KiCad-generated POS file for the same board contains the diodes,
switches, reset switch and power switch; the KiBot-generated one contains **2 of 98 placements**.
The difference is not geometry — it is `only_smd: true` in `kibot/jlpcb_pos.kibot.yaml` plus a
diode footprint with no `attr smd`. Rename/attribute them correctly and the placements appear.
That *is* B3, and B3 is genuinely a naming bug.

So: **naming is the mechanism, but it has to be complete naming.** The pipeline doesn't care what
you call the part; it cares that BOM ↔ CPL ↔ footprint ↔ attr agree.

### 5.3 "Can a nut replace it, is it just naming?"

No — **a nut is a different part, not a rename.** Naming can *describe* a nut, but it cannot
*turn* a standoff into one, because:

- the footprint changes (a nut is not soldered; it has no pads, so it cannot be a CPL entry at
  all — it is a *mechanical* part, and JLC places only electrical SMT parts in the standard
  service);
- the height and thread position change (a nut's thread starts at its face; a standoff's at a
  chosen depth);
- a nut has to be *captured* by something — it cannot sit loose on a PCB.

That said, "nut" is the right answer to the *same question* in a different topology: **F2c**
puts an M2 nut in a printed pocket, and then the nut is bought in a bag of 100 for pennies and
the PCB needs no special part at all. If the goal is "don't make the builder buy exotic parts",
F2c and F3 are equally good at it by opposite routes: F2c = "cheap nut you drop in", F3 = "no
loose part at all, it's already soldered".

Where naming *does* matter dangerously: the **value/comment** string is what a human (and JLC's
review) reads. If a switch footprint is valued `M2 standoff`, you get a query at best. So the
value must describe the part that the footprint actually is.

### 5.4 The blocker: B3

Any fab-side option (F3, or shipping hardware with the PCB) is **blocked by B3**: the CPL carries
2 of 98 placements because of `only_smd: true` and missing `attr smd`. Until B3 is closed, we
cannot hand JLC a board that has *any* placed part reliably, let alone a new one.

B3 is small (attributes + config), but it is the gate. See §7 Q2.

### 5.5 Economics (rough, to be confirmed)

- Standard assembly: 5 boards minimum in practice, cheaper per unit at 10–30.
- Extended part fee: ~$3 per unique non-basic part, once.
- Threaded SMT standoffs: order of $0.1–0.5 each at quantity, vs $0.02 for a nut, vs $0.00 for a
  printed boss.
- Screws: a bag of 100 M2×6 is a few dollars regardless of option.

So the money is not the decider. **Assembly friendliness and printed-part simplicity are.**

---

## 6. Recommendation — **ADOPTED 2026-11-16 (F3b is the default in `config.yaml`)**

1. **Close B3 first** (it gates everything fab-side, and it is a small, already-diagnosed fix).
2. **Adopt F3b** — `C192879` (M2×3+3, 5 333 in stock, $0.0126, `assemblyComponentFlag: true`,
   sold as 焊接辅料) soldered by JLC, plus a printed boss of `standoff_length − 3.0` under each.
   Both earlier objections are dissolved (§4.5): the stud tip clears the plate by 0.4 mm inside the
   B13 hole, and the boss supplies the height so the 3 mm body is the correct part. Only the
   *process* question remains (does JLC reflow it?).
3. If no such part exists, **fall back to F2d** (splined press-fit standoff — factory thread,
   pliers only, already modelled in `component_3d_models/`), or **F2c** (M2 nut pocket) if even a
   press-fit feels like too much. Keep F2a self-tapping as the last resort.
4. **Do not** revive heat-set inserts (rejected: needs an iron) or F1's counterbore (only if F3/F2
   both fail).
5. ~~Whichever wins, the B4 mirror pass is required first~~ — **now the top mechanical blocker:**
   the right half has no `r_screw_*` points, so its PCB has **no screw holes** and therefore
   nothing to solder a standoff into. The *printed* right case is a mirror of the left
   (`REVERSIBLE.md`), so the bosses come for free once the PCB is mirrored.

Rationale in one line: *the thread is the only thing the builder can't make themselves, so buy
the thread — and let the assembler solder it on.*

---

## 7. Open questions for the next session

| id | question | why it matters |
|---|---|---|
| **Q1** | ~~Does a threaded SMT standoff exist with an LCSC code?~~ **CLOSED 2026-11-16:** yes — `C192879` (§4.5); process question dissolved because PCB Assembly covers SMT+THT+mixed (§5.0). **Open sub-item:** a *button* that queries LCSC stock and auto-picks the nearest available body length (§4.6). | Decides nothing now; it is an UX upgrade. |
| **Q2** | B3: close the POS/CPL declaration so all 98 placements export. | Gates every fab-side option. |
| **Q3** | If the plate is no longer clamped, do we **drop the plate's 5 screw holes** (and the B13 outline constraint with them)? | Simplifies the plate; B13's fix stays valid either way. |
| **Q4** | Does the cover need *any* fastener, or is "held by 32 switches" enough? | Could remove the last 5 screws. |
| **Q5** | Re-derive the rim/plate relationship once the anchoring is fixed (B20 ledge; rim 1.2 mm proud of the plate top). | Cosmetic + cap clearance. |
| **Q6** | Mirror the 5 screw points to the right half (B4). | Right plate/cover/case have no anchoring today. |

---

## 8. Figures

| file | shows |
|---|---|
| `docs/img/fastener-options.png` | 5 topologies side by side, cartoon level |
| `docs/img/fastener-sections.png` | 5 aligned cross-sections at the screw plane |
| `docs/img/screw-move.png` | the B13 move, before/after, with clearances |
| `docs/img/plate-holes.png` | the plate's edge cuts with the 5 screw points; shows why the thumb clipped |
| `docs/img/B17-stackup.png` | measured stack-up, floor → plate top → rim |
| `docs/img/f3b-boss.png` | **F3b to scale:** printed boss + soldered standoff + M2×10 |

---

## 9. Where the numbers came from

| number | source |
|---|---|
| screw positions, clearances | `scripts/check_assembly.py` (PASS), 2026-11-16 |
| plate-outline distances | `ezdxf` distance from point to `l_coverpart_switch_plate_outline.dxf` |
| boss Ø vs key-distance | `scripts/hardware_bom.py --topology boss` + peg-clearance sweep |
| thread strength | tensile stress area × 400 MPa (conservative for plated steel) |
| stack constants | `ergogen/config.yaml` lines 38–81; case height verified on the STL (12.4) |
| 1 mm head protrusion | `hardware_bom.py` geometry, case floor at z=3.0 |
| 2-of-98 placements | `docs/STATUS.md` §5.7 (KiCad POS vs KiBot POS diff) |
| footprint peg geometry | `left_pcb.kicad_pcb` → `choc_v1_v2` pads |
