import trimesh
import shapely.geometry as geom
import numpy as np

# Define two 2D polygons (same number of points!)
polygon1 = geom.Polygon([(0, 0), (5, 0), (4, 4), (1, 3)])
polygon2 = geom.Polygon([(0.5, 0.5), (4.5, 0.5), (4, 3.5), (1.5, 2.5)])

# Function to create loft mesh
def loft_between_polygons(p1, p2, height):
    coords1 = np.array(p1.exterior.coords)[:-1]
    coords2 = np.array(p2.exterior.coords)[:-1]

    if len(coords1) != len(coords2):
        raise ValueError("Polygons must have the same number of points")

    # Bottom and top polygon vertices in 3D
    v1 = np.hstack([coords1, np.zeros((len(coords1), 1))])
    v2 = np.hstack([coords2, np.full((len(coords2), 1), height)])
    vertices = np.vstack([v1, v2])

    # Create faces connecting v1 and v2
    faces = []
    n = len(coords1)
    for i in range(n):
        a, b = i, (i + 1) % n
        # Two triangles per quad
        faces.append([a, b, b + n])
        faces.append([b + n, a + n, a])

    return trimesh.Trimesh(vertices=vertices, faces=faces)

# Create lofted mesh
loft_mesh = loft_between_polygons(polygon1, polygon2, height=5)

# Export the mesh as STL
loft_mesh.export("lofted_star_trimesh.stl")
print("✅ Exported lofted mesh to lofted_star_trimesh.stl")
