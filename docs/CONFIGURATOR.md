# CONFIGURATOR — the local web app

A localhost web app that edits a **JSON description** of the keyboard and then runs the *real*
repo pipeline on it: Ergogen → plates → checks → OpenJSCAD/trimesh print files → 3D viewer.

It is deliberately not a second implementation of anything. If the site shows a number, that
number came out of `ergogen`, `scripts/check_matrix.py` or `scripts/check_print_files.py`.

```
node configurator/server.mjs          # then open http://localhost:5173
```

> Run it from Windows (or from WSL with `node.exe`). Under WSL, `node` is not on PATH and the
> server must be reachable as a Windows process — `curl` from *inside* WSL cannot reach it, a
> browser on Windows can.

---

## 1. Why localhost and not a hosted site

Checked 2026-11-15: `ergogen.xyz` runs Ergogen fully in the browser ("generate PCB, DXF and 3D
model files, fully offline"), **but custom footprints do not work in that build** — an
r/ErgoMechKeyboards author hit exactly this ("the config makes heavy use of custom footprints,
which don't work in the web version"). SweepyWay is built almost entirely from the `ceoloide`
footprint submodule, so a browser build can render layout + outlines + plate DXF and *cannot*
produce the PCB.

That splits the problem cleanly:

| Layer | Where | Latency | What it gives you |
|---|---|---|---|
| 1. config → YAML | server (JS) | ~0 ms | reviewable `config.yaml`, validation errors |
| 2. YAML → geometry | server (`ergogen`) | ~10 s | PCB/plate/outlines/cases, key points |
| 3. checks | server (python) | ~0.2 s | matrix/pin/net validation, plate cutout sizes |
| 4. print files | server (openjscad + trimesh) | ~2 s | case, cover, tenting base, palm rest STLs |
| 5. view | browser (three.js) | instant | orbit/zoom the STLs, click through previews |
| 6. fabrication (gerbers, routing, POS/BOM) | CI only | ~7 min | the stuff that needs Docker/KiCad |

Layers 1–5 are what a configurator is for. Layer 6 stays in CI (see `docs/PIPELINE.md`).

## 2. The JSON contract

`configurator/lib/schema.mjs` is the authority. A config looks like:

```jsonc
{
  "name": "sweepyway",
  "switch":  { "family": "choc", "support": "v1+v2", "hotswap": true },
  "spacing": { "kx": 17, "ky": 17, "keycap": "cfx" },
  "layout": {
    "rows": ["row5","row4","row3","row2","row1"],      // bottom-first, like the YAML
    "columns": [
      { "name": "col1", "net": "C1", "stagger": 0, "spread": null, "splay": 0,
        "cells": ["row4","row3","row2","row1"] },       // which rows exist in this column
      ...
    ],
    "rowStagger": null,                                 // or ABSOLUTE x offsets per row, mm
    "thumb": { "enabled": true, "count": 3, "rotate": -10, "spread": 17, "splay": [-15,-5] }
  },
  "case":     { "bottomThickness": 3, "borderHeight": 16, "wallThickness": 1.2 },
  "palmRest": { "enabled": true, "height": 10, "curve": 3 },
  "tenting":  { "enabled": true, "angle": 6.5, "zMin": 3, "hollow": 10, "includePalmRest": false },
  "fab":      { "plateThickness": 1.2, "pcbThickness": 1.2 }
}
```

Rules that the validator enforces (`validate()` in `schema.mjs`):

- keycap must fit the pitch (`kx >= cap.width + 0.4`), otherwise caps collide;
- plate cutout must fit the pitch;
- every column needs at least one cell;
- **no two keys may share a (column net, row net) pair** — that is the classic matrix collision;
- enough MCU pins for rows + columns.

Warnings (not errors): plate thicker than 1.5 mm (choc ceiling), PCB thinner than 1.0 mm with
hotswap, thumb cluster disabled.

## 3. What the generator does (`lib/generate.mjs`)

The repo's `ergogen/config.yaml` stays the single source of truth for everything that is *not*
parameterised (outlines, cases, footprint wiring). The generator reads it and replaces only:

1. the `presets:` block (kx, ky, keycap size, plate cutout),
2. the whole `points:` block (columns/rows/thumb/controller/screws),
3. a handful of scalars: plate thickness, case dimensions, keycap size, `choc_v2_support`,
4. both `promicro` pin maps — **auto-assigned**, so a generated config can never repeat the
   off-by-one that left row `R1` unwired in the hand-written file,
5. point references inside the `outlines:` section (retargeted only when the layout actually renames
   them; a reference that cannot be resolved **throws** rather than snapping the polygon to the
   wrong key — see `docs/CONFIGURATOR-DRIFT.md`, B22).

Every splice is asserted: if the canonical file stops looking the way the generator expects, it
throws instead of emitting something broken.

**Equivalence check** (how it is validated now): `node scripts/check_config_drift.mjs` regenerates
`presets/sweepyway.json` **in memory**, parses both documents and compares them structurally;
comments/key order are ignored and ergogen expressions are evaluated, so `0.25 ky` == `4.25`. It is
step 3/4 of `scripts/pre-push.sh` and the `config-drift` CI job, so a configurator run can no longer
silently revert a hand-fix. Proof it is exact: ergogen's output for the committed `config.yaml` and
for the generated one are **byte-identical** (50 outlines, 4 pcbs, 3 cases).

## 4. Generated-config fixes vs the hand-written file

Historically the generated config was *better* than `ergogen/config.yaml`: it assigned the row pins
(B1), defined the right half's `r_screw_*` twin points (B4) and unified the MCU 3D offset. **All
three are now in the committed file too**, so a generator run is a no-op instead of a "fix" — that
is what `scripts/check_config_drift.mjs` enforces (B22, `docs/CONFIGURATOR-DRIFT.md`). The one
thing the generator still leaves alone is the left/right `mcu_3dmodel_xyz_offset` asymmetry
(2.5 vs 5): it is a committed value, so unifying it would itself be drift.

Still true and worth knowing: the generator **derives** `case_border_height` from the stack (B17)
and writes `standoff_body_length` from the JSON (F3b), so the two values that make the case and the
fasteners consistent can never be hand-edited into disagreement with the JSON.

## 5. Endpoints

| Route | Purpose |
|---|---|
| `GET /api/presets` | every `configurator/presets/*.json` |
| `POST /api/validate` | `{config}` → `{errors, warnings, normalized, keys, plateCutout}` |
| `POST /api/build` | `{config, stages:["geometry","prints"]}` → per-stage `{ok, ms, log, errors, data}` + SVG list |
| `GET /builds/<slug>/…` | generated files (config.yaml, meta.json, STLs, PCBs, SVGs, DXFs) |
| `GET /` | the UI |

Builds are content-addressed (`<name>-<sha1(config)[0:8]>`) and cached in
`configurator/builds/<slug>/`, which is gitignored. Re-running the same config reuses the
workspace (footprint junction, old outputs) and overwrites.

## 6. Presets

`configurator/presets/sweepyway.json` is the keyboard in this repo (auto-selected on load, since
the UI prefers the preset named `sweepyway`). It is the **only** preset that round-trips: it is the
one `scripts/check_config_drift.mjs` (and therefore CI) holds to the committed `config.yaml`.
`minimal-3x5.json` (3 columns × 4 rows + 3 thumbs, MBK caps at 18 mm pitch) is the layout-shape
test, but since B22 the generator **refuses** it with a readable error: the canonical `outlines:`
section hardcodes 7-column/5-row point names (`matrix_col7_row2`, `thumbfan_col3_*`) that a 5-column
layout does not have, and silently snapping those polygons to another key produced wrong geometry
before. Authoring per-preset outline references is the fix, and it is not done yet.

`row-stagger-1u.json` is the "normal keyboard" variant: **no column stagger, no thumb fan, all 1u
keys**, standard row stagger of 0.25u (4.25 mm at a 17 mm pitch) applied as absolute offsets
`[17, 12.75, 8.5, 4.25, 0]` bottom→top. 34 keys/half (7 columns of 5 rows, minus the top key of
the last column). Verified: `x` steps 35 → 52 mm monotonically, and both halves get 34 choc +
34 socket + 34 diode footprints.

> **`rowStagger` semantics**: values are *absolute* x offsets, in `layout.rows` order. Ergogen's
> own `shift` is cumulative (each row's value is a delta against the previous row), which is a
> footgun — `generate.mjs` converts absolute → delta for you. Authoring `[0, 4.25, 8.5]` by hand
> in the YAML silently produces 0 / 4.25 / 12.75.

To add a preset: drop a JSON file in `configurator/presets/` — it appears in the dropdown. The UI
can also export the current state as JSON ("Download JSON") and load one back.

## 7. Print-file pipeline

| File | Produced by | Notes |
|---|---|---|
| `assets/l_case_3d.stl` | Ergogen `.jscad` → OpenJSCAD → `scripts/repair_stl.py` | CSG leaves 3 coplanar T-junctions; the repair welds/orients, the checker reports them as a warning |
| `assets/l_cover.stl` | same | watertight; **Ergogen exports it at the preview offset z=25**, so `repair_stl.py --drop-to-bed` is now always applied (a slicer would otherwise need "drop to bed" by hand) |
| `assets/tenting_base.stl` | `create_tenting_system.py --angle --z-min --hollow` | watertight, positive volume (was inverted before 2026-11-15) |
| `assets/palm_rest.stl` | `create_palmrest.py --height --curve` | watertight (mesh rebuilt from a constrained triangulation) |

`create_palmrest.py` and `create_tenting_system.py` now take CLI arguments, so the configurator
can vary the palm-rest height/curve and the tenting angle/height/wall without touching code.
Their defaults are unchanged, so CI keeps working.

### Verifying the shape, not just the file

`scripts/check_print_files.py` answers "will a slicer take this file". Two more layers:

- `scripts/inspect_print_model.py` — cuts the model at given heights and counts closed loops
  (geometry-level "is the shape right").
- `scripts/render_stl.py` + `scripts/check_render.py` — renders orthographic top/front/iso PNGs
  with matplotlib (no GL) and then *measures the pixels*: fill fraction, number of islands, number
  of see-through holes, mirror symmetry. This is "look at it" done numerically, and it is the only
  way to catch a rendering bug — see the note below.

### Checking artifacts against *each other* (`check_assembly.py`)

Per-file checks cannot see the failures that matter most: cutouts that miss the switches, screw
holes that are not coaxial between the PCB, the FR4 plate, the printed cover and the printed case,
or a matrix wired one way on 31 keys and another way on the 32nd. `scripts/check_assembly.py`
parses the KiCad PCB + plate (real S-expression parser — a regex parse silently returned (0,0) for
every switch because KiCad puts `(tstamp ...)` between `(layer ...)` and `(at ...)`), the Ergogen
DXFs and the printed STLs, registers them onto PCB coordinates through the five screw holes using
an order-independent transform, then measures:

```bash
./.venv/Scripts/python.exe scripts/check_assembly.py \
    --cases configurator/builds/<slug>/assets
```

It reports 20 checks (wiring, cutout alignment, cutout size, screw coaxiality, screw-vs-cutout
clearance, cover coverage). It found B13/B14 in `docs/STATUS.md` on its first run.

**Rendering trap**: VTK/vedo was tried first and abandoned. `Plotter.show()` re-aims the camera, so
every "top" view silently rendered as a 3/4 view; `reset_camera()` re-aims it *again* after you set
it. The tell is that the rendered silhouette's aspect ratio no longer matches the mesh bounding box
(a 140.6 × 142.8 mm case came out 872 × 434 px). The current renderer projects the triangles itself,
so the check below is exact.

```bash
./.venv/Scripts/python.exe scripts/render_stl.py out/ assets/*.stl --views top,front,iso
./.venv/Scripts/python.exe scripts/check_render.py out/*-top.png
```

Self-validating readings (2026-11-15, rendered 1400 × 1400 px):

| File | render px | aspect | mesh aspect | err | holes seen from above |
|---|---|---|---|---|---|
| `l_case_3d` | 1232 × 1250 | 0.986 | 0.985 | 0.10 % | **5** = the five M2 screw holes |
| `l_cover` | 1230 × 1250 | 0.984 | 0.984 | 0.02 % | **32** = the switch cutouts |
| `tenting_base` | 1232 × 1250 | 0.986 | 0.985 | 0.05 % | **1** = the hollow interior |
| `palm_rest` | 1250 × 740 | 1.689 | 1.693 | 0.22 % | 0 = solid |

Do not pass `--title` when a render will be measured: the label itself is foreground and inflates
the mask bounding box (that is what made the palm rest read 1.59 instead of 1.69).

```bash
./.venv/Scripts/python.exe scripts/inspect_print_model.py build/assets/l_case_3d.stl \
    --slices 1.5,3.2,10,14
```

Expected readings for the current keyboard (2026-11-15):

| File | z | loops | meaning |
|---|---|---|---|
| `l_case_3d` | 1.5 | 6 | floor: outer perimeter + **5 screw holes** |
| `l_case_3d` | 3.2 / 10 | 1 | wall band, open where the **USB-C slot** cuts it |
| `l_case_3d` | 14 | 2 | closed wall ring above the slot |
| `l_cover` | 0.5 | 34 | plate: perimeter + **32 switch cutouts** + controller bay |
| `tenting_base` | 0.2 / 3.5 | 2 | hollow: outer wall + inner wall |
| `palm_rest` | 5 | 1 | solid ramp cross-section |

`bodies` should be 1 for everything (the case reports 3: the real body plus two zero-volume CSG
slivers from coplanar T-junctions).

## 8. UI

- **Left panel**: switch family + plate compatibility, keycaps and pitch, the layout grid (tick
  which cells exist; per-column stagger/spread/splay; optional row-stagger deltas; thumb
  cluster), case, palm rest, tenting, fabrication.
- **Right panel**: build stages with logs and errors, metric cards, SVG previews (key positions,
  PCB outline, switch plate, case bottom, hand rest, tenting), a three.js STL viewer with a
  button per file, and links to every artifact.
- Two buttons: **Generate geometry** (stages 1–3) and **+ print files** (adds stage 4). Both
  stream their stages into the timeline as they finish.

three.js is loaded from a CDN via an import map. Offline, the viewer degrades to a message and
the STL links still work.

## 9. Known limits / next layers

- **Only the `sweepyway` preset round-trips** (B22). Other presets need per-preset outline point
  references; until then the generator fails loudly instead of emitting an outline snapped to the
  wrong key. The drift gate (`scripts/check_config_drift.mjs`) checks the default preset only.
- Not yet exposed: **per-key width** (the model is 1u only — a 1.5u/2u spacebar is not expressible
  from the UI yet; see §10), row-level `shift` UI per cell (the model supports `cells`, not per-cell
  offsets), keycap profile choice beyond size, controller type (nice!nano only), screw scheme
  (M2 only), per-key `asym`/mirroring.
- No gerbers/routing/POS from the app — by design, that is CI (`docs/PIPELINE.md`).
- No persistence beyond the content-addressed build dir; "Download JSON" is the save mechanism.
- The layout preview is the *Ergogen output*, not a client-side approximation, so it costs one
  Ergogen run (~10 s). A cheap client-side sketch could be added later for drag-level
  responsiveness.

## 10. Adding a non-1u key (spacebar) — what it would take

Everything is 1u today, and the Lily58 guide confirms 1u thumb keys are a normal choice. A wider
key is *not* a config change; it needs five coordinated edits:

1. **Points**: give the key `width: 1.5` (ergogen multiplies by `u`), and make sure the column's
   `spread` accounts for the extra width or the neighbouring column collides.
2. **Footprint filter**: the left switch footprint currently matches `[leftkey]`, which would also
   match the wide key and emit a *second* switch on top of it. It needs `[leftkey, -space]`, and the
   canonical `choc_space` footprints need `[leftkey, 1_5u]` / `[rightkey, 1_5u]` — they currently use
   `-1_5u`, i.e. the negation of what was intended.
3. **Keycap**: `keycap_x_space`/`keycap_y_space` are referenced by those footprints but undefined in
   `points.key`; a 1.5u CFX is 24.75 mm wide (16.5 mm × 1.5), a 2u is 33 mm.
4. **Plate**: the cutout must grow by the width difference *only in X*, otherwise the switch won't
   seat; for 2u choc you also need stabiliser cutouts (1.5u does not).
5. **Firmware/matrix**: the wide key still occupies exactly one matrix position, so nothing changes
   electrically — but `check_matrix.py --counts` must expect 31 + 1 wide cells, not 32.

None of this is implemented; `row-stagger-1u.json` is the 1u answer, and a 1u space works fine on a
32-key hand-wired-since layout (it is what the 1.5u thumb keys on the Lily58 degrade to).
