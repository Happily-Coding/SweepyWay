import cadquery as cq
from cadquery import importers, exporters

input_dxf = "l_hand_rest_polygon.dxf"
output_stl = "hand_rest_loft.stl"
height = 20

# STEP 1: Import the DXF
wp_bottom = importers.importDXF(input_dxf)

# STEP 2: Validate that geometry was loaded
if len(wp_bottom.objects) == 0:
    raise ValueError("No geometry found in the DXF file")

# STEP 3: Extract wires from the imported DXF
bottom_wires = wp_bottom.wires().vals()
if len(bottom_wires) == 0:
    raise ValueError("No wires found in the DXF file")

# STEP 4: Create translated top wires
top_wires = []
for wire in bottom_wires:
    translated_wire = wire.translate((0, 0, height))
    top_wires.append(translated_wire)

# STEP 5: Convert wires to faces
bottom_faces = []
top_faces = []

for b_wire, t_wire in zip(bottom_wires, top_wires):
    b_face = cq.Face.makeFromWires(b_wire)
    t_face = cq.Face.makeFromWires(t_wire)
    bottom_faces.append(b_face)
    top_faces.append(t_face)

# STEP 6: Loft between corresponding bottom and top faces
loft_solids = []

for b_face, t_face in zip(bottom_faces, top_faces):
    wp = cq.Workplane("XY")
    wp = wp.add(b_face)
    single_loft = wp.loft([t_face], combine=True)
    loft_solids.append(single_loft)

# STEP 7: Combine all lofted solids into one result
result = loft_solids[0]
for solid in loft_solids[1:]:
    result = result.union(solid)

# STEP 8: Export the final solid
exporters.export(result, output_stl)
print(f"✅ Exported lofted solid to {output_stl}")
