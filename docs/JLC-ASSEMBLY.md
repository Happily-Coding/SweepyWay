# JLCPCB assembly: what we send, and why (B3)

**Status:** B3 closed 2026-11-16 — the per-half CPL went from **2 placements to 67**.
**Scope owner:** `kibot/jlpcb_pos.kibot.yaml`, `kibot/jlc_parts.csv`, `scripts/jlc_assembly.py`,
`ergogen/footprints/ceoloide/*.js` (submodule).

This document answers four questions: what JLC needs, what was broken, what we send now, and what
is still missing before the order can be placed.

---

## 1. What JLCPCB reads

JLC's PCB Assembly service validates **five** declarations and silently drops the part if any one is
absent (`FASTENERS.md` §5.1):

| # | Declaration | Where it lives here |
|---|---|---|
| 1 | BoM line: comment, designators, footprint, **LCSC part number** | `filtered-output/pcbs/bom/<board>/<board>_bom_jlc.csv` |
| 2 | CPL/POS row: X, Y, rotation, layer, per designator | `filtered-output/pcbs/pos/<board>/<board>_cpl_jlc.csv` |
| 3 | A footprint with **real pads** — 0 pads cannot be placed | `ergogen/footprints/ceoloide/*.js` |
| 4 | KiCad `attr` on the footprint (`smd` / `through_hole` / `exclude_from_pos_files`) | same |
| 5 | Package + height (their stencil/clearance check) | the BoM `Footprint` column |

Miss one and the part disappears from the order with no error. That is why B3 was invisible for
months.

---

## 2. What was actually broken (a *declaration* bug, not geometry)

`kibot/jlpcb_pos.kibot.yaml` exported **2 of 98** placements per half — `PWR1` and `RST1` — because

* it was invoked with `only_smd: true`, and
* the **diode footprint declared no `attr` at all** (`diode_tht_sod123.js`), and
* the **switch footprint declared `allow_soldermask_bridges` but not `smd`** (`switch_choc_v1_v2.js`).

`only_smd` was not wrong; the footprints were lying about what they were. Proof, on the *unfixed*
board, from KiCad itself — the same question asked of `kicad-cli` gives the same answer:

```
$ kicad-cli pcb export pos --smd-only .../left_pcb.kicad_pcb     # BEFORE
PWR1
RST1                                                              <- 2 rows, KiCad agrees with KiBot
$ kicad-cli pcb export pos .../left_pcb.kicad_pcb                 # no filter: 154 rows
```

Those 154 rows are *every footprint, including 3D previews* — which is the trap: dropping
`only_smd` without fixing the declarations would have put 32 keycaps, 32 socket previews, 10 screw
previews, 5 standoffs, 2 header previews and 5 mounting holes into the CPL as if they were parts.

**The fix, in both halves of the declaration:**

1. `diode_tht_sod123.js` → `(attr smd)` (`smd through_hole` when `include_tht` is on).
2. `switch_choc_v1_v2.js` → `(attr smd allow_soldermask_bridges)` when `include_in_pos_files` is
   true (its two hotswap pads are SMD; the rest of the footprint is holes).
3. Every *virtual* footprint now says so: `hs-socket-fab-preview_choc_v1_v2`,
   `keycap-fab-preview_choc_v1_v2`, `screw-preview-top`, `screw-preview-bottom`,
   `standoff-preview`, `header-preview_nano` → `exclude_from_pos_files exclude_from_bom`, and
   `mounting_hole_npth` → `exclude_from_pos_files exclude_from_bom` (a hole is not a part).

Result: KiCad and KiBot now agree exactly. After the fix, on the regenerated board:

```
$ kicad-cli pcb export pos --smd-only .../left_pcb.kicad_pcb     # AFTER
32 x D, 32 x S, PWR1, RST1                                        <- 66 rows
$ kicad-cli pcb export pos .../left_pcb.kicad_pcb                 # AFTER (no filter): 68 rows
32 x D, 32 x S, JST1, PWR1, RST1, MCU1                            <- previews gone, THT kept
```

