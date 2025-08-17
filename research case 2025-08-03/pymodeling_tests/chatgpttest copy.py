import cadquery as cq
from cadquery import importers, exporters

input_dxf = "l_hand_rest_polygon.dxf"
output_stl = "hand_rest_loft.stl"
height = 20

# Load DXF as a Workplane
wp_bottom = importers.importDXF(input_dxf)

# Create the top profile by copying and translating the bottom WP up by height
wp_top = wp_bottom.translate((0, 0, height))

# Loft between the bottom and top profiles
solid = wp_bottom.loft([wp_top.val()], combine=True)

# Export the solid as STL
exporters.export(solid, output_stl)

print(f"✅ Exported lofted solid to {output_stl}")
