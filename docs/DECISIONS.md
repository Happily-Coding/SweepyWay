# DECISIONS

Format is deliberately light: **D-n = locked**, **❓-n = open** (needs a human), with the
evidence and the consequence of each. When an open question gets answered, move it into the
locked table with a date and delete it from `STATUS.md` §7.

Locked decisions are *constraints*: changing one is a design change, not a refactor.

---

## 1. Locked decisions

### D-1 — Switch: Kailh Choc V1 (hotswap), with V1+V2 compatible PCB
The author uses **Choc Ambient** (nocturnals/twilights). The PCB footprint keeps
`choc_v2_support: true`, i.e. a 5 mm centre hole and wider pads, so V2 switches can also be
inserted. Rationale: choc = low actuation force, low profile (usable without a hand rest),
17 mm-class spacing (reachable outer columns), and cheap abundant keycaps.
> Consequence: the **plate** cutout must be 14.0 mm to accept V2 too; today it is 13.8 mm
> (`plate_kx`), i.e. V1-only. See ❓-1.

### D-2 — Keycaps and spacing: CFX (Chosfox) at 17 × 17 mm
Author owns both CFX and MBK sets and designed for **CFX 16.5 × 16.5 mm** keycaps with 17 mm
pitch on both axes (`presets.cfx_spacing`, `units: $extends: presets.cfx_spacing`).
1 mm of clearance per axis is the minimum that lets CFX caps sit without rubbing.
> Consequence: MBK 1u (17.5 × 16.5 mm) **will collide** in X at 17 mm pitch. Supporting MBK
> needs `kx: 17.5–18` and a re-derived outline. The 3D preview currently shows an MBK keycap
> model, which is therefore *not* representative of the finished keyboard.

### D-3 — Matrix: 7 columns × 5 rows with skips, + 3-key thumb fan per half
Column stagger follows Ferris Sweep philosophy (`col1..col7` stagger values in
`zones.matrix.columns`, ±0.2–0.66 `ky`), thumb fan is `-10°` rotated with `-15°`/`-5°` splay.
Skipped cells: `col1/col4/col5/col6 row5`, `col7 row1` and `col7 row5` → 29 matrix keys + 3
thumb = **32 keys per half, 64 total**.
> Consequence: the row↔MCU pin map must cover exactly 5 row nets (`R1..R5`) and 7 column nets
> (`C1..C7`). The current map covers `R2..R7` → see B1 in `STATUS.md`.

### D-4 — Diodes: SOD-123, one per key, on the component (F) side, COL2ROW
`ceoloide/diode_tht_sod123` with `include_tht: false` (SMD pads only), `side: F`,
`from: {{colrow}}`, `to: {{row_net}}`, rotated `90°` and shifted `[horizontal_diode_shift,
vertical_diode_shift]` = `[-7.75, 1.5]` mm with the current preset.
Rationale: COL2ROW is what ZMK expects by default (`col2row`), and keeping diodes on F means the
keyboard's *up* face (B) stays flat under the keycaps.
> Consequence: the PCB has an F-side and a B-side assembly; the case must clear both
> (`HARDWARE-STACK.md`).

### D-5 — Controller: nice!nano v2, reverse-mounted, in its own bay below the matrix
`reverse_mount: true`, `include_extra_pins: true`, rotated 90°. Placement rationale is written
verbatim in `../Design journey/design-journey.md`: *the controller must not push the mouse
further out, must not force a palm position, must not interfere with tenting, must not add
height, must be far from spill zones, must not add much space*. The chosen spot is behind/below
the matrix in a dedicated 50 × 30 mm bay, with the JST on a separate 18 × 14 mm tongue.
> Consequence: puck-shaped footprint, big board, USB-C exits at the bay edge through a 15 × 15 mm
> slot in the case wall. `P0/P1/P2` are reserved for nice!view (data/clock/CS) and the board is
> LED-free.

### D-6 — Everything hotswappable
Switches, keycaps, MCU, battery, case: replaceable without desoldering.
> Consequence: **hotswap sockets must be soldered, switches must not be**. JLC can place the
> sockets (SMD, B side) but not the switches. ❓-6 is the assembly-scope decision that follows
> from this; note `fix_pos_package_name.py` still encodes the *opposite* intent (it renames the
> switch footprint to the switch part number `CPG135001S30`).

