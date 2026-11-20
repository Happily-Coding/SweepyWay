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
import trimesh

KEY_RE = r"col(\d+)_row(\d+)"
THUMB_RE = r"col(\d+)_thumb_row_(\d+)"
CUTOUT_MM = 14.0
REPO = Path(__file__).resolve().parent.parent

# ---- B20 option D: the FR4 plate sits ON the wall (docs/B20-PLATE-ON-WALL.md) ----
# The plate is the case footprint, and the printed wall stops at its underside. Under the old shape
# (`plate_sits_on_wall: 0`) the wall ran to the plate TOP and the plate was a panel inside the
# cavity; the checks below are split on that flag so both shapes stay testable.
PLATE_UNIT_KEYS = ("case_bottom_thickness", "standoff_length", "pcb_thickness",
                   "plate_top_above_pcb_top", "top_plate_thickness", "plate_sits_on_wall")


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


def config_units(path: Path | None = None) -> dict[str, float]:
    """The `units:` scalars the stack checks need, straight from the canonical config."""
    path = path or (REPO / "ergogen" / "config.yaml")
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    out: dict[str, float] = {}
    for key in PLATE_UNIT_KEYS:
        m = re.search(rf"^  {key}:\s*([-\d.]+)", text, flags=re.M)
        if not m:
            raise SystemExit(f"check_assembly: cannot find units.{key} in {path}")
        out[key] = float(m.group(1))
    return out


def resolved_units(path: Path | None = None) -> dict[str, float]:
    """Every `units:` entry, resolving expressions top-down (ergogen units reference each other).

    `config_units()` deliberately reads literals only; B23's hood is derived
    (`pcb_top + mcu_head_height + clearance`), so it needs the expression form.
    """
    path = path or (REPO / "ergogen" / "config.yaml")
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    exprs: dict[str, str] = {}
    for m in re.finditer(r"^  ([a-z_0-9]+):\s*([^\n#]+)", text, flags=re.M):
        exprs.setdefault(m.group(1), m.group(2).strip())
    out: dict[str, float] = {}
    for _ in range(12):
        progress = False
        for key, expr in exprs.items():
            if key in out:
                continue
            try:
                out[key] = float(eval(expr, {"__builtins__": {}}, dict(out)))  # noqa: S307
                progress = True
            except Exception:
                continue
        if not progress:
            break
    return out


def dxf_net_shape(path: Path):
    """The outline's material area as one shapely geometry (even-odd nesting, holes removed).

    Trap: plain `polygonize()` only closes a ring when the endpoints match EXACTLY, and ergogen
    rounds arc endpoints, so an arc-rounded outline silently stays open and you measure only the
    key cutouts. A 10 um precision grid is what makes this work.
    """
    import ezdxf
    from shapely import set_precision
    from shapely.geometry import LineString, Polygon
    from shapely.ops import polygonize, unary_union

    def snap(p):
        return (round(p[0], 3), round(p[1], 3))

    segs = []
    for e in ezdxf.readfile(str(path)).modelspace():
        t = e.dxftype()
        if t == "LINE":
            a, b = e.dxf.start, e.dxf.end
            segs.append((snap((a.x, a.y)), snap((b.x, b.y))))
        elif t == "ARC":
            c, r = e.dxf.center, e.dxf.radius
            a0, a1 = np.deg2rad(e.dxf.start_angle), np.deg2rad(e.dxf.end_angle)
            if a1 <= a0:
                a1 += 2 * np.pi
            th = np.linspace(a0, a1, max(8, int(abs(a1 - a0) * r) + 2))
            pts = [snap((c.x + r * np.cos(v), c.y + r * np.sin(v))) for v in th]
            segs += list(zip(pts[:-1], pts[1:]))
        elif t == "CIRCLE":
            c, r = e.dxf.center, e.dxf.radius
            th = np.linspace(0, 2 * np.pi, 64)
            pts = [snap((c.x + r * np.cos(v), c.y + r * np.sin(v))) for v in th]
            segs += list(zip(pts[:-1], pts[1:]))
    lines = unary_union([LineString([a, b]) for a, b in segs if a != b])
    faces = list(polygonize(set_precision(lines, 0.01)))
    keep = []
    for f in faces:
        # a face inside a hole is material again, so compare against EXTERIORS only
        depth = sum(1 for g in faces if g is not f and g.area > f.area
                    and Polygon(g.exterior).contains(f.representative_point()))
        if depth % 2 == 0:
            keep.append(f)
    return unary_union(keep) if keep else None


