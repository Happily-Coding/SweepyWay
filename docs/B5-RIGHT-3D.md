# B5 — the right half now has generated 3D parts

Evidence report, 2026-11-17. Everything below was executed in this worktree, not recalled.
Reproduce with:

```bash
node.exe node_modules/ergogen/src/cli.js ./ergogen/ --output ./ergogen/output --clear
for f in l_case_3d l_cover l_3d_preview r_case_3d r_cover r_3d_preview; do
  node.exe node_modules/@jscad/cli/cli.js ergogen/output/cases/$f.jscad -of stla -o C:/tmp/b5/stl/$f.stl
done
./.venv/Scripts/python.exe scripts/check_print_files.py C:/tmp/b5/stl/*.stl   # (pass the files, not a glob)
./.venv/Scripts/python.exe scripts/check_assembly.py --cases C:/tmp/b5/stl
```

## 1. Audit — every `r_*` outline, and whether a mirror is valid

Method: read the DXF linework (lines, arcs, circles, polylines), mirror the **right** outline about
`x = 170` (the axis derived from the key outlines: `(xmin_r + xmax_l)/2 = (xmax_r + xmin_l)/2 = 170.0000`
to 0.0000 mm) and compare it to the left with the Hausdorff distance plus the length of linework
with no counterpart within 0.01 mm. `MIRROR` = both are 0.

