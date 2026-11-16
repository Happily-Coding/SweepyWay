# ERGOGEN-GUIDE — how `ergogen/config.yaml` is organised

Enough to make a change without breaking the two halves. Read
[`KEYBOARD-REFERENCE.md`](KEYBOARD-REFERENCE.md) for the domain vocabulary.

Ergogen 4.1.0, docs at <https://docs.ergogen.xyz/> (the config's `#` comments also link to
useful reference keyboards). Locally: `./scripts/regen.sh`.

---

## 1. Section map

```
meta:        engine version, name, version (v0.2), url      (the url is silk-printed on the PCB)
presets:     choc_spacing (kx17 ky18, MBK caps), cfx_spacing (kx17 ky17, CFX caps)
units:       $extends: presets.cfx_spacing  +  every physical constant of the build
points:      the anchor geometry (where things go)
  key:         the key point *template* (padding/spread/width/height + mirror tags)
  zones:       matrix, thumbfan, controller_center, {l,r}_jsph_area_center,
               {l,r}_controller_area_center, l_screw_{left_top,left_bottom,right_top,
               right_bottom,thumb}
outlines:    every 2D shape, built by adding/subtracting other outlines
pcbs:        plate_left, plate_right, left_pcb, right_pcb  (outline + footprint list)
cases:       l_case_3d, l_cover, l_3d_preview  (extrusions of outlines)
```

## 2. Units and presets

`units: $extends: presets.cfx_spacing` pulls in:

| from preset | value | meaning |
|---|---|---|
| `kx` | 17 | horizontal key pitch |
| `ky` | 17 | vertical key pitch |
| `keycap_x_1u` / `keycap_y_1u` | 16.5 / 16.5 | assumed keycap size |
| `px` / `py` | 5 / 5 | PCB padding around each key rectangle |
| `plate_kx` / `plate_ky` | 13.8 | plate cutout (**V1 only**, ❓-1) |
| `vertical_diode_shift` / `horizontal_diode_shift` | 1.5 / −7.75 | diode placement |
| `diode_rotation` | 0 | added to the 90° base rotation |

`presets.choc_spacing` is the MBK variant (ky 18, caps 17.5 × 16.5). Switching between them is
a one-line change **plus** the outline and plate consequences — see §4.5.

Everything else in `units:` is project-specific mechanical/electrical constants. They are all
listed with their consumers in [`HARDWARE-STACK.md`](HARDWARE-STACK.md) §1.

## 3. Points, zones and mirroring (the part that confuses everyone)

- A **point** is `[x, y, r]`. Outlines and footprints are anchored to points by name or by tag.
- `zones.matrix.columns.col1..col7` × `rows.row1..row5` generates keys named
  `matrix_col<N>_row<M>`. Per-column `key.stagger` gives the column stagger; per-key `skip: true`
  removes a cell.
- `zones.thumbfan` is anchored to `matrix_col6_row4` with `rotate: -10`, then 3 keys with
  `spread: kx` and `splay` −15°/−5° → `thumbfan_col{1,2,3}_thumb_row_1`.
- **Mirroring**: each zone can declare `mirror:`. The mirrored copy gets the `mirror_` name prefix
  and the tags in `points.key.mirror.tags` (here `key` + `rightkey`). Left keys are tagged
  `key` + `leftkey` explicitly via `key.tags` inside the zone.

| zone | mirror | result |
|---|---|---|
| `matrix` | `distance: 340` | right matrix 340 mm to the right of the left one |
| `thumbfan` | `ref: matrix_col6_row4, distance: 100` | right thumb fan |
| `controller_center` | `ref: matrix_col4_row1, distance: 165` | `mirror_mcu` |
| `l_jsph_area_center` | none (an `r_` twin is declared by hand) | |
| `l_controller_area_center` | none (an `r_` twin is declared by hand) | |
| `l_screw_*` | **none** | ⇒ **no `right_screw` points exist** (bug B4) |

So: the left and right halves are both present on the same KiCad sheet, 340 mm apart, and each
`pcbs:` entry selects one half's outline.

### Point filter syntax (used in `where:` and in outlines)

```yaml
where:
  - [ leftkey ]                 # single filter: has tag leftkey
  - [/^mirror.*/, key, -1_5u, -space]   # AND: name starts with mirror, tagged key,
                                        #      not 1.5u wide, not tagged space
  - /rightcluster_.*/           # regex on the point name (matches nothing today: dead filter)
```
Rules: `where:` is a **list = OR**; a nested list is **AND**; `-x` negates tag/key/property;
`/regex/` matches the point name.

## 4. Recipes