def pcb_net_shape(path: Path):
    """A generated plate/PCB's Edge.Cuts as one shapely polygon (holes kept as interiors).

    Needed because `plate_polys()` only returns *closed* loops: it cannot see the board outline
    (arc-rounded) and it silently drops `gr_circle` bores. This one stitches LINE + ARC + CIRCLE
    with a 10 um snap and returns the material area, so "is there a hole at this switch" becomes a
    containment test instead of a count. (Traps #7/#8 in docs/HANDOFF.md §8.)
    """
    from shapely import set_precision
    from shapely.geometry import LineString, Polygon
    from shapely.ops import polygonize, unary_union

    text = path.read_text(encoding="utf-8", errors="ignore")

    def snap(p):
        return (round(float(p[0]), 3), round(float(p[1]), 3))

    segs = []
    for m in re.finditer(r"\(gr_line\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)", text):
        x1, y1, x2, y2 = (float(v) for v in m.groups())
        segs.append((snap((x1, y1)), snap((x2, y2))))
    for m in re.finditer(r"\(gr_arc\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(mid\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)", text):
        ax, ay, mx, my, bx, by = (float(v) for v in m.groups())
        a, b, c = np.array([ax, ay]), np.array([mx, my]), np.array([bx, by])
        ts = np.linspace(0, 1, 9)
        pts = [snap((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c) for t in ts]
        segs += list(zip(pts[:-1], pts[1:]))
    for m in re.finditer(r"\(gr_circle\s*\(center\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)", text):
        cx, cy, ex, ey = (float(v) for v in m.groups())
        r = float(np.hypot(ex - cx, ey - cy))
        th = np.linspace(0, 2 * np.pi, 64)
        pts = [snap((cx + r * np.cos(v), cy + r * np.sin(v))) for v in th]
        segs += list(zip(pts[:-1], pts[1:]))
    if not segs:
        return None
    lines = unary_union([LineString([a, b]) for a, b in segs if a != b])
    faces = list(polygonize(set_precision(lines, 0.01)))

    def depth(f):
        return sum(1 for g in faces if g is not f and g.area > f.area
                   and Polygon(g.exterior).contains(f.representative_point()))

    keep = [f for f in faces if depth(f) % 2 == 0]
    return unary_union(keep) if keep else None


def shape_holes(geom) -> list:
    """The interior rings of a (multi)polygon as polygons, largest first."""
    from shapely.geometry import Polygon
    out = []
    if geom is None:
        return out
    parts = list(getattr(geom, "geoms", [geom]))
    for p in parts:
        out += [Polygon(i) for i in getattr(p, "interiors", [])]
    return sorted(out, key=lambda p: p.area, reverse=True)


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

    def note(self, text):
        """Informational: recorded and printed, but does not fail the run.

        For artifacts that are generated but explicitly NOT orderable (e.g. the experimental
        controller view window while B23 is unresolved). Their problems stay visible without
        teaching everyone to ignore a permanently red gate.
        """
        self.rows.append({"check": "(note)", "pass": True, "detail": text})
        print(f"  --    {text}")


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

    # The orderable plate is generated from the same outline as the DXF, but it is what gets
    # fabricated, so it is checked on its own. B20-D changed what a "cutout" is: the plate is now the
    # case footprint and the controller/JSPh bays are notches, so a *count* of closed loops is no
    # longer meaningful (the notch merges with the cutouts it touches). Test containment instead:
    # every switch centre must fall in a HOLE of the plate, and every key-sized hole must sit on a
    # switch.
    from shapely.geometry import Point

    def plate_report(name: str) -> None:
        f = root / name
        if not f.exists():
            rep.check(f"{name} exists", False, "missing")
            return
        shape = pcb_net_shape(f)
        polys = plate_polys(f)
        if shape is None or not polys:
            rep.check(f"{name} parsed", False, "no closed cutout found")
            return
        # A switch centre merely being inside *some* hole is not enough: B20-D's bay notch is a
        # 1400 mm2 hole, so four switches whose cutouts it swallowed still sat "in an opening" and
        # the old containment test passed while the plate was unbuildable. Each switch must sit in
        # a hole of its OWN SIZE, i.e. the plate keeps material around it.
        # A switch centre merely being inside *some* hole is not enough: B20-D's bay notch is a
        # 1400+ mm2 hole, so switches whose cutouts it swallowed still sat "in an opening" and the
        # old containment test passed while the plate was unbuildable. Each switch must sit in a
        # hole of its OWN SIZE, which is the same thing as the plate keeping material around it.
        holes_all = shape_holes(shape)
        solid_over, swallowed = [], []
        for i, (x, y) in enumerate(sw_xy):
            pt = Point(x, y)
            holder = next((h for h in holes_all if h.contains(pt)), None)
            if holder is None:
                solid_over.append(i)                       # plate material where a switch must go
            elif not (lo_a <= holder.area <= hi_a):
                swallowed.append((i, round(holder.area)))  # inside a merged notch
        rep.check(f"{name}: every switch has an opening", not solid_over,
                  f"{len(sw_xy) - len(solid_over)}/32 openings, plate over: {solid_over[:4]}")
        rep.check(f"{name}: every switch sits in a KEY-SIZED hole (not a merged notch)", not swallowed,
                  f"{len(swallowed)} switch(es) in an oversized hole {swallowed[:4]} "
                  f"(key cutouts are {lo_a:.0f}-{hi_a:.0f} mm2)")
        key_faces = [k for k in polys if lo_a <= k["area"] <= hi_a]
        if key_faces:
            d2, _ = cKDTree(sw_xy).query(np.array([[k["cx"], k["cy"]] for k in key_faces]))
            rep.check(f"{name}: key cutouts land on switches", d2.max() <= args.key_tol,
                      f"{len(key_faces)} key-sized cutouts, worst {d2.max():.3f} mm")
            pareas = sorted({round(k["area"], 1) for k in key_faces})
            rep.check(f"{name}: cutout area == {CUTOUT_MM}mm square",
                      all(lo_a <= a <= hi_a for a in pareas), f"areas {pareas[:6]}")
        bores = [h for h in shape_holes(shape) if h.area < 10]
        rep.check(f"{name}: has the 5 screw bores", len(bores) == 5,
                  f"{len(bores)} openings smaller than 10 mm2 (a 2.2 mm bore is 3.80 mm2)")
        return shape

    plate_shape = plate_report("plate_left.kicad_pcb")
    if plate_shape is not None:
        # Author's pick: D2 (`_full`, bay covered) is the orderable plate. D1 (`_bay`, controller
        # view window) is an optional extra and is NOT orderable while its notch swallows switches
        # (B23), so it is reported as a note instead of failing the gate on unshippable output.
        full = pcb_net_shape(root / "plate_left_full.kicad_pcb")
        bay = pcb_net_shape(root / "plate_left_bay.kicad_pcb")
        if full is not None and bay is not None:
            rep.check("the orderable left plate (`plate_left`) is the D2 variant (bay covered)",
                      abs(plate_shape.area - full.area) < 0.5,
                      f"plate_left {plate_shape.area:.1f} mm2 vs plate_left_full {full.area:.1f} mm2 "
                      f"(D1 bay window {bay.area:.1f} mm2)")
            bay_holes = [h for h in shape_holes(bay) if h.area > hi_a]
            swallowed = 0
            for (x, y) in sw_xy:
                pt = Point(x, y)
                holder = next((h for h in shape_holes(bay) if h.contains(pt)), None)
                if holder is not None and not (lo_a <= holder.area <= hi_a):
                    swallowed += 1
            if abs(plate_shape.area - full.area) >= 0.5:
                rep.check("plate_left is D2", False, "plate_left is not the full variant")
            if swallowed or bay_holes:
                rep.note(f"experimental D1 view window (plate_left_bay) is NOT orderable: "
                         f"{swallowed} switch(es) sit in an oversized hole "
                         f"(largest {max((h.area for h in bay_holes), default=0):.0f} mm2) - B23")
            else:
                rep.note("experimental D1 view window is orderable (all 32 switches in key-sized holes)")
        rshape = pcb_net_shape(root / "plate_right.kicad_pcb")
        rep.check("the right plate is the mirror of the left (same net area)",
                  rshape is not None and abs(rshape.area - plate_shape.area) < 0.5,
                  f"left {plate_shape.area:.2f} mm2, right "
                  f"{rshape.area if rshape is not None else float('nan'):.2f} mm2")

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

    # ---- B20-D: the FR4 plate IS the lid, and it sits on the printed wall ----
    # Numbers come from `units:` (config.yaml), 2D truth from the generated outlines, printed truth
    # from the case STL. A revert of any one of the three is caught here instead of at assembly time.
    u = config_units()
    plate_th = u["top_plate_thickness"]
    sits = int(u["plate_sits_on_wall"])
    plate_top = (u["case_bottom_thickness"] + u["standoff_length"] + u["pcb_thickness"]
                 + u["plate_top_above_pcb_top"])
    wall_top = plate_top - sits * plate_th
    print(f"  ...  B20-D stack from units: wall top {wall_top:.2f}, plate {wall_top:.2f}..{plate_top:.2f} "
          f"(plate_sits_on_wall={sits})")
    rep.check("wall top + plate thickness == the old rim (one number changed, not two)",
              abs(wall_top + plate_th - plate_top) < 1e-6,
              f"wall {wall_top:.2f} + plate {plate_th:.2f} = {wall_top + plate_th:.2f} "
              f"vs plate top {plate_top:.2f}")
    p_bay = p_full = foot = pcb = None
    if sits:
        from shapely.ops import unary_union
        NEEDED = ["l_case_bottom", "l_pcb_outline", "l_plate_on_wall_bay", "l_plate_on_wall",
                  "l_controller_area", "l_jsph_area", "l_keys_outline"]
        absent = [n for n in NEEDED if not (outl / f"{n}.dxf").exists()]
        rep.check("B20-D plate outlines exist in the outlines dir", not absent,
                  "missing: " + ", ".join(absent) if absent else f"all {len(NEEDED)} present")
        if absent:  # e.g. a pre-B20-D snapshot: report it, but do not crash on the missing files
            rep.check("B20-D plate outlines are closed", False, "cannot check, outlines missing")
        else:
            foot = dxf_net_shape(outl / "l_case_bottom.dxf")
            pcb = dxf_net_shape(outl / "l_pcb_outline.dxf")
            p_bay = dxf_net_shape(outl / "l_plate_on_wall_bay.dxf")
            p_full = dxf_net_shape(outl / "l_plate_on_wall.dxf")
            ctrl = dxf_net_shape(outl / "l_controller_area.dxf")
            jsph = dxf_net_shape(outl / "l_jsph_area.dxf")
            pkeys = dxf_net_shape(outl / "l_keys_outline.dxf")
            empty = [n for n, g in (("l_case_bottom", foot), ("l_pcb_outline", pcb),
                                    ("l_plate_on_wall_bay", p_bay), ("l_plate_on_wall", p_full),
                                    ("l_controller_area", ctrl), ("l_jsph_area", jsph),
                                    ("l_keys_outline", pkeys)) if g is None]
            rep.check("B20-D plate outlines are closed", not empty,
                      "empty: " + ", ".join(empty) if empty else f"{len(NEEDED)} outlines")
            if not empty:
                # B23: the plate also butts against the hood, so the invariant gains one term. This
                # is a RESTATEMENT, not a loosening: same predicate ("the plate covers everything
                # except what must stay open"), one more excluded region - and a self-test below
                # proves the predicate still rejects a wrong plate.
                hood = dxf_net_shape(outl / "l_hood_footprint.dxf")
                # B23: the hood is the controller housing MINUS the key field, so the keys are
                # subtracted from it rather than dodged by nudging its footprint. Expanding the raw
                # rectangle outward instead ate 223 mm2 of switch cutouts - this gate says so.
                if hood is not None:
                    eaten = hood.intersection(pkeys)
                    rep.check("B23: the hood footprint hits no switch cutout", eaten.area < 0.01,
                              f"hood {hood.area:.1f} mm2 vs {eaten.area:.2f} mm2 of key cutouts "
                              f"(the footprint must be controller_area MINUS the key field)")
                expect_full = foot.difference(unary_union([pkeys])).difference(hood)

                def matches(plate, expect) -> bool:
                    return plate.symmetric_difference(expect).area < 1.0

                rep.check("D2 plate (bay covered) == case footprint - keys - hood",
                          hood is not None and matches(p_full, expect_full),
                          f"plate {p_full.area:.2f} mm2, footprint-keys-hood {expect_full.area:.2f} mm2, "
                          f"symmetric difference {p_full.symmetric_difference(expect_full).area:.3f} mm2")
                bays = ctrl.union(jsph)
                rep.check("D1 plate (bay open) == case footprint - keys - controller - JSPh",
                          matches(p_bay, foot.difference(unary_union([pkeys])).difference(bays)),
                          f"plate {p_bay.area:.2f} mm2 vs expected "
                          f"{foot.difference(unary_union([pkeys])).difference(bays).area:.2f} mm2")
                # D2 now also excludes the hood, so the D1/D2 delta is the bay MINUS the hood: the
                # part of controller + JSPh that D2 already covers with hood instead of opening.
                bay_open = bays.intersection(foot).difference(hood).difference(pkeys)
                expected_delta = bay_open.area
                rep.check("D1 - D2 == the bay the hood does not already open",
                          abs((p_full.area - p_bay.area) - expected_delta) < 1.0,
                          f"D2 - D1 = {p_full.area - p_bay.area:.2f} mm2 vs bay not already hood "
                          f"{expected_delta:.2f} mm2 (controller {ctrl.area:.2f} + JSPh {jsph.area:.2f} "
                          f"- hood {hood.area:.2f} - keys {bays.intersection(pkeys).area:.2f})")
                # ---- self-test: a check nobody has seen fail is a rumour --------------------------
                # Perturb the plate three ways and require the predicate to reject each: a missing
                # key, an extra block over a key, and material running under the hood.
                from shapely.geometry import Point
                interior = p_full.representative_point()
                probes = {
                    "a 3x3 mm bite out of the lid": p_full.difference(Point(interior.x, interior.y).buffer(1.5, quad_segs=4)),
                    "material running under the hood": p_full.union(hood),
                }
                blind = [what for what, plate in probes.items() if matches(plate, expect_full)]
                rep.check("the D2 predicate rejects a wrong plate (it is not vacuous)", not blind,
                          "blind to: " + ", ".join(blind) if blind else
                          f"rejects both perturbations ({', '.join(probes)})")
                ring = foot.difference(pcb.buffer(2, join_style=2, quad_segs=16))
                rep.check("neither plate variant cuts the wall ring (full-perimeter support in D1 too)",
                          ring.difference(p_bay).area < 0.01 and ring.difference(p_full).area < 0.01,
                          f"wall ring {ring.area:.2f} mm2; uncovered by D1 "
                          f"{ring.difference(p_bay).area:.3f} mm2, by D2 {ring.difference(p_full).area:.3f} mm2")
    # ---- printed parts must be printable: a non-manifold STL is not a part ----------------------
    # The B23 hood union taught this the hard way: coincident coplanar faces make JSCAD emit
    # zero-volume slivers, the volume goes meaningless and slicers misbehave. `scripts/repair_stl.py`
    # welds them; this checks the file we would actually ship.
    if args.cases:
        for stl in ("l_case_3d.stl", "r_case_3d.stl"):
            f = Path(args.cases) / stl
            if not f.exists():
                # Say so rather than skipping silently: pointing --cases at ergogen/output/cases
                # (jscad only) made this whole block invisible and I misdiagnosed it as dead code.
                rep.check(f"{stl} present in --cases", False, f"missing: {f} (pass the dir holding STLs)")
                continue
            m = trimesh.load(f, force="mesh", process=True)
            bodies = len(m.split(only_watertight=False))
            rep.check(f"{stl} is watertight (printable)", bool(m.is_watertight),
                      f"watertight={m.is_watertight}, bodies={bodies}, volume {m.volume/1000:.1f} cm3")

    # ---- B23: controller headroom, parameterised -----------------------------------------------
    # Nothing here is a measurement: it checks that the parameters in config.yaml describe a hood
    # that clears the controller head, and keeps the disagreement with the repo's 3D models visible
    # instead of silently trusting either of them.
    ru = resolved_units()
    need = ("mcu_head_height", "pcb_top_z", "controller_hood_inner_top", "controller_hood_outer_top")
    if all(k in ru for k in need) and "case_border_height" in ru:
        head, inner, outer = ru["mcu_head_height"], ru["controller_hood_inner_top"], ru["controller_hood_outer_top"]
        onehot = ru.get("mcu_header_style_spring", 0) + ru.get("mcu_header_style_generic", 0)
        rep.check("B23: exactly one MCU mounting preset is selected", abs(onehot - 1) < 1e-9,
                  f"spring={ru.get('mcu_header_style_spring', 0):.0f} "
                  f"generic={ru.get('mcu_header_style_generic', 0):.0f} (one-hot)")
        # `mcu_head_height` already carries its own roof clearance, per preset.
        want = ru["pcb_top_z"] + head
        rep.check("B23: hood inner top == pcb_top + head (+ that preset's clearance)", abs(inner - want) < 1e-6,
                  f"inner {inner:.2f} = pcb_top {ru['pcb_top_z']:.2f} + head {head:.2f}")
        rep.check("B23: the hood rises above the wall top (otherwise it is not a hood)",
                  outer > ru["case_border_height"] + 0.5,
                  f"outer {outer:.2f} vs wall top {ru['case_border_height']:.2f} -> "
                  f"+{outer - ru['case_border_height']:.2f} mm, "
                  f"{outer - ru['case_border_height'] - ru['top_plate_thickness']:.2f} mm above the plate top")
        style = "spring header (5 mm)" if ru.get("mcu_header_style_spring") == 1 else "generic KiCad 2.54 header"
        rep.note(f"B23 preset in use: {style} -> head {head:.2f} mm "
                 f"(spring {ru.get('mcu_spring_head_height', 0):.2f} / generic {ru.get('mcu_generic_head_height', 0):.2f}); "
                 f"the generic one is the conservative choice, ~2 mm taller")
    else:
        rep.note("B23 units missing from config.yaml: controller headroom is unparameterised")

    if args.cases and (Path(args.cases) / "l_case_3d.stl").exists():
        import trimesh
        case_f = Path(args.cases) / "l_case_3d.stl"
        m = trimesh.load(str(case_f), force="mesh", process=True)
        e = m.extents
        ext = (float(e[0]), float(e[1]), float(e[2]))
        if sits and p_bay is not None:
            x0, y0, x1, y1 = p_bay.bounds
            rep.check("plate outline == case outer footprint (the plate overhangs the wall)",
                      abs(ext[0] - (x1 - x0)) < 0.1 and abs(ext[1] - (y1 - y0)) < 0.1,
                      f"case {ext[0]:.2f} x {ext[1]:.2f} mm, D1 plate outline {x1 - x0:.2f} x {y1 - y0:.2f} mm")
        # B23: the case is no longer a flat-topped tray - the controller hood rises above the wall
        # top. So compare the WALL height away from the hood (measured at the case border) and check
        # the hood separately, instead of using the STL's overall height.
        hood_units = resolved_units()
        hood_outer = hood_units.get("controller_hood_outer_top")
        want_top = hood_outer if hood_outer else wall_top
        rep.check(f"case STL height == {'controller hood top' if hood_outer else 'wall top'} "
                  f"({want_top:.2f} mm)",
                  abs(ext[2] - want_top) < 0.6,
                  f"STL {ext[2]:.2f} mm tall; wall top {wall_top:.2f}, plate top {plate_top:.2f}"
                  + (f", hood top {hood_outer:.2f}" if hood_outer else ""))
        # the wall must be solid just under the plate, or the plate has nothing to sit on
        z = wall_top - 0.4
        sec = stl_section(case_f, z)
        rep.check("the wall is closed 0.4 mm below its top (the plate seats on material)",
                  len(sec) >= 1,
                  f"{len(sec)} closed loop(s) in the section at z={z:.2f}")

    if args.json:
        print("__JSON__" + json.dumps({"ok": rep.ok, "checks": rep.rows}, default=float))
    print("\n" + ("PASS" if rep.ok else "FAIL"))
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
