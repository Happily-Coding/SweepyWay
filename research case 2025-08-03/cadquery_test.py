# CADQUERY PART
import cadquery as cq
from cadquery import exporters

# Strip Z for 2D polyline
p1_cq = [(x, y) for x, y, z in p1]
p2_cq = [(x, y) for x, y, z in p2]

part = (
    cq.Workplane("XY")
    .polyline(p1_cq).close()
    .workplane(offset=height)
    .polyline(p2_cq).close()
    .loft(combine=True)
)

exporters.export(part, filename_cq)
print("CADQUERY STL saved to:", os.path.abspath(filename_cq))