### 4.1 Add or remove a key
- Remove: set `skip: true` under `matrix.columns.col<N>.rows.row<M>`.
- Add: remove an existing `skip`, or add a new `col<N>`/`row<M>`.
- Auto-updates: `l_key_based_board_outline` (built from `leftkey` rectangles), the switch/diode/
  socket/keycap footprints, and `l_keys_outline` (plate cutouts).
- **Does not** auto-update: `l_thumb_suplementary_outline` (hardcoded shifts), the
  `l_hand_rest_overlapping_polygon` point list, `l_screw_*` anchors, and the
  `controller_center` anchor (it references `matrix_col4_row1`).
- Always: re-run `scripts/check_matrix.py` afterwards.

### 4.2 Wire a new row or column to the MCU
Add the net name to the `promicro` `params` **in both `left_pcb` and `right_pcb`** (`P<n>: "R<m>"`).
One pin per row/column net, no duplicates, no invented nets — `check_matrix.py` enforces all
three. Currently 7 columns (C1..C7) need 7 pins and 5 rows (R1..R5) need 5 pins; P10/DPD/DPC/DPE
are the only sensible spares left (P0..P2 are reserved for nice!view).

### 4.3 Add a screw point (this is bug B4)
Copy the `l_screw_*` zones and give the mirror counterparts. The cleanest fix is to add
`mirror: {ref: <corresponding matrix ref>, distance: 340}`-style mirroring to each `l_screw_*`
zone and then register `screws`/`standoffs`/`screws_top`/`screws_bottom` in `right_pcb`
(`where: right_screw`). `r_screws_outline` and `plate_right` already reference `right_screw`, so
they start working as soon as the points exist.

### 4.4 Add the right case (bug B5)
`r_case_bottom` and `r_case_border` already exist. Add:

```yaml
  r_case_3d:
    - name: r_case_bottom
      extrude: case_bottom_thickness
    - name: r_case_border
      extrude: case_border_height
    - name: r_usbc_border_outline
      extrude: 10
      shift: [-20, 5, case_bottom_thickness]
      operation: subtract
```
…mirroring the *sign* of the x/rotate adjustments of `l_case_3d` (the USB slot must end up on the
outside of the right half). Same for `r_cover`. Then `scripts/check_print_files.py` and an STL
bbox comparison against the left one.

### 4.5 Switch keycap family (CFX ⇄ MBK)
```yaml
units:
  $extends: presets.cfx_spacing   # → presets.choc_spacing for MBK
```
MBK needs `kx: 17.5` or more (cap is 17.45 wide) — the preset says `kx: 17` / `ky: 18`, which is
already wrong for MBK in X. Expect: outlines change (the key-based outline follows `kx`/`ky`),
plates change, the hand rest polygon shifts, and the screw offsets (`0.4 kx`, `−0.2 ky`) move.
Treat it as a layout change, not a toggle.

### 4.6 Change the plate cutout (❓-1)
`plate_kx` / `plate_ky` in `presets.choc_spacing` (inherited by `cfx_spacing`). V1-only = 13.8,
V1+V2 = 14.0. Affects `l_keys_outline` → both plates. Re-print a coupon before ordering plates.

### 4.7 Column stagger vs row stagger — both work (source-verified)

Ground truth is `node_modules/ergogen/src/points.js` (v4.1.0), not the docs. Two facts decide
everything:

**(1) Per-cell config is a 6-level merge** (`points.js` ~104-111):

```
default_key → global points.key → zones.<zone>.key → zones.<zone>.columns.<col>.key
            → zones.<zone>.rows.<row> → zones.<zone>.columns.<col>.rows.<row>
```

`rows.<row>` and `columns.<col>.rows.<row>` are merged **as key properties directly** — they are
*not* wrapped in `key:`:

```yaml
rows:
  r2:
    shift: [4, 0]          # ✅ works
  r3:
    key: {shift: [4, 0]}   # ❌ silently ignored (becomes a bogus "key" property)
```

**(2) Keys are laid out against a running anchor** (`points.js` ~164-190):

```js
running_anchor = column_anchor
for (key of rows, in yaml order) {
  point = running_anchor
  point.shift(key.shift)          // relative to the PREVIOUS row's position
  running_anchor = point          // commit
  running_anchor.shift([0, key.padding])
}
```

…and the column loop does `zone_anchor.y += keys[0].stagger` per column, so `stagger` is also
cumulative *column to column*.

| property | level it applies at | accumulates | use it for |
|---|---|---|---|
| `padding` | row | down the rows | row pitch (`ky`) |
| `shift` | row | **row → row** (delta) | **row stagger** |
| `orient` / `rotate` | row | row → row | fanning |
| `stagger` | column (read from `keys[0]`) | **column → column** (delta) | **column stagger** (what this board uses today) |
| `spread` | column (read from `keys[0]`) | column → column | horizontal pitch (`kx`) |
| `splay` | column | column → column | thumb fan |

