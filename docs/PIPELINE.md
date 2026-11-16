# PIPELINE — how the keyboard gets built

This is the second product of the repo. The pipeline is **CI-first**: GitHub Actions runs the
dockerised tools, and its output is committed/published to GitHub Pages. Local runs are possible
for the ergogen/OpenJSCAD/trimesh stages only (no Docker from WSL on this machine).

---

## 1. The build graph

```
                        ergogen/config.yaml  +  ergogen/footprints/**
                                     │
                    (1) npm run build │  node/Run in CI, ./scripts/regen.sh locally
                                     ▼
        ergogen/output/{pcbs,outlines,cases}  ──► points/, source/canonical.yaml (debug)
                    ┌────────────────┼─────────────────────┐
                    ▼                ▼                     ▼
        (2) kibot default     (4) export_dsn.py      (9) openjscad CLI
            gerbers+drill       → <board>.dsn           cases/*.jscad → *.stl
            images (pcbdraw)          │
                    ▼                 ▼
        filtered-output/pcbs/   (5) freerouting      (10) create_palmrest.py
            gerbers/ images/     .dsn → .ses               │
                                      │                    (11) create_tenting_system.py
                                      ▼                        │
                          (6) import_ses.py → *_autorouted.kicad_pcb
                                      │                        ▼
                                      ▼              filtered-output/{palmrest,cases}/*.stl
                          (7) kibot boards  ◄── DRC + gerbers + images
                                      │
                    (3) kibot 3d_preview (STEP/STL/GLB + 3D renders)
                    (8) kibot jlpcb_pos  (→ empty today!)  (8b) fix_pos_package_name.py
                    (12) kibot jlpcb_bom (→ ergogen/output/bom, never published)
                    (13) kibot pdf
                                      ▼
                    (14) fix_glb_scale.py   (m → mm)
                    (15) create_full_3d_visual.py → combined_scene.glb
                                      ▼
                      filtered-output/ (directory listing + Pages + artifact)
```

## 2. What each artifact is for

| Artifact | Consumer |
|---|---|
| `pcbs/gerbers/<board>.zip` (gerbers + drill) | JLCPCB PCB order |
| `pcbs/cad/*.kicad_pcb` | inspection / manual routing; **must contain `*_autorouted`** |
| `pcbs/pos/*/*.pos`, `*-jlcpcb.pos` | JLCPCB CPL (currently empty) |
| `pcbs/images/*.png` | quick visual check of copper/silk, README |
| `pcbs/pdfs/*.pdf` | **print the layout on paper and feel it** (a beginner-friendly feature) |
| `pcbs/3d/*.step/.glb/.stl` | 3D verification, CAD exchange |
| `cases/*.jscad`, `cases/*.stl` | printing the case/cover (via OpenJSCAD) |
| `palmrest/palm_rest.stl`, `cases/tenting_system.stl` | printing |
| `combined_scene.glb` | the "does everything fit" preview |
| `outlines/*.dxf` | laser cutting plates, and the input to the trimesh scripts |

## 3. GitHub Actions (`build.yaml`)

Trigger: `workflow_dispatch`, or `push` to a **path-filtered** list: `.github/workflows/*.yaml`,
`.github/actions/*/action.yaml`, `ergogen/footprints/*.js`, `ergogen/config.yaml`, `kibot/*`,
`freerouting/*`, `package.json`, `*.nix`, `palmrest_and_tenting_creation/*.py`,
`create_full_3d_visual*.py`.

> **Trap**: the filter does not include `.gitmodules`, `scripts/`, `docs/`, `README.md`, so a
> submodule-pointer-only commit (like `e36e9d5`, the current HEAD) never builds.

Steps: checkout (with submodules) → npm install → `npm run build` → kibot `default` →
export DSN → freerouting → import SES → kibot `boards` → kibot `3d_preview` → kibot `pdf` →
copy to `filtered-output` → kibot `jlpcb_pos` → POS post-process → kibot `jlpcb_bom` →
copy jscad → OpenJSCAD docker → `uv sync` → palm rest → tenting → `fix_glb_scale` →
`create_full_3d_visual` → directory listing → upload artifact + Pages.

## 4. Docker images used

| Image | Used by | Purpose |
|---|---|---|
| `ghcr.io/inti-cmnb/kicad9_auto:latest` | kibot action, export-dsn, import-ses | KiBot + KiCad 9 CLI |
| `ceoloide/ergogen-freerouting:latest` | autoroute action | FreeRouting CLI wrapper |
| built from `openjscad/Dockerfile` | jscad→stl | OpenJSCAD CLI |

