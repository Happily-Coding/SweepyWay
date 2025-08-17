import numpy as np
import trimesh
from shapely.geometry import Polygon as ShapelyPolygon
from trimesh.creation import triangulate_polygon

def polygon_to_numpy(polygon):
    coords = np.array(polygon.exterior.coords)
    if np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]
    return coords

def interpolate_edges(points, steps=10):
    interpolated = []
    n = len(points)
    for i in range(n):
        p0 = points[i]
        p1 = points[(i + 1) % n]
        for t in np.linspace(0, 1, steps, endpoint=False):
            interpolated.append((1 - t) * p0 + t * p1)
    return np.array(interpolated)

def add_height(poly2d, z):
    return np.column_stack((poly2d, np.full(poly2d.shape[0], z)))

def find_smallest_y(points):
    return np.min(points[:, 1])

def find_biggest_y(points):
    return np.max(points[:, 1])

def calculate_point_z(y, z_max, z_min, y_threshold, y_smallest, curve_strength=1.0):
    curve_strength = max(0.01, min(curve_strength, 10.0))
    ramp_range = y_threshold - y_smallest

    if ramp_range <= 0 or y >= y_threshold:
        return z_max

    t = (y - y_smallest) / ramp_range
    t = max(0.0, min(t, 1.0))

    eased = 0.5 * (1 - np.cos(np.pi * (t ** curve_strength)))
    return z_min + (z_max - z_min) * eased

def adjust_z(points, z_max, z_min, y_threshold, y_smallest, curve_strength=1.0):
    result = []
    for pt in points:
        x, y = pt
        z = calculate_point_z(y, z_max, z_min, y_threshold, y_smallest, curve_strength)
        result.append([x, y, z])
    return np.array(result)

# ---- MAIN EXECUTION ----
if __name__ == "__main__":
    # Load DXF and extract the largest polygon
    dxf_path = "l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')
    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)
    poly_2d = polygon_to_numpy(shapely_poly)

    # Interpolate to smooth the outline
    poly_2d = interpolate_edges(poly_2d, steps=50)

    # Compute slope-related values
    y_smallest = find_smallest_y(poly_2d)
    y_largest = find_biggest_y(poly_2d)
    y_threshold = y_largest - 20

    z_min = 3.0
    z_max = 10.0
    curve_strength = 1.0

    # Bottom and top vertices — use same 2D ordering
    bottom_verts = add_height(poly_2d, z=z_min)
    top_verts = adjust_z(poly_2d, z_max, z_min, y_threshold, y_smallest, curve_strength)

    # Triangulate caps using original 2D shape
    tri_faces = triangulate_polygon(ShapelyPolygon(poly_2d))[1]

    # Combine all vertices
    vertices = np.vstack((bottom_verts, top_verts))
    faces = []

    # Bottom cap (original winding)
    faces.extend(tri_faces)

    # Top cap (reverse winding, offset by bottom vertex count)
    offset = len(bottom_verts)
    for f in tri_faces:
        faces.append([offset + f[2], offset + f[1], offset + f[0]])

    # Side faces — use consistent indexing based on poly_2d
    n = len(poly_2d)
    for i in range(n):
        ni = (i + 1) % n
        # First triangle
        faces.append([i, ni, offset + i])
        # Second triangle
        faces.append([ni, offset + ni, offset + i])

    # Build mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    mesh.export("lofted_polyhedron_clean.stl")
    print("✅ Exported 'lofted_polyhedron_clean.stl'")
