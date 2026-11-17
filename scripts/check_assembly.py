#!/usr/bin/env python3
"""Check that the parts fit EACH OTHER, and that the wiring is what it claims to be.

Every other checker here looks at one artifact in isolation. The failures that actually cost a
PCB order are relational:

  - plate cutouts that do not sit on the switches (a switch cannot enter the plate)
  - screw holes not coaxial across PCB / plate / printed cover / printed case
  - the printed cover plate missing some of the keys
  - diode orientation differing between keys (one dead key each)
  - a matrix position shared by two switches, or a diode wired to the wrong row

It parses the KiCad PCB + plate, the Ergogen DXFs and the printed STLs, registers them onto PCB
coordinates using the five screw holes, then measures.

Usage:
  ./.venv/Scripts/python.exe scripts/check_assembly.py
  ./.venv/Scripts/python.exe scripts/check_assembly.py --root filtered-output/pcbs \
      --outlines filtered-output/pcbs/outlines --cases filtered-output/cases

Exit 0 = every check passed. `--json` emits a machine-readable report.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

KEY_RE = r"col(\d+)_row(\d+)"
THUMB_RE = r"col(\d+)_thumb_row_(\d+)"
CUTOUT_MM = 14.0


# --------------------------------------------------------------------------- parsing

def blocks(text: str, header: str) -> list[str]:
    """Balanced-paren blocks starting with `header`."""
    out, start = [], 0
    while True:
        i = text.find(header, start)
        if i < 0:
            return out
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    out.append(text[i:j + 1])
                    start = j + 1
                    break
        else:
            return out


def sexpr(text: str):
    """Minimal S-expression parser: '(' -> list, quoted strings -> str, atoms -> str."""
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack, cur = [], []
    for tok in tokens:
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif tok.startswith('"'):
            cur.append(tok[1:-1])
        else:
            cur.append(tok)
    return cur


def _kids(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def kicad_footprints(path: Path) -> list[dict]:
    tree = sexpr(path.read_text(encoding="utf-8", errors="ignore"))
    top = tree[0] if tree and isinstance(tree[0], list) else tree
    fps = []
    for node in _kids(top, "footprint"):
        name = node[1] if len(node) > 1 and isinstance(node[1], str) else ""
        layer = ""
        lyr = _kids(node, "layer")
        if lyr and len(lyr[0]) > 1:
            layer = lyr[0][1]
        x = y = rot = 0.0
        at = _kids(node, "at")
        if at:
            vals = [float(v) for v in at[0][1:] if isinstance(v, str)]
            x, y = vals[0], vals[1]
            rot = vals[2] if len(vals) > 2 else 0.0
        pads = []
        for pad in _kids(node, "pad"):
            num = pad[1] if len(pad) > 1 else ""
            ptype = pad[2] if len(pad) > 2 else ""
            nets = _kids(pad, "net")
            pads.append({"num": num, "type": ptype, "net": nets[0][2] if nets and len(nets[0]) > 2 else None})
        fps.append({"name": name, "layer": layer, "x": x, "y": y, "rot": rot, "pads": pads})
    return fps


def _polygons_from_segments(segs: list[tuple]) -> list:
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union
    lines = unary_union([LineString([a, b]) for a, b in segs])
    return list(polygonize(lines))


def _shape_info(poly) -> dict:
    mrr = poly.minimum_rotated_rectangle
    xs, ys = mrr.exterior.xy
    pts = np.array(list(zip(xs, ys)))[:-1]
    sides = np.linalg.norm(np.diff(np.vstack([pts, pts[:1]]), axis=0), axis=1)
    c = poly.centroid
    return {"cx": float(c.x), "cy": float(c.y),
            "w": float(sides.max()), "h": float(sides.min()),
            "area": float(poly.area)}


def dxf_polys(path: Path) -> list[dict]:
    """Closed polygons from a DXF of LINEs/ARCs (handles rotated cutouts)."""
    import ezdxf
    msp = ezdxf.readfile(str(path)).modelspace()
    segs = []
    for e in msp:
        t = e.dxftype()
        if t == "LINE":
            a, b = e.dxf.start, e.dxf.end
            segs.append(((a.x, a.y), (b.x, b.y)))
        elif t == "ARC":
            c, r = e.dxf.center, e.dxf.radius
            a0, a1 = np.deg2rad(e.dxf.start_angle), np.deg2rad(e.dxf.end_angle)
            if a1 <= a0:
                a1 += 2 * np.pi
            n = max(8, int(abs(a1 - a0) * r / 1.0))
            th = np.linspace(a0, a1, n)
            pts = [(c.x + r * np.cos(v), c.y + r * np.sin(v)) for v in th]
            segs += list(zip(pts[:-1], pts[1:]))
        elif t == "CIRCLE":
            c, r = e.dxf.center, e.dxf.radius
            th = np.linspace(0, 2 * np.pi, 36)
            pts = [(c.x + r * np.cos(v), c.y + r * np.sin(v)) for v in th]
            segs += list(zip(pts[:-1], pts[1:]))
    return [_shape_info(p) for p in _polygons_from_segments(segs)]


def plate_polys(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    segs = []
    for m in re.finditer(r"\(gr_line\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)", text):
        x1, y1, x2, y2 = (float(v) for v in m.groups())
        segs.append(((x1, y1), (x2, y2)))
    for m in re.finditer(r"\(gr_arc\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(mid\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)", text):
        x1, y1, xm, ym, x2, y2 = (float(v) for v in m.groups())
        segs.append(((x1, y1), (xm, ym)))
        segs.append(((xm, ym), (x2, y2)))
    return [_shape_info(p) for p in _polygons_from_segments(segs)]


def dxf_circles(path: Path) -> np.ndarray:
    import ezdxf
    msp = ezdxf.readfile(str(path)).modelspace()
    return np.array([[e.dxf.center.x, e.dxf.center.y] for e in msp if e.dxftype() == "CIRCLE"])


def stl_section(path: Path, z: float | None) -> list[dict]:
    """Interior openings of a horizontal slice: centre + oriented size.

    `cx/cy` is the BBOX centre, not the vertex mean: an STL section ring is triangulated, so its
    vertices are not distributed uniformly round the loop and the mean drifts by up to 6 mm on a
    14 mm square opening (that produced a fake "cover does not cover its switches"). `w/h` is the
    axis-aligned extent (fine for filtering); `aw/ah` is the minimum rotated rectangle, which is
    the rotation-proof size -- a 14 mm cutout reads 19.1 mm axis-aligned at 30 deg splay.
    """
    import trimesh
    from shapely.geometry import Polygon
    mesh = trimesh.load(str(path), force="mesh", process=True)
    if z is None:
        z = float(mesh.bounds[0][2]) + 0.6
    section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    res = section.to_2D()
    p2d = res[0] if isinstance(res, tuple) else res
    out = []
    for poly in p2d.polygons_full:
        for ring in poly.interiors:
            xs = np.array([p[0] for p in ring.coords], dtype=float)
            ys = np.array([p[1] for p in ring.coords], dtype=float)
            aw, ah = float(xs.max() - xs.min()), float(ys.max() - ys.min())
            try:
                mrr = Polygon(list(ring.coords)).minimum_rotated_rectangle
                ex, ey = np.array(mrr.exterior.coords).T
                sides = np.hypot(np.diff(ex), np.diff(ey))
                aw, ah = float(sides[0]), float(sides[1])
            except Exception:
                pass
            out.append({"cx": float((xs.min() + xs.max()) / 2), "cy": float((ys.min() + ys.max()) / 2),
                        "w": float(xs.max() - xs.min()), "h": float(ys.max() - ys.min()),
                        "aw": aw, "ah": ah})
    return out


def stl_info(path: Path) -> dict:
    import trimesh
    m = trimesh.load(str(path), force="mesh", process=True)
    lo, hi = m.bounds
    return {"lo": lo.tolist(), "hi": hi.tolist(),
            "size": (hi - lo).tolist(), "volume_cm3": float(m.volume) / 1000.0}


# --------------------------------------------------------------------------- registration

def register(src: np.ndarray, dst: np.ndarray) -> tuple[tuple[str, np.ndarray], float]:
    """Best axis-aligned flip + centroid translation, scored by SYMMETRIC nearest-neighbour
    distance. Order-independent: KiCad re-saves footprint order, so index-wise comparison
    falsely reports ~70 mm errors (that mistake was made once; it looked like a real defect).
    """
    from scipy.spatial import cKDTree
    best, best_res = ("id", np.zeros(2)), float("inf")
    for kind in ("id", "fy", "fx", "r180"):
        s = src.copy()
        if kind == "fy":
            s[:, 1] = -s[:, 1]
        elif kind == "fx":
            s[:, 0] = -s[:, 0]
        elif kind == "r180":
            s = -s
        t = dst.mean(axis=0) - s.mean(axis=0)
        moved = s + t
        d1, _ = cKDTree(dst).query(moved)
        d2, _ = cKDTree(moved).query(dst)
        res = float(max(d1.max(), d2.max()))
        if res < best_res:
            best, best_res = (kind, t), res
    return best, best_res


def apply(xy: np.ndarray, reg) -> np.ndarray:
    kind, t = reg
    s = xy.copy()
    if kind == "fy":
        s[:, 1] = -s[:, 1]
    elif kind == "fx":
        s[:, 0] = -s[:, 0]
    elif kind == "r180":
        s = -s
    return s + t


def nearest(src: np.ndarray, dst: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    d = np.linalg.norm(src[:, None, :] - dst[None, :, :], axis=2)
    return d.argmin(axis=1), d[np.arange(len(src)), d.min(axis=1).argmin() * 0 + d.argmin(axis=1)]


# --------------------------------------------------------------------------- report

class Report:
    def __init__(self):
        self.rows = []
        self.ok = True

    def check(self, name, passed, detail, **data):
        self.rows.append({"check": name, "pass": bool(passed), "detail": detail, **data})
        self.ok &= bool(passed)
        print(f"  {'ok  ' if passed else 'FAIL'}  {name:<46} {detail}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="ergogen/output/pcbs")
    ap.add_argument("--outlines", default="ergogen/output/outlines")
    ap.add_argument("--cases", default=None)
    ap.add_argument("--key-tol", type=float, default=0.25)
    ap.add_argument("--screw-tol", type=float, default=0.35)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root, outl = Path(args.root), Path(args.outlines)
    rep = Report()
    print(f"\n=== wiring + fit: {root/'left_pcb.kicad_pcb'}")

    fps = kicad_footprints(root / "left_pcb.kicad_pcb")
    switches = [f for f in fps if f["name"].endswith(":choc_v1_v2")]
    diodes = [f for f in fps if "diode" in f["name"]]
    mounts = [f for f in fps if "mounting_hole" in f["name"]]

    rep.check("32 switches", len(switches) == 32, f"{len(switches)} found")
    rep.check("32 diodes", len(diodes) == 32, f"{len(diodes)} found")
    rep.check("switches on B.Cu (component side)", all(f["layer"] == "B.Cu" for f in switches),
              f"layers {sorted({f['layer'] for f in switches})}")
    rep.check("diodes on F.Cu (opposite side)", all(f["layer"] == "F.Cu" for f in diodes),
              f"layers {sorted({f['layer'] for f in diodes})}")

    # ---- wiring: switch = {pos, col}, diode = {pos, row}
    sw_pos, problems = {}, []
    for f in switches:
        nets = [p["net"] for p in f["pads"] if p["net"]]
        cols = [n for n in nets if re.fullmatch(r"C\d+", n)]
        posnets = [n for n in nets if not re.fullmatch(r"[CR]\d+", n)]
        if len(nets) != 2 or len(cols) != 1 or len(posnets) != 1:
            problems.append((f["x"], f["y"], nets))
            continue
        sw_pos[posnets[0]] = {"col": cols[0], "x": f["x"], "y": f["y"]}
    rep.check("every switch has exactly 1 column net + 1 position net", not problems,
              f"{len(sw_pos)}/32 ok" + (f", bad: {problems[:2]}" if problems else ""))

    di_pos, di_order = {}, set()
    for f in diodes:
        nets = [(p["num"], p["net"]) for p in f["pads"] if p["net"]]
        rows = [(n, x) for n, x in nets if re.fullmatch(r"R\d+", x)]
        posnets = [(n, x) for n, x in nets if not re.fullmatch(r"[CR]\d+", x)]
        if len(nets) != 2 or len(rows) != 1 or len(posnets) != 1:
            problems.append((f["x"], f["y"], nets))
            continue
        di_pos[posnets[0][1]] = {"row": rows[0][1], "x": f["x"], "y": f["y"]}
        di_order.add((rows[0][0], posnets[0][0]))
    rep.check("every diode has exactly 1 row net + 1 position net", len(di_pos) == 32,
              f"{len(di_pos)}/32 ok")
    rep.check("diode orientation identical on every key", len(di_order) == 1,
              f"(pad#, net) pairs: {sorted(di_order)}")

    same = set(sw_pos) & set(di_pos)
    rep.check("position nets pair each switch with exactly one diode",
              len(same) == 32 and len(sw_pos) == len(di_pos) == 32,
              f"{len(same)} shared nets, {len(sw_pos)} switch / {len(di_pos)} diode nets")

    # ---- wiring: net names must agree with column/row nets (catches crossed routing)
    grid_bad = []
    for net, info in sw_pos.items():
        m = re.fullmatch(KEY_RE, net)
        if m:
            col, row = m.groups()
            if info["col"] != f"C{col}" or di_pos[net]["row"] != f"R{row}":
                grid_bad.append((net, info["col"], di_pos[net]["row"]))
    rep.check("grid nets match their column/row names", not grid_bad,
              f"{len([n for n in sw_pos if re.fullmatch(KEY_RE, n)])} grid keys" +
              (f", mismatched: {grid_bad[:3]}" if grid_bad else ""))

    thumbs = {n: v for n, v in sw_pos.items() if re.fullmatch(THUMB_RE, n)}
    thumb_rows = {di_pos[n]["row"] for n in thumbs}
    rep.check("3 thumb keys, one row net", len(thumbs) == 3 and len(thumb_rows) == 1,
              f"{len(thumbs)} thumbs on {sorted(thumb_rows)}; columns {sorted(v['col'] for v in thumbs.values())}")

    # ---- fit: plate cutouts on switches
    sw_xy = np.array([[f["x"], f["y"]] for f in switches])
    mount_xy = np.array([[f["x"], f["y"]] for f in mounts])
    screws_xy = dxf_circles(outl / "l_screws_outline.dxf")
    reg, res = register(screws_xy, mount_xy)
    rep.check("screw outline registers onto PCB mounting holes", res < 0.05,
              f"residual {res:.3f} mm, flip={reg[0]}")
    from scipy.spatial import cKDTree as _KD
    d_screw, _ = _KD(mount_xy).query(apply(screws_xy, reg))
    rep.check("screw outline has 5 holes coaxial with PCB", float(d_screw.max()) <= args.screw_tol,
              f"worst {d_screw.max():.3f} mm")

    keys = dxf_polys(outl / "l_keys_outline.dxf")
    cut = np.array([[k["cx"], k["cy"]] for k in keys])
    moved = apply(cut, reg)
    from scipy.spatial import cKDTree
    tree = cKDTree(sw_xy)
    dist, _ = tree.query(moved)
    rep.check("plate cutouts land on switches", len(keys) == 32 and dist.max() <= args.key_tol,
              f"{len(keys)} cutouts, worst {dist.max():.3f} mm")
    # Area is the rotation-proof measure of "is the opening switch sized"; a rotated square's
    # axis-aligned bbox is 14*(cos+sin) which reads as 16-19 mm and is not a defect.
    areas = sorted({round(k["area"], 1) for k in keys})
    lo_a, hi_a = (CUTOUT_MM - 0.4) ** 2, (CUTOUT_MM + 0.4) ** 2
    rep.check(f"plate cutout area == {CUTOUT_MM}mm square", all(lo_a <= a <= hi_a for a in areas),
              f"areas {areas[:5]}{' ...' if len(areas) > 5 else ''} (accept {lo_a:.0f}-{hi_a:.0f} mm2)")

    # Screw holes must not run into a switch cutout: the plate has to keep material around them.
    # This is the check that catches "the plate fits the switches but cannot be screwed down".
    measured_half = float(np.sqrt(np.median([k["area"] for k in keys]))) / 2.0
    worst = None
    for m in mounts:
        best = 1e9
        for f in switches:
            a = np.deg2rad(-f["rot"])
            d = np.array([m["x"] - f["x"], m["y"] - f["y"]])
            loc = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]) @ d
            q = np.abs(loc) - measured_half
            dist = float(np.linalg.norm(np.maximum(q, 0)) + min(q.max(), 0))
            best = min(best, dist)
        if worst is None or best < worst[1]:
            worst = ((m["x"], m["y"]), best)
    need = 1.1 + 0.6   # screw radius + a printable wall
    rep.check("screw holes clear of switch cutouts", worst[1] >= need,
              f"tightest screw {worst[0][0]:.1f},{worst[0][1]:.1f}: clearance {worst[1]:+.3f} mm "
              f"to a {2*measured_half:.2f} mm cutout (need >= {need:.1f}; negative = inside it)")

    pkeys = plate_polys(root / "plate_left.kicad_pcb")
    pc = np.array([[k["cx"], k["cy"]] for k in pkeys])
    if len(pc):
        d2, _ = cKDTree(sw_xy).query(pc)
        rep.check("orderable plate PCB cutouts land on switches", d2.max() <= args.key_tol,
                  f"{len(pkeys)} cutouts, worst {d2.max():.3f} mm")
        pareas = sorted({round(k["area"], 1) for k in pkeys if k["area"] < 400})
        rep.check(f"orderable plate cutout area == {CUTOUT_MM}mm square",
                  all(lo_a <= a <= hi_a for a in pareas), f"areas {pareas[:6]}")
    else:
        rep.check("orderable plate PCB parsed", False, "no closed cutouts found")

    # ---- fit: printed cover + case
    if args.cases:
        cdir = Path(args.cases)
        import trimesh
        cover = cdir / "l_cover.stl"
        if cover.exists():
            zmin = float(trimesh.load(str(cover), force="mesh").bounds[0][2])
            openings = stl_section(cover, zmin + 0.6)
            key_holes = [h for h in openings if 10 <= max(h["w"], h["h"]) <= 25]
            bay_holes = [h for h in openings if max(h["w"], h["h"]) > 25]
            screw_holes = [h for h in openings if max(h["w"], h["h"]) < 4]
            print(f"  ...  cover plate level: {len(key_holes)} key openings, "
                  f"{len(bay_holes)} controller bay, {len(screw_holes)} screw holes")
            kxy = np.array([[h["cx"], h["cy"]] for h in key_holes])
            sxy = np.array([[h["cx"], h["cy"]] for h in screw_holes])
            rep.check("printed cover has exactly 1 controller bay opening", len(bay_holes) == 1,
                      f"{len(bay_holes)} opening(s) larger than a key cutout at plate level")
            rep.check("printed cover has its 5 screw holes", len(screw_holes) == 5,
                      f"{len(screw_holes)} screw-sized openings at plate level")
            if len(sxy) >= 3:
                reg2, res2 = register(sxy, mount_xy)
                rep.check("cover registers onto PCB (screw holes)", res2 < 0.7,
                          f"residual {res2:.3f} mm, flip={reg2[0]}")
                d3, _ = cKDTree(sw_xy).query(apply(kxy, reg2))
                covered = int((d3 <= args.key_tol).sum())
                rep.check("printed cover covers every switch", covered == len(switches) and d3.max() <= args.key_tol,
                          f"{covered}/{len(switches)} covered, worst {d3.max():.3f} mm")
                csizes = sorted({(round(h["aw"], 1), round(h["ah"], 1)) for h in key_holes})
                rep.check(f"cover openings ~{CUTOUT_MM} mm",
                          all(CUTOUT_MM - 0.6 <= max(h["aw"], h["ah"]) <= CUTOUT_MM + 1.6 for h in key_holes),
                          f"sizes {csizes[:4]}{' ...' if len(csizes) > 4 else ''} (min-rect, rotation-proof)")
        case = cdir / "l_case_3d.stl"
        if case.exists():
            holes = stl_section(case, 1.5)
            if len(holes) >= 3:
                hxy = np.array([[h["cx"], h["cy"]] for h in holes])
                reg3, res3 = register(hxy, mount_xy)
                rep.check("case registers onto PCB (screw bosses)", res3 < 1.2,
                          f"residual {res3:.3f} mm, flip={reg3[0]}")
                dh, _ = cKDTree(mount_xy).query(apply(hxy, reg3))
                rep.check("case screw bosses coaxial with PCB holes", dh.max() <= args.screw_tol + 0.3,
                          f"worst {dh.max():.3f} mm")

    # ---- fit: the RIGHT printed parts (B5). Same checks on right-hand inputs: the right case and
    # cover must register onto the right PCB, or the author is back to trusting a slicer mirror.
    # Skipped silently when the right STLs are not in --cases, so old builds still work.
    if args.cases:
        cdir = Path(args.cases)
        rcase_f, rcover_f = cdir / "r_case_3d.stl", cdir / "r_cover.stl"
        if rcase_f.exists() or rcover_f.exists():
            import trimesh
            rfps = kicad_footprints(root / "right_pcb.kicad_pcb")
            rswitches = [f for f in rfps if f["name"].endswith(":choc_v1_v2")]
            rmounts = [f for f in rfps if "mounting_hole" in f["name"]]
            rep.check("right: 32 switches + 5 mounting holes",
                      len(rswitches) == 32 and len(rmounts) == 5,
                      f"{len(rswitches)} switches, {len(rmounts)} mounting holes")
            rsw_xy = np.array([[f["x"], f["y"]] for f in rswitches])
            rmount_xy = np.array([[f["x"], f["y"]] for f in rmounts])
            rscrews_xy = dxf_circles(outl / "r_screws_outline.dxf")
            rreg, rres = register(rscrews_xy, rmount_xy)
            rep.check("right: screw outline registers onto right PCB", rres < 0.05,
                      f"residual {rres:.3f} mm, flip={rreg[0]}")
            if rcover_f.exists():
                rzmin = float(trimesh.load(str(rcover_f), force="mesh").bounds[0][2])
                ropen = stl_section(rcover_f, rzmin + 0.6)
                rkey_holes = [h for h in ropen if 10 <= max(h["w"], h["h"]) <= 25]
                rbay_holes = [h for h in ropen if max(h["w"], h["h"]) > 25]
                rscrew_holes = [h for h in ropen if max(h["w"], h["h"]) < 4]
                print(f"  ...  right cover plate level: {len(rkey_holes)} key openings, "
                      f"{len(rbay_holes)} controller bay, {len(rscrew_holes)} screw holes")
                rep.check("right: printed cover has exactly 1 controller bay opening",
                          len(rbay_holes) == 1,
                          f"{len(rbay_holes)} opening(s) larger than a key cutout at plate level")
                rep.check("right: printed cover has its 5 screw holes", len(rscrew_holes) == 5,
                          f"{len(rscrew_holes)} screw-sized openings at plate level")
                if len(rscrew_holes) >= 3:
                    rreg2, rres2 = register(np.array([[h["cx"], h["cy"]] for h in rscrew_holes]), rmount_xy)
                    rep.check("right: cover registers onto right PCB (screw holes)", rres2 < 0.7,
                              f"residual {rres2:.3f} mm, flip={rreg2[0]}")
                    rd3, _ = cKDTree(rsw_xy).query(
                        apply(np.array([[h["cx"], h["cy"]] for h in rkey_holes]), rreg2))
                    rep.check("right: printed cover covers every switch",
                              len(rd3) == 32 and rd3.max() <= args.key_tol,
                              f"{int((rd3 <= args.key_tol).sum())}/32 covered, worst {rd3.max():.3f} mm")
                    rcsizes = sorted({(round(h["aw"], 1), round(h["ah"], 1)) for h in rkey_holes})
                    rep.check(f"right: cover openings ~{CUTOUT_MM} mm",
                              all(CUTOUT_MM - 0.6 <= max(h["aw"], h["ah"]) <= CUTOUT_MM + 1.6
                                  for h in rkey_holes),
                              f"sizes {rcsizes[:4]}{' ...' if len(rcsizes) > 4 else ''} (min-rect)")
            if rcase_f.exists():
                rholes = stl_section(rcase_f, 1.5)
                rep.check("right: case has 5 screw holes in its floor", len(rholes) == 5,
                          f"{len(rholes)} closed openings at z=1.5")
                if len(rholes) >= 3:
                    rreg3, rres3 = register(np.array([[h["cx"], h["cy"]] for h in rholes]), rmount_xy)
                    rep.check("right: case registers onto right PCB (screw bosses)", rres3 < 1.2,
                              f"residual {rres3:.3f} mm, flip={rreg3[0]}")
                    rdh, _ = cKDTree(rmount_xy).query(
                        apply(np.array([[h["cx"], h["cy"]] for h in rholes]), rreg3))
                    rep.check("right: case screw bosses coaxial with PCB holes",
                              rdh.max() <= args.screw_tol + 0.3, f"worst {rdh.max():.3f} mm")

    if args.json:
        print("__JSON__" + json.dumps({"ok": rep.ok, "checks": rep.rows}, default=float))
    print("\n" + ("PASS" if rep.ok else "FAIL"))
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
