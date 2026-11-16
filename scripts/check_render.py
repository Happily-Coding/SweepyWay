#!/usr/bin/env python3
"""Assert things about a rendered PNG - "look at the picture" done with pixels instead of eyes.

Usage:
  ./.venv/Scripts/python.exe scripts/check_render.py shot.png
  ./.venv/Scripts/python.exe scripts/check_render.py shot.png --json --min-fill .2

Reports: fill fraction (is anything drawn?), number of silhouette islands, number of enclosed
background regions (holes you can see through), and a mirror-symmetry score.
"""
from __future__ import annotations
import argparse, json, sys
import numpy as np
from PIL import Image
from scipy import ndimage


def analyse(path: str) -> dict:
    im = Image.open(path).convert("L")
    a = np.asarray(im, dtype=np.int16)
    w, h = im.size
    # background is white; anything darker is the model or its shading
    fg = a < 245
    fill = float(fg.mean())

    labels, n_islands = ndimage.label(fg)
    sizes = ndimage.sum(fg, labels, range(1, n_islands + 1)) if n_islands else np.array([])
    keep = sizes > (w * h * 0.0005)  # ignore specks/antialiasing
    islands = int(keep.sum())

    # enclosed background = holes visible through the part
    bg_labels, n_bg = ndimage.label(~fg)
    border = set(bg_labels[0, :]) | set(bg_labels[-1, :]) | set(bg_labels[:, 0]) | set(bg_labels[:, -1])
    holes = int(sum(1 for i in range(1, n_bg + 1) if i not in border
                    and (bg_labels == i).sum() > w * h * 0.00004))  # ~2.2 mm screw holes at this scale

    # symmetry: compare the mask with its mirror, after cropping to the bounding box
    ys, xs = np.nonzero(fg)
    sym = None
    if len(xs):
        box = fg[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        mir = box[:, ::-1]
        denom = max(box.sum(), mir.sum())
        sym = round(float((box & mir).sum()) / denom, 4) if denom else None
        bbox = [int(box.shape[1]), int(box.shape[0])]
    else:
        bbox = [0, 0]
    return {"path": path, "size": [w, h], "fill_fraction": round(fill, 4),
            "islands": islands, "visible_holes": holes,
            "mirror_symmetry": sym, "shape_bbox_px": bbox}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-fill", type=float, default=0.02)
    ap.add_argument("--expect-islands", type=int, default=1)
    args = ap.parse_args()
    reps, ok = [], True
    for p in args.images:
        r = analyse(p)
        r["problems"] = []
        if r["fill_fraction"] < args.min_fill:
            r["problems"].append(f"almost nothing drawn (fill {r['fill_fraction']})")
        if args.expect_islands and r["islands"] != args.expect_islands:
            r["problems"].append(f"{r['islands']} islands on screen (expected {args.expect_islands})")
        if r["problems"]:
            ok = False
        reps.append(r)
    if args.json:
        print("__JSON__" + json.dumps({"ok": ok, "images": reps}))
    else:
        for r in reps:
            name = r["path"].split("\\")[-1].split("/")[-1]
            print(f"{name:<28} fill={r['fill_fraction']:<7} islands={r['islands']:<2} "
                  f"holes={r['visible_holes']:<2} sym={r['mirror_symmetry']:<7} px={r['shape_bbox_px']}"
                  + ("  PROBLEM: " + "; ".join(r["problems"]) if r["problems"] else ""))
        print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
