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

## 2. The plate decision — D2 is the base, and it NEEDS a controller opening

- **Author picked D2** (`plate_*_full`). D1 "could work but needs tweaking so it doesn't cut
  into the keys".
- **The controller is on the SAME face as the keycaps — on top of the board** (author, from the
  render, twice). It is therefore between the PCB and the plate, so a flat plate **cannot** pass
  over it: whatever variant ships needs an opening over the controller. D1's bay was the right
  idea and is only wrong in **size/shape** (see the next bullet). I got this wrong twice in this
  session — first asserted it from an axis-flipped export, then "corrected" it to the underside.
  Do not trust my geometry claims here without re-measuring.
- D1 as generated **deletes 4 switch cutouts per half** — measured, not inferred:
  25+3 vs 29+3 switch-shaped loops, the notch contour is 65 × 46 mm centred (96.9, 64.9),
  swallowed positions (69.0, 66.5), (86.0, 70.8), (103.0, 73.3), (120.0, 76.7) on the left and
  the mirror on the right. `docs/img/B20-D1-DELETES-SWITCHES.png`. So the opening must be the
  MCU/pin **keep-out**, not the 50 × 30 controller-area rectangle.

Measure this before cutting (it decides whether an opening in the plate is even sufficient):

1. Load `filtered-output/pcbs/3d/left_pcb-3d.glb` and take **per-node transforms**
   (`scene.graph[node]`), *not* `scene.geometry[...].bounds` — those are model-local and rotated
   by the exporter; that is the source of the sign error above.
2. Establish up unambiguously: keycaps are the top (they reach ~10.9 on that axis, PCB top 1.51).
3. Measure the MCU + header stack on the **keycap side**, and the 2D extent of the tallest part.
4. Compare the stack top against the plate underside (**11.2**) and the case top (**11.2**), and
   the feet on the PCB against the switch cutouts' edges (the four cutouts start at y 59.5 on the
   PCB frame and the MCU keep-out reaches ~64.7 — that overlap is what makes the notch eat keys).
5. If the stack pokes above 11.2, an opening in the plate is not enough on its own: it needs a
   raised tower / window in the case too (same family of decision as B20 option C). Record the
   number before proposing anything.

---

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
