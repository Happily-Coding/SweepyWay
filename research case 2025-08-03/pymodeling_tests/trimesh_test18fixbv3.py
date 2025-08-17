"""
Important reminder: In 3d 
X is left to right
Y is far to close to you
Z is tall to low
First fix attempt for the faces fefinition
"""
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
    return np.column_stack((poly2d, np.full(len(poly2d), z)))

def interpolate_edges(points, steps=10):
    interpolated = []
    n = len(points)
    for i in range(n):
        p0, p1 = points[i], points[(i + 1) % n]
        for t in np.linspace(0, 1, steps, endpoint=False):
            interpolated.append((1 - t) * p0 + t * p1)
    return np.array(interpolated)

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



if __name__ == "__main__":
    dxf_path = "l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')
    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)
    poly_2d = polygon_to_numpy(shapely_poly)
    y_smallest = find_smallest_y(poly_2d)
    y_largest = find_biggest_y(poly_2d)

    # Smooth interpolation
    poly_2d = interpolate_edges(poly_2d, 50)

    # Create bottom and top
    poly1_3d = add_height(poly_2d, 0.0)

    poly2_3d = adjust_z(
        points=poly_2d,
        z_max=10.0,
        z_min=3.0,
        y_threshold=y_largest - 20,
        y_smallest=y_smallest,
        curve_strength=1.0
    ) #poly2_3d = add_height(poly_2d, 10.0)  # Could be adjusted with custom Z logic

    # Create triangulated faces for caps using shapely polygon
    polygon_shape = ShapelyPolygon(poly_2d)
    _, tri_faces = triangulate_polygon(polygon_shape)

    vertices = np.vstack((poly1_3d, poly2_3d))
    n = len(poly1_3d)
    faces = []

    # Bottom cap faces
    for face in tri_faces:
        faces.append([face[0], face[1], face[2]])

    # Top cap faces (reversed winding)
    for face in tri_faces:
        faces.append([n + face[2], n + face[1], n + face[0]])

    # Side faces
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, n + i])
        faces.append([next_i, n + next_i, n + i])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.export("lofted_polyhedron_optbv3.stl")
    print("Exported lofted_polyhedron_optb.stl")
