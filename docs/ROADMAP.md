# ROADMAP — the keyboard and the pipeline

Two tracks. The keyboard track is the critical path (nothing can be validated until it is built);
the pipeline track only gets work that the keyboard track needs, plus cheap wins that remove
toil.

---

## Track A — the keyboard (critical path)

### P0 — Make the current design manufacturable (days)
Blocks everything else.
- [ ] B1 fix the row→pin map (`R1..R5`), re-run `scripts/check_matrix.py` until PASS
- [ ] B2 make CI export the **routed** board; fail the build if routing produced nothing
- [ ] B4 mirror the screw points; register screws/standoffs on the right half
- [ ] B5 add `r_case_3d` / `r_cover`
- [ ] B6 repair the print files (`scripts/check_print_files.py` must PASS)
- [ ] B3/B7 decide the assembly scope (❓-6) and produce a real POS + BOM
- [ ] close ❓-1 (plate 13.8 vs 14.0), ❓-2 (PCB 1.2 vs 1.6), ❓-3 (finish)

### P1 — Test coupon + order (1–2 weeks, mostly waiting)
- [ ] one test print: plate coupon, stack spacer, case corner (`HARDWARE-STACK.md` §7)
- [ ] order 5 PCBs (+ assembly if ❓-6 says so), hardware, switches, keycaps, batteries
- [ ] flash + validate the matrix before final assembly (`ORDER-CHECKLIST.md` §5)

### P2 — First build + ergonomics (weeks)
- [ ] mechanical attachments: case ↔ tenting base (❓-4), palm rest (❓-5)
- [ ] print final case/cover/tenting/palm rest, assemble, type on it
- [ ] iterate on layout: stagger, splay, thumb cluster, tenting angle
- [ ] ZMK layer design (the actual point of the keyboard)

### P3 — v1.1 polish (opportunistic)
- [ ] adjustable / stackable tenting angles
- [ ] negative tilt option
- [ ] battery model + placement (enough room for a larger cell)
- [ ] travel case (see `../ultra cheap travel case solution keyboard.txt` / `../notas teclado.txt`)
- [ ] option: M1.6 screws (❓-9), reset button reachable with the cover on, drainage holes

---

## Track B — the pipeline

### B0 — Foundations (cheap, do alongside P0)
- [x] `scripts/regen.sh`, `scripts/check_matrix.py`, `scripts/check_print_files.py`
- [x] `.gitattributes` (kills the CRLF churn), `.env.example`
- [ ] one normalization commit for line endings (`git add --renormalize .`)
- [ ] CI gate: run `check_matrix.py` on the generated + routed boards
- [ ] publish BOM/CPL in the artifact so an order can be placed from Pages alone
- [ ] stop committing `filtered-output/` (publish via Pages, keep a release artifact)

### B1 — Make the config a *contract* (½–1 day, prerequisite for everything below)
Today `config.yaml` is one 1400-line file mixing layout, footprints, outlines and cases, with the
left and right halves duplicated by hand (that duplication is literally the source of bugs B1/B4).
Proposed shape:

```
keyboards/sweepyway.json      ← the only thing a human/UI edits
    layout:   { preset: column_stagger_7x5, thumb: fan3, stagger: {...}, splay: {...} }
    switch:   { family: choc, version: v1 | v2 | both, plate_cutout: 14.0 }
    keycaps:  { family: cfx | mbk, kx: 17, ky: 17 }
    mcu:      { kind: nice_nano, pins: { R1: P3, ... } }
    case:     { tenting: 6.5, palm_rest: true, screw: M2 }
    fab:      { pcb_thickness: 1.2, finish: hasl, assembly: [diodes, sockets] }
ergogen/config.yaml           ← generated, never hand-edited
ergogen/layouts/*.yaml        ← layout presets (column stagger, row stagger, …)
```

Deliverables: a `scripts/configure.py` (json → config.yaml), a JSON schema so a UI can be built
safely, and **one source of truth for the left/right symmetry** (generate the right half from the
left instead of duplicating blocks).

### B2 — Local, fast iteration without CI
- [x] **a local HTML configurator** that runs Ergogen + checks + STL generation (`docs/CONFIGURATOR.md`)
- [ ] a `just`/`make` target set that works on this machine (today `justfile` assumes Docker)
- [ ] KiCad/KiBot via Docker Desktop instead of WSL, wired into the same target
- [ ] cache `component_3d_models` + docker images locally

### B3 — Variant builds
- [x] output directory per configuration (`configurator/builds/<name>-<hash>/`) + `meta.json` manifest
- [ ] include the git sha / CI run id in the manifest so a local build can be traced to a commit
- [ ] `--dry-run`/`--preview-only` mode: ergogen + outlines + SVG previews in seconds, no kibot

