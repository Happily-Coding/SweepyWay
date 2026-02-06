#!/usr/bin/env python3
"""
Convert binary STL files to ASCII STL format for GitHub markdown rendering.
 
GitHub renders STL files in markdown using the ASCII STL format:
```stl
solid Mesh
  facet normal -0.000000 1.000000 0.000000
    outer loop
      vertex x y z
      vertex x y z
      vertex x y z
    endloop
  endfacet
endsolid Mesh
"""

import sys
import os
import struct


def read_binary_stl(filename):
    """Read binary STL file and return list of facets."""
    with open(filename, 'rb') as f:
        # Read header (80 bytes)
        header = f.read(80)

        # Read number of facets (4 bytes, little endian)
        num_facets = struct.unpack('<I', f.read(4))[0]

        facets = []
        for _ in range(num_facets):
            # Read normal (3 floats * 4 bytes = 12 bytes, little endian)
            normal = struct.unpack('<fff', f.read(12))

            # Read vertices (3 vertices * 3 floats * 4 bytes = 36 bytes, little endian)
            v1 = struct.unpack('<fff', f.read(12))
            v2 = struct.unpack('<fff', f.read(12))
            v3 = struct.unpack('<fff', f.read(12))

            # Read attribute byte count (2 bytes, little endian)
            attribute = struct.unpack('<H', f.read(2))[0]

            facets.append((normal, v1, v2, v3))

    return facets


def write_ascii_stl(filename, facets):
    """Write ASCII STL file."""
    with open(filename, 'w') as f:
        f.write(f"solid Mesh\n")

        for normal, v1, v2, v3 in facets:
            f.write("  facet normal {:.6f} {:.6f} {:.6f}\n".format(
                normal[0], normal[1], normal[2]))
            f.write("    outer loop\n")
            f.write("      vertex {:.6f} {:.6f} {:.6f}\n".format(*v1))
            f.write("      vertex {:.6f} {:.6f} {:.6f}\n".format(*v2))
            f.write("      vertex {:.6f} {:.6f} {:.6f}\n".format(*v3))
            f.write("    endloop\n")
            f.write("  endfacet\n")

        f.write("endsolid Mesh\n")


def convert_stl_to_ascii(input_file, output_file=None):
    """Convert binary STL to ASCII STL."""
    if output_file is None:
        output_file = input_file.replace('.stl', '-ascii.stl')

    print(f"Converting {input_file} to {output_file}...")

    # Read binary STL
    facets = read_binary_stl(input_file)

    # Write ASCII STL
    write_ascii_stl(output_file, facets)

    print(f"✓ Converted {len(facets)} facets")
    print(f"✓ Saved to {output_file}")
    return output_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python stl2ascii.py <input.stl> [output.stl]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    convert_stl_to_ascii(input_file, output_file)


if __name__ == '__main__':
    main()