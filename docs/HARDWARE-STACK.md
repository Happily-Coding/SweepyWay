# HARDWARE-STACK — physical dimensions, heights, fasteners

Everything here is either (a) a value read out of `ergogen/config.yaml`, (b) measured from the
STEP models in `component_3d_models/`, or (c) the author's own measurement table. Each block is
labelled, because the three do **not** fully agree — see §4.

---

## 1. Declared in `config.yaml` (`units:`)

| Unit | Value | Used for |
|---|---|---|
| `case_wall_thickness` | 1.2 mm | case wall |
| `case_bottom_thickness` | 3 mm | case floor |
| `case_border_height` | 16 mm | wall height above the floor |
| `top_plate_thickness` | 1.6 mm → **must be 1.2** (D-11) | switch plate extrude in `l_cover`; see §4.0 |
| `internal_distance_between_plates` | 4 mm | **unused** (dead unit) |
| `bottom_plate_thickness` | 1.0 mm | **unused** (dead unit) |
| `controller_area_height` | 5 mm | controller housing above the plate |
| `controller_area_wall_thickness` | 2 mm | controller housing wall (cover = area expanded by 2) |
| `controller_area_roof_z_thickness` | 2 mm | roof on top of the controller housing |
| `screw_radius` / `screw_head_radius` / `spacer_radius` | 1.1 / 2.05 / 2.15 mm | M2 screws / heads / standoffs |
| `via_size` / `via_drill` | 0.56 / 0.3 mm | at JLCPCB minimums |
| `plate_kx` / `plate_ky` | **14.0 mm** (was 13.8) | switch plate cutout, V1+V2 compatible |
| `l_keys_outline.size` | `[plate_kx, plate_ky]` | **must not be halved** — `rectangle.size` is the full extent; halving it silently gives 7 mm holes (bug B10) |
| `kx`, `ky` | 17 / 17 mm | key pitch (CFX preset) |
| `keycap_x_1u` | 16.5 mm | assumed keycap size |
| `mcu_x` × `mcu_y` | 20.5 × 33.02 mm | controller bay sizing (17.78 + 2.72 pin offset) |
| `controller_sorrounding_x/y` | 50 × 30 mm | PCB area reserved around the MCU |
| `batc_x/y`, `batp_x/y`, `sw_power_x/y`, `sw_reset_x/y` | 4.3×4.6, 3.75×2.5, 3.1×8.3, 3.4×5 | footprint sizing helpers |

Case derivation (from the `outlines:` section):

```
l_case_bottom            = l_pcb_outline expanded 4 mm, minus 5 × ⌀2.2 holes
l_case_border            = l_case_bottom minus (l_pcb_outline expanded 2 mm)
l_usbc_border_outline    = 15 × 15 mm square at the controller centre
USB-C slot in the case   = that square, shifted [-20, 5, +3] and extruded 10 mm through the wall
l_cover / plate          = l_coverpart_switch_plate_outline (keys outline − key holes − screw holes)
                           extruded 1.6 mm, placed at z = 25 mm **for preview only**
l_controller_area*       = 50 × 30 rect → expanded 2 → minus itself = housing wall
```

## 2. Measured from the STEP models (PCB top surface = z 0, +z = up)

Read directly with trimesh. Useful for height budgets, **not** authoritative for mounting
heights: vendor models are exported with their own origins, so treat the *sizes* as reliable and
the *z placement* as approximate.

| Model | X × Y × Z (mm) | z range |
|---|---|---|
| `Choc_V1_Switch` | 15.00 × 15.00 × 11.00 | −2.95 … +8.05 |
| `Choc_V1_Hotswap` (socket, sits under the PCB) | 13.15 × 6.85 × 3.05 | −3.47 … −0.42 |
| `Choc_V1_Keycap_MBK_White_1u` | **17.45 × 16.45** × 5.52 | −1.50 … +4.02 |
| `Nice_Nano_V2` | 17.78 × 33.80 × 3.34 | −1.58 … +1.76 |
| `PinHeader_1x12_P2.54mm_Vertical` | 2.54 × 30.48 × 11.54 | −3.00 … +8.54 |
| `JSTPH2-S2B-PH-K-S-LF-SN` | 5.90 × 8.18 × 7.60 | 0.00 … +7.60 |
| `EVQ-PUC02K` (reset) | 6.40 × 4.50 × 2.44 | −0.49 … +1.95 |
| `SSSS811101` (power) | 7.70 × 1.90 × 5.00 | −2.20 … +2.80 |
| `D_SOD-123` | 3.80 × 1.60 × 1.25 | 0.00 … +1.25 |

