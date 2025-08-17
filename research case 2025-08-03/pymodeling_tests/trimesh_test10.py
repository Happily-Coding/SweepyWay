import trimesh
import numpy as np

def loft_between_polygons(poly1, poly2, z1=0.0, z2=1.0):
    """
    Loft between two polygons and create a filled polyhedron using trimesh.
    
    Parameters:
    - poly1: Nx2 array-like of (x, y) points for the bottom polygon
    - poly2: Nx2 array-like of (x, y) points for the top polygon
    - z1: z-coordinate of the bottom polygon (default 0.0)
    - z2: z-coordinate of the top polygon (default 1.0)
    
    Returns:
    - trimesh.Trimesh object representing the lofted polyhedron.
    """
    poly1 = np.asarray(poly1)
    poly2 = np.asarray(poly2)
    
    if poly1.shape[0] != poly2.shape[0]:
        raise ValueError("Both polygons must have the same number of vertices.")
    
    n = poly1.shape[0]

    # Create vertices: bottom and top polygons in 3D
    vertices_bottom = np.column_stack((poly1, np.full(n, z1)))
    vertices_top = np.column_stack((poly2, np.full(n, z2)))
    
    vertices = np.vstack((vertices_bottom, vertices_top))
    
    faces = []

    # Create faces for bottom polygon (triangulate using fan method)
    for i in range(1, n-1):
        faces.append([0, i, i+1])
        
    # Create faces for top polygon (triangulate using fan method)
    top_offset = n
    for i in range(1, n-1):
        # Note reversed order for correct normal direction (top face)
        faces.append([top_offset, top_offset + i + 1, top_offset + i])
        
    # Create side faces connecting bottom and top polygons
    for i in range(n):
        next_i = (i + 1) % n
        # Each side face is made of two triangles forming a quad
        
        # Triangle 1
        faces.append([i, next_i, top_offset + i])
        # Triangle 2
        faces.append([next_i, top_offset + next_i, top_offset + i])
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    return mesh


if __name__ == "__main__":
    # Example polygons (square bottom, slightly scaled top)
    poly1 = [(0, 0), (1, 0), (1, 1), (0, 1)]
    poly2 = [(0.2, 0.1), (1.1, 0), (1.2, 1.1), (0, 1.2)]

    mesh = loft_between_polygons(poly1, poly2, z1=0, z2=2)

    # Export to STL file
    mesh.export('lofted_polyhedron.stl')
    print("STL file saved as 'lofted_polyhedron.stl'")
