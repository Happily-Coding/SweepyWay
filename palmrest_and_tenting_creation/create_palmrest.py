import argparse
import os

import trimesh
import numpy as np
from shapely.geometry import Polygon, Point
from scipy.spatial import cKDTree
from trimesh.creation import triangulate_polygon


def parse_args():
    ap = argparse.ArgumentParser(description="Generate the parametric palm rest STL from the hand-rest outline.")
    ap.add_argument("--dxf", default="./ergogen/output/outlines/l_hand_rest_polygon.dxf",
                    help="input outline (produced by ergogen)")
    ap.add_argument("--out", default="./filtered-output/palmrest/palm_rest.stl",
                    help="output STL path")
    ap.add_argument("--height", type=float, default=10.0, help="tall-end height in mm")
    ap.add_argument("--curve", type=float, default=3.0, help="curve strength (1 = linear ease)")
    ap.add_argument("--edge-steps", type=int, default=10, help="boundary interpolation steps")
    return ap.parse_args()

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

def find_smallest_y(points: np.ndarray) -> float:
    return np.min(points[:, 1])

def find_biggest_y(points: np.ndarray) -> float:
    return np.max(points[:, 1])

def calculate_point_z(y, z_max, z_min, y_threshold, y_smallest, curve_strength=1.0) -> float:
    curve_strength = max(0.01, min(curve_strength, 10.0))
    ramp_range = y_threshold - y_smallest
    if ramp_range <= 0 or y >= y_threshold:
        return z_max
    t = (y - y_smallest) / ramp_range
    t = max(0.0, min(t, 1.0))
    eased = 0.5 * (1 - np.cos(np.pi * (t ** curve_strength)))
    return z_min + (z_max - z_min) * eased

def adjust_z(points: np.ndarray, z_max, z_min, y_threshold, y_smallest, curve_strength=1.0) -> np.ndarray:
    result = []
    for pt in points:
        x, y = pt
        z = calculate_point_z(y, z_max, z_min, y_threshold, y_smallest, curve_strength)
        result.append([x, y, z])
    return np.array(result)

def sample_points_in_polygon(polygon: Polygon, spacing: float) -> np.ndarray:
    """
    Sample a grid of points inside the polygon.
    """
    minx, miny, maxx, maxy = polygon.bounds
    x_vals = np.arange(minx, maxx, spacing)
    y_vals = np.arange(miny, maxy, spacing)
    points = np.array([[x, y] for x in x_vals for y in y_vals if polygon.contains(Point(x, y))])
    return points

if __name__ == "__main__":
    ARGS = parse_args()
    # Load DXF and extract polygon
    dxf_path = ARGS.dxf
    entities = trimesh.load(dxf_path, force='2D')
    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)

    # Interpolate the boundary so the sloped top has enough resolution in y.
    poly_2d = polygon_to_numpy(shapely_poly)
    poly_2d = interpolate_edges(poly_2d, 50)
    shapely_poly = Polygon(poly_2d)

    # Constrained triangulation of the polygon itself (no interior points, so the
    # boundary of the mesh IS the polygon boundary -> watertight by construction).
    vertices_2d, faces_2d = triangulate_polygon(shapely_poly)

    # Z ramp: tallest at the back (far from the hands), easing down towards the keys.
    y_smallest = find_smallest_y(vertices_2d)
    y_largest = find_biggest_y(vertices_2d)
    last_key_end = y_largest - 20

    vertices_bottom = add_height(vertices_2d, 0.0)
    vertices_top = adjust_z(vertices_2d, ARGS.height, ARGS.height * 0.3, last_key_end,
                            y_smallest, curve_strength=ARGS.curve)

    vertices = np.vstack((vertices_bottom, vertices_top))
    offset = len(vertices_bottom)

    final_faces = []
    for f in faces_2d:                       # bottom cap
        final_faces.append(f.tolist())
    for f in faces_2d:                       # top cap, reversed winding
        final_faces.append([i + offset for i in f[::-1]])

    # Side walls from the edges that belong to exactly one triangle -> exact loop.
    edges = {}
    for f in faces_2d:
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            edges[(min(a, b), max(a, b))] = edges.get((min(a, b), max(a, b)), 0) + 1
    for (a, b), n in edges.items():
        if n != 1:
            continue
        if (a, b) in {(f[0], f[1]) for f in faces_2d}:   # keep original orientation
            a, b = a, b
        final_faces.append([a, b, a + offset])
        final_faces.append([b, b + offset, a + offset])

    # Final mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=final_faces, process=True)
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals()
    mesh.fill_holes()
    if mesh.volume < 0:          # winding came out inside-out -> flip
        mesh.invert()

    # Add color (blue for palm rest)
    mesh.visual.vertex_colors = np.tile(
        [60, 60, 200, 255], (len(mesh.vertices), 1)
    )
    
    os.makedirs(os.path.dirname(ARGS.out) or ".", exist_ok=True)
    mesh.export(ARGS.out)
    print(f"Palmrest STL saved: {ARGS.out}  (height={ARGS.height} curve={ARGS.curve})")
