# TROUBLESHOOTING — 3D previews and 3D exports

This consolidates what used to be spread over `latest-3d-model-issues.md`,
`plans/3d-merge-issue-documentation.md`, `plans/test-3d-merge-variants.md`,
`plans/fix-pcb-rotation-and-switch-positioning.md`, `plans/tenting-components-alignment.md`
and `debugging/`. Those files are kept for history; **this** is the current picture.

---

## 1. What the 3D pipeline actually does

```
CI: kibot 3d_preview.kibot.yaml
      ├── %f-3d.step            (STEP, full assembly)          → filtered-output/pcbs/3d/
      ├── %f-3d.stl             (STL, low resolution)
      ├── %f-3d-misscaled.glb   (GLB with materials, metres!)   ← KiCad exports mm, glTF wants m
      └── %f-3d-top/bottom.png  (render_3d, used in the README)

fix_glb_scale.py → %f-3d.glb    (scale 0.001 applied to the root node)

create_full_3d_visual.py (the "v11 hybrid")
   1. loads the *PCB* GLB with pygltflib so the scene graph survives
      (nodes keep their names: S25, HS8, K8, MCU1, …)
   2. builds a GLB from the STL parts with trimesh (Case, Cover, Palm_Rest), rotating
      each −90° about X to match the PCB's orientation
   3. concatenates the two binary buffers, offsets bufferViews/accessors/mesh indices,
      and re-parents the STL nodes into the PCB scene
   4. applies the tenting angle (6.5°) to everything except the tenting base itself
   5. shifts the PCB up (+7 on Y after rotation) and the cover down (−12) to line up
   6. writes filtered-output/combined_scene.glb
```

Why this is convoluted: every simpler approach was tried first (§3).

## 2. Known-open issues

| # | Symptom | Hypothesis | Next test |
|---|---|---|---|
| 1 | **JST (`JST1`) missing entirely** from both STEP and GLB (no node at all) | Not the same bug as #2/#3. Suspects, in order: the footprint's param is `model_filename` (not `connector_3dmodel_filename`), the model file itself, or a path-resolution quirk. The JST sits on the separate 18 × 14 "jsph" island, so it is also the only footprint placed there — worth checking that the area/pcb actually contains it | `grep -i jst left_pcb.kicad_pcb`; try swapping in another `.step`/wrl; try an absolute path |
| 2 | **MCU present in STEP but meshless in GLB** (node `MCU1`, `mesh: None`) | Node exists without geometry → something in the footprint's model block or the export filter | See #4 |
| 3 | **Reset switch same as #2** (`RST1`) | Same class as #2 | See #4 |
| 4 | **NPTH correlation (working theory)** | Every footprint that exports fine to GLB either is virtual (no pads) or has **mandatory NPTH holes** (choc switch, power switch). The two broken ones have none (MCU) or have them **disabled by default** (`include_bosses: false` in `reset_switch_smd_side`) | Set `include_bosses: true` on `reset` in **both** halves and re-export. If the reset switch then appears, the theory holds and the MCU needs cosmetic NPTH added to its footprint |
| 5 | Tenting base/case/palm rest misaligned in the combined scene | The preview applies a −90° X rotation + 6.5° tenting rotation with hand-tuned Y offsets (+7 PCB, −12 cover) — these are magic numbers, not derived | Compare bounding boxes numerically instead of visually (`scripts/check_print_files.py` prints them) |

Evidence collected for the NPTH theory (from the footprints, not from docs):

| footprint | attr | NPTH | GLB |
|---|---|---|---|
| `power_switch_smd_side` | smd | 2 mandatory | ✅ |
| `switch_choc_v1_v2` | exclude_from_pos_files | 3+ mandatory | ✅ |
| `header-preview_nano` | — (virtual, no pads) | none | ✅ |
| `standoff-preview` / `screw-preview-*` | — (virtual) | none | ✅ |
| `reset_switch_smd_side` | smd | optional, **default false** | ❌ |
| `mcu_nice_nano` | through_hole | none | ❌ |
| `battery_connector_jst_ph_2` | through_hole | none | ❌ (different symptom) |

