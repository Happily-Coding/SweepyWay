# HANDOFF — exhaustive session state, 2026-11-16

**Read this top to bottom once.** It exists because the previous session ended mid-flight and a new
agent must not re-do the verification, must not repeat six specific measurement mistakes, and must
not trust `filtered-output/`.

Everything here was executed, not recalled. Where a number is an estimate it says so. The markers
from `docs/README.md` §2 are used: `⚠️ UNVERIFIED`, `🟡 BEST-GUESS`, `❓ OPEN`.

**If you only read one section, read §5 (blockers) and §8 (traps).**

---

## 0. RESUME HERE (session 3, 2026-11-16)

**Session 3 in one line:** the mechanical architecture (F3b) shipped as a configurable knob, **B4 is
fixed** (right half now has 5 mounting holes, mirror axis x=170), **B1 is fixed** (`check_matrix` went
15 failures → **0**: no dead rows, no shorted GPIOs), and the router was re-proven end to end.
Next: **B7** is now only 5 LCSC lookups (`JLC-ASSEMBLY.md` §6); the remaining code work is a CI run for **B2**.
A new blocker, **B22**, says the configurator generator would revert B13 if anyone ran it
(`docs/CONFIGURATOR-DRIFT.md`).

**Superseded session-2 notes below (still accurate for F3b/B13/B17):**

**Read `docs/FASTENERS.md` §0 first**, then this. `FASTENERS.md` is the mechanical decision record
and it was written to be read cold after a pause of weeks.

### State of the keyboard, one line each

- **B13 is fixed** — screw points moved; `scripts/check_assembly.py` **PASSES** (first clean run
  ever). Plate, cover and case floor all carry 5 real Ø2.2 holes. **Do not redo this.**
- **The anchoring architecture is decided AND implemented: F3b.** A soldered M2 standoff
  (`LCSC C192879`, M2×3+3, 5 333 in stock, $0.013) supplies the thread; a printed, threadless boss
  supplies the height (`standoff_length − 3`); one M2×10 screw from below per point. **No inserts,
  no tapping, no press-fit, no top screw** — the 32 hot-swap switches hold the plate.
- **It is configurable by one number.** `ergogen/config.yaml` → `standoff_body_length`:
  `3` = F3b (default), `6` = press-fit standoff (the old design, boss height 0), `0` = printed post.
  The case boss, the BOM and the screw lengths all derive from it (`FASTENERS.md` §4.6).
- **The JLC service question is closed.** Their **PCB Assembly** covers SMT + THT + mixed, single-
  and double-sided, so the standoff joins the same assembly BOM as the sockets and diodes
  (`FASTENERS.md` §5.0). ~~`B3` is still what stops that BOM from exporting properly.~~
  **B3 is closed (2026-11-16)**: the assembly BOM/CPL now export 67 of 68 placeable parts per half;
  what remains is the 5 LCSC lookups (`JLC-ASSEMBLY.md` §6).
- Everything gated: `hardware_bom.py` **PASS**, regen stable, `check_published.py` reproduces B14
  exactly. `check_matrix.py` still fails on B1/B4 only.

### The next five things, in order

1. **B4 — mirror the 5 screw points to the right half.** This is now the *top mechanical blocker*:
   the right PCB has no mounting holes, so there is nothing to solder a standoff into. The printed
   right case is a slicer-mirror of the left (`REVERSIBLE.md`), so bosses appear for free; the PCB
   is the blocker.
2. ~~**B3 — close the POS/CPL declaration**~~ ✅ done 2026-11-16 (2 → 67 placements/half). The
   follow-up is **B7's data entry**: 5 LCSC codes in `kibot/jlc_parts.csv`.
3. **B2 — one CI run** of the rewritten autoroute action (root cause fixed, never executed in CI).
4. **B1 — pin maps** (the generated config already fixes them; the checked-in one does not).
5. **B20 / the ledge** and the rim-vs-plate relationship (`FASTENERS.md` §7 Q5).

### Deliberately deferred (do not lose these)

- **Stock-aware button:** query LCSC and auto-pick the nearest *available* `standoff_body_length`.
  The user asked for this as a later button; until then availability is a manual check.
  The query that produced `FASTENERS.md` §4.5 is the recipe (JLC SMT parts API, `POST
  /api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`).
- **Preview cosmetics:** `l_3d_preview` does not show the new bosses, and
  `ceoloide/standoff-preview` still draws a full `standoff_length` column instead of
  `standoff_body_length` + boss.
- Reversible PCB → v0.3 (`REVERSIBLE.md`); panelizing stays rejected (`DECISIONS.md`).

### Files touched this session

`ergogen/config.yaml` (5 screw shifts, B17 rim derivation, `standoff_body_length` + bosses) ·
`configurator/lib/{schema,generate}.mjs` · `configurator/public/{index.html,app.js}` ·
`configurator/server.mjs` · `.github/actions/autoroute/action.yaml` · `.github/workflows/build.yaml` ·
`docs/{STATUS,HANDOFF,FASTENERS(new),VISUAL-AUDIT,REVERSIBLE,HARDWARE-BOM,BOM,DECISIONS,
HARDWARE-STACK}.md` · `scripts/{hardware_bom,check_published}.py` · `scripts/pre-push.sh` ·
`docs/img/{B17-stackup,fastener-options,fastener-sections,screw-move,plate-holes,f3b-boss}.png`

### Traps discovered this session (in addition to §8)

- **Ergogen point y is inverted vs PCB y** — a shift delta must be applied as `-dy`.
- **The thumb point lives in a rotated frame (~25°)** — its shift is rotated too. Calibrated basis:
  `L(1,0)=(0.9063,0.4226)`, `L(0,1)=(0.42667,-0.90667)`. Solve, don't guess.
