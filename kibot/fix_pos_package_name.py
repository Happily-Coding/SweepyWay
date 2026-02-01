#!/usr/bin/env python3
"""
Post-processing script to replace footprint package names with JLCPCB part numbers
in KiCad position files for PCB assembly.

This script reads a position file and replaces specific footprint names with
their corresponding JLCPCB part numbers.
"""

import sys
import re
from pathlib import Path


# Mapping of footprint names to JLCPCB part numbers
PACKAGE_REPLACEMENTS = {
    'switch_choc_v1_v2': 'CPG135001S30',  # Kailh Choc V1 Hotswap Socket
    # Add more mappings here as needed
}


def process_pos_file(input_file, output_file=None, replacements=None):
    """
    Process a KiCad position file and replace package names.
    
    Args:
        input_file: Path to the input position file
        output_file: Path to the output file (defaults to input_file)
        replacements: Dictionary mapping footprint names to part numbers
    """
    if replacements is None:
        replacements = PACKAGE_REPLACEMENTS
    
    input_path = Path(input_file)
    if output_file is None:
        output_path = input_path
    else:
        output_path = Path(output_file)
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process each line
    processed_lines = []
    for line in lines:
        # Skip header lines and comments
        if line.strip().startswith('#') or line.strip().startswith('##') or not line.strip():
            processed_lines.append(line)
            continue
        
        # Check if any package name in our replacements exists in the line
        for old_package, new_package in replacements.items():
            if old_package in line:
                # Replace the package name in the line
                # Use regex to preserve the original spacing
                line = re.sub(
                    r'(\s+)' + re.escape(old_package) + r'(\s+)',
                    r'\1' + new_package + r'\2',
                    line
                )
                print(f"Replaced '{old_package}' with '{new_package}'")
                break  # Only replace once per line
        
        processed_lines.append(line)
    
    # Write the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)
    
    print(f"\nProcessed file: {output_path}")


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python fix_pos_package_name.py <input_file> [output_file]")
        print("\nExample:")
        print("  python fix_pos_package_name.py left_pcb-bottom.pos")
        print("  python fix_pos_package_name.py left_pcb-bottom.pos left_pcb-bottom-fixed.pos")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        process_pos_file(input_file, output_file)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()