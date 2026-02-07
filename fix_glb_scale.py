#!/usr/bin/env python3
"""
Fix GLB unit scale for SweepyWay PCBs using pygltflib.

KiCad exports GLB files in millimeters but glTF format expects meters.
This script applies a 1000x scale factor to convert meters → millimeters.

This version uses pygltflib to directly manipulate the glTF/GLB file at the
buffer level, preserving all scene structure.

Usage:
    python3 fix_glb_scale.py
    python3 fix_glb_scale.py --verbose
"""

import pygltflib
import numpy as np
import os
import argparse
import time


def debug_glb_info(gltf, label: str) -> None:
    """Print debug information about the GLB file."""
    print(f'  {label}:')
    print(f'    Nodes: {len(gltf.nodes)}')
    print(f'    Geometries (accessors): {len(gltf.accessors)}')
    print(f'    Buffers: {len(gltf.buffers)}')
    
    # Check position accessor min/max values
    position_accessors = [a for a in gltf.accessors if a.type == 'VEC3' and a.componentType == pygltflib.FLOAT]
    if position_accessors:
        print('  Sample position accessor min/max (first 3):')
        for i, accessor in enumerate(position_accessors[:3]):
            min_vals = accessor.min if accessor.min else [0, 0, 0]
            max_vals = accessor.max if accessor.max else [0, 0, 0]
            print(f'    Accessor {i}: min=[{min_vals[0]:.6f},{min_vals[1]:.6f},{min_vals[2]:.6f}], max=[{max_vals[0]:.6f},{max_vals[1]:.6f},{max_vals[2]:.6f}]')


