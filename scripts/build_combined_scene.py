#!/usr/bin/env python3
"""Build filtered-output/combined_scene.glb — one coherent 3D scene, in one explicit frame.

Why this replaces create_full_3d_visual.py:

  * that script reads `filtered-output/cases/case.stl` and `cover.stl`, which are **legacy
    committed files that nothing regenerates** (the committed cover is dated March 2026). The
    generated parts are `l_case_3d.stl` / `r_case_3d.stl` / `l_cover.stl` / `r_cover.stl`, so the
    published scene has been built on a 16 mm case while the design is 11.2 mm;
  * it applies a magic `-90 deg` rotation about X and then "moves the PCB up 7 units", both tuned
    to the old 16 mm case, so the parts do not stack coherently (published: Case 0..16,
    PCB 0..1.51, Cover 25..32);
  * it merges raw GLB buffers with pygltflib, which is why nobody noticed.

Here every part is placed by a number derived from ergogen/config.yaml:

    z = 0                        case floor (case STL is already z-up, 0..case_border_height)
    z = bottom + standoff        PCB bottom        (+ PCB thickness -> PCB top)
    z = wall top                 FR4 plate underside (= case_border_height)
    z = wall top + plate         plate top / printed cover underside

The PCB 3D export arrives in the *PCB* frame (y flipped against the case frame, z up from the
board's bottom face), so it gets `y -> -y` and a z offset. Everything is then rotatable in the
viewer without anything floating.

Open the result at https://3dviewer.net/ (GLB keeps colours and part names).
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import numpy as np
import trimesh

TENTING_ANGLE = 6.5
TILTED = ("case", "plate", "pcb", "palm")   # ride on the wedge -> tilted
FLAT = ("tenting",)                       # sits on the desk -> flat  # from create_tenting_system.py; the old scene applied it to the case too

ROOT = Path(__file__).resolve().parent.parent


def units() -> dict:
    """Resolve the stack numbers from ergogen/config.yaml (expressions, not literals).

    Ergogen units reference each other top-down (`case_border_height` is built from
    `case_bottom_thickness + standoff_length + pcb_thickness + ...`), so evaluate iteratively
    against what has already resolved. Nothing here may be hardcoded: the old scene builder's
    magic offsets are exactly why the published 3D was 16 mm while the design was 11.2.
    """
    text = (ROOT / "ergogen/config.yaml").read_text(encoding="utf-8")
    exprs: dict[str, str] = {}
    for m in re.finditer(r"^\s{2}([a-z_]+):\s*([^\n#]+)", text, re.M):
        key, expr = m.group(1), m.group(2).strip()
        exprs.setdefault(key, expr)          # first definition wins (ergogen: top-down)
    resolved: dict[str, float] = {}
    for _ in range(12):
        progress = False
        for key, expr in exprs.items():
            if key in resolved:
                continue
            try:
                value = float(eval(expr, {"__builtins__": {}}, dict(resolved)))  # noqa: S307
            except Exception:
                continue
            resolved[key] = value
            progress = True
        if not progress:
            break
    need = ("case_bottom_thickness", "standoff_length", "pcb_thickness", "case_border_height")
    missing = [k for k in need if k not in resolved]
    if missing:
        sys.exit(f"could not resolve units from config.yaml: {missing}")
    return {
        "floor": resolved["case_bottom_thickness"],
        "standoff": resolved["standoff_length"],
        "pcb": resolved["pcb_thickness"],
        "plate": resolved.get("top_plate_thickness", 1.2),
        "wall_top": resolved["case_border_height"],
        # B23: the controller hood stands above the wall, so "how tall is the case" has two answers
        "hood_top": resolved.get("controller_hood_outer_top", resolved["case_border_height"]),
    }


def colour(mesh: trimesh.Trimesh, rgb) -> trimesh.Trimesh:
    """Paint a part with vertex colours. Transparency is NOT set here on purpose: giving a mesh a
    TextureVisuals material makes trimesh's glTF writer unshare vertices per face, so the part exports
    as triangle soup (that is what broke the palm rest). Alpha is patched into the exported GLB's
    materials by `apply_alpha()`, which is what the original scene did too."""
    mesh.visual.vertex_colors = np.tile(np.array([*rgb, 255], dtype=np.uint8),
                                        (len(mesh.vertices), 1))
    return mesh


def apply_alpha(path: Path, palette: dict[str, tuple[int, int, int]],
                alpha: float = 0.4) -> int:
    """Give every part its own material with its RGB and 40% alpha, like the original scene.

    The original carried 17 materials (one per part) with baseColorFactor [r,g,b,0.4]; relying on
    COLOR_0 vertex colours instead means a viewer that ignores vertex colours shows everything white,
    which is exactly what "many parts lack transparency/colour" looks like. So: patch the exported GLB
    and point each mesh at a material built from the part's colour.
    """
    from pygltflib import GLTF2, Material, PbrMetallicRoughness
    gltf = GLTF2().load(str(path))
    gltf.materials = []
    index: dict[str, int] = {}

    def material_for(name: str) -> int:
        rgb = (255, 255, 255)
        for key, col in palette.items():
            if key in name:
                rgb = col
                break
        if rgb in index:
            return index[rgb]
        gltf.materials.append(Material(
            name=f"part_{rgb[0]}_{rgb[1]}_{rgb[2]}",
            pbrMetallicRoughness=PbrMetallicRoughness(
                baseColorFactor=[rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, alpha],
                metallicFactor=0.0, roughnessFactor=0.9),
            alphaMode="BLEND", doubleSided=True))
        index[rgb] = len(gltf.materials) - 1
        return index[rgb]

    for mesh in gltf.meshes or []:
        mname = mesh.name or ""
        for prim in mesh.primitives or []:
            prim.material = material_for(mname)
    gltf.save(str(path))
    return len(gltf.materials)


def apply_node_tilt(path: Path, angle_deg: float = TENTING_ANGLE) -> int:
    """Rotate the ride-on-the-wedge nodes about Z, leaving the tenting base unrotated.

    trimesh bakes any transform passed to add_geometry into the vertices on export, so the tilt cannot
    be expressed as a node transform through it. The reference scene has the tilt as a node quaternion
    (with the -90 deg X conversion baked), so patch the exported GLB the same way - that also makes
    "is the base flat, is the keyboard tilted" answerable by reading the file.
    """
    from pygltflib import GLTF2
    gltf = GLTF2().load(str(path))
    half = math.radians(angle_deg) / 2.0
    q = [0.0, 0.0, math.sin(half), math.cos(half)]
    tilted = 0
    for node in gltf.nodes or []:
        name = (node.name or "").lower()
        if any(k in name for k in TILTED) and not any(k in name for k in FLAT):
            node.rotation = q
            tilted += 1
        elif any(k in name for k in FLAT):
            node.rotation = None
    gltf.save(str(path))
    return tilted


def load_mesh(path: Path) -> trimesh.Trimesh | None:
    if not path.exists():
        return None
    try:
        m = trimesh.load(path, force="mesh", process=True)
        if not len(m.faces):
            return None
        # trimesh computes vertex normals lazily and the glTF writer does not force the cache: without
        # this the part exports with POSITION only and every viewer shades it flat (visible facets).
        _ = m.vertex_normals
        return m
    except Exception as exc:                      # noqa: BLE001 - report and continue
        print(f"  ! {path.name}: {exc}")
        return None


def load_pcb(path: Path, z_bottom: float) -> trimesh.Trimesh | None:
    """PCB 3D export -> assembly frame: y flipped, lifted to its slot."""
    if not path.exists():
        return None
    try:
        scene = trimesh.load(path, force="scene")
    except Exception as exc:                      # noqa: BLE001
        print(f"  ! {path.name}: {exc}")
        return None
    parts = []
    for node in scene.graph.nodes_geometry:
        T, gname = scene.graph[node]
        geom = scene.geometry[gname]
        if geom is None or not len(geom.faces):
            continue
        m = geom.copy()
        m.apply_transform(T)
        parts.append(m)
    if not parts:
        return None
    pcb = trimesh.util.concatenate(parts)
    # concatenate drops normals, and the PCB's vertices are per-component (unshared), so recomputing
    # them gives per-face normals = faceted switches/keycaps. Rebuild the array in the same vertex
    # order from each source mesh's own normals and hand it to the cache.
    try:
        collected = []
        for node in scene.graph.nodes_geometry:
            T, gname = scene.graph[node]
            geom = scene.geometry[gname]
            if geom is None or not len(geom.faces):
                continue
            n = geom.vertex_normals.copy()
            R = T[:3, :3]
            n = n @ np.linalg.inv(R).T              # normals transform by the inverse-transpose
            ln = np.linalg.norm(n, axis=1, keepdims=True)
            collected.append(n / np.where(ln == 0, 1, ln))
        merged = np.vstack(collected)
        if merged.shape == pcb.vertex_normals.shape:
            pcb.vertex_normals = merged
    except Exception as exc:                        # noqa: BLE001
        print(f"  ! could not carry the PCB normals ({exc}); geometry will shade flat")
    # The KiBot glTF export is (x right, y = UP (keycap side), z = along the board). The assembly
    # frame is (x right, y along the board, z = UP), so it needs +90 deg about X:
    # (x, y, z) -> (x, -z, y). Proper rotation (det +1), so normals survive.
    pcb.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0]))
    # Anchor on the BOARD, not on the glTF origin: the export's board plane sits ~0.17 mm off zero and
    # the MCU header pins reach 11 mm below it, so translating the raw origin puts the board 0.2 mm out
    # of its slot. Find the two biggest flat faces 1.6 mm apart (board bottom/top) and align the lower.
    c, a = pcb.triangles_center, pcb.area_faces
    h, edges = np.histogram(c[:, 2], bins=400, weights=a)
    centres = 0.5 * (edges[:-1] + edges[1:])
    # candidate faces = local maxima that carry real area (the board's two copper faces are the
    # biggest flat surfaces; header pins and sockets are thin slivers)
    cand = [i for i in range(1, len(h) - 1)
            if h[i] >= h[i - 1] and h[i] >= h[i + 1] and h[i] > 0.05 * h.max()]
    best = None
    for i in cand:
        for j in cand:
            if 1.25 <= centres[j] - centres[i] <= 1.95:      # 1.6 mm board, generous tolerance
                score = h[i] + h[j]
                if best is None or score > best[0]:
                    best = (score, float(centres[i]))
    board_lo = best[1] if best else float(pcb.bounds[0][2])
    print(f"  board plane found at z {board_lo:.2f} -> lifted to {z_bottom:.2f}"
          if best else "  ! could not find the board slab; using the raw origin")
    pcb.apply_translation([0.0, 0.0, z_bottom - board_lo])
    return pcb


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="filtered-output/combined_scene.glb")
    ap.add_argument("--sides", default="l,r")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    u = units()
    wall_top = u["wall_top"]
    pcb_bottom = u["floor"] + u["standoff"]
    pcb_top = pcb_bottom + u["pcb"]
    plate_top = wall_top + u["plate"]
    hood_top = u["hood_top"]
    print(f"stack from config: floor {u['floor']} + standoff {u['standoff']} -> PCB {pcb_bottom:.2f}"
          f"..{pcb_top:.2f}; wall top {wall_top:.2f}; plate underside {wall_top:.2f}"
          f"..{plate_top:.2f}")

    scene = trimesh.Scene()
    parts: list[tuple[str, trimesh.Trimesh, bool]] = []   # (node name, mesh, tilts with the case)

    for side in [s.strip() for s in args.sides.split(",") if s.strip()]:
        tag = "left" if side == "l" else "right"

        case = load_mesh(ROOT / f"filtered-output/cases/{side}_case_3d.stl")
        if case is not None:
            parts.append((f"1-case_{tag} (printed, incl. controller hood)",
                          colour(case, (200, 200, 208)), True))

        # FR4 plate: the lid, sitting ON the wall (B20 option D)
        plate = load_mesh(ROOT / f"export3d/plate_{tag}_full.stl")
        if plate is not None:
            plate.apply_translation([0, 0, wall_top - plate.bounds[0][2]])
            parts.append((f"2-plate_{tag} (FR4 1.2mm - the lid, butts against the hood)",
                          colour(plate, (26, 90, 52)), True))

        pcb = load_pcb(ROOT / f"filtered-output/pcbs/3d/{tag}_pcb-3d.glb", pcb_bottom)
        if pcb is not None:
            parts.append((f"3-pcb_{tag} (board + switches + keycaps)",
                          colour(pcb, (30, 110, 70)), True))

    # the tenting wedge stays on the desk; the case (and everything bolted to it) tilts onto it.
    # The old scene applied TENTING_ANGLE = 6.5 deg to Case/Cover/Palm_Rest and left Tenting_System
    # flat, which is why its parts lined up.
    tenting = load_mesh(ROOT / "filtered-output/cases/tenting_system.stl")
    if tenting is not None:
        parts.append(("4-tenting_system (desk, untilted)", colour(tenting, (120, 150, 190)),
                      False))

    palm_rest = load_mesh(ROOT / "filtered-output/palmrest/palm_rest.stl")
    if palm_rest is not None:
        # No translation: the original scene placed it exactly as authored and it looked right. It
        # overlaps the case footprint on purpose (it slides under the front wall) - my earlier "flush
        # against the front edge" shift was invented, not measured against anything.
        parts.append(("5-palm_rest (front, flush against the case)",
                      colour(palm_rest, (150, 160, 190)), True))

    if not parts:
        sys.exit("nothing to merge: no case/plate/PCB outputs found")

    # ---- coherence, measured FLAT (the tilt would make these numbers meaningless) ----------------
    problems = []
    for name, mesh, _ in parts:
        lo, hi = mesh.bounds[0][2], mesh.bounds[1][2]
        # hotswap sockets hang BELOW the board and keycaps sit above it, so allow both: this checks
        # that the board is in its slot, not that nothing protrudes.
        if name.startswith("3-pcb") and not (pcb_bottom - 12.0 <= lo <= pcb_top + 6.0):
            problems.append(f"{name} z {lo:.2f}..{hi:.2f} (expected to sit at {pcb_bottom:.2f})")
        if name.startswith("2-plate") and not abs(lo - wall_top) < 0.1:
            problems.append(f"{name} z {lo:.2f} (expected plate underside {wall_top:.2f})")
        # B23: the case is no longer flat-topped - the controller hood rises above the wall - so the
        # expected top is the taller of the two, and which one it is gets printed.
        if name.startswith("1-case") and not (abs(hi - wall_top) < 0.6 or abs(hi - hood_top) < 0.6):
            problems.append(f"{name} z top {hi:.2f} (expected wall top {wall_top:.2f} "
                            f"or hood top {hood_top:.2f})")
    if problems:
        print("\nINCOHERENT STACK:")
        for p_ in problems:
            print("  -", p_)
        return 1

    # ---- orientation, copied from the scene that looked right ---------------------------------
    # create_full_3d_visual.py rotated every STL -90 deg about X (z-up -> glTF y-up) and then applied
    # TENTING_ANGLE = 6.5 deg about Z to Case/Cover/Palm_Rest, leaving Tenting_System flat: the desk
    # base does not tilt, the keyboard that sits on it does. Reproduce that exactly.
    y_up = trimesh.transformations.rotation_matrix(-np.pi / 2.0, [1, 0, 0])
    tilt_z = trimesh.transformations.rotation_matrix(math.radians(TENTING_ANGLE), [0, 0, 1])
    for _n, mesh, tilts in parts:
        mesh.apply_transform(y_up)
    print(f"orientation: -90 deg about X for all parts; {TENTING_ANGLE} deg about Z for the case, "
          f"plate, PCB and palm rest; tenting base left flat")

    for name, mesh, _tilts in parts:
        scene.add_geometry(mesh, node_name=name)   # tilt goes on the NODE after export

    out = ROOT / args.out
    scene.export(out)
    palette = {
        "case": (200, 200, 208), "plate": (26, 90, 52), "pcb": (30, 110, 70),
        "tenting": (120, 150, 190), "palm": (150, 160, 190),
    }
    n_mat = apply_alpha(out, palette, 0.4)
    n_tilt = apply_node_tilt(out, TENTING_ANGLE)
    print(f"materials: {n_mat} set to 40% alpha, alphaMode BLEND (as in the original scene)")
    print(f"node tilt: {n_tilt} node(s) at {TENTING_ANGLE} deg about Z; tenting base left flat")
    b = scene.bounds
    print(f"wrote {args.out}: {len(scene.geometry)} parts, "
          f"x {b[0][0]:.1f}..{b[1][0]:.1f}  y {b[0][1]:.1f}..{b[1][1]:.1f}  z {b[0][2]:.1f}..{b[1][2]:.1f} mm")
    print(f"stack coherent: plate underside == wall top {wall_top:.2f}, case top == hood top "
          f"{hood_top:.2f}, PCB in its slot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
