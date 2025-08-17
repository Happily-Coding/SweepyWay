import trimesh
import shapely.geometry as geom
import shapely.ops as ops
import numpy as np

# --- Lofting function with caps ---
def loft_between_polygons(p1, p2, height):
    coords1 = np.array(p1.exterior.coords)[:-1]
    coords2 = np.array(p2.exterior.coords)[:-1]

    if len(coords1) != len(coords2):
        raise ValueError("Polygons must have the same number of points")

    v1 = np.hstack([coords1, np.zeros((len(coords1), 1))])
    v2 = np.hstack([coords2, np.full((len(coords2), 1), height)])
    vertices = np.vstack([v1, v2])

    faces = []
    n = len(coords1)
    for i in range(n):
        a, b = i, (i + 1) % n
        faces.append([a, b, b + n])
        faces.append([b + n, a + n, a])

    # Cap bottom
    tri_bottom = trimesh.Trimesh(vertices=v1, process=False)
    cap_bottom = tri_bottom.convex_hull.faces
    for face in cap_bottom:
        faces.append([i for i in face])

    # Cap top (reverse winding)
    tri_top = trimesh.Trimesh(vertices=v2, process=False)
    cap_top = tri_top.convex_hull.faces
    offset = len(v1)
    for face in cap_top:
        faces.append([offset + i for i in face[::-1]])

    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# --- Load DXF ---
dxf_path = "l_hand_rest_polygon.dxf"
entities = trimesh.load(dxf_path, force='2D')

# Merge all paths into a single shapely polygon
merged = entities.polygons_full
if not merged:
    raise ValueError("❌ No closed polygons found in the DXF")

# Use the largest polygon
polygon = max(merged, key=lambda p: p.area)

# Optional: simplify or preprocess
polygon = polygon.simplify(0.001)

# Create a slightly distorted or translated copy (for visible loft)
scaled_coords = [(x * 0.97, y * 1.02) for x, y in polygon.exterior.coords[:-1]]
top_polygon = geom.Polygon(scaled_coords)

# Loft between them
lofted = loft_between_polygons(polygon, top_polygon, height=15)

# Export
output_stl = "l_hand_rest_lofted.stl"
lofted.export(output_stl)

print(f"✅ Exported lofted solid to {output_stl}")