def fix_glb_scale_pygltflib(board_name: str, verbose: bool = False) -> bool:
    """
    Fix scale using pygltflib direct buffer manipulation.
    
    This approach reads the GLB file, scales the position data in the buffers,
    and updates the node transforms to preserve positions.
    """
    misscaled_path = f'./filtered-output/pcbs/3d/{board_name}_pcb-3d-misscaled.glb'
    glb_path = f'./filtered-output/pcbs/3d/{board_name}_pcb-3d.glb'
    
    if not os.path.exists(misscaled_path):
        if verbose:
            print(f'Skipping {misscaled_path} - not found')
        return False
    
    if verbose:
        print(f'Processing: {misscaled_path}')
    
    start_time = time.time()
    
    # Load GLB file (load the input file, not the output)
    gltf = pygltflib.GLTF2().load(misscaled_path)
    
    if verbose:
        debug_glb_info(gltf, 'Before scaling')
    
    # Get the scale factor (1000 for meters -> millimeters)
    scale_factor = 1000.0
    
    # Get binary data from the GLB file
    binary_data = gltf.binary_blob()
    
    if binary_data is not None:
        # Convert to mutable bytearray for modification
        data_array = bytearray(binary_data)
        
        # Scale positions in the binary blob and update accessor min/max
        for accessor in gltf.accessors:
            if accessor.type == 'VEC3' and accessor.componentType == pygltflib.FLOAT:
                buffer_view = gltf.bufferViews[accessor.bufferView]
                byte_offset = buffer_view.byteOffset or 0
                accessor_byte_offset = accessor.byteOffset or 0
                total_offset = byte_offset + accessor_byte_offset
                stride = buffer_view.byteStride or (3 * 4)
                
                # Track min/max for this accessor
                min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
                max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
                
                for i in range(accessor.count):
                    pos_offset = total_offset + i * stride
                    x = np.frombuffer(data_array[pos_offset:pos_offset+4], dtype=np.float32)[0]
                    y = np.frombuffer(data_array[pos_offset+4:pos_offset+8], dtype=np.float32)[0]
                    z = np.frombuffer(data_array[pos_offset+8:pos_offset+12], dtype=np.float32)[0]
                    
                    # Scale the position
                    data_array[pos_offset:pos_offset+4] = np.float32(x * scale_factor).tobytes()
                    data_array[pos_offset+4:pos_offset+8] = np.float32(y * scale_factor).tobytes()
                    data_array[pos_offset+8:pos_offset+12] = np.float32(z * scale_factor).tobytes()
                    
                    # Track min/max (convert to Python float)
                    scaled_x = float(x * scale_factor)
                    scaled_y = float(y * scale_factor)
                    scaled_z = float(z * scale_factor)
                    
                    min_x = min(min_x, scaled_x)
                    max_x = max(max_x, scaled_x)
                    min_y = min(min_y, scaled_y)
                    max_y = max(max_y, scaled_y)
                    min_z = min(min_z, scaled_z)
                    max_z = max(max_z, scaled_z)
                
                # Update accessor min/max (convert numpy types to Python float)
                accessor.min = [float(min_x), float(min_y), float(min_z)]
                accessor.max = [float(max_x), float(max_y), float(max_z)]
        
        # Update the binary blob with scaled data
        gltf.set_binary_blob(bytes(data_array))
    else:
        # Handle external buffer URIs
        for buffer in gltf.buffers:
            data = gltf.get_data_from_buffer_uri(buffer.uri)
            data_array = bytearray(data)
            
            # Scale positions in this buffer
            for accessor in gltf.accessors:
                if accessor.type == 'VEC3' and accessor.componentType == pygltflib.FLOAT:
                    buffer_view = gltf.bufferViews[accessor.bufferView]
                    if buffer_view.buffer == buffer.uri:
                        byte_offset = buffer_view.byteOffset or 0
                        accessor_byte_offset = accessor.byteOffset or 0
                        total_offset = byte_offset + accessor_byte_offset
                        stride = buffer_view.byteStride or (3 * 4)
                        
                        # Track min/max for this accessor
                        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
                        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
                        
                        for i in range(accessor.count):
                            pos_offset = total_offset + i * stride
                            x = np.frombuffer(data_array[pos_offset:pos_offset+4], dtype=np.float32)[0]
                            y = np.frombuffer(data_array[pos_offset+4:pos_offset+8], dtype=np.float32)[0]
                            z = np.frombuffer(data_array[pos_offset+8:pos_offset+12], dtype=np.float32)[0]
                            
                            data_array[pos_offset:pos_offset+4] = np.float32(x * scale_factor).tobytes()
                            data_array[pos_offset+4:pos_offset+8] = np.float32(y * scale_factor).tobytes()
                            data_array[pos_offset+8:pos_offset+12] = np.float32(z * scale_factor).tobytes()
                            
                            scaled_x = float(x * scale_factor)
                            scaled_y = float(y * scale_factor)
                            scaled_z = float(z * scale_factor)
                            
                            min_x = min(min_x, scaled_x)
                            max_x = max(max_x, scaled_x)
                            min_y = min(min_y, scaled_y)
                            max_y = max(max_y, scaled_y)
                            min_z = min(min_z, scaled_z)
                            max_z = max(max_z, scaled_z)
                        
                        # Update accessor min/max
                        accessor.min = [float(min_x), float(min_y), float(min_z)]
                        accessor.max = [float(max_x), float(max_y), float(max_z)]
            
            # Update the buffer with scaled data
            gltf.set_binary_blob(bytes(data_array))
    
    # Update node transforms to account for scaling
    for node in gltf.nodes:
        if node.translation:
            node.translation[0] *= scale_factor
            node.translation[1] *= scale_factor
            node.translation[2] *= scale_factor
        elif node.matrix:
            # Scale the translation component of the matrix (last column)
            m = node.matrix
            if len(m) >= 16:
                m[12] *= scale_factor  # tx
                m[13] *= scale_factor  # ty
                m[14] *= scale_factor  # tz
                node.matrix = m
    
    if verbose:
        debug_glb_info(gltf, 'After scaling')
        elapsed = time.time() - start_time
        print(f'  Processing time: {elapsed:.2f}s')
        print('  Verification: Check that accessor min/max values are ~1000x larger')
    
    # Save the modified GLB
    gltf.save(glb_path)
    
    if verbose:
        print(f'  Fixed: {board_name}')
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Fix GLB unit scale for SweepyWay PCBs using pygltflib'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )
    parser.add_argument(
        '--boards',
        nargs='+',
        default=['left', 'right'],
        help='Board names to process (default: left right)'
    )
    
    args = parser.parse_args()
    
    print('Fixing GLB unit scale (meters -> millimeters) using pygltflib...')
    
    # Debug: List all files ending with -misscaled anywhere in the project
    print('\n=== Searching for all files ending with -misscaled ===')
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('-misscaled.glb'):
                full_path = os.path.join(root, file)
                print(f'  Found: {full_path}')
    print('=== End of -misscaled file search ===\n')
    
    for board in args.boards:
        fix_glb_scale_pygltflib(board, args.verbose)
    
    print('Done.')


if __name__ == '__main__':
    main()
