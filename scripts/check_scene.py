#!/usr/bin/env python3
"""Verify combined_scene.glb against the three things a viewer immediately shows.

This exists because I shipped a scene that broke in three visible ways while every number I checked
was fine. Each check below corresponds to a complaint that a human spotted in 3dviewer.net and my
numeric "coherence" checks did not:

  1. TRANSPARENCY - every part must have a material with alpha < 1 and alphaMode BLEND. A viewer shows
     opaque parts if the alpha is left on vertex colours or defaults to OPAQUE.
  2. FLAT BASE - the tenting system sits on the desk and must NOT be rotated; the keyboard that sits on
     it must be tilted by TENTING_ANGLE. Getting this backwards tilts the base and leaves the case flat.
  3. NO TRIANGLE SOUP - a mesh exported with a per-face material has 3 vertices per triangle and reads
     as faceted triangles instead of a smooth surface, even though every other number looks right.

  check_scene.py                       # filtered-output/combined_scene.glb
  check_scene.py --glb other.glb
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

TENTING_ANGLE = 6.5
TILTED = ("case", "plate", "pcb", "palm")
FLAT = ("tenting",)


def gltf_json(path: Path) -> dict:
    b = path.read_bytes()
    _, _, total = struct.unpack("<III", b[:12])
    off = 12
    while off < total:
        clen, ctype = struct.unpack("<II", b[off:off + 8])
        if ctype == 0x4E4F534A:  # JSON
            return json.loads(b[off + 8:off + 8 + clen].decode("utf-8").rstrip("\x00 "))
        off += 8 + clen
    raise SystemExit(f"check_scene: no JSON chunk in {path}")


def node_angle_z(node: dict) -> float:
    """Rotation about Z in degrees, from the quaternion (0,0,sin,cos) a Z-only rotation leaves."""
    q = node.get("rotation")
    if not q:
        return 0.0
    x, y, z, w = q
    if abs(x) < 1e-6 and abs(y) < 1e-6:
        return math.degrees(2.0 * math.atan2(z, w))
    return float("nan")  # some other axis: not what this scene uses


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glb", default="filtered-output/combined_scene.glb")
    ap.add_argument("--alpha-max", type=float, default=0.95)
    args = ap.parse_args()
    path = Path(args.glb)
    if not path.exists():
        print(f"check_scene: {path} not found", file=sys.stderr)
        return 2
    j = gltf_json(path)
    nodes = j.get("nodes", [])
    meshes = j.get("meshes", [])
    mats = j.get("materials", [])
    acc = j.get("accessors", [])
    fails, rows = [], []

    # ---- 1. transparency -----------------------------------------------------------------------
    opaque = []
    for mi, m in enumerate(meshes):
        for p in m.get("primitives", []):
            idx = p.get("material")
            if idx is None:
                opaque.append(m.get("name") or f"mesh{mi}")
                continue
            mat = mats[idx]
            a = (mat.get("pbrMetallicRoughness", {}).get("baseColorFactor") or [1, 1, 1, 1])[3]
            if mat.get("alphaMode") != "BLEND" or a > args.alpha_max:
                opaque.append(f"{m.get('name')} (alpha {a}, {mat.get('alphaMode', 'OPAQUE')})")
    rows.append(("every part is translucent (BLEND, alpha <= %.2f)" % args.alpha_max,
                 not opaque, f"opaque/OPAQUE: {opaque}" if opaque else f"{len(mats)} materials"))

    # ---- 2. the base is flat, the keyboard is tilted -------------------------------------------
    base_bad, tilt_bad = [], []
    for n in nodes:
        name = (n.get("name") or "").lower()
        ang = node_angle_z(n)
        if any(k in name for k in FLAT):
            if abs(ang) > 0.01:
                base_bad.append(f"{n.get('name')} rotated {ang:.2f} deg")
        if any(k in name for k in TILTED):
            if not math.isnan(ang) and abs(abs(ang) - TENTING_ANGLE) > 0.2:
                tilt_bad.append(f"{n.get('name')} {ang:.2f} deg (want {TENTING_ANGLE})")
    rows.append(("the tenting base is flat on the desk (no rotation)", not base_bad,
                 "; ".join(base_bad) if base_bad else "identity"))
    rows.append((f"the case/plate/PCB/palm rest are tilted {TENTING_ANGLE} deg",
                 not tilt_bad, "; ".join(tilt_bad) if tilt_bad else "all tilted"))

    # ---- 3. no triangle soup -------------------------------------------------------------------
    # Only the STL-derived parts can be "triangle soup": one solid whose vertices are simply not
    # shared reads as faceted triangles. The PCB is an assembly of dozens of separate component
    # models, so unshared vertices there are correct and are reported as a note, not a failure.
    soup, note = [], []
    for m in meshes:
        mname = (m.get("name") or "").lower()
        for p in m.get("primitives", []):
            a = p.get("attributes", {})
            if "POSITION" not in a:
                continue
            v = acc[a["POSITION"]]["count"]
            f = acc[p["indices"]]["count"] // 3 if "indices" in p else 0
            if not f:
                continue
            ratio = v / f
            if "pcb" in mname or "geometry" in mname:
                note.append(f"{m.get('name')} {ratio:.2f} verts/face (component assembly)")
            elif ratio > 0.95:
                soup.append(f"{m.get('name')} {v} verts / {f} faces (ratio {ratio:.2f})")
    rows.append(("STL parts are welded (smooth shading, no triangle soup)", not soup,
                 "; ".join(soup[:4]) if soup else (note[0] if note else "all welded")))

    # ---- 4. shading normals -------------------------------------------------------------------
    # THE ONE THAT GOT THROUGH: trimesh computes vertex normals lazily and its glTF writer does not
    # force the cache, so a part can export with POSITION only. Every viewer then computes flat
    # per-face normals and a smooth solid renders as visible facets - while positions, volumes and
    # part counts are all perfectly correct.
    no_norm = [m.get("name") for m in meshes for p in m.get("primitives", [])
               if "NORMAL" not in p.get("attributes", {})]
    rows.append(("every mesh carries NORMAL (smooth shading in a viewer)", not no_norm,
                 f"missing on: {no_norm}" if no_norm else f"{len(meshes)} meshes"))

    # ---- report --------------------------------------------------------------------------------
    print(f"\n=== scene gate: {path} ({path.stat().st_size/1e6:.1f} MB, {len(meshes)} meshes)")
    for label, ok, detail in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {label:58s} {detail}")
        if not ok:
            fails.append(label)
    if fails:
        print(f"\nFAIL  {len(fails)} scene problem(s)")
        return 1
    print("\nPASS  translucent, base flat, keyboard tilted, welded AND shaded (NORMAL present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
