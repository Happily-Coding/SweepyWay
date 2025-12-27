import trimesh
import numpy as np
from shapely.geometry import Polygon, Point
from scipy.spatial import Delaunay, cKDTree

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

def find_biggest_x(points: np.ndarray) -> float:
    return np.max(points[:, 0])

def calculate_point_z(x, z_min, angle_rad, x_smallest) -> float:
    return z_min + np.tan(angle_rad) * (x - x_smallest)

def adjust_z(points: np.ndarray, z_min, angle_rad, x_smallest) -> np.ndarray:
    result = []
    for pt in points:
        x, y = pt
        z = calculate_point_z(x, z_min, angle_rad, x_smallest)
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

def create_shrunk_polygon(polygon: Polygon, offset: float) -> Polygon:
    """
    Create an inward-offset (shrunk) version of the polygon.
    """
    shrunk = polygon.buffer(-offset)
    if shrunk.is_empty:
        raise ValueError("Shrink offset too large, polygon vanished.")
    return shrunk

if __name__ == "__main__":
    # ===== PARAMETERS =====
    APPLY_HOLLOW_REMOVAL = True
    HOLLOW_OFFSET = 10.0  # wall thickness
    SLOPE_ANGLE_DEG = 6.5
    Z_MIN = 3.0 # min height
    # ======================

    # Load DXF and extract polygon
    dxf_path = './ergogen/output/outlines/l_tenting_base_bottom_outline.dxf' # <-- el problema es que el dxf no tiene las entities
    #dxf_path = "./ergogen/output/outlines/l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')

    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)

    # Interpolate boundary for smooth edge
    poly_2d = polygon_to_numpy(shapely_poly)
    poly_2d = interpolate_edges(poly_2d, 50)

    # Rebuild polygon after interpolation
    shapely_poly = Polygon(poly_2d)

    # Sample interior points
    interior_points = sample_points_in_polygon(shapely_poly, spacing=2.0)

    # Remove some interior points if we want it to be hollow
    if APPLY_HOLLOW_REMOVAL:
        shrunk_poly = create_shrunk_polygon(shapely_poly, HOLLOW_OFFSET)  # Create shrunk polygon for hollowing with the same shape as the outer
        shrunk_boundary = polygon_to_numpy(shrunk_poly)
        shrunk_boundary = interpolate_edges(shrunk_boundary, 50)
        interior_points = np.array([
            p for p in interior_points
            if not shrunk_poly.contains(Point(p))
        ])

    # Combine boundary and interior
    all_points = np.vstack((poly_2d, interior_points))

    # Triangulate all points
    delaunay = Delaunay(all_points)
    triangles = delaunay.simplices

    # Filter triangles that are inside the polygon
    valid_faces = []
    for tri in triangles:
        centroid = np.mean(all_points[tri], axis=0)

        if not shapely_poly.contains(Point(centroid)):
            continue

        # Also filter inside the shrunk polygon if we want to hollow it.
        if APPLY_HOLLOW_REMOVAL and shrunk_poly.contains(Point(centroid)):
            continue

        valid_faces.append(tri.tolist())

    valid_faces = np.array(valid_faces)

    # Z computation
    x_smallest = find_smallest_x(all_points)
    x_largest = find_biggest_x(all_points)

    # Bottom (flat)
    vertices_bottom = add_height(all_points, 0.0)

    # Top (sloped)
    vertices_top = adjust_z(all_points, Z_MIN, np.deg2rad(SLOPE_ANGLE_DEG), x_smallest)

    # Combine
    vertices = np.vstack((vertices_bottom, vertices_top))
    offset = len(vertices_bottom)

    # Build faces
    final_faces = []

    # Bottom cap
    for f in valid_faces:
        final_faces.append(f.tolist())

    # Top cap (reverse winding)
    for f in valid_faces:
        final_faces.append([i + offset for i in f[::-1]])

    # Side walls (outer boundary)
    tree = cKDTree(all_points)
    boundary_indices = [tree.query(p)[1] for p in poly_2d]

    for i in range(len(boundary_indices)):
        a = boundary_indices[i]
        b = boundary_indices[(i + 1) % len(boundary_indices)]
        a_top = a + offset
        b_top = b + offset
        final_faces.append([a, b, a_top])
        final_faces.append([b, b_top, a_top])

    # Side walls (inner boundary)
    if APPLY_HOLLOW_REMOVAL:
        inner_indices = [tree.query(p)[1] for p in shrunk_boundary]

        for i in range(len(inner_indices)):
            a = inner_indices[i]
            b = inner_indices[(i + 1) % len(inner_indices)]
            a_top = a + offset
            b_top = b + offset

            # Reverse winding to face inward
            final_faces.append([a, a_top, b])
            final_faces.append([b, a_top, b_top])

    # Final mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=final_faces, process=True)
    mesh.export("./filtered-output/tenting_system.stl")
    print("Tenting system STL file saved as 'tenting_system.stl'")
