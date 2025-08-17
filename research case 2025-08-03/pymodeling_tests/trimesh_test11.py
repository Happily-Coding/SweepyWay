import trimesh
import numpy as np
import ezdxf

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


def load_polygon_from_dxf():
    """
    Loads the first closed polyline (LWPOLYLINE or POLYLINE) from the DXF file.
    Returns a list of (x, y) tuples.
    """
    dxf_path = "l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')
    polygon = max(entities.polygons_full, key=lambda p: p.area)
    return polygon


if __name__ == "__main__":
    # Load polygon from DXF
    input_dxf = "l_hand_rest_polygon.dxf"  # change to your filename
    polygon = load_polygon_from_dxf()

    # Create a translated copy
    translation = (2.0, 1.0)  # translate by 2 in x, 1 in y
    #polygon_translated = [(x + translation[0], y + translation[1]) for x, y in polygon]
    polygon_translated = [(x + translation[0], y + translation[1]) for x, y in polygon.exterior.coords[:-1]]

    poly1 = np.array(polygon.exterior.coords[:-1])
    poly2 = np.array(polygon_translated)

    mesh = loft_between_polygons(poly1, poly2, z1=0, z2=3)

    # Loft between the original polygon and the translated one
    #mesh = loft_between_polygons(polygon, polygon_translated, z1=0, z2=3)

    # Export mesh to STL
    output_stl = "lofted_polyhedron_from_dxf.stl"
    mesh.export(output_stl)
    print(f"STL file saved as '{output_stl}'")
