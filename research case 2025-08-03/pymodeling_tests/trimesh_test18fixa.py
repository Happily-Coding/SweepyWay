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
    top_verts = add_height(tri_verts_2d, max_z)

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
    mesh.export("lofted_polyhedron_opta.stl")
    print("Exported lofted_polyhedron_opta.stl")