### B4 — Auto-generated firmware
- [ ] generate the ZMK shield from `config.yaml`: `matrix_transform` from the row/column nets,
      `kscan` pins from the `promicro` params, a default keymap template
- [ ] matrix transform is exactly where an off-by-one like B1 becomes visible again, so it should
      be generated, never typed

### B5 — Documentation as a build output
- [ ] auto-fill `docs/BOM.md` quantities and the `docs/HARDWARE-STACK.md` measurement table from
      the generated PCB (`check_matrix.py --counts` already prints the raw data)
- [ ] render a per-build HTML "spec sheet" (layout image, BOM, gerber renders, print files)

---

## The configurator website — when?

**Question raised by the author:** a small site where you pick the parts/characteristics, it
writes a JSON, and a GitHub Action builds it — instead of the current "edit YAML → push → wait"
loop. Build it now, or later?

**Recommendation: not now. Do B1 (the JSON contract) instead, and build the site after v1 has
been built and typed on.** Reasoning:

1. **A website does not solve the problem it looks like it solves.** The stated pain is
   *iteration speed*. A site that dispatches a CI run is still a CI run (~7 minutes, a push, an
   artifact download). The thing that actually makes iteration fast is a *local* loop with
   previews (B2/B3: ~10 s for geometry). Build the loop first; then the site is a thin layer.
2. **The abstraction is not stable yet.** You are considering row-stagger, possibly MBK spacing,
   possibly a different MCU/plate. A UI built now would freeze today's (buggy) shape — including
   the left/right duplication that causes B1/B4. The JSON schema must come from *working*
   parameterization, not from a form.
3. **The schema is 80% of the work.** Once `keyboards/sweepyway.json` exists with a validator and
   a generator, "the website" is a form that emits that JSON plus a button. Cheap, and it becomes
   a weekend project instead of a rewrite.
4. **Free CI minutes make a hosted builder unnecessary for cost**, and a public form that can
   trigger builds needs auth/rate-limiting (a PAT in a static page is a leak). The safe, cheap
   v0.5 is: a static page that *generates the JSON* and links to the Actions **"Run workflow"**
   form with inputs — no token, no server, no security surface.
5. **Ergogen already runs fully in the browser.** Checked 2026-11-15: `ergogen.xyz` is
   "Ergogen Web GUI — design ergonomic keyboard layouts and generate PCB, DXF, and 3D model files,
   **fully offline**", and `runinit/ergogen-gui` is a lighter wrapper with live SVG previews.
   **But**: custom footprints do not work in the web build — an r/ErgoMechKeyboards author of a
   flat split hit exactly this ("the config makes heavy use of custom footprints, which don't work
   in the web version. I created a simplified version that you can use that runs in ergogen web").
   SweepyWay is built almost entirely from the `ceoloide` footprint submodule, so the browser can
   immediately do **layout + outlines + plate DXF + points**, and *cannot* do the PCB.
   That splits the future site cleanly in two:
   - **client-side (instant, offline):** layout editing, stagger/splay, outline + plate DXF,
     key/point preview, "does this fit my hands" — this is where 90 % of iteration happens;
   - **CI (minutes):** PCB footprints, routing, gerbers, POS/BOM, 3D.
   A page that renders the layout live and hands off a JSON to a workflow dispatch covers almost
   everything the author wants, with no server.
6. **What already exists, so don't rebuild it:** `ergogen.xyz` (config-only playground),
   `runinit/ergogen-gui` (SVG preview wrapper), Keyboard Layout Editor + SwillKB plate builder
   (layout → plate/case, no PCB), QMK Configurator / ZMK keymap editors (firmware only, the
   opposite end of the pipeline). None of them does "config → fab-ready keyboard files" as a
   hosted service, which is exactly the gap this project's pipeline fills.

**Concrete sequencing if you want to start early:**
1. B1 (schema + generator + right-half-from-left) — 1 day, valuable on its own.
2. A static "config builder" page that emits JSON + links to `workflow_dispatch` with inputs —
   ≤ 1 day, no server. Gets you "configure → build without a PR".
3. After v1 is validated: local SVG preview in the browser + per-variant artifact pages.

**On switching to a row-staggered layout:** do not restructure `config.yaml` yet. Run a
*spike* first (`ERGOGEN-GUIDE.md` §4.7): a throwaway config with the same `matrix` zone but all
`stagger: 0` plus per-row `key.shift`. If that produces a sane outline + plate, then the layout
becomes a *preset file* (B1), which is exactly what makes the website trivially useful later. If
it doesn't work in ergogen, the fallback is generating the point list from the JSON directly.
