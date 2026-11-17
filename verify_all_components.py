#!/usr/bin/env python3
"""Verify that all problem components are present in 3D exports."""

import os
import sys

# Files to check
FILES = {
    'left_pcb': {
        'step': 'filtered-output/pcbs/3d/left_pcb-3d.step',
        'glb': 'filtered-output/pcbs/3d/left_pcb-3d.glb',
    },
    'right_pcb': {
        'step': 'filtered-output/pcbs/3d/right_pcb-3d.step',
        'glb': 'filtered-output/pcbs/3d/right_pcb-3d.glb',
    }
}

# Component designators and model names to search for
COMPONENTS = {
    'JST_PH': ['JST1', 'JSTPH2', 'JST_PH', 'JST_PH2-S2B-PH-K-S-LF-SN', 'battery_connector_jst_ph_2'],
    'MCU': ['MCU1', 'Nice_Nano', 'Nice_Nano_V2', 'mcu_nice_nano', 'nice!nano'],
    'Reset_Switch': ['RST1', 'EVQ-PUC02K', 'reset_switch_smd_side', 'Panasonic_EVQ'],
}


def check_step_file(step_path):
    """Check if component model is referenced in STEP file."""
    print(f"  Checking STEP file: {step_path}")
    
    if not os.path.exists(step_path):
        print(f"    [X] File not found")
        return {}
    
    try:
        with open(step_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        found_components = {}
        for comp_name, patterns in COMPONENTS.items():
            found = False
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    found = True
                    break
            found_components[comp_name] = found
        
        for comp_name, found in found_components.items():
            status = "[OK]" if found else "[MISS]"
            print(f"    {status} {comp_name}: {'Found' if found else 'Missing'}")
        
        return found_components
            
    except Exception as e:
        print(f"    [ERROR] reading file: {e}")
        return {}


def check_glb_binary(glb_path):
    """Search for component names in GLB binary data (fallback method)."""
    print(f"  Checking GLB file: {glb_path}")
    
    if not os.path.exists(glb_path):
        print(f"    [X] File not found")
        return {}
    
    try:
        with open(glb_path, 'rb') as f:
            content = f.read()
        
        try:
            text_content = content.decode('utf-8', errors='ignore')
        except:
            text_content = content.decode('latin-1', errors='ignore')
        
        found_components = {}
        for comp_name, patterns in COMPONENTS.items():
            found = False
            for pattern in patterns:
                if pattern.lower() in text_content.lower():
                    found = True
                    break
            found_components[comp_name] = found
        
        for comp_name, found in found_components.items():
            status = "[OK]" if found else "[MISS]"
            print(f"    {status} {comp_name}: {'Found' if found else 'Missing'}")
        
        print(f"    [WARNING] Binary search only finds filenames, may give false positives")
        
        return found_components
            
    except Exception as e:
        print(f"    [ERROR]: {e}")
        return {}


def check_glb_with_pygltflib(glb_path):
    """Check for components using pygltflib proper parsing.
    
    Must verify that nodes have actual meshes attached, not just matching names.
    """
    print(f"  Checking GLB file: {glb_path}")
    
    if not os.path.exists(glb_path):
        print(f"    [X] File not found")
        return {}
    
    try:
        try:
            from pygltflib import GLTF2
        except ImportError:
            print(f"    pygltflib not installed, falling back to binary search")
            return check_glb_binary(glb_path)
        
        gltf = GLTF2().load(glb_path)
        
        found_components = {}
        
        # Build a map of mesh indices that actually exist
        valid_mesh_indices = set()
        meshes = getattr(gltf, 'meshes', None)
        if meshes is not None:
            for i, mesh in enumerate(meshes):
                valid_mesh_indices.add(i)
        
        # For each component, check if there's a node with BOTH matching name AND a valid mesh
        for comp_name, patterns in COMPONENTS.items():
            found = False
            details = []
            
            nodes = getattr(gltf, 'nodes', None)
            if nodes is not None:
                for node in nodes:
                    if node.name:
                        node_name_lower = node.name.lower()
                        # Check if node name matches any pattern
                        for pattern in patterns:
                            if pattern.lower() in node_name_lower:
                                # CRITICAL: Must have a valid mesh index
                                if node.mesh is not None and node.mesh in valid_mesh_indices:
                                    found = True
                                    details.append(f"{node.name} (mesh {node.mesh})")
                                    break
                                else:
                                    details.append(f"{node.name} (NO MESH)")
            
            found_components[comp_name] = found
            
            status = "[OK]" if found else "[MISS]"
            print(f"    {status} {comp_name}:")
            if details:
                for d in details[:3]:  # Show first 3 details
                    print(f"        {d}")
            else:
                print(f"        No nodes with valid meshes found")
        
        return found_components
            
    except Exception as e:
        print(f"    [ERROR] parsing GLB: {e}")
        return {}


def print_header(text):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print('='*70)


def main():
    """Run verification for all board files."""
    
    print_header("Component 3D Export Verification")
    print("\nThis script verifies that all three problematic components appear in")
    print("3D export formats (STEP, GLB) for both left and right PCBs.")
    
    all_results = {}
    
    for board_name, file_types in FILES.items():
        print_header(f"Verifying {board_name}")
        
        results = {}
        for file_type, file_path in file_types.items():
            print(f"\n  Checking: {file_type.upper()}")
            if file_type == 'step':
                results[file_type] = check_step_file(file_path)
            elif file_type == 'glb':
                results[file_type] = check_glb_with_pygltflib(file_path)
        
        all_results[board_name] = results
    
    # Final summary
    print_header("Final Summary")
    
    print("\n[OK] = Present, [MISS] = Missing")
    
    for board_name, results in all_results.items():
        print(f"\n{board_name}:")
        
        step_results = results.get('step', {})
        glb_results = results.get('glb', {})
        
        for comp_name in COMPONENTS.keys():
            step_status = step_results.get(comp_name, False)
            glb_status = glb_results.get(comp_name, False)
            
            step_str = "[OK]" if step_status else "[MISS]"
            glb_str = "[OK]" if glb_status else "[MISS]"
            
            print(f"  {comp_name}:")
            print(f"    STEP: {step_str}")
            print(f"    GLB:  {glb_str}")
            
            if not step_status and not glb_status:
                print(f"    >> ISSUE: Missing from both formats")
            elif step_status and not glb_status:
                print(f"    >> ISSUE: Present in STEP but missing from GLB")
            elif glb_status and not step_status:
                print(f"    >> UNUSUAL: Present in GLB but missing from STEP")
            else:
                print(f"    >> OK: Present in both formats")
    
    print("\n" + "="*70)
    
    issuesFound = False
    
    for board_name, results in all_results.items():
        step_results = results.get('step', {})
        glb_results = results.get('glb', {})
        
        for comp_name in COMPONENTS.keys():
            step_status = step_results.get(comp_name, False)
            glb_status = glb_results.get(comp_name, False)
            
            if not step_status and not glb_status:
                print(f"\n[ISSUE] {comp_name}: Missing from both formats")
                issuesFound = True
            elif step_status and not glb_status:
                print(f"\n[ISSUE] {comp_name}: Present in STEP but missing from GLB")
                issuesFound = True
    
    if not issuesFound:
        print("\n[SUCCESS] All components present in all formats!")
    
    print()
    
    return 1 if issuesFound else 0


if __name__ == '__main__':
    sys.exit(main())
