# HANDOFF — 3D scene (`combined_scene.glb`) is still wrong

**Status: UNRESOLVED.** The scene generator `scripts/build_combined_scene.py` produces a file the author
rejects. Everything else in the repo (case/plate/PCB/hood geometry, gates, order-readiness) is separate
and in good shape — this document is only about the 3D scene.

Take this to a fresh session. Do **not** trust any "fixed" claim from the previous session; every one of
them was wrong (six in a row).

---

## 1. The reference the author accepts

| what | where |
|---|---|
| **Known-good scene** | **local file named `combined_scene(5).glb`** (author's copy; not in the repo) |
| Renders from it | smooth surfaces, no visible triangulation, at any zoom |
| Its generator | `create_full_3d_visual.py` (still in the repo root, unused by CI now) |
| Published copy of the same pipeline | `https://happily-coding.github.io/SweepyWay/combined_scene.glb` (13.2 MB, 154 meshes, nodes `Case`, `Cover`, `Palm_Rest`, `Tenting_System`, 17 materials) |

Note the reference is built from **legacy inputs**: `filtered-output/cases/case.stl` and `cover.stl` —
committed files that nothing regenerates, and a 16 mm case that is **not** the current design. It is a
*rendering* reference only, not a geometry reference.

## 2. What the author rejects

`filtered-output/combined_scene.glb` (repo) — 43.6 MB, 8 meshes, 848,643 verts, 5 materials:
`1-case_{left,right}`, `2-plate_{left,right}`, `3-pcb_{left,right}`, `4-tenting_system`,
`5-palm_rest`.

Symptoms, in the author's words, with the version each was reported against:

1. **v1–v3 (`bc1519a` and earlier)** — "triangles aren't fixed yet, mine isn't visibly faceted and yours
   clearly is": hard triangular facets on the tenting wedge, blotchy speckle across the green plate.
2. **v6 (`abd9c9f`)** — still wrong. New evidence: **clicking a part to select it makes the defect
   obvious.** In the author's screenshot the selected tenting base shows **long thin fan-shaped triangles
   across its top face and a striped/ribbed bottom edge**. This is the most useful observation in the
   whole thread — see §5.

## 3. Iterations already tried (all insufficient or wrong)

| # | change | commit | outcome |
|---|---|---|---|
| 1 | Replaced `create_full_3d_visual.py` (legacy inputs + magic `-90°` rotation + "PCB up 7") with `scripts/build_combined_scene.py`: real inputs, one explicit frame, coherence checks | `b432674` | correct geometry/stack, but the scene looked wrong |
| 2 | Per-part materials instead of one shared look; node names self-describing | `b432674` | helped inspection only |
| 3 | Tilt via node quaternion (6.5° about Z on case/plate/PCB/palm; tenting flat), copied from the reference file's node transforms | `bc1519a` | orientation now matches the reference; **not** the defect |
| 4 | `NORMAL` on every mesh (touch trimesh's lazy `vertex_normals`; carry PCB normals through `concatenate`) | `f77b673` | **not the cause** — see §4 |
| 5 | Lift the plate 20 µm in the scene only (its underside is exactly the wall-top plane = coplanar ⇒ z-fight) | `1e97e29` | plausible for the speckle, unproven |
| 6 | `clean()`: weld, drop zero-area/duplicate faces, renormalise, iterate; applied to every STL + PCB | `abd9c9f` | verts 1,608,593 → 848,643; degenerate 2,011 → 1,051; **author says still wrong** |

## 4. Ruled out, with evidence (do not re-investigate from scratch)

* **Missing NORMAL is NOT the cause.** The author's smooth reference has **no `NORMAL` on its four STL
  parts** (`Case`, `Cover`, `Palm_Rest`, `Tenting_System`) — proven by running `scripts/check_scene.py`
  against it. Found by an independent **codex** review, which refuted the previous session's hypothesis.
* **Index sharing is NOT the cause.** Both files: indexed, welded, verts/face = 0.50 for every STL part.
  Identical tenting mesh in both: 98,400 verts / 196,800 faces.
* **Material flags are NOT the cause.** Reference: 17 materials, `doubleSided: true`, `alphaMode: BLEND`,
  `baseColorFactor [r,g,b,0.4]`. Current build: same flags, 5 materials.
* **Alpha on vertex colours was** a real problem in an early build (a viewer that ignores `COLOR_0` shows
  everything opaque/white) — fixed by patching the exported GLB's materials (materials carry RGB+0.4).
* **`TextureVisuals`/`PBRMaterial` per mesh** caused genuine triangle soup (trimesh splits vertices
  per-face for those) — fixed by using vertex colours at build time and patching materials after export.
  This was a real bug, already fixed; it is not the current symptom.

## 5. Where to look next (the strongest lead, not yet tested)

The author's selected-part screenshot shows the **source triangulation** of the tenting shell: long thin
fan triangles across a nominally flat top, and ribbed/striped edges. Two competing explanations:

1. **Normal averaging across hard edges (introduced by `clean()`).** Welding fuses vertices that were
   deliberately split; `computeVertexNormals`/renormalisation then averages across creases, so a coarse
   fan triangulation becomes *visible* as smooth gradients where flat per-face shading previously hid it.
   Test: export the tenting **unwelded with per-face normals** vs **welded with averaged normals**, same
   camera, and compare. If unwelded+flat looks like the reference, `clean()` is the regression.
2. **The STL itself is coarse/oddly triangulated** and only *looks* fine in the reference because that
   build never welded it and the viewer shaded it flat. Test by rendering the raw STL in the viewer with
   and without welding, no other parts.

Whichever it is, this is a **per-part shading decision**, not a global one: an optics-quality answer may be
"flat normals for the tenting/palm rest, smooth for the case/plate".

Also unresolved: the blotchy speckle on the green **plate** (present in v1–v3). Candidates: coincident
faces (plate underside ≡ wall top — addressed by the 20 µm epsilon but unverified), and the PCB's
`*_fab_preview` components overlapping real geometry.

## 6. How to verify (this is the part that failed six times)

**Verify with pixels in the author's own renderer, never with geometric properties alone.**

Use Orca's **embedded browser** (NOT Computer Use — its skill explicitly excludes Orca's browser):

```bash
orca tab create --url "https://3dviewer.net/#model=https://raw.githubusercontent.com/Happily-Coding/SweepyWay/main/filtered-output/combined_scene.glb?v=N"
orca goto   --url "<same>"            # reload after a push
orca eval   --expression "(function(){const c=document.querySelector('canvas');const r=c.getBoundingClientRect();for(let i=0;i<10;i++)c.dispatchEvent(new WheelEvent('wheel',{deltaY:-480,clientX:r.left+r.width/2,clientY:r.top+r.height/2,bubbles:true,cancelable:true}));return 'ok';})()"
orca screenshot --format png --json    # → copy result.path out of the Windows temp dir and read it
```

Notes learned the hard way:
* `orca scroll` does **not** reach the WebGL canvas — dispatch `WheelEvent` via `orca eval`.
* The tab title bar in the middle of the screenshot shows the loaded file name; that is how the author and
  I tell the files apart (`combined_scene.glb` = ours, `combined_scene(5).glb` = his).
* The author inspects by **clicking a part to select it** — do the same, or hide meshes via the panel, to
  see one part in isolation. `orca eval` can walk the panel (`DIV` rows are named exactly like the nodes).
* Serving requires a push (raw.githubusercontent), or use `orca upload` on the viewer's file input with a
  local path.

Independent second opinion (worked well, found the refutation): the `ask-model` skill, codex.
Two traps on this machine:
* `codex.sh` needs a `node` on PATH — this box only has `node.exe`; `mkdir -p /mnt/c/tmp/bin && ln -sf "$(which node.exe)" /mnt/c/tmp/bin/node` then `export PATH=/mnt/c/tmp/bin:$PATH`.
* `-m gpt-5.5` is rejected ("not supported with a ChatGPT account") — omit `-m`.
* `-C` needs a **Windows** path: `-C "C:/a/IRL Products/Keyboard design/SweepyWay"` (`/mnt/c/...` → os error 3).
* Scripts live in `/mnt/c/Users/uriel/.agents/skills/ask-model/scripts/` (not `~/.Codex/...`).

## 7. Files that matter

```
scripts/build_combined_scene.py   # the generator (the subject)
scripts/check_scene.py            # gate over the GLB: alpha/BLEND, node tilt, welding, NORMAL presence
scripts/build_plate_stls.py       # export3d/plate_*.stl from the outlines (they were stale/hand-made)
scripts/repair_stl.py             # weld/clean for the STL export path
create_full_3d_visual.py          # the OLD generator = the look the author accepts
filtered-output/combined_scene.glb            # current output (rejected)
filtered-output/cases/{l,r}_case_3d.stl       # case incl. controller hood (z 0..20.08)
filtered-output/cases/tenting_system.stl      # tenting base, 196,800 faces
filtered-output/palmrest/palm_rest.stl        # palm rest (authored overlapping the case on purpose)
export3d/plate_{left,right}_full.stl          # FR4 plate 1.20 mm
filtered-output/pcbs/3d/{left,right}_pcb-3d.glb   # PCB + switches + keycaps (43,865 component nodes)
docs/img/ORDER-*.png                          # renders from the failed attempts
```

## 8. What NOT to redo

* Do not re-litigate NORMAL/indexing/materials — §4 has the numbers.
* Do not "fix" the tenting/palm-rest **placement**. The reference file's node quaternions are the spec:
  case/plate/PCB/palm rest **6.5° about Z**, tenting **identity**. The palm rest is authored overlapping
  the case footprint on purpose; a previous session "corrected" that and was wrong.
* Do not change `check_scene.py` tolerances to make it pass.
* Do not claim a fix without a screenshot of the author's viewer at high zoom, ideally with a single part
  selected.
