import trimesh
import numpy as np

def loft_between_polygons(poly1, poly2, z1=0.0, z2=1.0):
    poly1 = np.asarray(poly1)
    poly2 = np.asarray(poly2)
    
    if poly1.shape[0] != poly2.shape[0]:
        raise ValueError("Both polygons must have the same number of vertices.")
    
    n = poly1.shape[0]
    vertices_bottom = np.column_stack((poly1, np.full(n, z1)))
    vertices_top = np.column_stack((poly2, np.full(n, z2)))
    vertices = np.vstack((vertices_bottom, vertices_top))
    
    faces = []
    for i in range(1, n-1):
        faces.append([0, i, i+1])
    top_offset = n
    for i in range(1, n-1):
        faces.append([top_offset, top_offset + i + 1, top_offset + i])
    for i in range(n):
        next_i = (i + 1) % n
        faces.append([i, next_i, top_offset + i])
        faces.append([next_i, top_offset + next_i, top_offset + i])
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    return mesh

def load_polygon_from_dxf_with_trimesh(dxf_path):
    """
    Load polygons from DXF using trimesh.load(force='2D')
    Extracts the first polygon with vertices as Nx2 numpy array.
    """
    scene = trimesh.load(dxf_path, force='2D')

    # trimesh.Scene.geometry is a dict of geometry objects
    # We look for a Path2D or Polygon object
    for geom_name, geom in scene.geometry.items():
        # geom can be Path2D or Polygon
        # For Path2D, extract polygons (as list of Nx2 arrays)
        if isinstance(geom, trimesh.path.Path2D):
            polygons = geom.polygons_full  # list of shapely polygons
            if len(polygons) == 0:
                continue
            # Take the first polygon
            poly = polygons[0]
            # poly is a shapely Polygon, get exterior coords as Nx2 numpy array
            coords = np.array(poly.exterior.coords)
            # Remove the repeated last point (same as first in shapely polygons)
            if np.all(coords[0] == coords[-1]):
                coords = coords[:-1]
            return coords
        # Or if already a Polygon or Polygon-like mesh:
        elif isinstance(geom, trimesh.Trimesh):
            # Might have 3D mesh, get unique xy coords of vertices as polygon
            vertices = geom.vertices[:, :2]
            return vertices

    raise ValueError("No polygon found in DXF")

if __name__ == "__main__":
    dxf_path = "l_hand_rest_polygon.dxf"  # Replace with your DXF file path

    polygon = load_polygon_from_dxf_with_trimesh(dxf_path)
    print(f"Loaded polygon with {len(polygon)} vertices")

    # Translate polygon in XY
    translation = np.array([2.0, 1.0])
    polygon_translated = polygon + translation

    # Loft mesh between original and translated polygon
    mesh = loft_between_polygons(polygon, polygon_translated, z1=0, z2=3)

    # Export STL
    stl_path = "lofted_polyhedron_from_dxf.stl"
    mesh.export(stl_path)
    print(f"STL file saved as '{stl_path}'")
