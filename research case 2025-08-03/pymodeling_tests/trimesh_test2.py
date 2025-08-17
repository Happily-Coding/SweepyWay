import trimesh
import shapely.geometry as geom
import shapely.ops as ops
import numpy as np

def loft_between_polygons(p1, p2, height):
    coords1 = np.array(p1.exterior.coords)[:-1]
    coords2 = np.array(p2.exterior.coords)[:-1]

    if len(coords1) != len(coords2):
        raise ValueError("Polygons must have the same number of points")

    # Bottom and top polygon vertices in 3D
    v1 = np.hstack([coords1, np.zeros((len(coords1), 1))])
    v2 = np.hstack([coords2, np.full((len(coords2), 1), height)])
    vertices = np.vstack([v1, v2])

    # Side faces
    faces = []
    n = len(coords1)
    for i in range(n):
        a, b = i, (i + 1) % n
        # Two triangles per quad
        faces.append([a, b, b + n])
        faces.append([b + n, a + n, a])

    # Cap bottom polygon (use triangulation)
    tri_bottom = trimesh.Trimesh(vertices=v1, process=False)
    cap_bottom = tri_bottom.convex_hull.faces
    offset = 0
    for face in cap_bottom:
        faces.append([offset + i for i in face])

    # Cap top polygon (need to reverse winding)
    tri_top = trimesh.Trimesh(vertices=v2, process=False)
    cap_top = tri_top.convex_hull.faces
    offset = len(v1)
    for face in cap_top:
        # Reverse winding so normals face outward
        faces.append([offset + i for i in face[::-1]])

    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


from shapely.geometry import Polygon

polygon1 = Polygon([(0, 0), (5, 0), (4, 4), (1, 3)])
polygon2 = Polygon([(0.5, 0.5), (4.5, 0.5), (4, 3.5), (1.5, 2.5)])

lofted = loft_between_polygons(polygon1, polygon2, height=5)
lofted.export("solid_lofted_mesh.stl")
print("✅ Exported solid lofted mesh to solid_lofted_mesh.stl")