- **The binding clearance constraint is the plate OUTLINE, not the PCB edge.** The plate is the key
  cluster; the PCB has 2–4 mm of padding beyond it, so a screw 6 mm inside the PCB edge can still
  clip the plate and turn a hole into a notch (that is what happened to the thumb at 1.07 mm).
- **KiCad writes a full circle as `gr_circle`, but a circle touching an edge cut is split into
  `gr_arc`s** — count both or you will believe a hole is missing.
- **There is no `r_case_3d`** (B5). Only the left case is generated; the right is a slicer mirror.
  Do not add bosses to a right-hand case that does not exist — add them to the left.
- **`hardware_bom.py` now auto-detects the topology** from `standoff_body_length`; use
  `--topology standoff` to reproduce the old press-fit BOM, `--standoff 4.5` for a what-if.

---

## 1. What this project is

Two products in one repo, `C:/a/IRL Products/Keyboard design/SweepyWay`:

1. **The keyboard** — SweepyWay v0.2, a 2 × 32-key split, column-staggered, low-profile,
   Kailh **Choc V1** hotswap, nice!nano, printed case + FR4 plate, with a palm rest and a 6.5°
   tenting base. It is meant to be physically built and used by the author.
2. **The pipeline** — a declarative keyboard factory: YAML/JSON in → PCB + plates + case + palm rest
   + tenting + fab data + 3D previews out (Ergogen + OpenJSCAD + KiCad/KiBot + Python mesh scripts).

A **local configurator** (`configurator/`) was built during the previous session: JSON config →
`config.yaml` → Ergogen → checks → print files → three.js preview.

## 2. Environment — how to run anything (all of these were verified working)

| Thing | Reality |
|---|---|
| Shell | WSL bash, but **all tools are Windows binaries** |
| Node | `node.exe` (v24.12.0). Plain `node` **does not exist** in this shell. |
| Python | `./.venv/Scripts/python.exe` (3.12.8). Plain `python3` has **no** trimesh/shapely/PIL. |
| Venv packages | trimesh 4.7.4, ezdxf 1.4.2, shapely 2.1.1, scipy 1.16.1, numpy 2.3.2, pillow 11.3.0, matplotlib 3.10.5, vtk 9.2.6, vedo 2025.5.4 |
| KiCad | 8 and 9 installed (GUI). `pcbnew` python module: ⚠️ UNVERIFIED, assume not importable — all PCB parsing here is done with a hand-written S-expression parser. |
| Docker | ✅ **WORKS — the old "unreachable" claim was WRONG.** Use **`docker.exe`** (v29.7.2); the bare `docker` shim refuses with *"could not be found in this WSL 2 distro"*. The engine needs `docker.exe desktop start` (poll `docker.exe info` until it answers). Mounts must be **Windows paths** (`-v "C:/a/IRL Products/...:/workspace"`) and pass `MSYS_NO_PATHCONV=1`. Verified: `ghcr.io/inti-cmnb/kicad9_auto` + `ceoloide/ergogen-freerouting` both pull and run, KiBot writes gerbers/images, and freerouting+import round-trips (see B2). |
| `gh` CLI | **Not installed** ⇒ GitHub runs/artifacts must be inspected via `git`-committed output or the web UI. |
| Configurator port | **5173** (`node.exe configurator/server.mjs`, `--port` to override) |

### Path traps that will waste 20 minutes each

- `node.exe` cannot read WSL `/tmp`. Windows Python cannot read `/tmp` either. **Put temp files under
  the repo** (e.g. `configurator/builds/<dir>/`) or under `C:/tmp/...`.
- The `read` tool resolves `/tmp/x` to **`C:\tmp\x`**, not WSL `/tmp`. Same file, two names.
- A server started in a background subshell dies when the bash tool call ends ⇒ start the server and
  curl it **in the same call**.
- The server binds Windows localhost: WSL `curl` gets connection refused, use
  `/mnt/c/Windows/System32/curl.exe` or `curl.exe`.

## 3. Repo map

```
SweepyWay/
  ergogen/config.yaml          canonical design (~1400 lines) - the source of truth
  ergogen/footprints/          git SUBMODULE (ceoloide forks, pinned commit eb14fc3)
  ergogen/output/              local ergogen output (pcbs/, outlines/, cases/, points/)
  configurator/                JSON->YAML->PCB->STL->preview web app (new this session)
    server.mjs  lib/{schema,generate}.mjs  public/{index.html,app.js,styles.css}
    presets/{sweepyway,minimal-3x5,row-stagger-1u}.json
    builds/<name>-<sha1[0:8]>/  gitignored: config.yaml, out/, assets/, assets_fixed.stl
  palmrest_and_tenting_creation/  create_palmrest.py, create_tenting_system.py (now CLI-driven)
  scripts/                     regen.sh + 6 checkers (see §8)
  docs/                        14 docs incl. this one
  filtered-output/             COMMITTED snapshot of CI output - STALE AND MIXED, see §12
  .github/workflows/build.yaml the real pipeline (workflow_dispatch + push)
```

Build dir used below: `configurator/builds/sweepyway-2f79aca4/` (content-addressed by config sha1).

## 4. Verified facts — trust these

### Geometry (fresh local build, post-fix)

| Part | bbox (mm) | volume | notes |
|---|---|---|---|
| `l_case_3d.stl` | 140.61 × 142.80 × 16.00 | +56.74 cm³ | 5 screw bosses, 1.2 mm wall, USB-C slot |
| `l_cover.stl` | 132.62 × 134.80 × 7.00 | +8.85 cm³ | plate (1.2 mm) + controller housing + roof |
| `tenting_base.stl` | 144.62 × 146.80 × 19.48 | +59.99 cm³ | hollow, 6.5° |
| `palm_rest.stl` | 119.64 × 70.67 × 10.00 | +26.03 cm³ | solid curved ramp |

