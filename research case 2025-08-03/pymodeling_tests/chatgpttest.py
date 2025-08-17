import cadquery as cq
from cadquery import importers, exporters

input_dxf = "l_hand_rest_polygon.dxf"
output_stl = "hand_rest_loft.stl"
height = 20

# Load wires (list of Wire objects)
wires_bottom = importers.importDXF(input_dxf)

if not wires_bottom:
    raise ValueError("No wires found in the DXF file")

# Create top wires by translating the bottom wires up
wires_top = [wire.translate((0, 0, height)) for wire in wires_bottom]

# Create bottom compound and top compound
bottom_compound = cq.Compound.makeCompound(wires_bottom)
top_compound = cq.Compound.makeCompound(wires_top)

# Create Workplanes with bottom and top profiles
wp = cq.Workplane("XY").add(bottom_compound)
wp_top = cq.Workplane("XY").add(top_compound)

# Loft between bottom and top profiles
# Note: loft takes a list of shapes (wires/faces)
solid = wp.loft([wp_top.val()], combine=True)

# Export the result
exporters.export(solid, output_stl)

print(f"✅ Exported lofted solid to {output_stl}")
