import cadquery as cq
from cadquery import importers, exporters

input_dxf = "l_hand_rest_polygon.dxf"
output_stl = "hand_rest_extruded.stl"
height = 20

# Import DXF wires
wires = importers.importDXF(input_dxf)
wires2 = importers.importDXF(input_dxf).translate([0,0,height])


if not wires:
    raise ValueError("No wires found in the DXF file")

# Create a workplane and add all wires
wp = cq.Workplane("XY").add(wires)#.workplane(offset=height)

# Extrude the shape
solid = wp.extrude(height)

# Export to STL
exporters.export(solid, output_stl)

print(f"✅ Exported extruded solid to {output_stl}")
