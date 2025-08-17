"""
Important reminder: In 3d 
X is left to right
Y is far to close to you
Z is tall to low
"""
import trimesh
import numpy as np
from shapely.geometry import Polygon
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

    # Bottom face
    for i in range(1, n - 1):
        faces.append([0, i, i + 1])

    # Top face
    top_offset = n
    for i in range(1, n - 1):
        faces.append([top_offset, top_offset + i + 1, top_offset + i])

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

# def apply_x_based_z(points: np.ndarray, z_min: float, z_max: float) -> np.ndarray:
#     """
#     Apply a linear Z gradient based on X values.
#     """
#     x_vals = points[:, 0]
#     x_min = x_vals.min()
#     x_max = x_vals.max()

#     # Prevent divide-by-zero
#     if np.isclose(x_min, x_max):
#         z_vals = np.full_like(x_vals, (z_min + z_max) / 2.0)
#     else:
#         t = (x_vals - x_min) / (x_max - x_min)
#         z_vals = z_min + (1 - t) * (z_max - z_min)  # flip direction

#     return np.column_stack((points, z_vals))


# import numpy as np

# def set_correct_z(
#     points: np.ndarray,
#     z_max: float,
#     z_min: float,
#     x_threshold: float,
#     x_smallest: float,
#     curve_strength: float = 1.0
# ) -> np.ndarray:
#     """
#     Apply a non-linear Z gradient to points based on their X value.
#     - Z = z_max for X >= x_threshold
#     - Z smoothly interpolates to z_min as X approaches x_smallest
#     - Cosine interpolation controls the smoothness
#     - curve_strength can sharpen or soften the transition
#     """
#     x_vals = points[:, 0]
#     z_vals = np.full_like(x_vals, z_max)  # Default to z_max everywhere

#     # Find which points need interpolation
#     mask = x_vals < x_threshold
#     x_interp = x_vals[mask]

#     # Avoid divide-by-zero
#     ramp_range = x_threshold - x_smallest
#     if ramp_range <= 0:
#         return np.column_stack((points, z_vals))

#     # Clamp curve strength
#     curve_strength = max(0.01, min(curve_strength, 10.0))

#     # Normalized t in [0, 1]
#     t = np.clip((x_interp - x_smallest) / ramp_range, 0, 1)

#     # Cosine interpolation
#     eased = 0.5 * (1 - np.cos(np.pi * t ** curve_strength))
#     z_vals[mask] = z_min + (z_max - z_min) * eased

#     return np.column_stack((points, z_vals))

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
    from shapely.geometry import Polygon

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

    # Create elevated version
    translation_xy = np.array([2.0, 1.0])
    poly_2d_translated = poly_2d + translation_xy

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
    #poly2_3d = add_height(poly_2d_translated, z=10.0)
    # Lower the 2 vertexes closer to us in the y axis. to test shape warping
    # for id in lowest_y_indices:
    #     poly2_3d[id][2] -= 6.0  # lower the closer edges by 6 units

    mesh = loft_between_polygons(poly1_3d, poly2_3d)

    # Export STL
    mesh.export("lofted_polyhedron_refactored_s.stl")
    print("STL file saved as 'lofted_polyhedron_refactored_s.stl'")


#IMPORTANTE PARECE FUNCIONAR DEBE HABER QUE TICKEAR LA FUNCION DE SMOOTHING O LOS VALORES QUE LE ESTAMO SPASANDO