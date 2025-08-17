import trimesh
import shapely.geometry as geom
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

    # Cap bottom polygon (convex hull of bottom ring)
    tri_bottom = trimesh.Trimesh(vertices=v1, process=False)
    cap_bottom = tri_bottom.convex_hull.faces
    for face in cap_bottom:
        faces.append(face)

    # Cap top polygon (convex hull, reversed winding)
    tri_top = trimesh.Trimesh(vertices=v2, process=False)
    cap_top = tri_top.convex_hull.faces
    offset = len(v1)
    for face in cap_top:
        faces.append([offset + i for i in face[::-1]])

    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# --- Load DXF and extract polygon ---
dxf_path = "l_hand_rest_polygon.dxf"
entities = trimesh.load(dxf_path, force='2D')

# Get largest closed polygon
polygons = entities.polygons_full
if not polygons:
    raise ValueError("❌ No closed polygons found in the DXF")

polygon1 = max(polygons, key=lambda p: p.area)
polygon2 = geom.Polygon(polygon1.exterior.coords[:-1])  # exact copy, no distortion

# Perform the loft
height = 20
lofted = loft_between_polygons(polygon1, polygon2, height=height)

# Export to STL
output_path = "l_hand_rest_solid_loft.stl"
lofted.export(output_path)
print(f"✅ Exported solid lofted mesh to {output_path}")
print(f"Watertight: {lofted.is_watertight}")
