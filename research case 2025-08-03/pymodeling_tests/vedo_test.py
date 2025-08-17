import numpy as np
from vedo import write
from vedo.shapes import Loft
from vedo.i

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

arms = 5
height = 10
p1 = generate_star_points(10, 5, arms, 0)
p2 = generate_star_points(5, 2.5, arms, height)

profiles = [p1, p2]

loft_mesh = Loft(profiles, closed=True)

write(loft_mesh, "star_loft_vedo.stl")
print("VEDO STL saved to star_loft_vedo.stl")
