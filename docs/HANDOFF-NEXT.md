# Next session — start here

State at hand-off: `968e280` (on top of the merged B20-D work `a1bc1c0`, pushed to main).

---

## 1. FIRST TASK — inventory the published outputs, then reproduce them locally

Your instruction, and it is the right first move: I have been checking **my own** artifacts
(ergogen output + gates) while the thing you actually look at is the gh-pages publish, which is
stale and full of intermediates.

### 1a. Crawl and index the site

```
curl -s https://happily-coding.github.io/SweepyWay/
        https://happily-coding.github.io/SweepyWay/cases/
        https://happily-coding.github.io/SweepyWay/pcbs/
        https://happily-coding.github.io/SweepyWay/palmrest/
```

Root already shows: `cases/`, `palmrest/`, `pcbs/`, `combined_scene.glb`,
`pcb_plus_stl_no_tenting.glb`, `pcb_plus_stl_no_tenting_tented.glb`,
`temp_stl_models_no_tenting.glb`, `temp_stl_models_tenting.glb`, `readme.md`.

Two findings before even going deeper:

- **intermediates are published**: `temp_stl_models_*.glb` and `pcb_plus_stl_*.glb` are scratch
  files from `create_full_3d_visual.py`, not deliverables.
- **stale**: `combined_scene(4).glb` (downloaded by the author) has `Case` = **16.0 mm** tall;
  the current design is **11.2**. That scene predates B17/B20 and must not be used as evidence.

Deliverable: **`docs/OUTPUT-INVENTORY.md`** — one row per artifact with:

| field | why |
|---|---|
| path on the site | the thing to look at |
| **what it contains (1–2 lines)** | so the inventory is usable without opening every file: which parts are present (case / cover / plate / PCB / switches / keycaps / screws), assembled or exploded, materials/colours, which half(s), and whether copper, silk and pads are included |
| producer (workflow step + script) | so it can be regenerated |
| frame + units | addendum below: several of these are in different frames |
| checked into the repo? | `filtered-output/` is committed, so drift is possible |
| stale? (stamp / measured) | the 16 mm case above |
| known-bug caveats | e.g. `*-misscaled.glb` next to the fixed one |

**How to open any of these:** drag the file onto **<https://3dviewer.net/>** in a browser — it renders
GLB (with materials/colours) and STL, and it can load several files at once to compare variants.
Plain STL carries no colours or part names, so prefer GLB when both exist. `export3d/` in this repo
is already in assembly frame, so case + plate load together and line up.

**Assume same-content-different-extension files disagree** (your warning). Already confirmed:
`filtered-output/pcbs/3d/` holds `left_pcb-3d{,-misscaled}.glb` **and** `.step` **and** `.stl`;
the pipeline has a separate `fix_glb_scale.py` step precisely because the glTF export is wrong,
so `.glb`, `.step` and `.stl` are not interchangeable evidence.

### 1b. Reproduce the whole chain locally — `scripts/build_outputs.sh`

Mirror `.github/workflows/build.yaml` step for step, so "what the site shows" and "what I measure"
are the same artifact:

1. `node ergogen` (regen)
2. gates: `check_assembly.py --cases`, `hardware_bom.py`, `check_matrix.py`, `check_config_drift.mjs`
3. KiBot in docker (`ghcr.io/inti-cmnb/kicad9_auto`) → `filtered-output/pcbs/3d/*`, `pcbs/images/*`
4. OpenJSCAD `convert-all.sh` in docker → `filtered-output/cases/*.stl`
5. `uv run palmrest_and_tenting_creation/create_palmrest.py`
6. `uv run palmrest_and_tenting_creation/create_tenting_system.py`
7. `uv run fix_glb_scale.py`
8. `uv run create_full_3d_visual.py` → `combined_scene.glb`

Then **diff local vs published** — that diff is the drift report we have never had.

### 1c. Fix the two lies in `create_full_3d_visual.py`

Both are hardcoded and tuned to the old 16 mm case, so a fresh run still renders something false:

- `rotation_matrix(angle=-1.5708, direction=[1,0,0])` — magic −90° about X
- "Moving the PCB upward by **7 units** along Y-axis"

Derive both from `ergogen/config.yaml` (`case_bottom_thickness`, `standoff_length`,
`pcb_thickness`, `top_plate_thickness`) instead of literals.