### Board

- 32 keys/half = **29 grid** (`colX_rowY`) + **3 thumbs** (`colN_thumb_row_1`).
- 154 footprints/half: 32 choc + 32 hotswap-preview + 32 keycap-preview + 32 diode + 5 mounting
  holes + 5 standoff-preview + 5 screw-top + 5 screw-bottom + 2 header + MCU + JST + reset + power.
- **Wiring topology per key**: column net `CX` → switch pad 2 → switch pad 1 (`colX_rowY`) → diode
  pad 2 (anode) → diode pad 1 (`RY`) → row net. Diode pad order identical on all 32 keys.
  Thumbs sit on `R5` with columns `C5/C6/C7`.
- **The hotswap socket footprint has ZERO pads.** The switch footprint carries the two SMD pads
  (`colX_rowY` + `CX`) that the socket contacts land on. The socket footprint is 3D/silkscreen only.
- Plate: 32 cutouts, **14.0 × 14.0 mm**, rotated to match each switch (grid 0°, thumbs −10/−25/−30°),
  centres land on switches to **0.000 mm**.
- Screws: 5 per half, M2, Ø2.2 hole (r 1.1), at
  (41.8, 85.4) (41.8, 136.4) (126.8, 80.13) (126.8, 131.13) (131.7, 156.42) in PCB coords.
- **DXF ↔ PCB transform is exactly `(x, y) → (x, −y)`** (no translation). Verified residual 0.000 mm.
- Keycaps: CFX 16.5 mm on 17 mm pitch, splay included → **closest pair 0.50 mm gap**, no collision.
- PCB thickness in every generated file: **`(thickness 1.6)`**, ergogen's default. **There is no
  `pcb_thickness` parameter in `config.yaml`** (B15).

### Toolchain equivalence

- The `sweepyway` preset regenerates a `config.yaml` **byte-identical** to the verified build's.
- That config reproduces **38/38** key points of the repo build; the only additions are the
  `r_screw_*` twins (which fix B4 for generated configs).

## 5. Blockers — current list

Full prose lives in `docs/STATUS.md` §4. Status at session close (2026-11-16):
**open = B2, B5, B7 (LCSC data entry only), B8, B14, B15, B20, B22** (plus **B18**, accepted by design: the bay is open
on purpose); **fixed and guarded = B1, B4, B6, B9, B10, B11, B12, B13, B16, B17, B19, B21**.
B1 and B4 were fixed in session 3; **B22** (configurator drift would revert B13) is the new one.
(B-numbers are stable identifiers; do not renumber them.)

> **B16–B19 were found in the 2026-11-16 (session 2) visual pass — read `docs/VISUAL-AUDIT.md`
> before touching `config.yaml`.** It also corrects B1 (it is in *both* halves, and they differ) and
> records the measured B1 impact (12 of 64 keys dead).

