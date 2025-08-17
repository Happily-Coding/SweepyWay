import numpy as np
import os
import cadquery as cq
from cadquery import exporters

arms = 5
height = 10
filename_cq = "star_loft_cadquery.stl"

def generate_star_points(radius1, radius2, arms, z=0):
    pts = []
    step = np.pi / arms
    for i in range(2 * arms):
        r = radius1 if i % 2 == 0 else radius2
        angle = i * step
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        pts.append([x, y, z])
    return pts

def main():
    p1 = generate_star_points(10, 5, arms, 0)
    p2 = generate_star_points(5, 2.5, arms, height)

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


if __name__ == "__main__":
    main()