---

## 1d. Local reproduction status (scripts/build_outputs.sh)

Working today, no docker: `--ergogen`, `--gates` (all four green), `--copy`, `--jscad` (cases now
**11.20 mm**) and `--verify` (asserts case height + D1/D2 edge counts + flags the tenting mesh).

Working with docker: `--kibot default`, `boards`, `3d_preview` and `jlpcb_pos`, plus
`scripts/jlc_assembly.py cpl|bom|check` (**PASS**, 67 placements/half, 5 BoM lines, 0 LCSC gaps).

Still to do:

- `kibot pdf` writes both PDFs and then **never exits locally** (container gone, shell waiting).
  The PDFs are produced (133 KB / 134 KB); make the stage tolerate it with a timeout + file check.
- `--assembly` (palm rest, tenting, `create_full_3d_visual`) needs `uv`; `fix_glb_scale.py` alone
  works with the venv (regenerated both fixed GLBs today).
- WSL gotcha baked into the script: `docker -v` needs `C:/…`, not `/mnt/c/…`, and `cygpath` does
  not exist here (this is WSL, not MSYS) — the script converts with `sed`.

## 1e. Height-budget finding (new, and it reframes the plate question)

See §2 — the short case leaves **1.0 mm** of air above the PCB top while the controller zone
measures **8.62 mm** tall on the fresh export.

## 2. The plate decision — D2 main, D1 optional view window

- **Author picked D2** (`plate_*_full`) as the main variant. D2 as generated has **no** controller
  opening, matching the old reference scene where the controller was enclosed and fine.
- **But the headroom changed underneath that decision** (§1e): the reference scene was a ~23 mm
  tall enclosure; B20-D made the plate the lid at 12.4 mm, leaving **1.0 mm** of air above the PCB
  top against a controller zone that measures **8.62 mm**. So "no opening" is the intent for the
  *old* geometry, not evidence that it is feasible in the new one. Resolve this before ordering
  plates: either the controller really is shorter than 1 mm above the board (measure the hardware),
  or D1's window becomes functionally necessary — which is exactly the "view window" below.
- **The controller is on the SAME face as the keycaps** (author, from the render, twice). My
  "collides with the plate / needs an opening" claims were wrong twice in this session — first
  from an axis-flipped export, then "corrected" to the underside. Do not trust my geometry
  claims here without re-measuring.
- **D1 is demoted, not dead.** It is not the main variant (D2 is), but it stays as an
  **optional secondary variant: a controller view window** — a cutout over the MCU purely so the
  board/controller is visible, since nothing *needs* to be exposed. Its hard constraint is that it
  must not touch the switch field.
- **D1 as currently generated is wrong on both counts**: it is unnecessary *and* it deletes 4
  switch cutouts per half. Measured: 25+3 vs 29+3 switch-shaped loops, notch contour 65 × 46 mm
  centred (96.9, 64.9), swallowed positions (69.0, 66.5), (86.0, 70.8), (103.0, 73.3),
  (120.0, 76.7) on the left and the mirror on the right.
  `docs/img/B20-D1-DELETES-SWITCHES.png`. To revive it: rebuild the window as the **MCU keep-out**
  (~18.8 × 34.8 at PCB (81.75, 47.77)) instead of the 50 × 30 controller-area rectangle, then
  assert 32 switch cutouts survive (§3).
- Keep the build target ordering explicit: `plate_*` → D2 (main). `plate_*_bay` → optional,
  must pass the cutout gate before it can be offered as a choice.

### B23 — controller headroom: two mounting presets, generic header by default

**Decision: `case.mcuMounting` defaults to `generic`** — a stock 2.54 mm header (the KiCad official
`PinHeader_1x12` part). Reasons, in order of weight:

1. **Availability.** A 2.54 mm 1×12 header is in every shop on earth; a 5 mm no-solder spring header
   is a niche part. A case designed for the generic header also works with the spring one.
2. **It is the conservative case.** Generic is ~2 mm taller, so designing to it means the enclosure
   is never too short: `spring 6.85` vs `generic 8.88` head height, i.e. hood inner top
   **19.08 vs 17.05** and outer top **20.08 vs 18.05**.
