import trimesh
import shapely.geometry as geom
import numpy as np

def loft_between_polygons(p1, p2, height):
    coords1 = np.array(p1.exterior.coords)[:-1]
    coords2 = np.array(p2.exterior.coords)[:-1]

    if len(coords1) != len(coords2):
        raise ValueError("Polygons must have the same number of points")

    # Create bottom and top 3D vertices
    v1 = np.hstack([coords1, np.zeros((len(coords1), 1))])
    v2 = np.hstack([coords2, np.full((len(coords2), 1), height)])
    vertices = np.vstack([v1, v2])

    # Side faces
    faces = []
    n = len(coords1)
    for i in range(n):
        a, b = i, (i + 1) % n
        faces.append([a, b, b + n])
        faces.append([b + n, a + n, a])

    # Cap bottom
    bottom_tris = trimesh.Trimesh(vertices=v1, process=True).faces
    for tri in bottom_tris:
        faces.append(tri)

    # Cap top (reverse winding for correct normals)
    offset = len(v1)
    top_tris = trimesh.Trimesh(vertices=v2, process=True).faces
    for tri in top_tris:
        faces.append([offset + i for i in tri[::-1]])

    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

# --- Load DXF and prepare polygons ---
dxf_path = "l_hand_rest_polygon.dxf"
entities = trimesh.load(dxf_path, force='2D')

# Get largest polygon from the DXF
polygons = entities.polygons_full
if not polygons:
    raise ValueError("❌ No closed polygons found in the DXF")

polygon = max(polygons, key=lambda p: p.area)

# Duplicate the shape exactly (no distortion), just lift in Z
top_polygon = geom.Polygon(polygon.exterior.coords[:-1])  # exact copy

# Loft from bottom to top at given height
height = 20
lofted_mesh = loft_between_polygons(polygon, top_polygon, height=height)

# Export
output_file = "l_hand_rest_lofted_solid.stl"
lofted_mesh.export(output_file)

print(f"✅ Exported solid loft to: {output_file}")