Consequences worth knowing:

- **Hotswap socket is ~3.0–3.5 mm deep below the PCB.** The case floor must sit ≥ 3.5 mm below
  the PCB bottom face, or add cut-outs under the sockets.
- **MBK 1u is 17.45 mm wide.** At the CFX 17 mm pitch this overlaps the neighbouring cap — this
  is why MBK is *not* supported by the current spacing (D-2).
- **Pin headers (8.54 mm above PCB) are taller than the switch (8.05 mm).** Confirms the note in
  `component_3d_models/readme.md`. Anything sitting above the PCB must clear the headers, which
  is exactly why the controller lives in its own raised bay.
- The JST is 7.6 mm tall — the tallest part on the board. It lives on the separate 18 × 14 mm
  "jsph" tongue *outside* the keys area, so it does not have to fit under the switch plate, but
  it does have to fit under the controller housing/roof.

## 3. The author's own measurement table

`typematrix layup dimensions.ods` (raw, verbatim):

| layer | thickness (mm) | accumulated |
|---|---|---|
| Top | 1.3 | 2.3 |
| Space | 1 | |
| PCB | 1.3 | 3.05 |
| Hotplug | 1.8 | |
| Bottom | 1.6 | |
| **total** | **7** | 4.1 |

🟡 **BEST-GUESS interpretation**: this is a caliper measurement of an existing low-profile
sandwich — plate 1.3 mm, ~1 mm gap, **PCB 1.3 mm**, hotswap socket protrusion 1.8 mm, bottom
1.6 mm, total 7.0 mm. The accumulated column and the stray `4.1` only partially reconcile
(2.3 = 1.3 + 1; 4.1 = 2.3 + 1.8), so the exact reference planes are unknown.

**The one number to carry forward: PCB = 1.2 mm** (the measured 1.3 mm is a 1.2 mm board with
solder mask and measurement error). This matches the author's recollection of having decided to
"make the PCB a bit thinner" and matches choc hotswap socket practice (❓-2).

## 4. Conflicts and unvalidated assumptions ⚠️

### 4.0a The air gap is enforced by the SWITCH, not by the case (2026-11-16)

The 1.0 mm air gap and the plate↔PCB distance are self-enforcing: the switch latches into the plate
and its pins are gripped by the hot-swap socket that is peg-anchored to the PCB, so **plate +
switches + PCB form one rigid unit** and the switch body physically cannot seat at any other
spacing. The case therefore does not set this gap — `standoff_length` only sets how high the whole
unit floats above the case floor. Full reasoning, and what it removes from the fastener problem
(the top screw, and the "two screws through one bore" constraint), in
[`FASTENERS.md`](FASTENERS.md) §1–§2.

### 4.0 The choc plate rule (verified) — and why `top_plate_thickness` is wrong

Kailh PG1350 geometry (from the drawing reproduced in `daprice/keyboard_parts/parts.scad`):

```
        plate top surface ────────────────  0.0
        │ switch lower body 2.2 tall │      ── the plate lives in this band
        plate bottom ─── (plate thickness) ── 1.2 (steel) / ≤1.5 (FR4)
        air gap ──────────────────────────  1.0
        PCB top ─────────────────────────── −2.2
        PCB bottom ───── PCB thickness ────
        hotswap socket ~3 mm below PCB
```

Two hard numbers follow:

| Rule | Value | Consequence for this build |
|---|---|---|
| plate cutout | **14.0 mm** (D / ❓-1) | V1 clips with ~0.1 mm play, V2 clips properly |
| plate **top** surface above PCB **top** | **2.2 mm** | with a 1.2 mm plate ⇒ 1.0 mm air gap between plate and PCB (this is exactly the `Space 1` row in `typematrix layup dimensions.ods`) |
| plate **thickness** | **1.2 mm** (steel) / **≤1.5 mm** FR4 | **`top_plate_thickness: 1.6` is too thick**: the switch housing shoulders cannot seat, so switches sit high and may not register. Change to 1.2 mm (FR-4 order) for the printed plate too. |

This also resolves the "keycap clearance unverified" worry: the keycap skirt only has to clear
2.2 mm above the PCB top. CFX is 3.7 mm tall with its skirt well above that, MBK ~5.5 mm.

**Correction to §3:** the ODS table is now fully explained by the choc geometry — plate 1.3
(≈1.2 nominal + mask), gap 1.0, PCB 1.3, so the author was measuring a choc sandwich. The
`Hotplug 1.8` entry is the *socket protrusion below the PCB* as seen in that particular board
(our socket models measure ~3.0–3.5 mm, i.e. that board may have had the PCB flush or a recess).