Local equivalents in `build.sh`, `justfile`, `preview.sh`, `run_kibot.bat` use
`setsoft/kicad_auto:ki8` (KiCad 8) — **stale**; the CI uses the kicad9 image. Prefer the CI.

## 5. ⚠️ Known pipeline bugs (read before trusting any output)

1. **The kibot action always exports the unrouted board.**
   `.github/actions/kibot/action.yaml` runs
   `kibot -b $GITHUB_WORKSPACE/ergogen/output/pcbs/${board}.kicad_pcb`, and `build.yaml` passes
   `boards: left_pcb right_pcb, config: boards` "for the autorouted board". Consequently:
   gerbers, DRC and 3D all come from the **unrouted** file, and `*_autorouted.kicad_pcb` is never
   used. Verified: the published board has **0 segments, 0 vias**; the gerbers contain no
   `Conductor` apertures; the drill file has only 3 tool sizes (no 0.3 mm via drill).
   **Fix**: pass a full board path (or a `suffix` input, e.g. `_autorouted`) and fail the job if
   the routed file is missing.
2. **Freerouting failure is silent.** Each step is guarded by `if [ -e … ]`, so a missing `.dsn`
   or `.ses` just skips and the build still goes green.
3. **DRC is meaningless as a gate.** `boards.kibot.yaml` sets `ignore_unconnected: true`
   ("auto-routing doesn't always connect all traces") and filters `track_width`,
   `hole_clearance`, `solder_mask_bridge`, `shorting_items`, `copper_edge_clearance`,
   `lib_footprint_issues`. The February 2026 reports show `0 errors (+244 excluded)`, of which
   **105 were `unconnected_items`**. Do not treat green DRC as manufacturable.
4. **BOM never reaches the published output.** `jlpcb_bom.kibot.yaml` writes to
   `ergogen/output/bom/`, and the copy step only syncs gerbers/images/pdfs/pos/outlines/cases.
   Plus `*.csv` is gitignored.
5. **POS covers 2 of 196 placements** (see B3 in `STATUS.md`): the CPL contains only
   `PWR1` and `RST1`. Diodes have no `attr` at all, switches have no `smd` flag, and the hotswap
   sockets are virtual footprints with no pads.
6. **`filtered-output/` is manual-ish**: the older docs (`latest-3d-model-issues.md`) state it was
   downloaded by hand at some point. Treat it as a CI cache, not an authority.

## 6. Local build (no Docker) — what you can and cannot do

| Stage | Local? | How |
|---|---|---|
| ergogen (PCB, plate, outlines, cases) | ✅ | `./scripts/regen.sh` |
| jscad → STL | ✅ | `npx @jscad/cli ergogen/output/cases/l_case_3d.jscad -of stla -o out.stl` |
| palm rest / tenting | ✅ | `./.venv/Scripts/python.exe palmrest_and_tenting_creation/create_*.py` |
| GLB scale fix + combined scene | ✅ | `fix_glb_scale.py`, `create_full_3d_visual.py` |
| checks (`check_matrix.py`, `check_print_files.py`) | ✅ | any of the above |
| STL repair (`repair_stl.py`) | ✅ | `./.venv/Scripts/python.exe scripts/repair_stl.py x.stl` |
| the whole geometry+print loop, with UI | ✅ | `node configurator/server.mjs` (see `docs/CONFIGURATOR.md`) |
| gerbers / drill / POS / BOM / DRC / 3D | ❌ (docker) | CI, or Windows Docker Desktop |
| freerouting | ❌ (java + docker) | CI |

So the tight local loop is *geometry*; anything electrical/fabrication-shaped has to go through a
CI run (~7 minutes) or a Docker Desktop shell.

## 7. The configurator (local, no Docker)

`configurator/` runs stages 1–4 of this graph from a browser: it generates `config.yaml` from a
JSON config, runs Ergogen, runs the two check scripts, and converts the cases + palm rest +
tenting base to STL. It is the fast local loop; layer 6 (gerbers/routing/POS) stays in CI.
Details and limits: `docs/CONFIGURATOR.md`.

## 8. Improving the pipeline (see also `ROADMAP.md`)

- Make the kibot action take an explicit board path; make the job fail if routing or DRC
  preconditions are not met.
- Publish the BOM/CPL in the artifact so an order can be placed from the Pages site alone.
- Add `scripts/check_matrix.py --routing` as a CI gate.
- Replace the `filtered-output` commit-churn with a release artifact.
