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

def find_smallest_y(points: np.ndarray) -> float:
    return np.min(points[:, 0])  # X axis instead of Y

def find_biggest_y(points: np.ndarray) -> float:
    return np.max(points[:, 0])  # X axis instead of Y

def calculate_point_z(x, z_max, z_min, x_threshold, x_smallest, curve_strength=1.0) -> float:
    curve_strength = max(0.01, min(curve_strength, 10.0))
    ramp_range = x_threshold - x_smallest
    if ramp_range <= 0 or x >= x_threshold:
        return z_max
    t = (x - x_smallest) / ramp_range
    t = max(0.0, min(t, 1.0))
    eased = 0.5 * (1 - np.cos(np.pi * (t ** curve_strength)))
    return z_min + (z_max - z_min) * eased

def adjust_z(points: np.ndarray, z_max, z_min, x_threshold, x_smallest, curve_strength=1.0) -> np.ndarray:
    result = []
    for pt in points:
        x, y = pt
        z = calculate_point_z(x, z_max, z_min, x_threshold, x_smallest, curve_strength)
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
    # Load DXF and extract polygon
    dxf_path = './ergogen/output/outlines/l_tenting_base_bottom_outline.dxf' # <-- el problema es que el dxf no tiene las entities
    #dxf_path = "./ergogen/output/outlines/l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')

    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)

    # Interpolate boundary for smooth edge
    poly_2d = polygon_to_numpy(shapely_poly)
    poly_2d = interpolate_edges(poly_2d, 50)

    # Sample interior points
    shapely_poly = Polygon(poly_2d)
    interior_points = sample_points_in_polygon(shapely_poly, spacing=2.0)

    # Combine boundary and interior
    all_points = np.vstack((poly_2d, interior_points))

    # Triangulate all points
    delaunay = Delaunay(all_points)
    triangles = delaunay.simplices

    # Filter triangles that are inside the polygon
    valid_faces = []
    for tri in triangles:
        centroid = np.mean(all_points[tri], axis=0)
        if shapely_poly.contains(Point(centroid)):
            valid_faces.append(tri.tolist())

    valid_faces = np.array(valid_faces)

    # Z computation
    y_smallest = find_smallest_y(all_points)
    y_largest = find_biggest_y(all_points)
    last_key_end = y_largest - 20

    # Bottom (flat)
    vertices_bottom = add_height(all_points, 0.0)

    # Top (curved)
    vertices_top = adjust_z(all_points, 10, 3, last_key_end, y_smallest, curve_strength=1)

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

    # Side walls (using boundary)
    tree = cKDTree(all_points)
    boundary_indices = [tree.query(p)[1] for p in poly_2d]

    for i in range(len(boundary_indices)):
        a = boundary_indices[i]
        b = boundary_indices[(i + 1) % len(boundary_indices)]
        a_top = a + offset
        b_top = b + offset
        final_faces.append([a, b, a_top])
        final_faces.append([b, b_top, a_top])

    # Final mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=final_faces, process=True)
    mesh.export("./filtered-output/tenting_system.stl")
    print("Tenting system STL file saved as 'tenting_system.stl'")


"""
El objetivo de este prompt es crear un tenting system (fijo) basado en un contenedor alrededor del teclado, que esté inclinado
eso es con lo que hay que seguir!

Prompt para empezar con chat gpt despues de resolver tuple out of range issue
Im designing a parametric keyboard tenting system using python trimesh.

I've already created a parametric palmrest, so i'd like to modify my working code to fit my new purpose.
I have done the bare minimun, (modified the shape i loaded) , and modified the name of the output file, but now i want to modify the code to do what i want to.

The next step will be to remove the smoothing on the top adjustment, 
the third will be to calculate the z based on a certain angle and distance from the most negative x

The final step will be to add a border which should go higher than the rest of the shape, I have another dxf file which has its outline and we should adjust it in the same way.

"""
