#!/usr/bin/env python3
"""Inspect a printable model the way a person would - by looking at it - but numerically.

`check_print_files.py` answers "will a slicer accept this file". This script answers
"is the *shape* right": how many separate bodies, what does a horizontal cross-section
look like at a given height (how many outlines, how many holes), is the part symmetric,
and does it still fit its neighbours.

Also renders PNG views (top / side / isometric) so a human can eyeball the result.

Usage:
  ./.venv/Scripts/python.exe scripts/inspect_print_model.py file.stl
  ./.venv/Scripts/python.exe scripts/inspect_print_model.py file.stl --slices 1.5,6,10 --render out/
  ./.venv/Scripts/python.exe scripts/inspect_print_model.py --json a.stl b.stl

Exit code is 0 unless the model has more than one body (floating/degenerate shells).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import trimesh


def slice_report(mesh: trimesh.Trimesh, zs: list[float]) -> list[dict]:
    out = []
    lo, hi = mesh.bounds[0][2], mesh.bounds[1][2]
    for z in zs:
        if not (lo < z < hi):
            out.append({"z": z, "skipped": "outside the model's z range"})
            continue
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if section is None:
            out.append({"z": z, "outlines": 0, "holes": 0, "area_mm2": 0.0})
            continue
        try:
            res = section.to_2D()
        except AttributeError:  # older trimesh
            res = section.to_planar()
        p2d = res[0] if isinstance(res, tuple) else res
        polygons = list(p2d.polygons_full)
        holes = sum(len(p.interiors) for p in polygons)
        area = float(sum(abs(p.area) for p in polygons))
        out.append({"z": z, "outlines": len(polygons), "holes": holes, "area_mm2": round(area, 1)})
    return out


def bodies(mesh: trimesh.Trimesh) -> list[dict]:
    welded = mesh.copy()
    welded.merge_vertices()
    welded.remove_unreferenced_vertices()
    parts = welded.split(only_watertight=False)
    parts = sorted(parts, key=lambda m: abs(m.volume), reverse=True)
    return [
        {
            "volume_cm3": round(float(p.volume) / 1000.0, 3),
            "triangles": int(len(p.faces)),
            "bbox": [round(float(x), 2) for x in (p.bounds[1] - p.bounds[0])],
        }
        for p in parts
    ]


def asymmetry(mesh: trimesh.Trimesh) -> dict:
    """Mirror-symmetry indicator that actually means something.

    Comparing a mirrored mesh's *volume* proves nothing (any closed mesh mirrors to the same
    volume). The useful signal is the mass-centre offset from the bounding-box centre: a part
    that is symmetric in an axis has ~0 offset there, an asymmetric one (USB slot, controller
    bay) does not.
    """
    lo, hi = mesh.bounds
    centre = (lo + hi) / 2.0
    cm = mesh.center_mass
    return {
        "centroid_offset_mm": [round(float(cm[0] - centre[0]), 2), round(float(cm[1] - centre[1]), 2)],
        "symmetric_in_x": abs(float(cm[0] - centre[0])) < 0.5,
        "symmetric_in_y": abs(float(cm[1] - centre[1])) < 0.5,
    }


def render(mesh: trimesh.Trimesh, outdir: str, name: str) -> list[str]:
    """Top / front / isometric renders with trimesh's built-in rasteriser."""
    os.makedirs(outdir, exist_ok=True)
    made = []
    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name=name)
    views = {
        "top": ([0, 0, 1], [0, 1, 0]),
        "front": ([0, -1, 0.15], [0, 0, 1]),
        "iso": ([0.7, -1, 0.8], [0, 0, 1]),
    }
    for view, (eye, up) in views.items():
        path = os.path.join(outdir, f"{name}-{view}.png")
        try:
            # trimesh can rasterise via pyglet; headless machines often can't
            scene.set_camera(angles=None, distance=None)
            scene.camera_transform = trimesh.scene.cameras.look_at(
                points=np.array([eye]) * 400, fov=45, center=mesh.centroid, up=up
            )[0]
            png = scene.save_image(resolution=(900, 700), visible=True)
            with open(path, "wb") as fh:
                fh.write(png)
            made.append(path)
        except Exception:  # noqa: BLE001 - rendering is best-effort
            pass
    return made


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--slices", default=None, help="comma separated z heights (mm)")
    ap.add_argument("--render", default=None, help="directory for PNG renders")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    reports = []
    ok = True
    for path in args.files:
        if not os.path.exists(path):
            print(f"missing: {path}", file=sys.stderr)
            ok = False
            continue
        mesh = trimesh.load(path, force="mesh", process=False)
        lo, hi = mesh.bounds[0][2], mesh.bounds[1][2]
        if args.slices:
            zs = [float(x) for x in args.slices.split(",")]
        else:
            zs = [round(lo + (hi - lo) * f, 2) for f in (0.1, 0.5, 0.9)]
        name = os.path.splitext(os.path.basename(path))[0]
        rep = {
            "path": path,
            "name": name,
            "bbox": [round(float(x), 2) for x in (mesh.bounds[1] - mesh.bounds[0])],
            "z_range": [round(float(lo), 2), round(float(hi), 2)],
            "volume_cm3": round(float(mesh.volume) / 1000.0, 2),
            "bodies": bodies(mesh),
            **asymmetry(mesh),
            "slices": slice_report(mesh, zs),
        }
        if len(rep["bodies"]) > 1:
            extra = [b for b in rep["bodies"][1:] if b["volume_cm3"] > 0.01]
            if extra:
                ok = False
                rep["warning"] = f"{len(extra)} extra bodie(s) with volume - floating shells?"
        if args.render:
            rep["renders"] = render(mesh, args.render, name)
        reports.append(rep)

    if args.json:
        print("__JSON__" + json.dumps({"ok": ok, "models": reports}))
    else:
        for r in reports:
            print(f"\n=== {r['name']}")
            print(f"  bbox {r['bbox'][0]} x {r['bbox'][1]} x {r['bbox'][2]} mm   z {r['z_range'][0]}..{r['z_range'][1]}")
            print(f"  volume {r['volume_cm3']} cm3   bodies {len(r['bodies'])}")
            print(f"  centroid offset {r['centroid_offset_mm']} mm  "
                  f"(symmetric: x={r['symmetric_in_x']} y={r['symmetric_in_y']})")
            for s in r["slices"]:
                if "skipped" in s:
                    print(f"  z={s['z']:>6}: skipped ({s['skipped']})")
                else:
                    print(f"  z={s['z']:>6}: outlines={s['outlines']:<3} holes={s['holes']:<3} area={s['area_mm2']} mm2")
            if r.get("warning"):
                print(f"  WARNING: {r['warning']}")
            for p in r.get("renders", []):
                print(f"  render: {p}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
