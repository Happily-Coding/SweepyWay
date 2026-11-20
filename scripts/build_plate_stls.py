#!/usr/bin/env python3
"""Build the plate STLs in export3d/ from the outlines, so a 3D scene can never show a stale plate.

Why this exists: `export3d/plate_*.stl` were hand-made once (D2, 7808 mm², before the B23 hood) and
nothing regenerated them, while `build_combined_scene.py` reads them. The scene therefore kept drawing
a plate with no hood cutout over a case that has a hood - 9.40 cm3 of plate instead of 8.07.

The plate is a flat sheet: the outline (with its key cutouts, screw bores and hood cutout as interior
holes) extruded by `top_plate_thickness`. That is the whole part.

  build_plate_stls.py                      # export3d/plate_{left,right}_{bay,full}.stl
  build_plate_stls.py --thickness 1.2 --out export3d
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_assembly import dxf_net_shape  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
VARIANTS = (("full", "{side}_plate_on_wall.dxf"), ("bay", "{side}_plate_on_wall_bay.dxf"))


def thickness_from_config(config: Path) -> float:
    import re
    m = re.search(r"^  top_plate_thickness:\s*([\d.]+)", config.read_text(encoding="utf-8"),
                  flags=re.M)
    return float(m.group(1)) if m else 1.2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outlines", default="ergogen/output/outlines")
    ap.add_argument("--out", default="export3d")
    ap.add_argument("--config", default="ergogen/config.yaml")
    ap.add_argument("--thickness", type=float)
    args = ap.parse_args()

    th = args.thickness if args.thickness is not None else thickness_from_config(REPO / args.config)
    out_dir = REPO / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    built = 0
    for tag, side in (("right", "r"), ("left", "l")):
        for variant, pattern in VARIANTS:
            outline = REPO / args.outlines / pattern.format(side=side)
            if not outline.exists():
                print(f"build_plate_stls: missing {outline}", file=sys.stderr)
                return 2
            poly = dxf_net_shape(outline)
            if poly is None:
                print(f"build_plate_stls: {outline.name} is not a closed outline", file=sys.stderr)
                return 2
            solid = trimesh.creation.extrude_polygon(poly, th)
            target = out_dir / f"plate_{tag}_{variant}.stl"
            solid.export(target)
            b = solid.bounds
            print(f"  ok  {target.name:26s} {b[1][0]-b[0][0]:7.2f} x {b[1][1]-b[0][1]:7.2f} x {th} mm"
                  f"   {solid.volume/1000:5.2f} cm3   watertight {solid.is_watertight}"
                  f"   holes {len(poly.interiors)}")
            if not solid.is_watertight:
                print(f"build_plate_stls: {target.name} is not watertight", file=sys.stderr)
                return 1
            built += 1

    print(f"\nbuild_plate_stls: {built} plate STL(s) rebuilt from the outlines at {th} mm")
    return 0


if __name__ == "__main__":
    sys.exit(main())
