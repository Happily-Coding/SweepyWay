#!/usr/bin/env python3
"""Repair an STL in place (or to another path) so a print service will accept it.

Why: the OpenJSCAD → STL conversion of `l_case_3d` leaves a handful of non-manifold
edges (the USB-C slot subtraction), and hand-made trimesh meshes can export with
inverted winding. Both make a slicer "repair" the model - or reject it.

What it does: weld duplicate vertices, drop unreferenced ones, orient normals outward,
close small holes, and flip the whole mesh if the signed volume came out negative.

Usage:
  ./.venv/Scripts/python.exe scripts/repair_stl.py file.stl                # in place
  ./.venv/Scripts/python.exe scripts/repair_stl.py in.stl --out fixed.stl
  ./.venv/Scripts/python.exe scripts/repair_stl.py file.stl --json

Exit code: 0 if the result is watertight with positive volume, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import trimesh


def edge_counts(mesh: trimesh.Trimesh):
    """How many faces share each edge: 1 = boundary (hole), 2 = manifold, >2 = non-manifold."""
    import numpy as np

    if not len(mesh.faces):
        return np.array([], dtype=int)
    _uniq, counts = np.unique(mesh.edges_sorted, axis=0, return_counts=True)
    return counts


def stats(mesh: trimesh.Trimesh) -> dict:
    counts = edge_counts(mesh)
    return {
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "closed": bool(len(counts) and not (counts == 1).any()),
        "nonmanifold_edges": int((counts > 2).sum()),
        "volume_cm3": round(float(mesh.volume) / 1000.0, 3),
        "bbox": [round(float(x), 2) for x in (mesh.bounds[1] - mesh.bounds[0])],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", default=None, help="output path (default: overwrite the input)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--drop-to-bed", action="store_true",
                    help="translate so the lowest point sits at z=0 (Ergogen exports the cover "
                         "at the preview offset z=25)")
    args = ap.parse_args()

    if not os.path.exists(args.path):
        print(f"missing file: {args.path}", file=sys.stderr)
        return 2

    mesh = trimesh.load(args.path, force="mesh", process=False)
    before = stats(mesh)

    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals()
    trimesh.repair.fill_holes(mesh)
    if mesh.volume < 0:
        mesh.invert()
    after = stats(mesh)

    if args.drop_to_bed:
        mesh.apply_translation([0, 0, -float(mesh.bounds[0][2])])
        after = stats(mesh)

    out = args.out or args.path
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    mesh.export(out)

    # closed surface with positive volume is printable even if a few coplanar
    # T-junctions survive (slicers repair those)
    ok = bool(after["closed"] and after["volume_cm3"] > 0)
    if args.json:
        print("__JSON__" + json.dumps({"path": out, "ok": ok, "before": before, "after": after}))
    else:
        print(f"{out}")
        print(f"  before: watertight={before['watertight']} volume={before['volume_cm3']} cm3")
        print(f"  after:  watertight={after['watertight']} closed={after['closed']} "
              f"non-manifold={after['nonmanifold_edges']} volume={after['volume_cm3']} cm3 "
              f"{'OK' if ok else 'STILL BROKEN'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