Measured with spike configs (all reproducible in ~1 min):

| config | result |
|---|---|
| `rows: r1:{}, r2:{shift:[4,0]}, r3:{shift:[4,0]}` | x = 0, 4, 8 → per-row deltas accumulate ✅ |
| `columns.c1.key.stagger: 5`, `columns.c2.key.stagger: 5` | columns at y = 5, 10 → cumulative ✅ |
| `columns.c1.rows.r3: {shift: [2,0]}` on top of a `+4` row delta | that one key lands at +6 (per-cell override replaces the row delta) ✅ |
| `rows.r2: {stagger: 5}` | **no effect** — `stagger` is only read from `keys[0]` |

**So a row-staggered variant needs no transposing and no generated point list:**
1. set every `columns.<c>.key.stagger` to 0 (drop the column stagger),
2. add `rows.<r>.shift: [<delta>, 0]` per row (the delta, not the absolute offset),
3. use `columns.<c>.rows.<r>.shift` for the odd cell that needs an exception.

The key-based outline follows automatically because it is generated from key rectangles. What
still needs review after such a change: the thumb anchor (`matrix_col6_row4`), the controller
anchor (`matrix_col4_row1`), `l_thumb_suplementary_outline` and the hand-rest polygon, which all
carry hardcoded refs/shifts.

(Generating explicit `points:` remains the better long-term target for a JSON-driven pipeline —
see `ROADMAP.md` B1 — but it is no longer *required* just to switch stagger styles.)

## 5. Footprints used (all `ceoloide/*` except the two local files)

| config key | footprint | role | key params |
|---|---|---|---|
| `choc` | `switch_choc_v1_v2` | switch + hotswap pads | `side: B`, `hotswap: true`, `choc_v2_support: true`, `include_keycap`, `keycap_width/height 16.5`, `model_filename` |
| `choc_hotswap` | `hs-socket-fab-preview_choc_v1_v2` | **virtual** (3D/BOM only, no pads) | `side: B`, `model_filename`, `do_not_populate: ''` |
| `choc_keycap` | `keycap-fab-preview_choc_v1_v2` | virtual keycap preview | `do_not_populate: 'DNP'` |
| `choc_space` | `switch_choc_v1_v2` | 1.5u space key | **matches nothing today** (no `space` tag, and `keycap_x_space` is undefined) |
| `diode` | `diode_tht_sod123` | SOD-123 SMD pads | `side: F`, `include_tht: false`, `from: {{colrow}}`, `to: {{row_net}}` |
| `promicro` | `mcu_nice_nano` | MCU + pin map | `reverse_mount`, `include_extra_pins`, `P<n>: net`, model offsets |
| `header_left/right` | `header-preview_nano` | virtual 12-pin header preview | `pin_count: 12`, `model_xyz_offset: ±7.62`, `do_not_populate: DNP` |
| `pads_bat` | `battery_connector_jst_ph_2` | JST PH | `model_filename` (**param name differs from the others** — no `connector_3dmodel_*` prefix) |
| `reset` | `reset_switch_smd_side` | EVQ-PUC02K | `side: F`, `from: GND`, `to: RST`, `include_bosses` (false → GLB mesh issue) |
| `power` | `power_switch_smd_side` | SSSS811101 | `side: F` |
| `screws` | `mounting_hole_npth` | ⌀2.2 NPTH | `hole_size`/`hole_drill` = `screw_diameter` |
| `standoffs` | `standoff-preview` | virtual standoff | `screw_diameter: m2`, `length: 6`, `do_not_populate: DNP` |
| `screws_top/bottom` | `screw-preview-top/bottom` | virtual screws | `length`, `head_type`, `standoff_height`, `plate_thickness` |
| `jlc` / `url` | `utility_text` | silk text (JLC order-number trick, repo URL) | |

**Virtual footprints** add nothing to the PCB — they only contribute 3D models, BOM and POS
entries. That is why `hs-socket-fab-preview` cannot be used to have JLC place sockets (❓-6).

## 6. Debugging ergogen

- `npm run debug` (or `./scripts/regen.sh --debug`) writes the preprocessed source to
  `ergogen/output/source/canonical.yaml` — the fastest way to see what a `$extends` or a variable
  actually resolved to.
- `ergogen/output/points/units.yaml` and `points.yaml` list every resolved point and unit.
- Undefined variables do **not** error: they silently become the literal string. After any edit,
  `grep -i nan ergogen/output/pcbs/*.kicad_pcb` and `scripts/check_matrix.py` catch the fallout.
