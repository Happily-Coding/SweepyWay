"""
Important reminder: In 3d 
X is left to right
Y is far to close to you
Z is tall to low
First fix attempt for the faces fefinition
"""
# Version A: Independent cap triangulation
import trimesh
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon
from trimesh.creation import triangulate_polygon

def polygon_to_numpy(polygon):
    coords = np.array(polygon.exterior.coords)
    if np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]
    return coords

def add_height(poly2d, z):
    return np.column_stack((poly2d, np.full(poly2d.shape[0], z)))

def find_smallest_y(points: np.ndarray) -> float:
    """
    Return the smallest Y value from a Nx2 array of (x, y) points.
    """
    if points.shape[1] < 2:
        raise ValueError("Input must be an Nx2 array.")
    return np.min(points[:, 1])

def find_biggest_y(points: np.ndarray) -> float:
    """
    Return the smallest Y value from a Nx2 array of (x, y) points.
    """
    if points.shape[1] < 2:
        raise ValueError("Input must be an Nx2 array.")
    return np.max(points[:, 1])

def calculate_point_z(
    y: float,
    z_max: float,
    z_min: float,
    y_threshold: float,
    y_smallest: float,
    curve_strength: float = 1.0
) -> float:
    """
    Calculate Z based on a single Y coordinate using a cosine ramp.
    """
    curve_strength = max(0.01, min(curve_strength, 10.0))
    ramp_range = y_threshold - y_smallest

    if ramp_range <= 0 or y >= y_threshold:
        return z_max

    # Normalize and clamp
    t = (y - y_smallest) / ramp_range
    t = max(0.0, min(t, 1.0))

    # Cosine easing
    eased = 0.5 * (1 - np.cos(np.pi * (t ** curve_strength)))
    return z_min + (z_max - z_min) * eased


def adjust_z(
    points: np.ndarray,
    z_max: float,
    z_min: float,
    y_threshold: float,
    y_smallest: float,
    curve_strength: float = 1.0
) -> np.ndarray:
    """
    Apply calculate_point_z to each point in a polygon based on Y.
    """
    result = []
    for pt in points:
        x = pt[0]
        y = pt[1]
        z = calculate_point_z(y, z_max, z_min, y_threshold, y_smallest, curve_strength)
        result.append([x, y, z])
    return np.array(result)



def interpolate_edges(points, steps=10):
    interpolated = []
    n = len(points)
    for i in range(n):
        p0, p1 = points[i], points[(i + 1) % n]
        for t in np.linspace(0, 1, steps, endpoint=False):
            interpolated.append((1 - t) * p0 + t * p1)
    return np.array(interpolated)

if __name__ == "__main__":
    dxf_path = "l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')
    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)
    poly_2d = polygon_to_numpy(shapely_poly)
    poly_2d = interpolate_edges(poly_2d, 50)

    max_z = 10.0
    min_z = 0.0

    # Triangulate 2D polygon (bottom cap)
    tri_verts_2d, tri_faces = triangulate_polygon(ShapelyPolygon(poly_2d))
    bottom_verts = add_height(tri_verts_2d, min_z)
    y_smallest = find_smallest_y(poly_2d)
    y_largest = find_biggest_y(poly_2d)
    top_verts = adjust_z(
        points=tri_verts_2d,
        z_max=10.0,
        z_min=3.0,
        y_threshold=y_largest - 20,
        y_smallest=y_smallest,
        curve_strength=1.0
    )

    # Combine vertices
    vertices = np.vstack((bottom_verts, top_verts))
    faces = []

    # Bottom cap
    for f in tri_faces:
        faces.append([f[0], f[1], f[2]])

    # Top cap (reverse winding)
    offset = len(bottom_verts)
    for f in tri_faces:
        faces.append([offset + f[2], offset + f[1], offset + f[0]])

    # Side faces (connect bottom_verts to top_verts)
    n = len(tri_verts_2d)
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, offset + i])
        faces.append([next_i, offset + next_i, offset + i])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.export("lofted_polyhedron_opta2.stl")
    print("Exported lofted_polyhedron_opta2.stl")