### D-7 — Tenting for v1: fixed 6.5° base, two printed pieces
`create_tenting_system.py`: hollow sloped shell, `SLOPE_ANGLE_DEG = 6.5`, `Z_MIN = 3`,
`HOLLOW_OFFSET = 10` (wall), pivot at the smallest X, generated from
`l_tenting_base_bottom_outline.dxf` only (left side; the right side is the mirror).
Author's note (`estado_de_situacion.txt`): the sloped hollow base "looks perfect", what is
missing is a way to grab the keyboard, and ideally stackable angle pieces; *"the most important
thing is to prepare the files for printing"*.
> Consequence: attachment is undefined (❓-4) and adjustability is deferred, but stacking
> spacers are acceptable in v1 if cheap.

### D-8 — Palm rest is in v1
`create_palmrest.py` generates a curved slab from `l_hand_rest_polygon`, 10 mm tall at the tall
end, tapering, hollow-free, coloured blue in the preview. Attachment undecided (❓-5).

### D-9 — Case: printed shell, no metal plates
3 mm base + 16 mm wall, 1.2 mm wall thickness, base = PCB outline expanded 4 mm, wall = base
minus PCB outline expanded 2 mm, 2.2 mm NPTH mounting holes. Rationale (`README.md`): "no metal
plates to help prevent static discharge from frying the keyboard", plus a power switch for
transport and an accident-prepared controller position.
> Consequence: printed material choice matters for ESD/rigidity (❓-8).

### D-10 — Build system: Ergogen + KiBot + FreeRouting + trimesh, CI-first
The *pipeline* is the second product. Anything that has to be done by hand in KiCad is a
pipeline bug (except final manual routing if the autorouter fails, which the pipeline supports
via `*_manually_routed.kicad_pcb`).

### D-13 — Configurator: local app that drives the real tools — *locked 2026-11-15*
A localhost web app (`configurator/`) edits a JSON config, generates `config.yaml`, and runs
Ergogen + the check scripts + the STL generators; a three.js panel shows the parts.
Rationale: a hosted site cannot produce the PCB, because the **Ergogen web build does not support
custom footprints** and this keyboard is nearly all `ceoloide` footprints (verified
2026-11-15). Layers 1–5 stayed local; fabrication stays in CI. The JSON contract is what a future
hosted UI would consume, so nothing is wasted if the site is built later.
> Consequence: `ergogen/config.yaml` remains the canonical file for a human; the configurator
> *derives* from it and only replaces the parameterised blocks (`docs/CONFIGURATOR.md` §3).

## 2. Open questions

### ❓-1 — Plate cutout: 13.8 (V1) or 14.0 (V1+V2)?  → **resolved: 14.0**
**Verified numbers** (see `KEYBOARD-REFERENCE.md` §2): V1 = 13.8 mm; V2 = 13.95 mm. No single
cutout lets both clip properly. 14.0 is the usual "universal" compromise: V2 clips, V1 has
~0.1 mm play per side and is still held by the plate.
**Decision (2026-11-15):** 14.0 mm, because the author wants V1+V2 compatibility. Combined with
the plate-thickness fix below, V1 switches will have ~0.1 mm play per side and be held by the
plate clips. Validate with one coupon plate before ordering the pair.

### D-11 — Plate thickness: **1.2 mm** (was 1.6) — *locked*
A choc switch's housing shoulders must seat against the plate; 1.2 mm is the spec value
(1.5 mm FR4 absolute ceiling, verified — `KEYBOARD-REFERENCE.md` §2). `top_plate_thickness: 1.6`
means switches perch and may never register. Applies to the FR-4 plate order **and** to the
printed `l_cover`. Plate **top** must sit 2.2 mm above PCB top → with a 1.2 mm plate there is a
1.0 mm air gap (`HARDWARE-STACK.md` §4.0).

### D-12 — 3D-printing material: **PLA for v1**, ASA only if heat/UV demands it — *locked*
Researched against the author's "prefer non-toxic" constraint plus r/ErgoMechKeyboards,
r/3Dprintmything and r/3Dprinting consensus (2026-11-15):
- **PLA** is the cleanest choice for toxicity (plant-derived, no styrene, low odour, all the
  MSDS sheets on file say "safe to touch"): the finished part is inert and it is the only material
  the author can print locally for free iteration. Weaknesses: softens ~55–60 °C (never leave it
  in a car or direct sun) and is brittle for thin walls / press-fit M2 bosses.
