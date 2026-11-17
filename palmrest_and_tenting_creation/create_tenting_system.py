import argparse
import os

import trimesh
import numpy as np
from shapely.geometry import Polygon, Point, MultiPolygon
from scipy.spatial import cKDTree
from trimesh.creation import triangulate_polygon

def polygon_to_numpy(polygon: Polygon) -> np.ndarray:
    coords = np.array(polygon.exterior.coords)
    if np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]
    return coords

def add_height(poly2d: np.ndarray, z: float) -> np.ndarray:
    n = poly2d.shape[0]
    return np.column_stack((poly2d, np.full(n, z)))

def interpolate_edges(points: np.ndarray, steps: int = 10) -> np.ndarray:
    interpolated = []
    n = len(points)
    for i in range(n):
        p0 = points[i]
        p1 = points[(i + 1) % n]
        for t in np.linspace(0, 1, steps, endpoint=False):
            interp = (1 - t) * p0 + t * p1
            interpolated.append(interp)
    return np.array(interpolated)

def find_smallest_x(points: np.ndarray) -> float:
    return np.min(points[:, 0])

def calculate_point_z(x, z_min, angle_rad, x_smallest) -> float:
    return z_min + np.tan(angle_rad) * (x - x_smallest)

def adjust_z(points: np.ndarray, z_min, angle_rad, x_smallest) -> np.ndarray:
    result = []
    for pt in points:
        x, y = pt
        z = calculate_point_z(x, z_min, angle_rad, x_smallest)
        result.append([x, y, z])
    return np.array(result)

def create_shrunk_polygon(polygon: Polygon, offset: float) -> Polygon:
    """
    Create an inward-offset (shrunk) version of the polygon.
    """
    shrunk = polygon.buffer(-offset)
    if shrunk.is_empty:
        raise ValueError("Shrink offset too large, polygon vanished.")
    return shrunk

def ensure_single_outer_polygon(geom) -> Polygon:
    if isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda p: p.area)
    return geom

