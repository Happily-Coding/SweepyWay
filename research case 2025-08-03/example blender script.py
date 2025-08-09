import bpy

# Get the active object (assuming your imported curve is selected)
curve_obj = bpy.context.active_object

if curve_obj and curve_obj.type == 'CURVE':
    # Set bevel depth to add thickness (adjust value as needed)
    curve_obj.data.bevel_depth = 0.5  # Blender units (try 0.1 to 1)
    
    # Optionally, increase resolution for smoother curve
    curve_obj.data.bevel_resolution = 4
    
    print("Curve bevel added!")
else:
    print("Select a curve object before running this script.")


import bpy
import bmesh

# Clean the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Define 5 points
points = [
    [-1, -1, 0],
    [ 1, -1, 0],
    [ 1,  1, 0],
    [-1,  1, 0], 
    
    [-1, -1, 1],
    [ 1, -1, 1],
    [ 1,  1, 2],
    [-1,  1, 2]
]

# Create a new mesh and object
mesh = bpy.data.meshes.new('AutoPyramid')
obj = bpy.data.objects.new('AutoPyramid', mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj

# Use BMesh to generate convex hull from points
bm = bmesh.new()
verts = [bm.verts.new(p) for p in points]
bm.verts.ensure_lookup_table()

# Convex hull operator to automatically create faces
bmesh.ops.convex_hull(bm, input=bm.verts)

# Write BMesh to Blender mesh
bm.to_mesh(mesh)
bm.free()