- **ASA** is the community favourite for a durable case ("harder and more durable", UV-stable,
  r/ErgoMechKeyboards) but emits VOCs while printing and needs an enclosure — irrelevant if a
  service prints it, relevant if the author does.
- **PETG** is the middle ground (tough, low odour) but creeps under sustained load — a poor match
  for press-fit standoffs.
- **SLA 9600 resin** (the MSDS mystery number): do **not** use for a functional case — brittle
  and creep-prone under screw load.
Recommendation: **PLA for all v1 parts** (case, cover, tenting base, palm rest), printed locally;
review to ASA/PA12-CF/SLS-3301PA only if a part fails mechanically or lives in the heat. If the
M2 press-fit standoffs crack PLA, switch to heat-set inserts or add a boss.

### ❓-2 — PCB thickness: 0.8 / 1.2 / 1.6 mm? (author asked for 0.8)
**Verified:** choc hotswap sockets work on **both** 1.2 and 1.6 mm; the thinner board is more
prone to flexing under switch-insertion force, which stresses socket legs and pads. JLC offers
0.8/1.0/1.2/1.6 mm, from ~$2, and 0.8–1.0 mm is capped at 300 × 300 mm (our board is
132 × 135, fine either way).
**Evidence for 1.2:** `typematrix layup dimensions.ods` records PCB = 1.3 mm measured, the choc
sandwich math only closes with a ~1.2 mm board (§4.0 of `HARDWARE-STACK.md`), and the author
remembers choosing thinner.
**Author's stated wish (2026-11-15):** 0.8 mm, "the thinner the better".
**Why I recommend 1.2 instead of 0.8 for the hotswap board:**
- No choc-hotswap build I could find uses 0.8 mm; the observed range is 1.2–1.6 mm.
- The switch's two plastic pegs (⌀1.8 × 2.65 mm) pass through ⌀1.9 holes: on 1.6 mm they
  protrude 1.05 mm below the board, on 0.8 mm they protrude **1.85 mm** — into the same space the
  hotswap socket body occupies. Nothing I found confirms that clearance at 0.8.
- A 132.5 × 134.7 mm panel at 0.8 mm flexes noticeably; every switch insertion loads the socket
  pads through that flex.
- The height win is small compared to the alternatives: 0.8-vs-1.2 saves 0.4 mm, while the CFX
  keycaps already save **1.8 mm** versus MBK, and the printed plate going 1.6 → 1.2 saves another
  0.4 mm.
**Recommendation:** **1.2 mm** for the real board; 0.8 mm is cheap to settle empirically —
add one 0.8 mm board to the order, solder a socket, insert/pull a switch 20 times, inspect the
pads. If it holds up, 0.8 becomes the v2 default. (JLC allows 0.8 mm up to 300 × 300 mm, so the
board size is not a blocker.) The generated `.kicad_pcb` files declare `(thickness 1.6)` — that
field is cosmetic for JLC (the order form wins) but it does feed 3D export offsets.

### ❓-3 — Surface finish and mask colour
Not recorded anywhere in the repo. JLC: lead-free HASL (cheap, fine on 1.2–1.6 mm boards; only
restricted on very thin 0.4 mm boards), ENIG (RoHS, flat, better for fine pitch, small upcharge).
Choc hotswap pads are large so HASL is electrically fine; ENIG is nicer for repeated socket
insertion and doesn't oxidise while the board sits waiting for assembly.
**Recommendation:** lead-free HASL, black mask, for the first prototype — unless the boards will
sit unassembled for months, in which case ENIG.

### ❓-4 — Case ↔ tenting base attachment ⭐ design work needed
Four candidate mechanisms exist in the author's notes:
1. `notas teclado.txt` — small removed circles/squares in the case bottom to insert the base
   "without making it wider" (reference: Silakka54 tenting platform); insertion from below via
   little tabs, which double as drainage when not tented.
2. `pensando sobre el tenting kit.txt` — screw through the tray into the keyboard; tabs inserted
   *into* the case from below at any position; for inverted tilt, a triangle to insert through;
   travel-case lid inserted from above with the same hole concept, maybe magnet-held.
3. Heat-set inserts in the base + screws.
4. Basket/"nesting" approach — rejected by the author as annoying near the palm rest.
**Recommendation:** (2) — inward tabs from below, they are cheap, tool-free, double as drains.