1. ~~**The plate height is never actually defined in the pipeline.**~~ **FIXED 2026-11-16 (B17).**
   The rule is now *structural*, not implicit: `case_border_height` is a derived unit —
   `case_bottom_thickness + standoff_length + pcb_thickness + plate_top_above_pcb_top`
   (= 3 + 6 + 1.2 + 2.2 = **12.4** mm) — so the rim top *is* the plate top by construction, and the
   1.0 mm air gap below it follows from `plate_top_above_pcb_top: 2.2` minus `top_plate_thickness`.
   `l_cover` still places the plate at the preview offset `z = 25`; that remains a *preview-only*
   convention, not the physical height.
2. **`screws_top.standoff_height: 4` contradicts `standoffs.length: 6`.** They describe the same
   gap (plate ↔ PCB region). One of them is wrong; both feed the 3D preview, so the preview is
   inconsistent with itself.
3. **Left/right asymmetries in `config.yaml`** (each one is a latent bug):
   | param | left | right |
   |---|---|---|
   | MCU pin→row map | `R2,R3,R5,R4,R7,R6,R5` | `R2,R3,R4,R5,R5,R6,R7` |
   | `mcu_3dmodel_xyz_offset` | `[0,0,2.5]` | `[0,0,5]` |
   | `power.adjust.rotate` | 90 | 270 |
   | `screws_top.length` | 4 (+`model_xyz_offset`) | 5 (no offset) |
   | screws / standoffs / mounting holes | 5 sets | **none** |
4. **Keycap clearance is now bounded** (see §4.0): the plate top must be 2.2 mm above the PCB
   top, so any cap whose skirt sits higher than that clears. Still worth a test print, because
   `l_cover` places the plate at a *preview-only* z = 25 mm and no config value ties the plate to
   the PCB.
5. **`screw_offset_x = 0.4 kx` (6.8 mm) / `screw_offset_y = -0.2 ky` (-3.4 mm)** relative to the
   corner keys — note the `#TODO: aplicar offset adicional por screw minimo. porque no va a
   entrar asi, hay que buscar a la esquina posta. si no choca con switch` ("needs an extra offset
   or the screw will hit the switch"). Not resolved.

## 5. Fasteners (per half, currently left only)

Sandwich implied by the config: `bottom screw → case floor → press-fit standoff → PCB →
[screws_top params] → plate → top screw`.

| Part | Spec in config | Notes |
|---|---|---|
| Standoff ×5 | M2, 6 mm, splined press-fit (`92985A817/818` = 2 mm and 3 mm variants exist) | press into the printed case floor |
| Top screw ×5 | M2 low-profile socket head, 4 mm (right half says 5 mm) | through the plate into the standoff |
| Bottom screw ×5 | M2 low-profile socket head, 4 mm | through the case floor into the standoff |
| Mounting hole | ⌀2.2 mm NPTH (`hole_size = screw_diameter = 2 × 1.1`) | in PCB, plate and case floor |
| Coupling nut | `93020A101` M2 6 mm | 3D model present, purpose unclear 🟡 |

Shopping links for the hardware live in `shopping links/*.url` and the model sources in
`component_3d_models/readme.md`.

## 6. Clearances that matter when editing geometry

| Gap | Required | Source |
|---|---|---|
| PCB edge → case wall | ≥ 2 mm | `l_case_border` = base − (pcb + 2) |
| PCB edge → case outer | 4 mm | `l_case_bottom` = pcb + 4 |
| Under PCB → floor | ≥ 3.5 mm (hotswap socket) | measured §2 |
| Screw hole → switch body | ≥ 1 mm | unresolved TODO §4.5 |
| USB-C plug → wall | 15 × 15 mm opening, 10 mm deep | `l_usbc_border_outline` |
| Controller housing interior | 50 × 30 − 2 × 2 mm walls | `l_controller_area*` |
| Keycap → neighbouring keycap | ≥ 0 (CFX: 17 − 16.5 = 0.5 mm/side) | D-2 |

## 7. To validate with one test print (do this before ordering many)

1. One plate with 3 switch cutouts at the chosen `plate_k / plate_k` (13.8 vs 14.0, ❓-1).
2. A ~20 mm tall spacer stack: floor + standoff + PCB dummy (1.2 mm card) + plate, to check the
   keycap clearance gap (target: keycap skirt clearly below the plate).
3. One case corner with one screw hole, to check the screw→switch offset (§4.5).
4. One hotswap socket test-fit in the PCB coupon (socket should clip with a definite click and
   not rock at 1.2 mm).
