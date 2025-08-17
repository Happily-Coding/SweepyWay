import trimesh
import numpy as np

# Define bottom square (CCW order)
bottom = np.array([
    [0, 0, 0],  # 0
    [1, 0, 0],  # 1
    [1, 1, 0],  # 2
    [0, 1, 0],  # 3
])

# Define top square with slope in Z (same XY order)
top = np.array([
    [0, 0, 0],  # 4  (same X,Y as bottom 0, Z=0)
    [1, 0, 1],  # 5  (sloped higher at X=1)
    [1, 1, 1],  # 6
    [0, 1, 0],  # 7  (same height as bottom 3)
])

# Combine vertices (bottom first, then top)
vertices = np.vstack((bottom, top))

faces = []

# Bottom face (two triangles)
faces.append([0, 1, 2])
faces.append([0, 2, 3])

# Top face (reverse winding for outward normal)
offset = len(bottom)
faces.append([offset + 2, offset + 1, offset + 0])
faces.append([offset + 3, offset + 2, offset + 0])

# Side faces (two triangles per edge)
n = len(bottom)
for i in range(n):
    next_i = (i + 1) % n
    # Triangle 1
    faces.append([i, next_i, offset + i])
    # Triangle 2
    faces.append([next_i, offset + next_i, offset + i])

# Create mesh
mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

# Export to STL
mesh.export('sloped_cube.stl')
print("Exported sloped_cube.stl")