| outline pair | exists | empty? | mirror verdict | max deviation |
|---|---|---|---|---|
| `l_all_key_clusters_outline` / `r_…` | both | no | **MIRROR** | 0.0000 mm |
| `l_key_based_board_outline` / `r_…` | both | no | **MIRROR** | 0.0000 mm |
| `l_key_based_board_outline_with_extra_padding` / `r_…` | both | no | **MIRROR** | 0.0000 mm |
| `l_keys_outline` / `r_…` | both | no | **MIRROR** | 0.0000 mm |
| `l_coverpart_switch_plate_outline` / `r_…` | both | no | **MIRROR** | 0.0000 mm |
| `l_screws_outline` / `r_…` | both | no | **MIRROR** | 0.0000 mm |
| `l_standoff_bosses` / `r_…` | both | no | **MIRROR** | 0.0000 mm |
| `l_case_bottom` / `r_case_bottom` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_case_border` / `r_case_border` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_case_border_do_not_ocupy` / `r_…` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_pcb_outline` / `r_pcb_outline` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_cover_outline` / `r_cover_outline` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_controller_area` / `r_…` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_controller_area_cover` / `r_…` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_controller_area_border` / `r_…` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_jsph_area` / `r_…` (+ `_cover`, `_border`) | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_usbc_border_outline` / `r_…` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_tenting_base_bottom_outline` / `r_…` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_tenting_base_border_outline` / `r_…` | both | no | mirror ± controller bay | **3.0000 mm** |
| `l_controller_area_to_cover_outline` / `r_…` | **left only → added** | was missing | mirror ± controller bay | 3.0000 mm |
| `l_controler_area_to_not_fill` / `r_…` | **left only → added** | was missing | mirror ± controller bay | 4.3023 mm (the `expand: -2` ring where the 3 mm bay meets the key cluster) |
| `l_thumb_suplementary_outline` / `r_…` | both | no | **NOT a mirror** | 3.8634 mm, and the right has 7 vertices vs 9 |
| `l_hand_rest_overlapping_polygon` / `r_…` | both | no | **NOT a mirror** | 81.35 mm |
| `l_hand_rest_polygon` / `r_hand_rest_polygon` | both | no | **NOT a mirror** | 91.26 mm |

No outline is empty (no B16-style silently-empty geometry). Every 3.0 mm row has **one** cause and
one only: `points.zones.mcu.mirror.distance: 165` puts the MCU mirror axis at **x = 168.5**, while
the keys mirror about **x = 170** (`matrix` distance 100, `thumbfan` 120+100/2 — both agree).
Measured: left MCU at x 81.75, right MCU at **255.25**, true mirror **258.25** → the right MCU, its
controller bay (`222.25…272.25` vs `225.25…275.25`), the JST area and the USB-C footprint are all
**3.0 mm toward the mirror seam**. That is a property of the *right PCB* (it is generated from
`r_pcb_outline`), so the generated right parts are correct for the board that will be manufactured,
and a slicer-mirrored left case is the thing that would be 3 mm out. **Not fixed here**: changing
`mirror.distance` would move the already-verified right PCB (B4/B13), so it is a separate decision.

### 3D assembly blocks that needed a right twin

| left block | needs | existed before | now |
|---|---|---|---|
| `l_case_3d` (`l_case_bottom`, `l_standoff_bosses`, `l_case_border`, `l_usbc_border_outline` − slot) | `r_case_3d` | **no** | added |
| `l_cover` (`l_coverpart_switch_plate_outline`, `l_controller_area_to_cover_outline`, `l_controler_area_to_not_fill`, roof) | `r_cover` | **no**, and 2 of its 3 outlines were missing too | added (outlines + block) |
| `l_3d_preview` | `r_3d_preview` | **no** | added |
| tenting base | right tenting base | printed by `palmrest_and_tenting_creation/create_tenting_system.py`, which hardcodes `l_tenting_base_bottom_outline.dxf` | **not done** — see §5 |
| palm rest | right palm rest | printed by `create_palmrest.py` from `l_hand_rest_polygon.dxf` | **not done** — see §5 |

## 2. What changed

| file | change |
|---|---|
| `ergogen/config.yaml` | +2 outlines (`r_controller_area_to_cover_outline`, `r_controler_area_to_not_fill`); +3 case blocks (`r_case_3d`, `r_cover`, `r_3d_preview`); B21 residue `length: 4` → `length: screw_bottom_length` in `right_pcb.r_screws_bottom` |
| `scripts/check_assembly.py` | new right-hand fit checks (right PCB ↔ `r_screw` DXF ↔ `r_cover.stl` ↔ `r_case_3d.stl`); `stl_section()` now reports the **bbox centre** (the vertex mean drifted up to 6 mm on a triangulated square ring) and the **minimum-rotated-rectangle** size (a 14 mm cutout reads 19.1 mm axis-aligned under 30° splay — HANDOFF §8 trap 2); the controller bay is no longer counted as a key opening |
| `docs/STATUS.md`, `docs/HANDOFF.md` | B5 marked fixed, the "there is no `r_case_3d`" trap replaced with the 3 mm caveat |

Left geometry is provably untouched: regenerating from `git show HEAD:ergogen/config.yaml` gives
`l_case_3d.jscad`, `l_cover.jscad`, `l_3d_preview.jscad` **byte-identical** (md5 `9124ea49…`,
`15a04590…`, `1c66a5b7…`), all 25 pre-existing `l_*`/`r_*` DXFs byte-identical, `left_pcb` and both
plates byte-identical. The only other changed artifact is `right_pcb.kicad_pcb`, and only where the
B21 fix rewrites the 5 bottom screw previews: `Screw Length` **4 mm → 6 mm**, model
`…_m2_4mm` → `…_m2_6mm`, i.e. now identical to the left.

## 3. The new artifacts

`.jscad` (what ergogen writes) and the STL rendered from it with `@jscad/cli -of stla`:

| artifact | `.jscad` bytes | STL bytes | triangles | watertight | volume | bbox (mm) |
|---|---|---|---|---|---|---|
| `r_case_3d` | 16 147 | 939 195 | 4 580 | **yes, outward normals** | **52.923 cm³** | 140.612 × 142.799 × 12.400 |
| `r_cover` | 15 866 | 669 427 | 3 986 | **yes, outward normals** | **8.923 cm³** | 132.617 × 134.804 × 7.000 |
| `r_3d_preview` | 29 819 | 1 530 194 | 8 174 | **yes, outward normals** | **77.816 cm³** | 140.612 × 142.799 × 28.000 |

Nothing is empty: every file is 6–7 orders of magnitude above 0 bytes, and the mesh checks are on
real solids (4.5k–8.2k triangles, positive signed volume, `check_print_files.py` PASS).

### Mirror comparison against the left counterparts

| pair | vol left | vol right | Δvol | area Δ | bodies | watertight L/R | mirrored bbox error |
|---|---|---|---|---|---|---|---|
| `l_case_3d` / `r_case_3d` | 52.832 cm³ | 52.923 cm³ | **+0.172 %** | +0.149 % | 3 / 5 | no (3 coplanar T-junctions, pre-existing B6) / **yes** | **0.0000 mm** |
| `l_cover` / `r_cover` | 8.832 cm³ | 8.923 cm³ | **+1.030 %** | +0.546 % | 1 / 1 | yes / **yes** | **0.0000 mm** |
| `l_3d_preview` / `r_3d_preview` | 77.694 cm³ | 77.816 cm³ | **+0.156 %** | +0.152 % | 5 / 4 | no / **yes** | **0.0000 mm** |

`mirrored bbox` = `2·170 − x` of the left bbox compared with the right bbox, on all six numbers.

Exact slice test (`symmetric_difference` area of mirrored right section vs left section):

| part | z | area L | area R | symdiff | where |
|---|---|---|---|---|---|
| case | 1.50 | 14 079.7 mm² | 14 110.3 mm² | 137.31 mm² (0.98 %) | (120.2, −45.3) |
| case | 3.00 / 4.00 | 1 157.3 | 1 157.2 | 141.17 mm² | (64.2, −52.x) |
| case | 6.00 / 10.00 | 1 107.3 | 1 107.2 | 141.17 mm² | (92.0, −35.8) |
| case | 12.00 | 1 141.5 | 1 141.4 | 202.64 mm² | (120.8, −45.5) |
| cover | 25.50 / 26.00 | 4 675.5 | 4 681.5 | 171.45 mm² (3.67 %) | (68.8, −46.5) |
| cover | 26.50 / 28.00 (bay walls only) | 276.6 | 282.6 | 171.45 mm² | (68.8, −45.2) |
| cover | 31.00 (roof) | 1 085.4 | 1 116.0 | 137.16 mm² | (116.3, −50.4) |
| preview | 26.00 (plate only) | 4 398.9 | 4 398.9 | **0.00 mm²** | — |

Every deviation lands in the controller-bay band, i.e. exactly the 3.0 mm of §1; the parts are an
exact mirror everywhere else (identical areas to 0.1 mm² on the floor, the wall band and the key
plate).

### Cross-artifact fit (`check_assembly.py --cases`, both halves)

```
ok  printed cover has exactly 1 controller bay opening   1 opening at plate level
ok  printed cover has its 5 screw holes                  5 screw-sized openings
ok  cover registers onto PCB (screw holes)               residual 0.000 mm, flip=fy
ok  printed cover covers every switch                    32/32 covered, worst 0.000 mm
ok  cover openings ~14.0 mm                              sizes [(14.0, 14.0)]  (min-rect)
ok  case registers onto PCB (screw bosses)               residual 0.000 mm
ok  case screw bosses coaxial with PCB holes             worst 0.000 mm
ok  right: 32 switches + 5 mounting holes                32 switches, 5 mounting holes
ok  right: screw outline registers onto right PCB        residual 0.000 mm, flip=fy
ok  right: printed cover has exactly 1 controller bay opening
ok  right: printed cover has its 5 screw holes
ok  right: cover registers onto right PCB (screw holes)  residual 0.000 mm
ok  right: printed cover covers every switch             32/32 covered, worst 0.000 mm
ok  right: cover openings ~14.0 mm                       sizes [(14.0, 14.0)]
ok  right: case has 5 screw holes in its floor           5 closed openings at z=1.5
ok  right: case registers onto right PCB (screw bosses)  residual 0.000 mm
ok  right: case screw bosses coaxial with PCB holes      worst 0.000 mm
```

`inspect_print_model.py` on the right case: 1 contour + **5 holes** at z=1.5 (floor + bosses),
6 contours + 5 holes at z=3.2 (wall band, cut open by the USB-C slot, + 5 boss rings), 1 contour +
0 holes at z=6 and z=10 (wall only, i.e. the slot really is through) — the same signature as the left.

## 4. Gates

```
scripts/check_assembly.py                    PASS
scripts/hardware_bom.py --no-write           exit 0
scripts/check_matrix.py                      PASS  (0 failures; L/R parity ok)
node.exe scripts/check_config_drift.mjs      B22 gate: PASS  (generator reproduces config.yaml)
```

`check_assembly.py --cases C:/tmp/b5/stl` also PASSes with both halves' STLs present. The
configurator needs no change: `stageCases()` renders every `cases/*.jscad` except `*3d_preview`, so
`r_case_3d.stl` and `r_cover.stl` appear in `assets/` automatically.

## 5. What could NOT be mirrored, and why

1. **Right palm rest.** `r_hand_rest_polygon` is not the mirror of `l_hand_rest_polygon` (91.26 mm
   Hausdorff, 207 mm of left-only linework). The cause is one vertex: the right polygon's third
   point is `mirror_thumbfan_col1_thumb_row_1` where the mirror demands
   `thumbfan_col1_thumb_row_1`. Fixing it changes the right palm-rest outline only, and
   `create_palmrest.py` still hardcodes the `l_` DXF, so it is a separate change (and a wrong
   mirrored palm rest would be worse than none).
2. **Right tenting base.** The `r_tenting_base_*` outlines *are* valid right parts, but the printed
   tenting base is not an ergogen case — `create_tenting_system.py` builds it from
   `l_tenting_base_bottom_outline.dxf` + `l_hand_rest_polygon.dxf` with a 6.5° tilt and pockets. It
   needs a `--side r` flag there; emitting a flat `r_tenting_base` case would produce a
   plausible-looking but wrong part.
3. **Exact mirror of the case/cover.** Blocked by the 3.0 mm MCU/bay offset described in §1, which
   lives in the right PCB. The generated right parts match the real right PCB; the left/right
   volume delta (+0.17 % / +1.0 %) and the slice deltas above are entirely that offset.

## 6. Remaining asymmetry between the halves (preview-only, not changed)

- `right_pcb.r_screws_top` has no `model_xyz_offset: [0,0,-1.25]` while `left_pcb.screws_top` does,
  so the right top screw renders 1.25 mm higher in the 3D preview. Preview only, no printed part.
- `r_thumb_suplementary_outline` is not a mirror (7 vertices vs 9) and is unused — it is commented
  out of both `*_all_key_clusters_outline`.
- Neither `*_3d_preview` shows the F3b bosses (pre-existing deferred item, HANDOFF §0); the right
  preview mirrors the left exactly, so the halves stay comparable.
