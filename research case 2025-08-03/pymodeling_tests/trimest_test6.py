import trimesh
import shapely.geometry as geom
import numpy as np

def loft_with_caps_using_extrude_polygon(polygon, height):
    """
    Create a solid mesh loft by using extrude_polygon to get caps and 
    manually connecting side walls for exact vertex control.
    """
    # Step 1: Use extrude_polygon to get caps (does triangulation internally)
    extrusion = trimesh.creation.extrude_polygon(polygon, height)
    extrusion.merge_vertices()  # cleanup, just in case

    return extrusion

# Load DXF
dxf_path = "l_hand_rest_polygon.dxf"
entities = trimesh.load(dxf_path, force='2D')

# Extract the largest polygon
polygons = entities.polygons_full
if not polygons:
    raise ValueError("❌ No closed polygons found in the DXF")

polygon = max(polygons, key=lambda p: p.area)

# Height of extrusion
height = 20

# Create solid loft using internal triangulation (no extra deps!)
solid = loft_with_caps_using_extrude_polygon(polygon, height)

# Export
output_file = "l_hand_rest_extruded_solid.stl"
solid.export(output_file)

print("✅ Exported solid with caps to:", output_file)
print("Watertight:", solid.is_watertight)
