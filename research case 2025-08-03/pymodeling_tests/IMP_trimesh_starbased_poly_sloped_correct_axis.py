import trimesh
import numpy as np
from shapely.geometry import Polygon
from trimesh.creation import triangulate_polygon

def create_star_points(radius_outer=1.0, radius_inner=0.5, points=5):
    angles = np.linspace(0, 2 * np.pi, points * 2, endpoint=False)
    radii = np.empty(points * 2)
    radii[::2] = radius_outer
    radii[1::2] = radius_inner
    xs = radii * np.cos(angles)
    ys = radii * np.sin(angles)
    return np.column_stack((xs, ys))


def polygon_to_numpy(polygon: Polygon) -> np.ndarray:
    """
    Convert a shapely Polygon to an Nx2 NumPy array of (x, y) coordinates.
    The last (repeated) point is removed.
    """
    coords = np.array(polygon.exterior.coords)
    if np.allclose(coords[0], coords[-1]):
        coords = coords[:-1]
    return coords



# Create star polygon
#star_2d = create_star_points()
#poly = Polygon(star_2d)

# Triangulate polygon (returns new vertices and faces)
from shapely.geometry import Polygon

# Load from DXF
dxf_path = "l_hand_rest_polygon.dxf"
entities = trimesh.load(dxf_path, force='2D')
poly = max(entities.polygons_full, key=lambda p: p.area)

star_2d = polygon_to_numpy(poly)
tri_verts_2d, tri_faces = triangulate_polygon(poly)

# Bottom vertices (triangulation vertices at z=0)
bottom_verts = np.column_stack((tri_verts_2d, np.zeros(len(tri_verts_2d))))

# Top vertices (same XY as bottom_verts, slope in Z)
# Here, just slope by y coordinate normalized to [0,1]
y_norm = (tri_verts_2d[:,1] - tri_verts_2d[:,1].min()) / np.ptp(tri_verts_2d[:,1])
z_top = 0.5 + y_norm * 1.0 * 20 #Linear, works perfectly
#z_top = 0.5 + (y_norm ** 2) * 20 #Curved, works like the rest

top_verts = np.column_stack((tri_verts_2d, z_top))

# Combine vertices
vertices = np.vstack((bottom_verts, top_verts))

faces = []

n_bottom = len(bottom_verts)
offset = n_bottom

# Bottom faces: use tri_faces as is
for f in tri_faces:
    faces.append([f[0], f[1], f[2]])

# Top faces: reverse winding order and offset indices
for f in tri_faces:
    faces.append([offset + f[2], offset + f[1], offset + f[0]])

# Side faces: connect the edges of the original polygon (not triangulation vertices)
n_orig = len(star_2d)

for i in range(n_orig):
    next_i = (i + 1) % n_orig
    # Find matching indices of star_2d points in tri_verts_2d
    # Since tri_verts_2d may include extra points, we find the closest matching vertices by coords
    idx_bottom_i = np.argmin(np.linalg.norm(tri_verts_2d - star_2d[i], axis=1))
    idx_bottom_next = np.argmin(np.linalg.norm(tri_verts_2d - star_2d[next_i], axis=1))
    
    # Create two triangles for each side quad
    faces.append([idx_bottom_i, idx_bottom_next, offset + idx_bottom_i])
    faces.append([idx_bottom_next, offset + idx_bottom_next, offset + idx_bottom_i])

mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
mesh.export("sloped_star_corrected.stl")
print("Exported sloped_star_corrected.stl")