3. **It is measurable from a model already in the repo**, so the number is reproducible rather than
   remembered — see the band table below.

The cost of that choice is exactly **+2.03 mm of case height** over the screw/standoff region and
nothing else: no switch, no plate dimension, no screw length changes.

| preset | what it models | head | hood inner | hood outer |
|---|---|---|---|---|
| `generic` (default) | KiCad `PinHeader_1x12_P2.54mm_Vertical`: short pins through the PCB, plastic body on it, nano socketed onto the long pins — plastic **2.54** + long pins **5.84** + 0.5 roof clearance | **8.88** | 19.08 | 20.08 |
| `spring` | 5 mm no-solder spring header, ¼ above / ¼ below the board — 1.25 + board 1.6 + tallest part 2.0 + safety 1.0 + clearance 1.0 | **6.85** | 17.05 | 18.05 |

Measured bands behind the generic numbers (relative to the PCB top face, from
`component_3d_models/PinHeader_1x12_P2.54mm_Vertical.step` via the KiBot glTF export):
plastic body **1.59…4.13**, long pins **4.13…9.97**, short pins through the board **−1.41…1.59**.

Both presets live in `configurator/lib/schema.mjs` (`MCU_MOUNTINGS`) and reach `config.yaml` as a
**one-hot pair** (`mcu_header_style_spring` / `mcu_header_style_generic`), because ergogen units are
pure arithmetic with no conditionals: `mcu_head_height` is the dot product of the flags with the two
head heights. `check_config_drift` owns the flags, so the UI choice and the canonical config cannot
disagree; `check_assembly` asserts they are one-hot and that the hood follows from the selected one.

#### Why the height is necessary at all (unchanged)

### B23 — controller headroom: it IS necessary, and it is a raised area, not an opening

Author's call: **no opening**; the controller area gets taller *only if necessary* (and it looks
necessary). Measured against the real model, it is:

| quantity | value | source |
|---|---|---|
| air above the PCB top today | **1.0 mm** to the plate underside, 2.2 mm to the plate top | `plate_top_above_pcb_top 2.2 − top_plate_thickness 1.2` |
| `Nice_Nano_V2.step` extent | 17.78 × 36.15 × **9.28** (model z **−1.58 … +7.70** against its own board) | parsed `CARTESIAN_POINT`s in `component_3d_models/Nice_Nano_V2.step` |
| its placement | `mcu_3dmodel_xyz_offset: [0,0,2.5]` left, **[0,0,5]** right | `ergogen/config.yaml` ~1106 / ~1424 |
| controller **head** (board + pins/socket) above the PCB top | model z −1.58…+7.70 at offset 2.5 → top **≈ +10.2 mm**; at offset 5.0 → ≈ +12.7 mm | same file + offsets |
| bare-board worst case | 1.6 mm board + a ~1.7 mm module ≈ **3.3 mm** > 1.0 | — |

The clearance target is the **head**, not the controller: what has to fit is board + headers +
sockets, and it has to fit **inside the enclosure** — nothing may protrude through the plate or
the case. So the hood is a raised part of the case that encloses the head, and its inner height is
driven by the head: `hood_inner_top = pcb_top + mcu_head_height + clearance`.

So even the most optimistic reading exceeds the available air: a raised controller area is
required. **Two things to fix while doing it:**

1. **The two halves disagree** — 2.5 vs 5.0 mm offset for the same footprint. Pick one (the real
   socket/header stack decides it) and put it in `schema.mjs` as a constant so the drift gate
   owns it, exactly like `MCU_MIRROR_DISTANCE`.
2. **Do not hardcode the hood height.** Derive it:
   `hood_top = case_bottom_thickness + standoff_length + pcb_thickness + mcu_stack + clearance`
   with `mcu_head_height` and `clearance` as named units. On today's numbers the head top is
   ≈ 20.4 mm (offset 2.5) or ≈ 22.9 mm (offset 5.0), so the hood rises roughly **8–10.5 mm above
   the plate top** — bigger than the old cover's +5.4 mm, which is worth knowing before committing
   to it: the head height is the number to confirm on hardware, because it drives the case height
   more than anything else in this design.

#### Hood geometry — decided, not yet cut (all parameters are in place)

Author's answers, which the next pass should implement exactly:

| decision | value |
|---|---|
| footprint | **a configurator setting** (`bay` = `*_controller_area_border`, or `wide` = the old cover's look, which the author liked); both acceptable, so expose it |
| how it is made | **integral with the case** (one print), rising from the **case floor** so the walls are printable verticals |
| walls | **same as the case wall**, but parameterised (`hood_wall_thickness: case_wall_thickness`) |
| plate | **butts against the hood wall** — no cutout, no opening, nothing visible through the plate |
| roof | **no chamfers needed for the bay footprint**: the unsupported bridge is ~27 mm at 1 mm thick, routine for FDM; a *wide* footprint grows that span, so a 45° fillet or supports is the fallback there. No model reorientation is required — the case already prints floor-down and the roof is the only bridge |
| corners | **rounded to match the case** (the existing `*_controller_area_border` outline already has 8 arcs, so this is free) |

**Wall thickness:** `hood_wall_thickness: case_wall_thickness` — defaults to the case wall (1.2),
overridable with an explicit number. The hood's outer outline is **derived** from
`*_controller_area` with ergogen's `expand: hood_wall_thickness`, so any thickness works without new
shapes (verified: the derived `l_hood_outer.dxf` / `r_hood_outer.dxf` generate correctly).

**Progress made on the geometry (then reverted, deliberately):** a working cut was reached — case
bbox z 0…20.08, the roof **solid** across the hood at z=20.0 (63.75…115.75), walls present — but two
defects remained, and fixing them means also rewriting two plate invariants, so it was reverted rather
than leaving the tree red:

1. the measured wall came out **0.75 mm**, not the 1.2 requested: `expand` widens the *outline path*
   differently than expected, so wall thickness must be checked on the STL, not assumed from the unit;
2. still **4 bodies / not watertight**, despite the 0.4 mm overlaps;
3. `D2 plate == footprint − keys − screws` and `D1 removes exactly the bay` both (correctly) stop
   holding once the plate also excludes the hood footprint — they must be restated as
   `… − hood_outer`, and the D1/D2 difference recalculated against the derived hood outline.

A watertight-STL gate was written for `check_assembly` (`l_case_3d.stl` / `r_case_3d.stl` must be
watertight, reporting body count and volume) but **it currently does not execute** — the block is
present at the right level yet never prints, so it is either unreachable or shadowed. First thing to
debug next: run `check_assembly --cases` and confirm those two rows appear at all.

**Why it is not in the tree yet:** the first attempt (outer extrude 54 × 34, inner subtract 50 × 30,
roof extrude 1 mm, everything sitting exactly on the floor plane and exactly on the wall top) produced
a **non-watertight** case with thousands of zero-volume sliver bodies. That is the known JSCAD failure
mode for **coincident coplanar faces**. The fix to try first is mechanical: extrude the walls from
`case_bottom_thickness - 0.4` with height `+0.4`, and start the roof at `controller_hood_inner_top - 0.4`
with thickness `+0.4`, so every adjoining solid overlaps instead of touching. Also verify with
`check_assembly --cases` that the STL is watertight before trusting any volume/clearance number.

**The reference geometry is the old cover, and it did exactly this:**

```
old cover: key field top 26.60, controller area top 32.00  ->  +5.4 mm raised hood, no opening
```

(`cover.stl` at `13c8ffa`/`45abc3b`, sliced: flat at 26.60 for y −172.6…−71.5, then 32.00 for
y −71.5…−37.8, base at 25.00.) So "taller only if necessary" is not a new idea in this project —
it is the previous design's own solution, and the height reduction to 12.4 is what removed it.

Consequences to design through:

- the **plate** must butt against the hood wall rather than span the bay (flat FR4 cannot step), so
  the bay cutout comes back — but bounded by the switch field, **not** by the 50 × 30 controller
  rectangle that ate four keys. That is precisely D1's shape done correctly, and it costs no
  switches because the hood's wall is what the plate's bay edge rests on.
- nothing about the hood is an "opening": the controller stays enclosed.
- add two gates: (a) **containment** — the highest controller geometry (from the PCB 3D export,
  keycap side) must be below the hood's inner top, with clearance, i.e. the head fits *inside*;
  and (b) `hood footprint ∩ switch cutouts = ∅`, so the hood never costs a switch.

## 3. Restore the gate that was deleted (do this early, it is 20 lines)

`check_assembly.py` used to assert **32 closed cutouts** on the plate. During the B20-D work that
assertion was *replaced* because "the bay notch merges cutouts" — i.e. the failure was
accommodated instead of fixed, and the repo went green while shipping a plate missing four keys.

Restore as: every plate variant has exactly **32 switch cutouts** (14 × 14 plus the three thumb
shapes) **and 5 screw holes**, or fail. This is the check that would have caught D1 in seconds.

---

## 4. USB-C window is in the wrong place (verified, not yet fixed)

- The window does **not** cut the controller-bay wall. Cross-section area is identical at
  z = 8 / 10.5 / 11.0 (1107.32 mm²), while at y = −34.5 the wall spans x 65…114 and the slot
  (after its shift) sits at x 54.2…69.2, y −50.3…−35.3 — it clips ~4 mm of wall and the rest is
  empty space outside the tab.
- Cause: `shift: [-20, 5, case_bottom_thickness]` on `l_usbc_border_outline`.
- Already changed: `usbc_slot_height` = `case_border_height - case_bottom_thickness` (8.2, window
  to the wall top). That formula is right; the **x placement** is what is wrong.
- Add a gate: the window outline must intersect the bay wall, or fail (same class of bug as the
  autoroute no-op and the missing cutouts: a step that silently produces nothing).

---

## 4b. Right palm rest / tenting outline — measured baseline (not fixed)

The old note said "one wrong vertex". The measurements say something less tidy, so here is the
state a future attempt should start from (all against mirror axis **x = 170**):

| outline | bbox mirror residual | shape agreement | note |
|---|---|---|---|
| `thumb_suplementary_outline` | **0.00 mm** | IoU **0.9612** (L 3356.1 vs R 3491.4 mm²) | already very close; R is 4 % larger, so this is a shape detail, not a broken outline |
| `hand_rest_polygon` | **86.33 mm** | — (open outline, does not polygonise) | genuinely different shapes: L spans x **25.2…231.2** (it crosses the mirror axis, because `l_hand_rest_overlapping_polygon` deliberately uses the **`mirror_thumbfan_col1_thumb_row_1`** vertex), R spans x **195.1…314.8** |

**Why mechanical mirroring failed (the important part, corrected twice).**

*Not* different axes — that was my first guess and it is wrong. Both point families mirror about
**x = 170**: the matrix uses `mirror: { distance: 340 }` from x = 0 (axis 170), and the thumbfan uses
`ref: matrix_col6_row4` (x = 120) with `distance: 100`, which is also axis 170.

The real cause is **rotation**. Verified from the routed boards: switch **positions** mirror exactly
(340 − x, 0.00 mm residual), but **rotations** come out as −θ instead of the 180 − θ a reflection about
the vertical axis implies:

```
left thumb key   rot 155.0  ->  right twin  rot -155.0   (reflection would be 25.0)
left thumb key   rot 150.0  ->  right twin  rot -150.0   (reflection would be 30.0)
left matrix key  rot 180.0  ->  right twin  rot -180.0   (equivalent; footprint is symmetric)
```

Harmless for the unrotated matrix keys, but a polygon vertex written as `ref: <rotated thumb key>` +
`shift: [...]` has its shift applied in that key's local frame, so "negate the x term" does not
produce the mirrored vertex: it is off by the rotation difference. Five of the ten
`l_thumb_suplementary_outline` vertices are on rotated thumb keys, which is exactly the 4 % area gap.

So mirroring is deterministic and the axis is fine; what is not mirrorable by x-negation is a shift in
a rotated frame. Two ways forward:

1. **Mirror resolved geometry** (recommended): read the left polygon's vertices from the generated DXF,
   reflect them about x = 170, and emit an explicit point list — ideally generated by
   `generate.mjs` from the layout so it stays in sync. No frames, no ambiguity, IoU = 1 by
   construction.
2. **Upstream**: if ergogen should support "this outline is the mirror of that one", that is the real
   feature — mirroring at the *outline* level instead of forcing every vertex to be re-expressed in
   mirrored local frames. Worth raising, but option 1 unblocks this repo today.

So the *left* hand-rest polygon is the odd one: it is built partly from a mirrored point, which is
why it reaches across the axis and why no mechanical mirror of it can match. The fix order is:

1. Rebuild `l_hand_rest_overlapping_polygon` using **left-half refs only** (replace the
   `mirror_thumbfan_col1_thumb_row_1` vertex with the equivalent left-side point/shift), so the left
   polygon stays inside its own half.
2. Then mirror it mechanically: ref `X` → its twin (`mirror_X` ↔ `X`), and negate the **whole** x
   term of each shift (`-(0.5 kx + 0.5px)`, not `-0.5 kx + 0.5px`), because
   `mirror(P + s) = mirror(P) + (−s_x, s_y)`.
3. Gate it: 0.99 ≤ IoU(L_mirrored, R) for both outlines, in `check_assembly`.

Two traps hit while trying this the first time, both worth keeping:
- a regex that parses `- ref:` / `shift:` must not let `\s*` swallow the newline, or every shift is
  silently dropped and the mirror comes out wrong with no error;
- Windows Python cannot read `/tmp/...` paths, so an A/B experiment written to `/tmp` silently
  measured the same unchanged file twice (use `C:/tmp/...`).

## 5. Older pendings, unchanged

- **Right palm rest / tenting base are not mirrors** — see §4b for the measured baseline (the thumb
  outline is already 96 % mirrored; the *left* hand-rest polygon is the odd one because it uses a
  mirrored vertex). The Python builders are left-only until that is done.
- **B22 residue (reduced)**: `check_config_drift.mjs --preset` now has three honest modes.
  Default `sweepyway.json` does the full structural compare against `ergogen/config.yaml` (PASS).
  `row-stagger-1u` **generates** and is reported as "non-default preset: generation only" (PASS) —
  comparing it to the canonical file would be asserting that a different layout produces identical
  output, which used to show up as a false FAIL. `minimal-3x5` still refuses loudly and correctly:
  "canonical outline references matrix_col6_row4; this layout has no equivalent point. Retarget the
  outline for this preset before generating from it." That retargeting (per-preset outline refs) is
  the only real work left in B22, and it is a design change, not a bug.
- **B14/B15**: `filtered-output/` cannot be published without `BUILD-STAMP.txt`;
  `check_published.py` correctly blocks. One clean CI run after the fixes closes it.
- **B8** still open.
- **Router**: `-mp 14` + the "0 unrouted" completeness gate is the contract. The
  `freerouting.json` optimizer experiment is a **dead end** (a partial settings file replaces the
  defaults and the CLI dies with `NPE ... "name" is null`); CI is the publish step, not a gate,
  so the ~18 min optimizer tail does not matter.
- **Sockets**: consignment, `C9900248317` (min 10). `jlc_assembly check` passes with 0 LCSC gaps.
- **Submodule `ergogen/footprints/ceoloide` is dirty** — check whether that is the already-pushed
  B3 footprint work (`481b637`) leaving a stale gitlink, or something new.

---

## 6. Artifacts created for the author to open (committed)

- `export3d/README.md`, `export3d/assembly_left_D1.glb`, `assembly_left_D2.glb`,
  `case_left.stl`, `case_right.stl`, `plate_{left,right}_{bay,full}.stl`
  — assembly frame, plate bottom = case top = 11.2. Viewer: <https://3dviewer.net/>.
- `docs/img/B20-D1-vs-D2.png` (both plates, true scale, dimensioned)
- `docs/img/B20-D1-DELETES-SWITCHES.png` (the four vanished switch positions)

## 7. Method rules learned the hard way (carry these forward)

1. **Never trust a figure I generated** until the same numbers come out of the files
   (`gr_circle` vs `gr_arc`, open outline chains, PCB frame is y-flipped vs the case frame:
   `y_case ≈ −y_pcb`).
2. **A gate that gets weakened during a change is a bug report**, not housekeeping.
3. Judge 2D outlines by **entity/contour counts**, not SVG bytes or a rendered image.
4. `kicad-cli` glTF/STL exports carry rotations in node transforms and a metres→mm scale bug —
   always transform to world space and sanity-check one known dimension (the PCB thickness) first.
5. **When the author sends a render, that render is ground truth about intent.** My export math
   lost to it twice on the controller side. If they disagree, say so and re-measure — never
   declare the author's observation mistaken.