### ❓-5 — Palm rest attachment
`idea palmrest anchoring.txt`: *"plastic tongues with a screw hole that insert into the main
palm rest below the PCB"*. Alternative: separate slab, no attachment.
**Recommendation:** separate slab for v1 (zero risk), tongues as a v2 refinement.

### ❓-6 — JLCPCB assembly scope ⭐ blocks the POS file
Given D-6 (hotswap), the coherent set is: **F side** = 32 diodes; **B side** = 32 hotswap
sockets + JST + reset + power switch; **hand** = switches, keycaps, MCU, battery, headers.
Sub-problems:
- The hotswap pads are emitted by `switch_choc_v1_v2.js` (one footprint per key, excluded from
  POS). JLC needs a *distinct* footprint with an LCSC part number for the socket. So this needs a
  small footprint refactor, not just a config change.
- `⚠️ UNVERIFIED`: whether LCSC/JLC stock a Choc hotswap socket at all (I could not search from
  this environment). If not, sockets are hand-soldered and only diodes are assembled by JLC.
- Optional extra: have JLC solder the MCU headers into the through-holes (see ❓-7).

### ❓-7 — MCU mounting
Options: (a) two 12-pin male headers per half (`PinHeader_1x12`, currently only a *virtual*
preview footprint, `do_not_populate: DNP`), (b) no-solder spring headers
(`README.md` says compatible; `⚠️ UNVERIFIED` 0.8–0.9 mm hole requirement vs our `mcu_nice_nano`
pad size), (c) JLC-soldered pins.
Note `component_3d_models/readme.md`: "the nice!nano + headers is still less tall than the
switches, but not by much" — measured: headers 8.54 mm above PCB vs switch top 8.05 mm
(`HARDWARE-STACK.md`).

### ❓-8 — 3D printing vendor + material
**Verified (JLC3DP catalogue):** SLS **3301PA nylon**, MJF **PA11**, SLA **9600 / 8228 / black
resin**, FDM **PA12-CF**. The mystery MSDS is solved: **"9600" is JLC3DP's SLA resin** (cheapest,
matte white, "high toughness"). So the three MSDS files are ABS (conductive, FDM), ASA (INTAMSYS,
FDM), 9600 (SLA) — the author was comparing FDM vs resin.
From the JLC chat (`3d printing jlpcb.txt`): FDM infill defaults to 50% (20–100% allowed, ≥20%
recommended), SLS/resin fixed at 100%, multicolour only on PAC-nylon and WJP resin.
**Recommendation:** print locally (PLA) while iterating; for the final parts ASA or PA12-CF
(rigidity + UV + temperature) or SLS 3301PA (isotropic, no layer lines, best for the screw
bosses). Avoid SLA 9600 for a functional case: resin is brittle and creeps under screw load.

