import numpy as np
import mapbox_earcut as earcut
import trimesh
from shapely.geometry import Polygon

def triangulate_shapely_polygon(polygon: Polygon):
    # Get exterior coords, exclude duplicate last point
    exterior_coords = np.array(polygon.exterior.coords[:-1], dtype=np.float64)
    coords_flat = exterior_coords.flatten()

    hole_indices = np.array([], dtype=np.uint32)

    # Triangulate using earcut
    faces = earcut.triangulate_float64(coords_flat, hole_indices)
    faces = faces.reshape(-1, 3)

    return exterior_coords, faces

# Example polygon (no holes)
poly = Polygon([(0, 0), (5, 0), (4, 4), (1, 3), (0, 0)])

verts, faces = triangulate_shapely_polygon(poly)

print("Vertices shape:", verts.shape)  # should be (nverts, 2)
print("Faces shape:", faces.shape)    # should be (nfaces, 3)
print("Vertices:\n", verts)
print("Faces:\n", faces)

# Create trimesh to check it works
mesh = trimesh.Trimesh(vertices=np.hstack([verts, np.zeros((verts.shape[0],1))]), faces=faces)

print("Created trimesh with", len(mesh.faces), "faces and", len(mesh.vertices), "vertices.")
mesh.export("test_polygon_mesh.stl")
print("Exported STL to test_polygon_mesh.stl")