| # | One-line | Sev | Where |
|---|---|---|---|
| **B1** | Row `R1` has no MCU pin, in **both** halves, and the two halves' maps differ: left P5+P9→`R5`, right P6+P7→`R5`; R6/R7 don't exist. Kills **R1 = 6 keys/half ⇒ 12 of 64 keys**. Generated configs already fix it (`P3..P7 → R5,R4,R3,R2,R1`). | 🔴 | `config.yaml` pin maps |
| **B2** | ~~Published gerbers are unrouted.~~ **ROOT CAUSE FOUND 2026-11-16, fix pending.** `autoroute/action.yaml` reads `pcbs/${board}.dsn` **relative to the repo root**, where no `pcbs/` directory exists — and the body is wrapped in `if [ -e pcbs/... ]`, so it **silently does nothing**. No `.ses` is produced, `import-ses` is guarded on the `.ses` too so it also no-ops, and KiBot then exports the unrouted board: every step "succeeds". Proven routable locally: freerouting closed **105 nets, 0 unrouted, 0 violations** (score 1000.00) and the SES import produced a board with **980 segments + 91 vias** (`check_matrix.py --routing` agrees). Fix = prefix the paths with `ergogen/output/`, add `-mp 3` (the default `-mp 25` spent >10 min optimising), and gate on segment count. | 🔴 fix is 3 lines | `.github/actions/autoroute|import-ses|export-dsn/action.yaml` |
| **B3** | ~~Assembly data is 2 of 98 placements/half.~~ **FIXED 2026-11-16** — declaration bug, not geometry: `only_smd: true` was asked of footprints that lied (diode had *no* `attr`, switch had no `smd`, and the 86 preview/hole footprints were not marked virtual). CPL per half **2 → 67** (66 SMD + 1 THT); `kicad-cli pos --smd-only` now returns the same 66. Socket decision: its pads live in the switch footprint, so `S1…S32` *are* the socket placements. Gated by `scripts/jlc_assembly.py check`. Full story: `JLC-ASSEMBLY.md`. | ✅ fixed | `kibot/jlpcb_pos.kibot.yaml`, `kibot/jlc_parts.csv`, ceoloide footprints, `scripts/jlc_assembly.py` |
| **B4** | Right half has no screws/standoffs/mounting holes (repo config). | 🔴 | `config.yaml` right_pcb |
| **B5** | No `r_case_3d` / `r_cover` case at all ⇒ **you cannot print a right case**. (The `r_*` *outlines* DO exist as DXF.) | 🔴 | `config.yaml` `cases:` |
| **B7** | ~~No BOM with LCSC part numbers; not published.~~ **Mechanism fixed 2026-11-16** — and the old `jlpcb_bom` config never ran at all (KiBot's BoM outputs need a *schematic*; Ergogen makes none). `scripts/jlc_assembly.py bom` builds it from the PCB into `filtered-output/pcbs/bom/` with the LCSC column. **5 part numbers are still missing** (diode, socket, JST, reset, power) → `kibot/jlc_parts.csv`, listed in `JLC-ASSEMBLY.md` §6. | 🟠 data entry | `kibot/jlc_parts.csv`, `scripts/jlc_assembly.py` |
| **B8** | Case↔tenting attachment, palm-rest attachment undefined. | 🟠 | ❓-4, ❓-5 |
| **B13** | ~~4 of 5 screw points sit INSIDE the switch cutouts.~~ **FIXED 2026-11-16.** New points (PCB coords): **(43.80, 86.15) (43.80, 137.15) (128.80, 80.13) (128.80, 132.63) (131.70, 160.30)**. `check_assembly.py` **PASSES** (tightest +1.769 mm to a 14 mm cutout). FR4 plate now has 5 clean Ø2.2 holes; printed cover plate level = 32 keys + 5 screw holes; case floor 5 holes. **Three traps found doing it:** (a) **ergogen point y runs opposite to PCB y** — a shift delta must be `-dy`; (b) the thumb point lives in a **rotated frame (~25°)**, so a shift is rotated with it — solve with the calibrated basis `L(1,0)=(0.9063,0.4226)`, `L(0,1)=(0.42667,-0.90667)`; (c) the binding constraint is the **plate OUTLINE**, not the PCB edge — the plate is the key cluster while the PCB has 2–4 mm of padding beyond it, so a screw 6 mm inside the PCB edge can still clip the plate and turn the hole into a notch. | ✅ fixed | `config.yaml` → `l_screw_*` |
| **B14** | `filtered-output/` **mixes two builds**: PCB+plate are current layout but with 6.9 mm cutouts; `outlines/` and `cases/l_cover.stl` are an older layout — cover registers on screws to 0.019 mm yet its key openings are **21.77 mm off the switches**. | 🔴 | `filtered-output/` **Root cause found + gated 2026-11-16:** the workflow copied with `rsync -a` (no `--delete`) and never wiped the folder, so files from older runs survived; it also never committed back, so the folder is a *manual* merge of artifact zips. The workflow now does `rm -rf filtered-output` first, uses `rsync --delete`, writes `BUILD-STAMP.txt` (commit + config sha1) and runs `scripts/check_published.py` before publishing. **The folder as committed is still stale** — it fails the new gate (no stamp, 6.9 mm cutouts, cover 21.770 mm off). | 🔴 until rebuilt in CI | `filtered-output/`, `.github/workflows/build.yaml` |
| **B15** | `left_pcb-3d-misscaled.glb` is a 0.1 mm mesh published beside the good one; `cases/cover.stl` is byte-identical to `l_cover.stl`; PCB thickness 1.6 mm unparameterised. | 🟠 | `filtered-output/`, `config.yaml` |
| **B16** | ~~Right tenting bottom outline was empty geometry.~~ **FULLY FIXED 2026-11-16.** Outline: subtracted `l_case_bottom expand -5` (wrong side, twice) so the boolean collapsed — the original emitted a **210-byte DXF with 0 entities**. Now a true mirror (`r_case_bottom` expand 2 − `r_pcb_outline`) ⇒ **132 entities, 143.42 × 145.60 mm**. Configurator: `stagePrints` hardcoded the `l_` DXF names, so only a left part was ever printed; it is now **side-aware** (`cfg.printSides`, default `['l','r']`) with an explicit "outline is EMPTY" error instead of a cryptic Python failure, and `stageSvgs` shows the right outlines too. Verified end-to-end: right tenting base **watertight, 59.29 cm³** (left 59.99) and right palm rest STL both generate. ⚠️ The **SVG preview is still empty** even when the DXF is correct — judge outlines by DXF entity count. | ✅ fixed | `config.yaml`, `configurator/server.mjs` |
| **B17** | ~~Case rim stands ~3.6 mm proud of the plate.~~ **FIXED 2026-11-16 (author chose to lower the rim).** `case_border_height` is now **DERIVED**: `case_bottom_thickness + standoff_length + pcb_thickness + plate_top_above_pcb_top` = 3 + 6 + 1.2 + 2.2 = **12.4** (was a literal 16). New units `standoff_length`, `pcb_thickness` (also closes B15's unparameterised thickness) and `plate_top_above_pcb_top`. Verified: case STL is now **140.61 × 142.80 × 12.4** (was 16.00), floor still has its 5 holes, wall still closed at z=12.0. Lowering the rim also forced the USB-C cut from `extrude: 10` to **8** (10 mm from z=3 reached z=13, past the new rim). The configurator's `schema.mjs` default and all 3 presets were carrying the literal 16 too — all now derive. `standoffs.length` reads the unit instead of a literal 6. ⚠️ ergogen evaluates units **top-down** (mathjs), so a derived unit must be declared *after* its symbols. | ✅ fixed | `config.yaml` units, `configurator/lib/{schema,generate}.mjs`, presets |
| **B18** | **Controller bay is open-topped; reset/power sit outside the roof** — **ACCEPTED BY THE AUTHOR (2026-11-16) as a deliberate tradeoff** (dust/water ingress is the priority; the switches only need touching during initial setup/testing). Not a blocker. Roofed area = 50 × 30 mm at the MCU (x ≤ 106.75); reset (112.0, 47.8), power (108.0, 39.8) and JST (107.0, 58.0) all fall outside it, so they are finger-reachable from above. **Optional later improvement:** a small recessed cut-out per switch. **Still open:** the USB-C plug path (15×15 mm rim tunnel at z 3…13 vs connector at PCB level z ≈ 9–10) has never been checked — see ❓-13. | 🟡 by design | `config.yaml` `l_cover`, ❓-13 |
| **B19** | ~~The two FR4 plates are different parts.~~ **FIXED 2026-11-16.** `plate_right` referenced `r_cover_outline` (132.622 × 134.808) instead of `r_coverpart_switch_plate_outline` (132.622 × 117.048). The **117 mm one is correct**: it is *key cluster − key holes − screw holes*, i.e. a switch plate, and it is what the printed `l_cover` plate also uses; `r_cover_outline` is *full PCB outline* (incl. controller + JST bays) and would lay plate over the MCU. After the fix both plates measure **132.22 × 116.65** — identical, so the two files are genuine mirrors. Promoted from `STATUS.md` §5.2. | ✅ fixed | `config.yaml` `pcbs.plate_right` |
| **B20** | **The cover/plate has no ledge.** Case top opening 135.95 × 138.14 vs plate 132.22 × 116.65 ⇒ the plate is smaller than the hole, so its height/position come only from the 5 screws and it can shift ~1.9 mm per side. Now that rim top == plate top, shrinking `l_case_border_do_not_ocupy` to ≈ PCB + 0.2 turns the 1.7 mm rim top into a seat. | 🟠 before printing | `config.yaml` |
| **B21** | ~~The screws cannot reach the standoffs.~~ **FIXED 2026-11-16.** Top screw crossed plate 1.2 + air 1.0 + PCB 1.2 = 3.4 mm before meeting a standoff that sits *below* the PCB, so a 4 mm screw had 0.6 mm of bite (bottom 1.0 mm). Now `screw_top_length: 6` (min 5.9) and `screw_bottom_length: 6` (min 5.5) with `screw_engagement: 2.5`; budget 2.5+2.5 ≤ `standoff_length`. **BOM: both screws M2 × 6 mm.** | ✅ fixed | `config.yaml` |

### B13 in detail (the important one — this is what "the plate doesn't fit" means now)

Measured with `scripts/check_assembly.py`:

```
screw (41.8, 85.4)   dist to nearest switch 7.603 mm   cutout half 7.000 mm → clearance −0.200 mm (inside)
screw (41.8,136.4)   same                                                → −0.200 mm
screw (126.8, 80.13) same                                                → −0.200 mm
screw (126.8,131.13) same                                                → −0.200 mm
screw (131.7,156.42)                                                    → +0.395 mm  ok
```

A Ø2.2 hole whose centre is 0.2 mm past the cutout edge leaves a ~0.9 mm sliver, and in the boolean
the hole is swallowed: the fresh `l_cover.stl` has **0 screw-sized openings** at plate level (the
stale published one had 5, because its cutouts were 6.9 mm).

**Fix options, with the constraint made explicit:**
- The material between two adjacent columns is `17 − 14 = 3.0 mm`. M2 (2.2 hole) + 2 × 0.5 mm wall =
  3.2 mm > 3.0 ⇒ **nudging a screw into the gap does not work.**
- Therefore move the screw points **outboard into the frame padding** (the board outline is
  `l_key_based_board_outline_with_extra_padding`, so there is room outside the key cluster), or
- drop to **M1.6** (1.8 hole + 1.0 wall = 2.8 ≤ 3.0, marginal), or
- accept screws between rows instead of columns (row gaps are larger: rows are 17 mm apart too, so
  same 3.0 mm — no help).
- Whichever is chosen, it must change the **screw points** (`left_screw`/`right_screw`) so that PCB,
  plate, case, cover, tenting and palm rest all follow automatically, then be re-gated with
  `check_assembly.py`.

## 6. Open questions (need the author)

❓-1 **resolved** (cutout 14.0). Still open: ❓-2 PCB thickness (0.8 requested, 1.2 recommended,
**file says 1.6** — hotswap is verified fine at 1.2 and 1.6, ⚠️ UNVERIFIED at 0.8); ❓-3 spacebar
(see below); ❓-4 case↔tenting attachment; ❓-5 palm rest attachment; ❓-6 JLC assembly scope;
❓-7..❓-12 — see `docs/DECISIONS.md`.

**Spacebar / non-1u keys**: not expressible today. Five coordinated edits are required and the
canonical file has the logic *inverted* — `choc_space` filters on `[leftkey, -1_5u, space]`
("space AND NOT 1.5u") and `keycap_x_space` is referenced but never defined. Full recipe in
`docs/CONFIGURATOR.md` §10.

## 7. Locked decisions (see `docs/DECISIONS.md`)

D-1..D-13. Most load-bearing: **D-11 plate 1.2 mm** (choc needs ≤1.5 FR4), **D-12 PLA for v1**
(never SLA resin for a screw-loaded case), **D-13 configurator is local-first** (the Ergogen *web*
build cannot load the custom footprints, so no hosted PCB build). Row order is **bottom-first**
everywhere; `layout.rows[0]` is the bottom row.

## 8. The verification toolbox — and the SIX traps that produce false findings

All commands run from the repo root with `./.venv/Scripts/python.exe`.

| Script | Purpose | Command |
|---|---|---|
| `scripts/regen.sh` | local ergogen run (`node.exe` inside) | `./scripts/regen.sh` |
| `scripts/check_matrix.py` | matrix↔MCU pins, dup pins, dangling/wasted nets, L/R parity, `--routing`, `--counts`, `--plates`, `--pcbs-dir`, `--json` | `./.venv/Scripts/python.exe scripts/check_matrix.py --counts` |
| `scripts/check_print_files.py` | watertight / normals / signed volume / scale, `--json` | `... scripts/check_print_files.py <stls>` |
| `scripts/inspect_print_model.py` | **shape** check: section at given z, count closed loops + bodies + centroid offset | `... inspect_print_model.py x.stl --slices 1.5,10` |
| `scripts/render_stl.py` | headless orthographic PNG renders (matplotlib painter's algorithm) | `... render_stl.py OUT *.stl --views top,front,iso` |
| `scripts/check_render.py` | measure a PNG: fill, islands, see-through holes, symmetry | `... check_render.py out/*-top.png` |
| `scripts/repair_stl.py` | weld/orient/fill/invert; **`--drop-to-bed`** (Ergogen exports the cover at z=25) | `... repair_stl.py x.stl --drop-to-bed` |
| `scripts/check_assembly.py` | **the new one**: 20 cross-artifact checks (wiring + fit) | `... check_assembly.py --cases configurator/builds/<slug>/assets` |
| `scripts/jlc_assembly.py` | **B3/B7**: KiBot raw POS → JLC CPL (`cpl`), PCB → JLC BoM with an LCSC column (`bom`), and the agreement gate (`check`) | `./.venv/Scripts/python.exe scripts/jlc_assembly.py check` |
| `scripts/check_published.py` | **B14 gate**: refuses a stale/mixed `filtered-output/` (build stamp + config sha1 + cross-artifact checks + 14 mm cutout signature) | `./.venv/Scripts/python.exe scripts/check_published.py` |

### Traps (each one produced a fake defect in this session — do not repeat)

1. **Substring footprint matching.** `"choc_v1_v2" in name` also matches the socket and keycap
   previews ⇒ "96 switches". Use `name.endswith(":choc_v1_v2")`.
2. **Axis-aligned bbox of a rotated square.** A 14 mm cutout rotated 30° measures 19.1 mm
   (14·(cos30+sin30)) ⇒ fake "16/19 mm oversized cutouts" and fake "merged openings". Use **area**
   (196 mm² ± tolerance), or `minimum_rotated_rectangle`, or compare to the switch rotation.
3. **Order-dependent point matching.** KiCad re-saves reorder footprints, so comparing point *i* to
   point *i* reported **70 mm** residuals on a perfectly aligned set. Use symmetric
   nearest-neighbour (`cKDTree` both ways).
4. **Regex-parsing `.kicad_pcb` headers.** KiCad puts `(tstamp …)` between `(layer …)` and `(at …)`;
   a strict regex silently returned **(0,0) for all 32 switches**, which looked like "the published
   board is 213 mm displaced / incoherent". Use the `sexpr()` parser in `check_assembly.py`.
5. **Net-name regex.** Thumb nets are `col1_thumb_row_1` — there **is** an underscore before the row
   digit, so `col(\d+)_thumb_row(\d+)` never matches. Pattern: `col(\d+)_thumb_row_(\d+)`.
6. **Measuring a render that contains text.** A title drawn on the PNG is foreground and inflates the
   mask bbox (palm rest read 1.59 instead of 1.69). `render_stl.py` has `--title` **off by default**;
   keep it off when measuring.

**Trap: editing `config.yaml` from Windows Python silently rewrites it as CRLF.** `open(p,'w')` in text mode turns every
`\n` into `\r\n`, and `configurator/lib/generate.mjs` matches *literal* markers (`"presets:\\n"`,
`"units:\\n  $extends: …"`), so it dies with `canonical config: start marker not found`. ergogen does not care, so ONLY the
configurator breaks — very confusing. Write bytes or `newline='\n'`, and after any scripted edit run
`node.exe configurator/lib/generate.mjs configurator/presets/sweepyway.json --out C:/tmp/x.yaml`.

Two more, non-obvious:
- **VTK/vedo re-aims the camera.** `Plotter.show()` and `reset_camera()` both change direction after
  you set it ⇒ every "top" view silently became a 3/4 view (a 140.6 × 142.8 part rendered 872 × 434).
  Use `render_stl.py` (own projection), never vedo, for measurement.
- **`check_matrix.py` used to PASS a 0-key board.** Fixed: it now fails with "no matrix keys found".
  Never point `--board` at a YAML.

### Self-validating expectations (paste these to detect regressions)

`check_assembly.py` on the fresh build must print **18 ok / 2 FAIL**, and the 2 failures are exactly
B13 (`screw holes clear of switch cutouts … −0.200 mm`) and its symptom
(`printed cover has its 5 screw holes … 0`).

```
32 switches / 32 diodes                      layers B.Cu / F.Cu
diode orientation identical                  (pad#, net) pairs: [('1','2')]
position nets pair switch+diode              32 shared nets
grid nets match names                        29 grid keys
thumbs                                       3 on R5, columns C5/C6/C7
screw outline → PCB                          residual 0.000 mm, flip=fy
screw holes coaxial                          0.000 mm
plate cutouts land on switches               32, worst 0.000 mm
plate cutout area                            196.0 mm²
orderable plate cutouts on switches          32, worst 0.040 mm
case registers / bosses coaxial              0.025 mm
```

`inspect_print_model.py` expectations (z, loops): case 1.5 → **6** (perimeter + 5 screw holes);
case 3.2 & 10 → **1** (wall band, open where the USB-C slot cuts it); case 14 → **2**;
cover plate level → 32 key openings + controller bay, 0 screw holes (B13);
tenting 0.2/3.5 → **2** (hollow); palm 5 → **1** (solid).

`check_render.py` expectations (rendered 1400×1400): case 1232×1250 (0.986 vs 0.985 mesh),
cover 1230×1250, tenting 1232×1250, palm 1250×740 (1.689 vs 1.693) — all ≤0.25 % error, and
see-through holes: **case 5, cover 32, tenting 1, palm 0**.

## 9. What was verified this session (and how)

| Area | Method | Result |
|---|---|---|
| Wiring, per key | parse pads/nets, check set equality | 32/32 switch = {pos, C#}; diode = {pos, R#} |
| Diode orientation | pad-index carrying the row, all keys | identical ⇒ COL2ROW consistent |
| Wiring vs net names | `col3_row2` must land on C3/R2 | 29/29 grid consistent |
| Plate cutouts | register DXF→PCB (residual 0.000), KD-tree | 32 cutouts on switches, worst **0.000 mm**, all 14.0 mm |
| Cutout rotation | longest-edge angle vs switch rotation | matches on 32/32 incl. thumbs |
| Orderable plate PCB | same, on `plate_left.kicad_pcb` | **0.000 mm** |
| Printed cover | register on screw holes | **32/32 covered** (fresh); stale published: 0/32 (21.77 mm off) |
| Case | register on screw bosses | **0.025 mm** |
| Screw ↔ cutout clearance | rotated-frame signed distance | **−0.200 mm** ⇒ B13 |
| Keycaps | 16.5 mm squares, rotation-aware, pairwise distance | **+0.50 mm**, no collision |
| STL shape | sections (loops) | as listed in §8 |
| Renders | aspect ratio vs bbox | 0.02–0.22 % error ⇒ projection exact |
| Website (structure) | HTTP 200, `/api/presets` JSON, `$('id')` vs `id=` | 42 ids, 18 call sites, **0 dead refs** |
| Website (appearance) | — | ❌ **not verified**, needs images |
| Published artifacts | same checker on `filtered-output/` | B14 (mixed builds), B10 alive (6.9 mm) |
| GitHub | `gh` absent; inspected committed output + workflow yaml | artifacts = `upload-artifact` (ephemeral) + Pages; no release |

## 10. Vision / image support — RESOLVED 2026-11-16

**Status: working.** A fresh session (2026-11-16, session 2) read
`configurator/builds/sweepyway-2f79aca4/assets/renders/l_cover-top.png` and described the part
correctly. 20 images were then inspected. See `docs/VISUAL-AUDIT.md` for what sight found — it is
the single most productive pass in the project's history (4 new blockers, 1 blocker correction).

**Do not re-derive §10.** The `"input": ["text","image"]` fix in `~/.pi/agent/models.json` holds;
images arrive.

If a later session ever sees `(tool image omitted)` again, fall back to:
1. `scripts/render_stl.py` + `scripts/check_render.py` (pixel measurement, §8), and/or
2. the `ask-model` skill (dispatch a vision model to describe the PNGs), and/or
3. `scripts/inspect_print_model.py` (geometry-level shape checks).

Do **not** claim a visual check was performed if the image was omitted.

**Rules learned the hard way (all in `VISUAL-AUDIT.md` §1):** the painter's-algorithm renderer draws
**false internal seams** — faint diagonal creases across flat faces and vertical striping on walls.
Never report those as geometry defects; cross-check with `inspect_print_model.py` sections.

**History, for the record:** the model always had vision; pi strips images via
`downgradeUnsupportedImages(messages, model)`, which keeps them only when
`model.input.includes("image")`. That field was missing from `~/.pi/agent/models.json` (backup:
`models.json.bak-before-image-input`). It is now set to `["text","image"]` and verified by a direct
provider call (a 96×96 PNG of a blue ellipse → *"Blue circle shown"*,
`multimodal_tokens: {'image': 184}`) and then by a real `read` in session 2.

## 11. Next steps, in priority order

> Rewritten at the end of session 2. **§0 is the canonical list**; this is the same order with the
> reasoning attached. Items 1–3 of the previous version (B19, B16, B17) are **done**.

1. **B4 — mirror the 5 screw points to the right half.** Now the top mechanical blocker: the right
   PCB has no mounting holes, so the soldered standoffs (F3b) have nothing to go into, and the right
   half has no anchoring at all. The printed right case is a slicer-mirror of the left
   (`REVERSIBLE.md`), so the bosses come for free — the PCB is the blocker.
2. **B3 — close the POS/CPL declaration.** 2 of 98 placements export (`only_smd: true` + a diode
   footprint with no `attr smd`). This is the last thing between us and a real assembly order, and
   it is small: attributes + config, not geometry (§5.7 has the proof).
3. **B2 — one CI run** of the rewritten autoroute action. The root cause is fixed locally (paths
   pointed at a nonexistent `pcbs/`, inside an `if [ -e … ]`, so it was a silent no-op) and the
   router is proven (0 unrouted), but the workflow has never executed it end to end.
4. **B1 — pin maps.** The configurator's generated `config.yaml` already assigns
   `P3..P7 → R5,R4,R3,R2,R1` correctly; the checked-in one does not (12 of 64 keys dead).
   Adopting the generated config would close B1 and B4 together.
5. **B20 / the ledge** — the cover has no ledge and the case opening (135.95 × 138.14) is larger than
   the plate (132.22 × 116.65); plate height is currently set only by screws. Follows from the
   anchoring decision, so revisit with `FASTENERS.md` §7 Q5.
6. **B5 / B18 / Q-13 — right-hand 3D parts, open controller bay, USB-C plug path.** Render
   `l_3d_preview` with the MCU/socket/switch models.
7. **B14 / B15 — publishing.** Regenerate `filtered-output/` from the current config; the gate
   (`scripts/check_published.py`) exists and reproduces the bug, so this is now mostly "run it in
   CI". Also delete the `-misscaled.glb` after `fix_glb_scale.py` (one line).
8. **B7 / B8** — the remaining PCB-side cleanups (socket pads, silkscreen/board-name issues).

**Do not redo:** B13 (screw positions are final and gated), B16, B17, B19, B21, the F3b architecture.

## 12. What NOT to trust

- **`filtered-output/`** — stale and mixed (B14). Do not upload anything from it. Do not cite its
  PNG/PDF/STEP/GLB as evidence of the current design.
- **`ergogen/output/cases/`** — the `.jscad` files are current (2026-11-15) but the directory's
  STLs are not regenerated by `regen.sh` at all — CI/configurator turn jscad into STL. Prefer the
  configurator build's `assets/`.
- **Git working tree** — nothing from this session is committed. `git status` reports 105 modified,
  3 deleted, 12 untracked entries; `docs/` and `scripts/` are **entirely untracked**, as are
  `configurator/`, `AGENTS.md`, `.gitattributes`, `.env.example`. Most of the 105 modified files are
  pre-existing CRLF churn — use `git diff -w` to see the real changes.
- **`config.yaml` B9/B10 fixes are uncommitted** (plate 1.2 mm, cutout 14.0 mm). They exist in the
  working tree only.

## 13. Gotchas learned about Ergogen (source-verified in `node_modules/ergogen/src/points.js`)

- Merge order: defaults → global `points.key` → `zones.<z>.key` → `columns.<c>.key` → `rows.<r>` →
  `columns.<c>.rows.<r>`; row entries merge **as key props directly** (no `key:` wrapper).
- `shift` accumulates row→row; `stagger`/`spread`/`splay` accumulate column→column and are read only
  from `keys[0]`. ⇒ `shift` is a **delta**, so absolute row offsets must be converted (the
  configurator's `rowStagger` does this; hand-authoring `[0, 4.25, 8.5]` yields 0/4.25/12.75).
- `rectangle.size` is the **full** extent, not half. (This was B10: half-size ⇒ 6.9 mm cutouts.)
- Any mirrored point gets `rightkey` **appended**, so mirroring a screw zone produced 5 phantom
  diodes ⇒ the right screws must be explicit `r_screw_*` twins.
- Rows are **bottom-first**: `layout.rows[0]` = bottom; a column's `cells[0]` is its bottom key.
- Ergogen exports HTML **cases at the preview z-offset** (the cover sits at z=25) ⇒ always
  `repair_stl.py --drop-to-bed` before printing or measuring.

## 14. Cheat sheet

```bash
cd "/mnt/c/a/IRL Products/Keyboard design/SweepyWay"

./scripts/regen.sh                                              # config -> PCB/plate/outlines/jscad
./.venv/Scripts/python.exe scripts/check_matrix.py --counts      # wiring sanity
./.venv/Scripts/python.exe scripts/check_print_files.py <stl>... # slicer-readiness
./.venv/Scripts/python.exe scripts/check_assembly.py --cases configurator/builds/<slug>/assets
./.venv/Scripts/python.exe scripts/inspect_print_model.py <stl> --slices 1.5,10
./.venv/Scripts/python.exe scripts/render_stl.py C:/tmp/out <stl>... --views top,front,iso
./.venv/Scripts/python.exe scripts/check_render.py C:/tmp/out/*-top.png
./.venv/Scripts/python.exe scripts/repair_stl.py <stl> --drop-to-bed

node.exe configurator/lib/generate.mjs configurator/presets/<p>.json --out <yaml>
node.exe configurator/server.mjs            # http://localhost:5173
node.exe node_modules/ergogen/src/cli.js ./<dir>/ --output ./<dir>/out --clear --debug
```

The configurator build dir needs a `footprints` junction to `ergogen/footprints`:
`cmd.exe /c mklink /J "<repo>\\configurator\\builds\\<slug>\\footprints" "<repo>\\ergogen\\footprints"`
(the server does this itself; do it by hand only when driving ergogen manually).

## 15. Document index

**Start here:** `FASTENERS.md` (**the mechanical decision record — read §0 first; F3b is adopted and implemented**) · `HANDOFF.md`
§0 (resume point) · `STATUS.md` (§4 blockers — keep updated).

Then: `DECISIONS.md` (D-1..D-13, Q-1..Q-14) · `VISUAL-AUDIT.md` (**read before editing
`config.yaml`** — 2026-11-16 visual pass, B16–B19) · `REVERSIBLE.md` (reversible plate/PCB
feasibility, cost, risk — Q-14) · `HARDWARE-STACK.md` (heights/gaps/fasteners) ·
`ORDER-CHECKLIST.md` (**§0.1 = what is missing for the JLC order**) · `KEYBOARD-REFERENCE.md`
(verified part specs + source URLs) · `BUILD-REFERENCE.md` (Lily58 build-guide audit) ·
`CONFIGURATOR.md` (§7 print-file pipeline, §10 spacebar) · `PIPELINE.md` ·
`TROUBLESHOOTING-3D.md` · `ERGOGEN-GUIDE.md` · `BOM.md` · `ROADMAP.md` · `HARDWARE-BOM.md`
(generated — screw lengths, do not hand-edit).

**Figures:** `docs/img/{B17-stackup,fastener-options,fastener-sections,screw-move,plate-holes,f3b-boss}.png`

**Scripts that are gates:** `scripts/check_assembly.py` (17 checks, currently PASS) ·
`scripts/hardware_bom.py` (BOM + geometry, currently PASS) · `scripts/check_published.py`
(B14, reproduces the bug on an unstamped folder) · `scripts/check_matrix.py` (B1/B4, still
failing by design) · `scripts/pre-push.sh` (`ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push`).