68 = the four SMD part types + the JST (THT) + the nice!nano (THT). Nothing else is a part.

---

## 3. Conventions: columns, Y axis, rotation, origin

**Columns.** Exactly JLC's five, in their order, and nothing else:

```
Designator,Mid X,Mid Y,Layer,Rotation
D1,27.1500,-131.5000,Top,90.0000
S1,35.0000,-133.0000,Bottom,0.0000
```

No `Val`, no `Package`. JLC reads the part from the **BoM**, so a package column is not data — it is
what made `kibot/fix_pos_package_name.py` look necessary — and that script was writing a part
number into a column that carries no part semantics at all. The script and its workflow step are
deleted. (Note: `CPG135001S30` is in fact the *socket*'s part number — see §6 — a point this file
previously got backwards.)

**Y axis.** Positive up, i.e. KiCad's own `.pos` convention (`PosY = -Y_board`). No negation and no
translation: this board has no aux origin (`use_aux_axis_as_origin: false`), so the gerbers and the
CPL share the page origin and agree without anything to align. Verified: all 67 X/Y pairs in the CPL
are **bit-identical** to `kicad-cli pcb export pos` on the same board (0 mismatches, and the gate
re-checks that every placement is inside the `Edge.Cuts` bbox — a Y flip would land the whole board
at `y +37…+172` and fail).

**Rotation.** KiCad's angle on top, mirrored as `(180 − rot)` on the bottom, because that is how JLC
reads a bottom-side rotation. This is the exact rule of KiBot's own `_rot_footprint_jlcpcb`
transform (`fil_base.py`: `mirror_bottom: True`, documented upstream as "This is used by JLCPCB"),
which **cannot be used here**: it is a *component* transform and this board has no schematic, so
`pre_transform` dies with "No SCH file found". The mirroring is applied by
`scripts/jlc_assembly.py` instead. Consequences on this board:

| Designator | KiCad rot | JLC rot | note |
|---|---:|---:|---|
| D1…D29 | 90 | 90 | top, unchanged |
| S1…S29 | 180 | 0 | symmetric 2-pad socket → harmless either way |
| S30 / S31 / S32 | 170 / 155 / 150 | 10 / 25 / 30 | thumbs: **not** harmless, a 120° error if unmapped |
| RST1 / JST1 | −90 | 270 | normalised into `[0, 360)` |

---

## 4. The hotswap socket: decision

**Verified:** the dedicated socket footprint is `hs-socket-fab-preview_choc_v1_v2` and it has
**0 pads** — it is a 3D-model carrier only (`// This footprint does NOT add any pads, holes, or
silkscreen to the PCB`, and 0 `(pad` forms in the file). A footprint with no pads can never be a CPL
row, so "JLC places HS1…HS32" is not expressible and never will be.

**But the socket is still placed, and correctly.** The pads that the Kailh Choc hotswap socket is
soldered to live in the *switch* footprint `choc_v1_v2` (`hotswap: true`), which has exactly two
SMD pads numbered `1`/`2`, wired to the column net and the position net — `check_assembly.py`
asserts "every switch has exactly 1 column net + 1 position net, 32/32". So:

> **Decision (D-6 stays in force):** the CPL row for each key is the *switch* designator `S1…S32`,
> and the part JLC places there is the **hotswap socket**. The switch itself is supplied by the
> builder and hand-inserted; keycaps likewise. The BoM `Comment` says "Kailh Choc V1 hotswap
> socket", the footprint column says `choc_v1_v2` — that is the honest description of the physical
> part being soldered at that position, and it is what the pads belong to.

No real pads were added to the preview footprint: adding them would double-count the socket (two
footprints claiming the same two pads), and the design already has the pads in the right place. The
preview footprints stay in the file for the 3D exports, now declared `exclude_from_pos_files`.

---

## 5. What is in the CPL, and what is deliberately out

Per half: **154 footprints on the board → 68 placeable → 67 sent to JLC.**