def make_tented_solid(shapely_poly: Polygon,
                      apply_hollow_removal: bool,
                      hollow_offset: float,
                      slope_angle_deg: float,
                      z_min: float,
                      global_x_smallest: float) -> trimesh.Trimesh:
    # Interpolate boundary for smooth edge
    outer_boundary = interpolate_edges(polygon_to_numpy(shapely_poly), 50)

    # Hollowing
    holes = []
    if apply_hollow_removal:
        try:
            shrunk_poly = create_shrunk_polygon(Polygon(outer_boundary), hollow_offset)
            holes.append(interpolate_edges(polygon_to_numpy(shrunk_poly), 50))
        except ValueError:
            # Polygon too small to hollow safely → fall back to solid
            holes = []

    # Build final polygon with holes
    final_polygon = Polygon(shell=outer_boundary, holes=holes)

    # ---- CONSTRAINED TRIANGULATION ----
    vertices_2d, faces_2d = triangulate_polygon(final_polygon)

    # Bottom (flat)
    vertices_bottom = add_height(vertices_2d, 0.0)

    # Top (sloped) — use global X reference
    vertices_top = adjust_z(
        vertices_2d,
        z_min,
        np.deg2rad(slope_angle_deg),
        global_x_smallest
    )

    # Combine
    vertices = np.vstack((vertices_bottom, vertices_top))
    offset = len(vertices_bottom)

    # Build faces
    final_faces = []

    # Bottom cap
    for f in faces_2d:
        final_faces.append(f.tolist())

    # Top cap (reverse winding)
    for f in faces_2d:
        final_faces.append([i + offset for i in f[::-1]])

    # Side walls (outer boundary)
    tree = cKDTree(vertices_2d)
    boundary_indices = [tree.query(p)[1] for p in outer_boundary]

    for i in range(len(boundary_indices)):
        a = boundary_indices[i]
        b = boundary_indices[(i + 1) % len(boundary_indices)]
        final_faces.append([a, b, a + offset])
        final_faces.append([b, b + offset, a + offset])

    # Side walls (inner boundary)
    if holes:
        inner_indices = [tree.query(p)[1] for p in holes[0]]

        for i in range(len(inner_indices)):
            a = inner_indices[i]
            b = inner_indices[(i + 1) % len(inner_indices)]
            final_faces.append([a, a + offset, b])
            final_faces.append([b, a + offset, b + offset])

    # Final mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=final_faces, process=False)

    # Weld duplicate vertices so the shell closes, then orient outward.
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals()
    mesh.fill_holes()
    if mesh.volume < 0:          # winding came out inside-out -> flip
        mesh.invert()
    return mesh

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate the sloped/hollow tenting base STL.")
    ap.add_argument("--dxf", default="./ergogen/output/outlines/l_tenting_base_bottom_outline.dxf")
    ap.add_argument("--palm-dxf", default="./ergogen/output/outlines/l_hand_rest_polygon.dxf")
    ap.add_argument("--out", default="./filtered-output/cases/tenting_system.stl")
    ap.add_argument("--angle", type=float, default=6.5, help="slope angle in degrees")
    ap.add_argument("--z-min", type=float, default=3.0, help="height at the low end in mm")
    ap.add_argument("--hollow", type=float, default=10.0, help="wall thickness when hollowed")
    ap.add_argument("--no-hollow", action="store_true", help="solid part instead of a shell")
    ap.add_argument("--include-palm-rest", action="store_true",
                    help="merge the palm rest area into the same tented solid")
    ARGS = ap.parse_args()

    # ===== PARAMETERS =====
    APPLY_HOLLOW_REMOVAL = not ARGS.no_hollow
    INCLUDE_PALM_REST = ARGS.include_palm_rest
    HOLLOW_OFFSET = ARGS.hollow  # wall thickness
    SLOPE_ANGLE_DEG = ARGS.angle
    Z_MIN = ARGS.z_min  # min height
    # ======================

    # Load keyboard base polygon
    dxf_path = ARGS.dxf
    entities = trimesh.load(dxf_path, force='2D')
    keyboard_poly = max(entities.polygons_full, key=lambda p: p.area)

    # Compute global X reference from the widest polygon
    keyboard_boundary = polygon_to_numpy(keyboard_poly)
    global_x_smallest = find_smallest_x(keyboard_boundary)

    keyboard_mesh = make_tented_solid(
        shapely_poly=keyboard_poly,
        apply_hollow_removal=APPLY_HOLLOW_REMOVAL,
        hollow_offset=HOLLOW_OFFSET,
        slope_angle_deg=SLOPE_ANGLE_DEG,
        z_min=Z_MIN,
        global_x_smallest=global_x_smallest
    )

    final_mesh = keyboard_mesh

    # Optionally include palm rest as a separate tented solid
    if INCLUDE_PALM_REST:
        palm_rest_path = ARGS.palm_dxf
        palm_entities = trimesh.load(palm_rest_path, force='2D')
        palm_poly = max(palm_entities.polygons_full, key=lambda p: p.area)

        palm_mesh = make_tented_solid(
            shapely_poly=palm_poly,
            apply_hollow_removal=APPLY_HOLLOW_REMOVAL,
            hollow_offset=HOLLOW_OFFSET,
            slope_angle_deg=SLOPE_ANGLE_DEG,
            z_min=Z_MIN,
            global_x_smallest=global_x_smallest
        )

        # Merge tented solids (allow overlapping volumes)
        final_mesh = trimesh.util.concatenate(
            [keyboard_mesh, palm_mesh]
        )
    
    # Add color (red for tenting system)
    final_mesh.visual.vertex_colors = np.tile(
        [200, 60, 60, 255], (len(final_mesh.vertices), 1)
    )
    
    os.makedirs(os.path.dirname(ARGS.out) or ".", exist_ok=True)
    final_mesh.export(ARGS.out)
    print(f"Tenting base saved: {ARGS.out}  (angle={SLOPE_ANGLE_DEG} z_min={Z_MIN} "
          f"hollow={HOLLOW_OFFSET if APPLY_HOLLOW_REMOVAL else 'no'})")
    print(f"  watertight={final_mesh.is_watertight} volume={final_mesh.volume/1000:.2f} cm3")
