#!/usr/bin/env python3
"""Sanity-check the printable STL files before uploading them to a print service.

For every file it reports triangle count, bounding box (mm), signed volume and
whether the mesh is watertight with consistent outward-facing normals.

Why: slicers and print services silently "repair" broken meshes. The tenting base
once exported with *negative* volume (all normals inverted), which is the kind of
thing that produces a hollow-shell print or a rejected upload depending on the day.

Pure stdlib (binary + ASCII STL), no dependencies.

Usage:
  ./scripts/check_print_files.py
  ./scripts/check_print_files.py file.stl [more.stl ...]
  ./scripts/check_print_files.py --expect-mm 100    # warn if size looks like metres
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

DEFAULT_FILES = [
    "filtered-output/cases/l_case_3d.stl",
    "filtered-output/cases/l_cover.stl",
    "filtered-output/cases/tenting_system.stl",
    "filtered-output/palmrest/palm_rest.stl",
]


def read_stl(path: Path):
    """Return (name, [(v0, v1, v2), ...])."""
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("file too small to be an STL")
    # ASCII?
    head = data[:512].lstrip()
    if head[:5].lower() == b"solid" and b"facet" in data[:2048]:
        tris = []
        verts = []
        for line in data.decode("ascii", errors="ignore").splitlines():
            parts = line.split()
            if len(parts) == 4 and parts[0] == "vertex":
                verts.append(tuple(float(x) for x in parts[1:4]))
                if len(verts) == 3:
                    tris.append(tuple(verts))
                    verts = []
        return "ascii", tris
    n = struct.unpack("<I", data[80:84])[0]
    if 84 + n * 50 > len(data) + 1:
        raise ValueError(f"truncated binary STL: says {n} triangles, file only fits "
                         f"{(len(data) - 84) // 50}")
    tris = []
    off = 84
    for _ in range(n):
        vals = struct.unpack("<12fH", data[off:off + 50])
        tris.append((vals[3:6], vals[6:9], vals[9:12]))
        off += 50
    return "binary", tris


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def analyse(tris):
    xs = [v[0] for t in tris for v in t]
    ys = [v[1] for t in tris for v in t]
    zs = [v[2] for t in tris for v in t]
    size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))

    volume = 0.0
    edges = {}
    for v0, v1, v2 in tris:
        volume += dot(v0, cross(v1, v2)) / 6.0
        for a, b in ((v0, v1), (v1, v2), (v2, v0)):
            key = tuple(sorted((a, b)))
            edges[key] = edges.get(key, 0) + 1

    boundary = sum(1 for c in edges.values() if c == 1)
    nonmanifold = sum(1 for c in edges.values() if c > 2)
    watertight = boundary == 0 and nonmanifold == 0
    return size, volume, watertight, boundary, nonmanifold


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", default=None)
    ap.add_argument("--json", action="store_true", help="machine-readable summary on stdout")
    ap.add_argument("--expect-mm", type=float, default=10.0,
                    help="warn if the largest dimension is below this many mm "
                         "(suggests a metres/mm unit mistake)")
    args = ap.parse_args()

    files = [Path(f) for f in (args.files or DEFAULT_FILES)]
    good = True
    records = []
    for path in files:
        print(f"\n=== {path} ===")
        if not path.exists():
            print("  SKIP  file not found (build it first: see docs/PIPELINE.md §6)")
            continue
        try:
            kind, tris = read_stl(path)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL  cannot parse: {exc}")
            good = False
            continue
        if not tris:
            print("  FAIL  no triangles")
            good = False
            continue

        size, volume, watertight, boundary, nonmanifold = analyse(tris)
        records.append({
            "path": str(path), "triangles": len(tris),
            "bbox": [round(x, 2) for x in size], "volume_cm3": round(volume / 1000.0, 2),
            "watertight": watertight, "boundary_edges": boundary, "nonmanifold_edges": nonmanifold,
            "ok": bool(boundary == 0 and volume > 0 and max(size) >= args.expect_mm),
            "closed": bool(boundary == 0),
        })
        print(f"  {kind} STL, {len(tris)} triangles")
        print(f"  bbox: {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm")
        print(f"  signed volume: {volume / 1000.0:+.2f} cm^3")

        if max(size) < args.expect_mm:
            print("  FAIL  model looks like metres, not millimetres (scale by 1000)")
            good = False
        if volume <= 0:
            print("  FAIL  non-positive volume -> inverted normals (mesh.fix_normals() / "
                  "re-export needed)")
            good = False
        if boundary:
            print(f"  FAIL  open surface: {boundary} boundary edges (a slicer cannot close this)")
            good = False
        elif nonmanifold:
            print(f"  warn  closed but {nonmanifold} non-manifold edges (coplanar T-junctions; "
                  f"slicers repair these)")
        if watertight:
            print("  ok    watertight, outward normals")
        elif not boundary:
            print("  ok    closed surface (printable after slicer repair)")

    if args.json:
        print("__JSON__" + json.dumps({"ok": good, "files": records}))
    else:
        print("\n" + ("PASS" if good else "FAIL"))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
