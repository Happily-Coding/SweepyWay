import trimesh
import shapely.geometry as geom
import numpy as np

def loft_between_polygons_with_caps(polygon, height):
    """
    Create a solid mesh by lofting a polygon vertically and capping both ends.
    """
    coords = np.array(polygon.exterior.coords)[:-1]

    # Bottom and top 3D vertices
    bottom_vertices = np.hstack([coords, np.zeros((len(coords), 1))])
    top_vertices = np.hstack([coords, np.full((len(coords), 1), height)])
    vertices = np.vstack([bottom_vertices, top_vertices])

    n = len(coords)
    faces = []

    # Side faces (two triangles per side)
    for i in range(n):
        a, b = i, (i + 1) % n
        faces.append([a, b, b + n])
        faces.append([b + n, a + n, a])

    # Cap bottom using triangulation
    bottom_2d = geom.Polygon(coords)
    if not bottom_2d.is_valid:
        bottom_2d = bottom_2d.buffer(0)

    bottom_trimesh = trimesh.creation.extrude_polygon(bottom_2d, 0.01)
    for face in bottom_trimesh.faces:
        faces.append(face)

    # Cap top using same triangulation, offset and reverse winding
    top_offset = len(bottom_vertices)
    for face in bottom_trimesh.faces:
        reversed_face = [top_offset + idx for idx in face[::-1]]
        faces.append(reversed_face)

    solid_mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    return solid_mesh

# Load DXF and get polygon
dxf_path = "l_hand_rest_polygon.dxf"
entities = trimesh.load(dxf_path, force='2D')
polygon = max(entities.polygons_full, key=lambda p: p.area)

# Create solid lofted mesh
height = 20
solid_mesh = loft_between_polygons_with_caps(polygon, height)

# Export to STL
output_path = "l_hand_rest_solid_loft_fixed.stl"
solid_mesh.export(output_path)

# Optional: Check watertightness
print("✅ Exported:", output_path)
#print("Watertight:", solid_mesh.is_watertight)
