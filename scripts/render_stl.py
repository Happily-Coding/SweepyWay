#!/usr/bin/env python3
"""Render STL(s) to PNG, headless and deterministic - no GL, no display, no camera hijacking.

VTK/vedo was tried first and rejected: `Plotter.show()` re-aims the camera, so every "top" view
silently became a 3/4 view (verified by the render's aspect ratio not matching the mesh bbox).
This does the projection itself: orthographic, painter's algorithm, flat shading.

usage:
  ./.venv/Scripts/python.exe scripts/render_stl.py OUTDIR file.stl [...] [--views top,front,iso]
      [--size 1200x1200] [--wire]
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


# camera direction (where the eye sits, relative to the part centre) and the screen-up hint
VIEWS = {
    "top": ((0.0, 0.0, 1.0), (0.0, 1.0, 0.0)),
    "under": ((0.0, 0.0, -1.0), (0.0, -1.0, 0.0)),
    "front": ((0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),
    "back": ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    "side": ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    "iso": ((0.75, -1.0, 0.8), (0.0, 0.0, 1.0)),
}


def project(vertices: np.ndarray, eye: tuple, up: tuple) -> tuple[np.ndarray, np.ndarray]:
    """Return (xy in camera plane, depth along the view axis)."""
    eye_v = np.array(eye, dtype=float)
    eye_v /= np.linalg.norm(eye_v)
    up_v = np.array(up, dtype=float)
    if abs(np.dot(eye_v, up_v)) > 0.999:  # up must not be parallel to the view axis
        up_v = np.array([1.0, 0.0, 0.0])
    right = np.cross(up_v, eye_v)
    right /= np.linalg.norm(right)
    true_up = np.cross(eye_v, right)
    xy = np.stack([vertices @ right, vertices @ true_up], axis=1)
    depth = vertices @ eye_v
    return xy, depth


def shade(mesh: trimesh.Trimesh, eye: tuple) -> np.ndarray:
    light = np.array([0.35, -0.55, 0.75])
    light /= np.linalg.norm(light)
    n = np.asarray(mesh.face_normals, dtype=float)
    eye_v = np.array(eye, dtype=float)
    eye_v /= np.linalg.norm(eye_v)
    lam = np.abs(n @ light)                      # two-sided: normals may point either way
    lam = 0.25 + 0.75 * lam
    return lam


def render_one(mesh: trimesh.Trimesh, view: str, size: tuple[int, int], out: str,
               title: str = "", wire: bool = False) -> str:
    eye, up = VIEWS[view]
    v = np.asarray(mesh.vertices, dtype=float)
    f = np.asarray(mesh.faces)
    xy, depth = project(v, eye, up)
    tri_xy = xy[f]                                # (n, 3, 2)
    face_depth = depth[f].mean(axis=1)
    order = np.argsort(face_depth)                # far to near
    colors = shade(mesh, eye)[order]

    cmap = plt.get_cmap("Blues")
    facecolors = cmap(0.25 + 0.55 * colors)       # type: ignore[arg-type]
    if wire:
        facecolors[:, 3] = 0.92

    lo = tri_xy.reshape(-1, 2).min(axis=0)
    hi = tri_xy.reshape(-1, 2).max(axis=0)
    span = (hi - lo)
    pad = 0.06 * max(span)
    lo -= pad
    hi += pad

    w, h = size
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_aspect("equal")                        # no distortion: aspect ratio stays measurable
    ax.axis("off")
    ax.add_collection(PolyCollection(tri_xy[order], facecolors=facecolors,
                                     edgecolors="none" if not wire else (0.1, 0.2, 0.35, 0.5),
                                     linewidths=0.15 if wire else 0.0, antialiased=True))
    if title:
        ax.set_title(title, fontsize=9, loc="left", color="#333")
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--views", default="top,front,iso")
    ap.add_argument("--size", default="1200x1200")
    ap.add_argument("--wire", action="store_true")
    ap.add_argument("--title", action="store_true",
                    help="draw the name on the image; keep off when the PNG will be measured, "
                         "since the text itself counts as foreground and inflates the bbox")
    args = ap.parse_args()

    w, h = (int(x) for x in args.size.split("x"))
    os.makedirs(args.outdir, exist_ok=True)
    for path in args.files:
        mesh = trimesh.load(path, force="mesh", process=False)
        name = os.path.splitext(os.path.basename(path))[0]
        for view in [v for v in args.views.split(",") if v in VIEWS]:
            out = os.path.join(args.outdir, f"{name}-{view}.png")
            render_one(mesh, view, (w, h), out, title=f"{name} - {view}" if args.title else "", wire=args.wire)
            print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
