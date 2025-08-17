"""
Important reminder: In 3d 
X is left to right
Y is far to close to you
Z is tall to low
Fixed the issue that added a convex outer hull, but not the definition of the top faces
"""
import trimesh
import numpy as np
from shapely.geometry import Polygon
from trimesh.creation import triangulate_polygon
from typing import List, Tuple

def polygon_to_numpy(polygon: Polygon) -> np.ndarray:
    """
    Convert a shapely Polygon to an Nx2 NumPy array of (x, y) coordinates.
    The last (repeated) point is removed.
    """
    coords = np.array(polygon.exterior.coords)
    if np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]
    return coords

def add_height(poly2d: np.ndarray, z: float) -> np.ndarray:
    """
    Add a constant Z value to a 2D polygon, returning an Nx3 array.
    """
    n = poly2d.shape[0]
    return np.column_stack((poly2d, np.full(n, z)))

def get_two_lowest_y_indices(poly2d: np.ndarray) -> List[int]:
    """
    Return indices of the two points with the smallest Y values.
    """
    return np.argsort(poly2d[:, 1])[:2].tolist()

def loft_between_polygons(poly1_3d: np.ndarray, poly2_3d: np.ndarray) -> trimesh.Trimesh:
    """
    Loft between two 3D polygons (Nx3). Assumes same vertex count and order.
    Returns a trimesh mesh with side faces and caps.
    """
    if poly1_3d.shape != poly2_3d.shape or poly1_3d.shape[1] != 3:
        raise ValueError("Both polygons must be Nx3 arrays of equal shape.")

    n = poly1_3d.shape[0]
    vertices = np.vstack((poly1_3d, poly2_3d))

    faces: List[List[int]] = []

    # Use shapely to create a polygon for triangulation
    polygon_2d = Polygon(poly1_3d[:, :2])
    tri_verts, tri_faces = triangulate_polygon(polygon_2d)

    # Add triangulated bottom face
    for face in tri_faces:
        faces.append(face.tolist())

    # Add triangulated top face (with offset and reversed winding order)
    top_offset = n
    for face in tri_faces:
        # Reverse winding order for correct normal direction
        faces.append([top_offset + idx for idx in face[::-1]])


    # Side faces
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, top_offset + i])
        faces.append([next_i, top_offset + next_i, top_offset + i])

    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)

def interpolate_edges(points: np.ndarray, steps: int = 10) -> np.ndarray:
    """
    Linearly interpolate between consecutive 2D points in a polygon.
    Returns a new Nx2 array with added points.
    """
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
    # Load from DXF
    dxf_path = "l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')
    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)

    # Convert to 2D NumPy array
    poly_2d = polygon_to_numpy(shapely_poly)

    #detect the 2 points closeer to the user (we may need them later )
    lowest_y_indices = get_two_lowest_y_indices(poly_2d)

    #Find the smallest y since we need to know where our palmrest and our slope will end
    palmrest_end = find_smallest_y(poly_2d)

    #increase the resolution so we can smoothly create a slope based on position
    poly_2d = interpolate_edges(poly_2d, 50)

    # Add height to the bottom to convert it to 3D
    max_palmrest_height = 10
    min_palmrest_height = 3
    last_key_end = find_biggest_y(poly_2d) - 20
    slope_strength = 1
    

    poly1_3d = add_height(poly_2d, z=0.0)
    poly2_3d = add_height(poly_2d, z=0.0) #simply add z to every point, we'll modify it.
    poly2_3d = adjust_z(
        poly2_3d,
        max_palmrest_height,
        min_palmrest_height,
        last_key_end,
        palmrest_end,
        1
    )

    mesh = loft_between_polygons(poly1_3d, poly2_3d)

    # Export STL
    mesh.export("lofted_polyhedron_refactored_s2.stl")
    print("STL file saved as 'lofted_polyhedron_refactored_s2.stl'")


#IMPORTANTE PARECE FUNCIONAR DEBE HABER QUE TICKEAR LA FUNCION DE SMOOTHING O LOS VALORES QUE LE ESTAMO SPASANDO