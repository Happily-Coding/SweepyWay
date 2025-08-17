for wire in workplane:
    for vertex in wire.Vertices():
        print(vertex.X, vertex.Y, vertex.Z)

# for solid in result.val().Solids():
#     for face in solid.Faces():
#         for wire in face.Wires():
#             for vertex in wire.Vertices():
#                 print(vertex.X, vertex.Y, vertex.Z)