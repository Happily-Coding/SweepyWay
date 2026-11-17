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

## 5. Older pendings, unchanged

- **Right palm rest / tenting base are not mirrors** (`r_hand_rest_polygon`,
  `r_thumb_suplementary_outline` — one wrong vertex, `mirror_thumbfan_col1` vs `thumbfan_col1`),
  so the Python builders are left-only.
- **B22 residue**: only the default preset round-trips; `minimal-3x5` refuses loudly,
  `row-stagger-1u` generates a valid but different config (needs per-preset outline refs).
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
