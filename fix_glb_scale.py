#!/usr/bin/env python3
"""
Fix GLB unit scale for SweepyWay PCBs.

KiCad exports GLB files in millimeters but glTF format expects meters.
This script applies a 1000x scale factor to convert meters → millimeters.

Usage:
    python3 fix_glb_scale.py
    python3 fix_glb_scale.py --verbose
"""

import trimesh
import os
import argparse


def fix_glb_scale(board_name: str, verbose: bool = False) -> bool:
    """Fix scale for a single PCB GLB file."""
    misscaled_path = f'./filtered-output/pcbs/3d/{board_name}_pcb-3d-misscaled.glb'
    glb_path = f'./filtered-output/pcbs/3d/{board_name}_pcb-3d.glb'
    
    if not os.path.exists(misscaled_path):
        if verbose:
            print(f'Skipping {misscaled_path} - not found')
        return False
    
    if verbose:
        print(f'Processing: {misscaled_path}')
    
    mesh = trimesh.load(misscaled_path)
    
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(list(mesh.geometry.values()))
    
    # Apply 1000x scale (meters → millimeters)
    mesh.apply_scale(1000)
    
    # Export to the correct path (avoiding permission issues)
    mesh.export(glb_path)
    
    if verbose:
        bounds = mesh.bounds[1] - mesh.bounds[0]
        print(f'  Fixed: {board_name} - size: {bounds}')
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Fix GLB unit scale for SweepyWay PCBs'
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
    
    print('Fixing GLB unit scale (meters -> millimeters)...')
    
    for board in args.boards:
        fix_glb_scale(board, args.verbose)
    
    print('Done.')


if __name__ == '__main__':
    main()