| Footprint | n | In the CPL | Why |
|---|---:|---|---|
| `diode_tht_sod123` | 32 | ✅ `D1…D32` | SMD, `attr smd` (was: no attr at all) |
| `choc_v1_v2` | 32 | ✅ `S1…S32` | the hotswap **socket** pads live here (§4) |
| `battery_connector_jst_ph_2` | 1 | ✅ `JST1` | THT — needs the mixed SMT+THT service |
| `reset_switch_smd_side` | 1 | ✅ `RST1` | SMD |
| `power_switch_smd_side` | 1 | ✅ `PWR1` | SMD |
| `mcu_nice_nano` | 1 | ❌ | placeable, but **`assemble=no`**: a nice!nano is a module the builder owns and hand-solders (it is not in JLC's library). `ORDER-CHECKLIST.md` scope: "you keep the MCU, switches, keycaps and battery" |
| `hs-socket-fab-preview_choc_v1_v2` | 32 | ❌ | **0 pads** (3D preview) — cannot be placed by anyone |
| `keycap-fab-preview_choc_v1_v2` | 32 | ❌ | 0 pads (3D preview), DNP by design |
| `screw-preview-top` / `-bottom` | 5+5 | ❌ | 0 pads (3D preview); screws are hardware, bought separately |
| `standoff-preview` | 5 | ❌ | 0 pads (3D preview). ⚠️ The **soldered M2×3+3 standoff, LCSC `C192879`, is a JLC part** — but there is no pad-bearing footprint for it, so it cannot be placed today. Making it placeable is a footprint job, not a B3 job (`FASTENERS.md` §5, §6/F3b) |
| `header-preview_nano` | 2 | ❌ | 0 pads (3D preview of the headers) |
| `mounting_hole_npth` | 5 | ❌ | NPTH hole — a hole, not a part |

The scope filter is **not** a KiCad attribute: it is the `assemble` column of
`kibot/jlc_parts.csv`, because "is this placeable" (design) and "do we order this from JLC"
(purchasing) are different questions. A **new** footprint that is placeable but absent from that
file makes `scripts/jlc_assembly.py check` **fail** — the paperwork cannot silently skip a part
again.

Two CPLs are emitted per board:

* `<board>_cpl_jlc.csv` — 67 rows (66 SMD + 1 THT), the scope above. **Upload this one.**
* `<board>_cpl_jlc_smd.csv` — 66 rows, no `JST1`, for a plain SMT-only order (cheaper, and the JST
  is then hand-soldered). Do not upload both.

---

## 6. LCSC part numbers — **RESOLVED 2026-11-17** (B7)

Verified against JLCPCB's live parts API (`selectSmtComponentList`), not a catalogue page. All five
are now in `kibot/jlc_parts.csv`, and `jlc_assembly.py check` reports **0 LCSC gaps**:

| Footprint | Designators | Part | LCSC | library | stock | price@1 |
|---|---|---|---|---|---|---|
| `diode_tht_sod123` | D1…D32 | 1N4148W, SOD-123 | **C81598** | **base** | 3,154,652 | $0.0124 |
| `battery_connector_jst_ph_2` | JST1 | S2B-PH-K-S(LF)(SN) | **C173752** | expand | 179,586 | $0.0397 |
| `reset_switch_smd_side` | RST1 | Panasonic EVQPUC02K | **C79174** | expand | 11,299 | $0.1822 |
| `power_switch_smd_side` | PWR1 | Alps SSSS811101 | **C109335** | expand | 41,819 | $0.1488 |
| `choc_v1_v2` | S1…S32 | Kailh Choc socket **CPG135001S30** | **C9900248317** (mail-in, min 10) | expand | 0 → **consigned** | — |
| `mcu_nice_nano` | MCU1 | nice!nano v2 | n/a — `assemble=no`, hand-soldered | | | |

### The hotswap socket is the one special case

No hotswap socket is *in stock* at JLC: every registration returns `stockCount: 0` and
`isBuyComponent: 0`. But JLC explicitly supports non-stock parts — from `jlcpcb.com/pcb-assembly`:

> "Components for PCB assembly can be sourced in multiple ways: in-stock components from JLCPCB's
> parts library (fastest); global sourcing via trusted distributors (lead time 9–15 days);
> **pre-order parts added to your private library**; **consigned parts supplied by you**; new part
> requests if a component is not yet listed."

The full route comparison for the socket — including which registration is the right one, and why
the minimum matters — is in the next section. In short: **consign** (buy 64 sockets, mail them, JLC
reflows them — CPL stays 67/half). If that is unattractive, set `assemble=no` for `choc_v1_v2` and
hand-solder them; the CPL then drops to **35 placements/half** and the rest still arrives assembled.

### The socket is CPG135001S30 — and it is consigned (corrected 2026-11-17)

Kailh's own product page (`kailhswitch.com` → *Choc Type Hot Swap Socket*) states:

> "Kailh PCB Hot Swapping Sockets which can support Kailh Choc V1 Low Profile switches,
> **product no#CPG135001S30**" … "The Choc socket only works with Kailh's low profile Choc V1
> switches."

So **CPG135001S30 is the socket**, not the switch. (An earlier version of this file claimed the
opposite, based on JLC's `componentTypeEn` reading "Mechanical Keyboard Shaft" — that is just a bad
category on their listing, not the part's identity. The model string matches Kailh's part number
exactly.) Kailh also sells a separate MX-line socket ("Rainbow MX Hot Swapping PCB Socket"), which is
**not** what this board uses.

Searching JLCPCB by that part number returns exactly three registrations — all `stockCount: 0`,
all `allowPostFlag: true` (mail-in accepted):

| LCSC | registration | min | note |
|---|---|---|---|
| **C9900248317** (chosen) | 【邮寄专用】CPG135001S30 | **10** | mail-in registration for this exact part |
| C5333465 | CPG135001S30 | 71 | the ordinary LCSC listing — this is what the old project notes recorded |
| C9900009224 | CPG135001S30 | 1000 | |

`【邮寄专用】` is JLC's marker for **mail-in only**, so `C9900248317` is the intended anchor for a
consignment and its minimum (10) is the only one that suits a 64-socket order. All three report
`noBuyReason: "no longer manufactured"`, which is irrelevant here: the code tells JLC's assembly
system *which part and footprint* to place, and **you post the physical sockets**.

Other socket registrations exist but are **not** this part: `C9900010116` (Kailh Low-Profile
Hot-Swappable Socket), `C9900034372` (Gateron low-profile), `C9900190495/496/497` (DUROCK, MX-type)
and `C9900017168` (Gaote, MX-type).

**Do not treat `C5333465` as a purchasable part** — it is the same socket, but stock 0.**Do not use `C5333465`.** The project's old notes recorded it for "CPG135001S30"; the API types it
as `Mechanical Keyboard Shaft` — that is the Choc *switch*, not the socket, and it is discontinued
(stock 0).

## 7. What JLC would receive today

| | per half | full keyboard |
|---|---:|---:|
| CPL placements (`_cpl_jlc.csv`) | **67** (66 SMD + 1 THT) | 134 |
| Unique parts in the BoM | 6 (5 ordered + 1 hand-solder) | 6 |
| BoM lines with an LCSC code | **0 of 5** | 0 of 5 |
| Parts not in JLC's library | nice!nano (hand-solder, intentional) | 1 |

So: **the CPL is complete and correct; the BoM is structurally complete but has no part numbers
yet.** That is the literal state of the repo, and it is now visible in one place instead of being
guessed at.

---

## 8. Regenerate and verify

```sh
# 1. declarations: footprints -> PCB  (writes to ergogen/output unless --out is given)
./scripts/regen.sh

# 2. KiBot: board -> raw POS  (Docker; writes filtered-output/pcbs/pos/<board>/<board>_cpl_raw.csv)
docker.exe run --rm -v "C:/a/<repo>:/work" -w /work ghcr.io/inti-cmnb/kicad9_auto:latest \
    kibot -b /work/ergogen/output/pcbs/left_pcb.kicad_pcb -c /work/kibot/jlpcb_pos.kibot.yaml

# 3. raw POS -> JLC CPL, and PCB -> JLC BoM
./.venv/Scripts/python.exe scripts/jlc_assembly.py cpl
./.venv/Scripts/python.exe scripts/jlc_assembly.py bom

# 4. gate
./.venv/Scripts/python.exe scripts/jlc_assembly.py check      # PASS
```

CI runs steps 2–4 in `.github/workflows/build.yaml` ("Run KiBot to generate jlpcb pos" → "Build the
JLCPCB assembly files" → "Gate the JLCPCB assembly data"). The gate fails on: a placeable part
missing from the CPL, a virtual/mechanical footprint leaking **into** the CPL, wrong columns, a
duplicate designator, a placement outside the board outline, or a placeable footprint absent from
`kibot/jlc_parts.csv`. Missing LCSC codes are a **warning with the full list**, not a failure: they
are purchasing data, and a gate that is red until someone buys a part is a gate nobody reads.

⚠️ The committed `filtered-output/` still predates this fix (it is the B14 snapshot); it must be
rebuilt by one CI run before anything is uploaded from it. Do not hand-copy these files into it.

---

## 9. KiBot config inventory (`kibot/*.yaml`)

| Config | Invoked by | Produces | State |
|---|---|---|---|
| `default` | workflow step 4 | JLCPCB gerbers + drill + zip, PCB top/bottom images (→ `filtered-output/pcbs/{gerbers,images}`) | live |
| `boards` | after autoroute | DRC (→ `kibot/drc`) + everything `default` does, for the routed board | live |
| `3d_preview` | after the folder is recreated | STEP/STL/GLB + 3D renders (→ `filtered-output/pcbs/3d`, `images`) | live |
| `pdf` | after autoroute | PCB print PDF (→ `filtered-output/pcbs/pdfs`) | live |
| `jlpcb_pos` | after the copies | **raw** placement CSV, JLC's five columns, unfiltered (→ `filtered-output/pcbs/pos`) | **rewritten in B3** |
| `jlpcb_bom` | — | nothing: KiBot `bom` is a *schematic* output and Ergogen has no schematic (`ERROR: No SCH file found`), so it never wrote a file, which is why B7 was mis-diagnosed as "a BOM without an LCSC column" | **deleted** — replaced by `scripts/jlc_assembly.py bom` |
| `jlpcb_pos_t1` | — | `import: - file: JLCPCB` (the stock JLC template) with no outputs of its own; gets the gerbers/BoM/CPL from the template, which fails on this project for the same schematic reason | **deleted** (dead experiment) |
| `jlpcb_pos_t2` | — | every output commented out except a BoM that writes to `ergogen/output/pos/%f` — a directory that is never published | **deleted** (dead experiment) |
| `preview` | — | a duplicate of `default`'s pcbdraw images into `ergogen/output/images`, which nothing reads | kept, **unused** (harmless; `default` already draws both views) |

Also deleted: `kibot/fix_pos_package_name.py` (see §3) and its workflow step, plus the
"Debug – List POS file locations" step that existed only to chase B3.

---

## 10. Not done here, on purpose

* **LCSC codes** (§6) — they have to be looked up; inventing them is worse than leaving them blank.
* **`filtered-output/` was not regenerated** — it is generated and gated (`scripts/check_published.py`,
  B14); one CI run produces the real files.
* **The standoff has no pad-bearing footprint** (§5) — a footprint/design task, not a declaration
  task. `C192879` is verified, stocked and JLC-placeable *in principle*; it needs a real footprint.
* **`ergogen/config.yaml` was not touched** (owned by another worker). The LCSC numbers therefore do
  not live on individual component instances either: `kibot/jlc_parts.csv` is deliberately outside
  the config so that part numbers and layout can be edited by different people without conflict.
* **The footprint fix lives in the `ergogen/footprints/ceoloide` submodule**, which is a separate
  repo (`Happily-Coding/ergogen-footprints`). The 9 attribute edits are uncommitted there: they must
  be committed and the parent repo's gitlink bumped, or the next `submodules: true` checkout in CI
  will silently export 2 placements again (the gate will catch it).
