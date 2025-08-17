import numpy as np
import trimesh
import mapbox_earcut as earcut
from shapely.geometry import Polygon

import numpy as np
import trimesh
import mapbox_earcut as earcut
from shapely.geometry import Polygon

def triangulate_shapely_polygon(polygon: Polygon):
    """
    Triangulate a shapely polygon with holes using mapbox_earcut.
    Returns vertices as Nx2 numpy array and faces as Mx3 numpy array.
    """

    if not polygon.is_valid:
        polygon = polygon.buffer(0)  # fix self-intersections if any

    # Extract exterior ring coords (without repeated last point)
    exterior_coords = np.array(polygon.exterior.coords[:-1])
    if exterior_coords.ndim != 2 or exterior_coords.shape[1] != 2:
        raise ValueError(f"Exterior coords shape invalid: {exterior_coords.shape}")

    # Extract interior rings (holes) coords
    holes_coords = []
    for interior in polygon.interiors:
        coords = np.array(interior.coords[:-1])
        if coords.ndim != 2 or coords.shape[1] != 2:
            raise ValueError(f"Interior ring coords shape invalid: {coords.shape}")
        holes_coords.append(coords)

    # Combine all vertices into a single array
    vertices = exterior_coords.copy()
    hole_indices = []
    offset = len(exterior_coords)

    for hole in holes_coords:
        hole_indices.append(offset)
        vertices = np.vstack([vertices, hole])
        offset += len(hole)

    # Flatten vertices for earcut (1D array [x0, y0, x1, y1, ...])
    coords_flat = vertices.flatten()

    print(polygon)
    print("Is valid:", polygon.is_valid)
    print("Exterior coords shape:", np.array(polygon.exterior.coords).shape)
    print("Number of interior rings (holes):", len(polygon.interiors))
    for i, interior in enumerate(polygon.interiors):
        print(f"Interior ring {i} coords shape:", np.array(interior.coords).shape)


    # Triangulate
    faces = earcut.triangulate_float64(coords_flat, hole_indices)

    # Reshape faces to Nx3 triangles
    faces = np.array(faces, dtype=np.int64).reshape(-1, 3)

    return vertices, faces


# The rest of your loft_between_polygons function stays unchanged


def loft_between_polygons(polygon: Polygon, height: float):
    """
    Creates a solid loft mesh between a polygon and its raised copy.

    Returns:
      trimesh.Trimesh solid mesh
    """
    vertices_2d, faces_2d = triangulate_shapely_polygon(polygon)
    n = len(vertices_2d)

    # Bottom and top vertices with Z
    bottom_vertices = np.hstack([vertices_2d, np.zeros((n,1))])
    top_vertices = np.hstack([vertices_2d, np.full((n,1), height)])

    # Combine bottom and top vertices
    vertices_3d = np.vstack([bottom_vertices, top_vertices])

    faces = []

    # Side faces (quads split into triangles)
    for i in range(n):
        next_i = (i + 1) % n
        # Quad = bottom_i, bottom_next, top_next, top_i
        faces.append([i, next_i, next_i + n])
        faces.append([next_i + n, i + n, i])

    # Bottom cap faces (keep original winding)
    for tri in faces_2d:
        faces.append(tri.tolist())

    # Top cap faces (reverse winding so normals face outward)
    for tri in faces_2d:
        faces.append([idx + n for idx in tri[::-1]])

    # Create the mesh
    mesh = trimesh.Trimesh(vertices=vertices_3d, faces=faces, process=True)

    return mesh


if __name__ == "__main__":
    # Example polygon (replace with your loaded DXF polygon!)
    poly = Polygon([(0, 0), (5, 0), (4, 4), (1, 3)])

    height = 10

    lofted_mesh = loft_between_polygons(poly, height)

    # Export to STL
    lofted_mesh.export("lofted_solid.stl")
    print("✅ Exported solid lofted mesh to 'lofted_solid.stl'")
