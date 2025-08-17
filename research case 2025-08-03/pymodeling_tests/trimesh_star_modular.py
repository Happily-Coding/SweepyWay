import numpy as np
import trimesh
from shapely.geometry import Polygon
from trimesh.creation import triangulate_polygon

def create_star_points(outer=40, inner=20, points=5):
    angles = np.linspace(0, 2*np.pi, points*2, endpoint=False)
    radii = np.array([outer if i % 2 == 0 else inner for i in range(points*2)])
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return np.column_stack((x, y))

def calculate_z_from_y(y, z_min, z_max, y_min, y_max, strength=1.0):
    # Clamp strength
    strength = max(0.01, min(strength, 10.0))
    if y >= y_max:
        return z_max
    t = (y - y_min) / (y_max - y_min)
    t = np.clip(t, 0, 1)
    eased = 0.5 * (1 - np.cos(np.pi * (t ** strength)))
    return z_min + (z_max - z_min) * eased

def generate_lofted_star_mesh():
    # Create 2D star polygon points
    star_2d = create_star_points()

    # Triangulate polygon to get vertices and faces
    polygon = Polygon(star_2d)
    tri_verts_2d, tri_faces = triangulate_polygon(polygon)

    # Bottom vertices at z=0
    bottom_verts = np.column_stack((tri_verts_2d, np.zeros(len(tri_verts_2d))))

    # Compute slope parameters
    y_min = tri_verts_2d[:,1].min()
    y_max = tri_verts_2d[:,1].max() - 1  # leave a little ramp near top

    # Top vertices with z from y
    top_verts = []
    for x, y in tri_verts_2d:
        z = calculate_z_from_y(y, z_min=2.0, z_max=10.0, y_min=y_min, y_max=y_max, strength=1.5)
        top_verts.append([x, y, z])
    top_verts = np.array(top_verts)

    # Combine vertices
    vertices = np.vstack((bottom_verts, top_verts))

    # Build faces list
    faces = []

    # Bottom faces (same as triangulation)
    for f in tri_faces:
        faces.append([f[0], f[1], f[2]])

    # Top faces (reverse winding order for correct normal)
    offset = len(bottom_verts)
    for f in tri_faces:
        faces.append([offset + f[2], offset + f[1], offset + f[0]])

    # Connect sides (rim of polygon)
    hull = polygon.exterior.coords[:-1]  # remove duplicate last point

    # Find indices of hull vertices in tri_verts_2d
    hull_indices = []
    for hx, hy in hull:
        dist = np.linalg.norm(tri_verts_2d - np.array([hx, hy]), axis=1)
        idx = np.argmin(dist)
        hull_indices.append(idx)

    n = len(hull_indices)
    for i in range(n):
        i0 = hull_indices[i]
        i1 = hull_indices[(i + 1) % n]
        # Side quad split into two triangles
        faces.append([i0, i1, offset + i0])
        faces.append([i1, offset + i1, offset + i0])

    # Create mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    return mesh

if __name__ == "__main__":
    mesh = generate_lofted_star_mesh()
    mesh.export("star_lofted_basic.stl")
    print("Exported star_lofted_basic.stl")
