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

if __name__ == "__main__":
    dxf_path = "l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')
    shapely_poly = max(entities.polygons_full, key=lambda p: p.area)
    poly_2d = polygon_to_numpy(shapely_poly)

    # Smooth interpolation
    poly_2d = interpolate_edges(poly_2d, 50)

    # Create bottom and top
    poly1_3d = add_height(poly_2d, 0.0)
    poly2_3d = add_height(poly_2d, 10.0)  # Could be adjusted with custom Z logic

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
    mesh.export("lofted_polyhedron_optb.stl")
    print("Exported lofted_polyhedron_optb.stl")
