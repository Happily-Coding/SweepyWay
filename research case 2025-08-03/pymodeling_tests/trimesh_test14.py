import trimesh
import numpy as np
from shapely.geometry import Polygon
from typing import List, Tuple, Union

def loft_between_polygons(
    poly1: Union[np.ndarray, List[Tuple[float, float]]],
    poly2: Union[np.ndarray, List[Tuple[float, float]]],
    z1: float = 0.0,
    z2: float = 1.0
) -> trimesh.Trimesh:
    poly1 = np.asarray(poly1)
    poly2 = np.asarray(poly2)
    
    if poly1.shape[0] != poly2.shape[0]:
        raise ValueError("Both polygons must have the same number of vertices.")
    
    n: int = poly1.shape[0]
    vertices_bottom: np.ndarray = np.column_stack((poly1, np.full(n, z1)))
    vertices_top: np.ndarray = np.column_stack((poly2, np.full(n, z2)))
    vertices: np.ndarray = np.vstack((vertices_bottom, vertices_top))
    
    faces: List[List[int]] = []
    for i in range(1, n-1):
        faces.append([0, i, i+1])
    top_offset: int = n
    for i in range(1, n-1):
        faces.append([top_offset, top_offset + i + 1, top_offset + i])
    for i in range(n):
        next_i: int = (i + 1) % n
        faces.append([i, next_i, top_offset + i])
        faces.append([next_i, top_offset + next_i, top_offset + i])
    
    mesh: trimesh.Trimesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    return mesh


def load_polygon_from_dxf() -> Polygon:
    """
    Loads the first closed polyline (LWPOLYLINE or POLYLINE) from the DXF file.
    Returns a shapely Polygon object.
    """
    dxf_path: str = "l_hand_rest_polygon.dxf"
    entities = trimesh.load(dxf_path, force='2D')
    polygon: Polygon = max(entities.polygons_full, key=lambda p: p.area)
    return polygon


if __name__ == "__main__":
    # Load polygon from DXF
    input_dxf: str = "l_hand_rest_polygon.dxf"  # change to your filename
    polygon: Polygon = load_polygon_from_dxf()

    # Create a translated copy
    translation: Tuple[float, float] = (2.0, 1.0)  # translate by 2 in x, 1 in y
    polygon_translated: List[Tuple[float, float]] = [
        (x + translation[0], y + translation[1]) for x, y in polygon.exterior.coords[:-1]
    ]

    poly1: np.ndarray = np.array(polygon.exterior.coords[:-1])
    poly2: np.ndarray = np.array(polygon_translated)

    mesh: trimesh.Trimesh = loft_between_polygons(poly1, poly2, z1=0, z2=3)

    # Export mesh to STL
    output_stl: str = "lofted_polyhedron_from_dxf.stl"
    mesh.export(output_stl)
    print(f"STL file saved as '{output_stl}'")


#FULLY WORKING