## 3. The eleven variants that were tried (results are real, keep them)

| variant | approach | position | orientation | object structure |
|---|---|---|---|---|
| v1 baseline | iterate `scene.geometry.items()` | ❌ | ❌ | ❌ |
| v2 graph transforms | `graph.get(node)` + `apply_transform` | ✅ | ✅ | ❌ fragmented |
| v3 scene merge | `scene.to_mesh()` | ✅ | ✅ | ❌ all merged |
| v4 graph edges | iterate `graph.edges` | ✅ | ✅ | ❌ fragmented |
| v5 re-export | export → reimport | ✅ | ✅ | ❌ all merged |
| v6 scene transform | transform whole scene, then extract | ❌ | ❌ | ❌ |
| v7 preserve structure | `add_geometry(transform=…)` | ✅ | ✅ | ❌ fragmented |
| v8 copy graph | `graph.update` | ✅ | ✅ | ❌ fragmented |
| v9 scene add | `scene + scene` | ✅ | ✅ | ❌ fragmented |
| v10 pygltflib | load + re-export GLB | ✅ | ✅ | ✅ **but STL parts missing** |
| **v11 hybrid** | pygltflib for the PCB + trimesh for the STLs, merge buffers | ✅ | ✅ | ✅ | ← current |

**Lesson**: the only thing that preserves KiCad's named node hierarchy is pygltflib (or another
glTF-native library). Anything that goes through trimesh geometry lists destroys the structure
(fragments or merges). If v11 needs replacing, replace the *merge* step, not the loading step.

## 4. How to inspect a GLB without a GUI

```bash
./.venv/Scripts/python.exe - <<'EOF'
import pygltflib
g = pygltflib.GLTF2().load("filtered-output/pcbs/3d/left_pcb-3d.glb")
print("nodes:", len(g.nodes), "meshes:", len(g.meshes))
missing = [n.name for n in g.nodes if n.mesh is None]
print("nodes without mesh:", missing[:40])
print("has JST:", [n.name for n in g.nodes if n.name and "JST" in n.name.upper()])
EOF
```

`verify_all_components.py` does a cruder version of this (searches the binary for strings) and is
kept because it was useful when pygltflib was not installed.

## 5. Unit scale

KiCad's glTF export is in millimetres, glTF's convention is metres, so `combined_scene.glb` comes
out 1000× too big in most viewers. `fix_glb_scale.py` applies `0.001` to the root node of each
PCB GLB and writes the correctly-named `*-3d.glb`. If a model looks "enormous" or "invisible"
depending on the viewer's camera, this is why.

## 6. Local iteration

The PCB GLB/STEP can only be produced by KiBot (CI or Docker Desktop). Everything downstream of
them (scale fix, merge, STL checks) runs locally:

```bash
./.venv/Scripts/python.exe fix_glb_scale.py --verbose
./.venv/Scripts/python.exe create_full_3d_visual.py
./scripts/check_print_files.py
```

Practical shortcut: commit the STL/GLB you want to iterate on into `filtered-output/` (that is
what the repo already does) so the local merge can be run without a CI round trip.

## 7. Known-unrelated annoyances

- `filtered-output/*.stl` files above the gitignore threshold are excluded, so some outputs exist
  in CI artifacts but not in the repo.
- `create_full_3d_visual.py` reads `cases/case.stl` and `cases/cover.stl`, which are *copies* of
  `l_case_3d.stl` / `l_cover.stl` (same triangle counts) — a leftover from the OpenJSCAD era.
  If the case geometry changes, make sure the copies are refreshed or point the script at the
  `l_*` files directly.
- `debugging/readme.md` warns its scripts have stale paths (they were moved out of the root).
