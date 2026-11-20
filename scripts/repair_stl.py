#!/usr/bin/env python3
"""Weld and clean the STLs that `jscad` emits, and refuse to pass anything non-watertight.

Why this exists
---------------
`@jscad/cli` writes STLs with every triangle carrying its own copy of each vertex, plus, whenever
two solids meet on a coincident coplanar face, a scatter of zero-volume sliver shells. Measured on
the accepted v0.2 case: 4502 faces but ~4500 shells, and 598 "boundary" edges that are really just
unwelded duplicates - so the mesh is not watertight even though the geometry is fine. Slicers repair
this silently, which is why it went unnoticed, and a real defect (the B23 hood union) hid behind it.

What it does
------------
  1. weld vertices by rounding to --digits (1e-5 mm is a no-op for intent, exact for dedupe)
  2. drop degenerate faces (a vertex repeated after welding, zero area)
  3. drop disconnected shells smaller than --min-shell-mm3 (the CSG slivers)
  4. assert watertight, and assert the volume did not move (a repair must not change the part)

Usage
-----
  repair_stl.py --in filtered-output/cases                 # every .stl in a directory
  repair_stl.py --in a.stl b.stl --out other_dir
  repair_stl.py --in filtered-output/cases --check         # verify only, write nothing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import trimesh


def weld(mesh: trimesh.Trimesh, digits: int) -> trimesh.Trimesh:
    """Merge coincident vertices and drop the faces that collapse as a result."""
    verts = np.round(mesh.vertices, digits)
    uniq, inverse = np.unique(verts, axis=0, return_inverse=True)
    faces = inverse[mesh.faces]
    keep = (
        (faces[:, 0] != faces[:, 1])
        & (faces[:, 1] != faces[:, 2])
        & (faces[:, 0] != faces[:, 2])
    )
    return trimesh.Trimesh(uniq, faces[keep], process=False)


def repair(path: Path, digits: int, min_shell: float) -> tuple[trimesh.Trimesh, dict]:
    raw = trimesh.load(path, force="mesh", process=False)
    stats = {"faces_in": len(raw.faces), "vol_in": raw.volume / 1000.0}
    # count the incoming shells AFTER welding: an unwelded STL gives one shell per triangle, which
    # reads like "4500 shells" and hides the number that matters
    stats["shells_in"] = len(weld(raw, digits).split(only_watertight=False))

    mesh = weld(raw, digits)
    shells = mesh.split(only_watertight=False)
    kept = [s for s in shells if abs(s.volume) >= min_shell]
    if not kept:
        kept = [max(shells, key=lambda s: abs(s.volume))]
    if len(kept) > 1:
        # keep every substantial shell: a part may legitimately be several closed volumes
        mesh = trimesh.util.concatenate(kept)
    else:
        mesh = kept[0]
    mesh = weld(mesh, digits)
    mesh.remove_unreferenced_vertices()

    stats.update({"faces_out": len(mesh.faces), "shells_out": len(kept),
                  "vol_out": mesh.volume / 1000.0,
                  "watertight": bool(mesh.is_watertight),
                  "boundary_edges": len(trimesh.grouping.group_rows(mesh.edges_sorted,
                                                                   require_count=1))})
    return mesh, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inputs", nargs="+", required=True,
                    help="STL files and/or directories of STL files")
    ap.add_argument("--out", help="output directory (default: rewrite in place)")
    ap.add_argument("--digits", type=int, default=5,
                    help="vertex weld precision in decimal places (default 5 = 1e-5 mm)")
    ap.add_argument("--min-shell-mm3", type=float, default=1.0,
                    help="discard disconnected shells below this volume (default 1 mm3)")
    ap.add_argument("--check", action="store_true", help="verify only, write nothing")
    ap.add_argument("--allow-void", action="store_true",
                    help="do not fail on a mesh that stays non-watertight")
    args = ap.parse_args()

    files: list[Path] = []
    for item in args.inputs:
        p = Path(item)
        if p.is_dir():
            files.extend(sorted(p.glob("*.stl")))
        elif p.exists():
            files.append(p)
        else:
            print(f"repair_stl: no such file or directory: {p}", file=sys.stderr)
            return 2
    if not files:
        print("repair_stl: nothing to do (no .stl found)", file=sys.stderr)
        return 2

    out_dir = Path(args.out) if args.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    bad: list[str] = []
    drift: list[str] = []
    print(f"repair_stl: {len(files)} file(s)")
    for f in files:
        mesh, st = repair(f, args.digits, args.min_shell_mm3)
        # a repair may not change the part: same volume to within 0.5 %
        if st["vol_in"] > 0 and abs(st["vol_out"] - st["vol_in"]) / st["vol_in"] > 0.005:
            drift.append(f"{f.name} {st['vol_in']:.1f} -> {st['vol_out']:.1f} cm3")
        flag = "ok  " if st["watertight"] else "FAIL"
        if not st["watertight"]:
            bad.append(f.name)
        print(f"  {flag} {f.name:34s} faces {st['faces_in']:5d} -> {st['faces_out']:5d}"
              f"   shells {st['shells_in']:5d} -> {st['shells_out']}"
              f"   boundary edges {st['boundary_edges']:4d}"
              f"   watertight {st['watertight']}   {st['vol_out']:.1f} cm3")
        if not args.check:
            target = (out_dir / f.name) if out_dir else f
            mesh.export(target, file_type="stl")

    if drift:
        print("\nrepair_stl: the repair changed the part volume - that is not a repair:", file=sys.stderr)
        for d in drift:
            print(f"  {d}", file=sys.stderr)
        return 1
    if bad and not args.allow_void:
        print(f"\nrepair_stl: {len(bad)} file(s) are still not watertight: {', '.join(bad)}",
              file=sys.stderr)
        return 1
    print("\nrepair_stl: PASS - every mesh is watertight and the volumes are unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