### ❓-9 — Screw scheme
Currently M2 everywhere: `screw_radius 1.1`, `screw_head_radius 2.05`, `spacer_radius 2.15`,
5 standoffs (6 mm) + 5 top screws (4 mm) + 5 bottom screws (4 mm) per half, holes drawn as
2.2 mm NPTH. Note in repo root: `PROBABLEMENTE QUEREMOS M mas chicos de screw.txt` ("probably we
want smaller screws") — M1.6 would allow smaller corner radius and less visual weight.
**Recommendation:** finish v1 with M2 (all models/links exist), evaluate M1.6 afterwards.

### ❓-10 — Tenting adjustability in v1
Author is fine with fixed 6.5° for the first iteration, but stacking spacers would be "useful".
Design ideas already collected: nested parts of different heights re-using the same pieces; a
shorter leg at the same anchor; print several angles outright.

### ❓-11 — Firmware
Nothing exists. The matrix definition (once B1 is fixed) must be mirrored into a ZMK shield
(kscan matrix transform + keymap). Non-priority, but it *is* the only way to know whether the
pin map is right.

### ❓-12 — Row-stagger variant
Author is considering switching the layout from column-stagger to row-stagger, and wants to be
able to switch between configurations. See `ROADMAP.md` §3 for the mechanism and for the
configurator-website recommendation.

### ❓-13 — Controller-bay access and the USB-C plug path
*(2026-11-16, from the visual audit — see `VISUAL-AUDIT.md` §5 B18.)*

`l_cover` roofs a **50 × 30 mm** rectangle centred on the MCU (x 56.75…106.75, y 32.77…62.77). The
three parts that need human access all fall outside that rectangle but on the board:

| part | centre | outside the roof by |
|---|---|---|
| reset switch | (112.0, 47.8) | 5.25 mm |
| power switch | (108.0, 39.8) | 1.25 mm |
| JST battery | (107.0, 58.0) | 0.25 mm |

Because the printed plate only covers the key cluster, the bay is **open from above** — so the
switches *are* finger-reachable, and no access hole is strictly required. But nothing in the config
subtracts one deliberately, the interior is therefore not sealed, and the MCU's USB-C plug path has
never been checked: the case opening is a 15 × 15 mm tunnel through the rim at z 3…13, while the
connector sits at PCB level (z ≈ 9–10).

**Questions for the author:**
1. Is the open bay intended (accept dust/open interior), or should the cover get a recessed access
   cut-out with a lip so the switches cannot be bumped?
2. Is the USB-C tunnel aligned with the connector in the assembled stack? Settle it with one
   assembly render of `l_3d_preview` plus the MCU/socket/switch preview models.

### ❓-14 — Reversible parts (one design for both hands)
Author raised it on 2026-11-16 for iteration cost (JLCPCB minimum = 5 boards per design). Full
analysis in [`REVERSIBLE.md`](REVERSIBLE.md). Outcome needed:

1. **FR4 plate — decide "yes" (free).** One plate design, flipped for the other hand; the geometry is
   already mirror-correct after B19. Implies a standing rule: *the switch plate must remain
   symmetric through its thickness* (no counterbores/one-sided features).
2. **Printed case / tenting / palm rest — accept flipping them too.** Removes most of the need for
   `r_case_3d` / `r_cover` (B5) because a printed part can simply be mirrored in the slicer.
3. **PCB — recommended: defer to v0.3.** Every ceoloide footprint already supports
   `reversible: true` (including the MCU), so it will not get harder later; but it changes pad
   geometry (invalidating the current verification baseline) and mirrors the physical matrix, which
   is only detectable after soldering.

### Q-15 — Where the thread lives (fastener architecture) — **analysis done, decision open**
Raised repeatedly; now fully analysed in [`FASTENERS.md`](FASTENERS.md). The hot-swap insight
that reframed it: the sockets grip the switch pins and are peg-anchored to the PCB, so
**plate + switches + PCB are one rigid self-clamping unit** — the top screw is redundant, and the
former "two screws through one bore" problem was self-inflicted and is gone. What remains is a
single question: what provides the thread?

- **F3 (recommended, author's idea)** — a threaded standoff soldered onto the PCB by JLCPCB as an
  SMT placement. Builder buys only screws; printed parts get *simpler* (no pedestals/bosses).
  Unverified: needs an LCSC part number (FASTENERS §7 Q1).
- **F2c** — M2 nut dropped into a printed hex pocket. Screwdriver only, cheapest parts.
- **F2a** — M2 self-tapping into a printed boss. Low priority, not discarded (author's sourcing worry).
- **F1 (current)** — bottom screws into printed pedestals; head protrudes 1.0 mm below the floor,
  so it needs a counterbore or feet.
- **Rejected:** heat-set inserts (needs a soldering iron — author's objection), F5 press-fit.

### Q-16 — "Is the JLCPCB insert option just a naming matter, and can a nut substitute?"
**Answer: partly yes, and no.** For parts we already have, the placement is *entirely* a
declaration matter — B3 is literally a naming/attribute bug (`only_smd: true` + a diode footprint
without `attr smd`, proved by diffing a KiCad POS against the KiBot POS: 98 placements vs 2). JLC
reads five declarations: BOM (with LCSC code), CPL (position/rotation/layer), a footprint with real
pads, the KiCad `attr`, and the part height; miss one and the part silently vanishes. But **a nut
is a different part, not a rename** — it is not soldered, has no pads, and cannot be a CPL entry at
all in the standard service. A nut belongs to topology F2c (a pocket in the print), not to F3. The
shared goal — "don't make the builder buy exotic parts" — is reached by opposite routes: F2c =
"cheap nut you drop in", F3 = "no loose part at all, it is already soldered". Full detail in
[`FASTENERS.md`](FASTENERS.md) §5.
