#!/usr/bin/env python3
"""Gate the *published* snapshot (``filtered-output/``) before it can ship.

`filtered-output/` is not produced by a single tool: CI uploads an artifact zip and the author
unpacks it into the repo folder, and the workflow copies with `rsync -a` (no `--delete`). Nothing
ever removes a file. That is exactly how B14 happened — a folder holding the PCB/plate from one CI
run and the outlines/case STL from an older run, with a printed cover whose key openings sit
21.77 mm away from the switches. It also silently kept the pre-B10 6.9 mm plate cutouts.

This script makes that state impossible to miss:

  1. ``BUILD-STAMP.txt`` must exist  -> proves which run produced the folder,
  2. the stamp's ``config_sha1`` must equal the sha1 of the *current* ``ergogen/config.yaml``
     -> proves the snapshot is not stale w.r.t. the design,
  3. ``scripts/check_assembly.py`` must pass on the published files
     -> proves the artifacts are mutually consistent (cover <-> switches <-> plate <-> screws),
  4. every published plate cutout must be 14.0 mm (not the pre-B10 6.9 mm).

Usage
-----
    ./.venv/Scripts/python.exe scripts/check_published.py
    ./.venv/Scripts/python.exe scripts/check_published.py --dir filtered-output
    ./.venv/Scripts/python.exe scripts/check_published.py --allow-unstamped   # local triage only

Exit code 0 = the folder may be published. Non-zero = it must be rebuilt from one single CI run.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_assembly import dxf_net_shape, pcb_net_shape  # noqa: E402
PLATE_CUTOUT_MM = 14.0
CUTOUT_TOL = 0.25


def sha1_file(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def find(stamp_dir: Path, *names: str) -> list[Path]:
    out = []
    for n in names:
        out.extend(sorted(stamp_dir.rglob(n)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="filtered-output")
    ap.add_argument("--config", default="ergogen/config.yaml")
    ap.add_argument("--allow-unstamped", action="store_true",
                    help="downgrade a missing/stale stamp to a warning (local triage only)")
    args = ap.parse_args()

    root = Path(args.dir)
    config = Path(args.config)
    fails: list[str] = []
    warns: list[str] = []

    print(f"\n=== published snapshot gate: {root}")

    if not root.is_dir():
        print(f"FAIL  {root} does not exist", file=sys.stderr)
        return 2

    # ---------------------------------------------------------------- 1+2 stamp
    stamp = root / "BUILD-STAMP.txt"
    want = sha1_file(config)
    if not stamp.exists():
        msg = (f"no BUILD-STAMP.txt in {root} -> provenance unknown, the folder may mix CI runs "
               f"(this is B14)")
        (warns if args.allow_unstamped else fails).append(msg)
    else:
        text = stamp.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"config_sha1\s*[:=]\s*([0-9a-f]{8,40})", text)
        if not m:
            (warns if args.allow_unstamped else fails).append(
                f"{stamp} has no config_sha1 line")
        elif not want.startswith(m.group(1)):
            msg = (f"stale snapshot: stamp says config_sha1={m.group(1)}, current config is "
                   f"{want[:12]} -> rebuild filtered-output from one fresh CI run")
            (warns if args.allow_unstamped else fails).append(msg)
        else:
            print(f"  ok  stamp matches current config ({want[:12]})")

    # ---------------------------------------------------------------- 3 cross-artifact
    cad = root / "pcbs" / "cad"
    outl = root / "pcbs" / "outlines"
    cases = root / "cases"
    if (cad / "left_pcb.kicad_pcb").exists() and outl.is_dir():
        cmd = [sys.executable, str(REPO / "scripts" / "check_assembly.py"),
               "--root", str(cad), "--outlines", str(outl)]
        if cases.is_dir() and any(cases.glob("*.stl")):
            cmd += ["--cases", str(cases)]
        cp = subprocess.run(cmd, capture_output=True, text=True)
        tail = (cp.stdout or "").strip().splitlines()
        if cp.returncode != 0:
            bad = [ln.strip() for ln in tail if ln.strip().startswith("FAIL")]
            fails.append("check_assembly.py failed on the published files: "
                         + (" | ".join(bad[:6]) if bad else "see output"))
            print(cp.stdout)
        else:
            print(f"  ok  check_assembly.py passed on {cad}")
    else:
        fails.append(f"{cad}/left_pcb.kicad_pcb or {outl} missing -> nothing internally verified")

    # ---------------------------------------------------------------- 4 B10 signature
    plates = find(cad, "plate_left.kicad_pcb", "plate_right.kicad_pcb")
    if not plates:
        fails.append("no plate_*.kicad_pcb in the published CAD folder")
    for p in plates:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        # every plate key cutout is a 4-line square; measure the segment lengths
        lens = [((float(b) - float(a)) ** 2 + (float(d) - float(c)) ** 2) ** 0.5
                for a, c, b, d in re.findall(
                    r"\(gr_line\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*"
                    r"\(end\s+([-\d.]+)\s+([-\d.]+)\)", txt)]
        sq = [round(L, 3) for L in lens if abs(L - PLATE_CUTOUT_MM) < CUTOUT_TOL]
        half = [round(L, 3) for L in lens if abs(L - PLATE_CUTOUT_MM / 2) < CUTOUT_TOL]
        if abs(len(sq) / 4 - 32) > 0.5:
            msg = (f"{p.name}: {len(sq)//4} cutouts of {PLATE_CUTOUT_MM} mm, expected 32 "
                   f"(pre-B10 half-size segments found: {len(half)})")
            fails.append(msg)
        else:
            print(f"  ok  {p.name}: 32 cutouts at {PLATE_CUTOUT_MM} mm")

    # ---------------------------------------------------------------- 5 geometry is current
    # The stamp proves WHICH config produced the snapshot. It does not prove the PCBs inside were
    # regenerated from it: kibot against a stopped Docker fails all six stages, and the stamp still
    # validates. So compare what was published against the outline it must have been cut from.
    outl_dir = REPO / "ergogen" / "output" / "outlines"
    for name, side in (("plate_left.kicad_pcb", "l"), ("plate_right.kicad_pcb", "r")):
        pcb = next(iter(find(cad, name)), None)
        if pcb is None:
            continue
        outline = outl_dir / f"{side}_plate_on_wall.dxf"
        if not outline.exists():
            warns.append(f"{outline.name} missing -> cannot prove {name} matches the design")
            continue
        # Compare the HOLES, not the areas: the generated PCB's exterior sits ~0.8 mm inside the
        # plate outline (an edge trim), which moves the material area ~107 mm2 without anything
        # being stale. Every hole - 32 keys, the screw bores, the hood footprint - must match.
        from shapely.geometry import Polygon as _Poly
        want_holes = sorted(_Poly(i).area for i in dxf_net_shape(outline).interiors)
        shape = pcb_net_shape(pcb)
        got_holes = sorted(_Poly(i).area for i in shape.interiors) if shape is not None else []
        worst = max((abs(a - b) for a, b in zip(got_holes, want_holes)), default=0.0)
        if len(got_holes) != len(want_holes) or worst > 2.0:
            fails.append(f"{name}: {len(got_holes)} holes vs {len(want_holes)} in the current outline, "
                         f"worst area difference {worst:.1f} mm2 - not regenerated from this design")
        else:
            hood = max(want_holes)
            print(f"  ok  {name}: {len(got_holes)} holes match the current outline "
                  f"(largest {hood:.1f} mm2 = the hood footprint; board edge trim ignored)")

    # ---------------------------------------------------------------- report
    for w in warns:
        print(f"WARN  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    if fails:
        print(f"\nPUBLISH BLOCKED ({len(fails)} problem(s)) — rebuild filtered-output from a single "
              f"CI run instead of merging artifacts.\n", file=sys.stderr)
        return 1
    print("\nPASS  published snapshot is stamped, consistent and not stale\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
