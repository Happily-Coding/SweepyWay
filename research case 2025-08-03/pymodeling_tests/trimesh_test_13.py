import trimesh
import numpy as np

def load_polygon(dxf_path):
    scene = trimesh.load(dxf_path, force='2D')

    for geom in scene.geometry.values():
        if isinstance(geom, trimesh.path.Path2D):
            polygons = geom.polygons_full
            if polygons:
                largest_polygon = max(polygons, key=lambda p: p.area)
                coords = np.array(largest_polygon.exterior.coords)
                if np.all(coords[0] == coords[-1]):
                    coords = coords[:-1]
                return coords

    raise ValueError("No polygon found in DXF.")

if __name__ == "__main__":
    polygon = load_polygon("l_hand_rest_polygon.dxf")
    print("Loaded polygon vertices:")
    print(polygon)
