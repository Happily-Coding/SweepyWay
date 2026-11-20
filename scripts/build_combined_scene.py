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
import re
import sys
from pathlib import Path

import numpy as np
import trimesh

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
    mesh.visual.vertex_colors = np.tile(np.array([*rgb, 255], dtype=np.uint8), (len(mesh.vertices), 1))
    return mesh


def load_mesh(path: Path) -> trimesh.Trimesh | None:
    if not path.exists():
        return None
    try:
        m = trimesh.load(path, force="mesh", process=True)
        return m if len(m.faces) else None
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
    # The KiBot glTF export is (x right, y = UP (keycap side), z = along the board). The assembly
    # frame is (x right, y along the board, z = UP), so it needs +90 deg about X:
    # (x, y, z) -> (x, -z, y). Proper rotation (det +1), so normals survive.
    pcb.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2.0, [1, 0, 0]))
    pcb.apply_translation([0.0, 0.0, z_bottom])
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
    added = []

    for side in [s.strip() for s in args.sides.split(",") if s.strip()]:
        tag = "left" if side == "l" else "right"

        case = load_mesh(ROOT / f"filtered-output/cases/{side}_case_3d.stl")
        if case is not None:
            scene.add_geometry(colour(case, (200, 200, 208)), node_name=f"case_{tag}")

        # FR4 plate: the lid, sitting ON the wall (B20 option D)
        plate = load_mesh(ROOT / f"export3d/plate_{tag}_full.stl")
        if plate is not None:
            plate.apply_translation([0, 0, wall_top - plate.bounds[0][2]])
            scene.add_geometry(colour(plate, (26, 90, 52)), node_name=f"plate_{tag} (FR4)")

        pcb = load_pcb(ROOT / f"filtered-output/pcbs/3d/{tag}_pcb-3d.glb", pcb_bottom)
        if pcb is not None:
            scene.add_geometry(colour(pcb, (30, 110, 70)), node_name=f"pcb_{tag}")

        added.append(tag)

    tenting = load_mesh(ROOT / "filtered-output/cases/tenting_system.stl")
    if tenting is not None:
        scene.add_geometry(colour(tenting, (170, 170, 180)), node_name="tenting_system")

    palm_rest = load_mesh(ROOT / "filtered-output/palmrest/palm_rest.stl")
    if palm_rest is not None:
        # The palm rest model is authored above the board's front edge; park it beside the case
        # rather than guessing a placement that would look authoritative and be wrong.
        palm_rest.apply_translation([0, 0, 0])
        scene.add_geometry(colour(palm_rest, (150, 160, 190)), node_name="palm_rest (own frame)")

    if not scene.geometry:
        sys.exit("nothing to merge: no case/plate/PCB outputs found")

    out = ROOT / args.out
    scene.export(out)
    b = scene.bounds
    print(f"wrote {args.out}: {len(scene.geometry)} parts, "
          f"x {b[0][0]:.1f}..{b[1][0]:.1f}  y {b[0][1]:.1f}..{b[1][1]:.1f}  z {b[0][2]:.1f}..{b[1][2]:.1f} mm")
    # coherence assertions: this is the check the old script never had
    problems = []
    for name, mesh in scene.geometry.items():
        lo, hi = mesh.bounds[0][2], mesh.bounds[1][2]
        if "pcb" in name and not (pcb_bottom - 0.5 <= lo <= pcb_top + 6.0):
            problems.append(f"{name} z {lo:.2f}..{hi:.2f} (expected to sit at {pcb_bottom:.2f})")
        if "plate" in name and not abs(lo - wall_top) < 0.1:
            problems.append(f"{name} z {lo:.2f} (expected plate underside {wall_top:.2f})")
        # B23: the case is no longer flat-topped - the controller hood rises above the wall - so the
        # expected top is the taller of the two, and which one it is gets printed.
        if "case" in name and not (abs(hi - wall_top) < 0.6 or abs(hi - hood_top) < 0.6):
            problems.append(f"{name} z top {hi:.2f} (expected wall top {wall_top:.2f} "
                            f"or hood top {hood_top:.2f})")
    if problems:
        print("\nINCOHERENT STACK:")
        for p in problems:
            print("  -", p)
        return 1
    print(f"stack coherent: plate underside == wall top {wall_top:.2f}, case top == hood top "
          f"{hood_top:.2f}, PCB in its slot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
