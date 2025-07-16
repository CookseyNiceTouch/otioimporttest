#!/usr/bin/env python3
"""
Simple OTIO Import Tool for DaVinci Resolve

Takes an OTIO file path as input and imports it into the currently open DaVinci Resolve project.
"""

import sys
import os
import argparse
from pathlib import Path
from importotio import import_otio_timeline


def get_otio_file_path(args_input: str = None) -> str:
    """
    Get OTIO file path from command line args or user input.
    
    Args:
        args_input: Command line input file path
        
    Returns:
        Valid OTIO file path
    """
    if args_input:
        return args_input
    
    # Interactive mode - ask user for file path
    print("Enter the path to your OTIO file:")
    while True:
        file_path = input("> ").strip()
        if not file_path:
            print("Please enter a valid file path.")
            continue
        
        # Handle quoted paths
        if file_path.startswith('"') and file_path.endswith('"'):
            file_path = file_path[1:-1]
        elif file_path.startswith("'") and file_path.endswith("'"):
            file_path = file_path[1:-1]
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            print("Please enter a valid file path.")
            continue
        
        return file_path


def main():
    """Main function for OTIO import."""
    parser = argparse.ArgumentParser(
        description="Import OTIO files into DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run main.py exported_timeline.otio
  uv run main.py /path/to/timeline.otio
  uv run main.py --name "My Timeline" timeline.otio
  uv run main.py  # Interactive mode
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input OTIO file path (optional, will prompt if not provided)')
    parser.add_argument('--name', '-n', help='Timeline name (optional, uses filename if not provided)')
    parser.add_argument('--import-clips', action='store_true', 
                       help='Import source clips into media pool')
    parser.add_argument('--clips-path', help='Filesystem path to search for source clips')
    
    args = parser.parse_args()
    
    print("=== DaVinci Resolve OTIO Import Tool ===")
    print()
    
    # Get OTIO file path
    try:
        otio_file_path = get_otio_file_path(args.input)
        print(f"OTIO file: {otio_file_path}")
        print()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    
    # Validate file
    if not Path(otio_file_path).exists():
        print(f"ERROR: File does not exist: {otio_file_path}")
        sys.exit(1)
    
    # Import timeline
    print("Starting OTIO import...")
    print()
    
    success = import_otio_timeline(
        otio_file_path=otio_file_path,
        timeline_name=args.name,
        import_source_clips=args.import_clips,
        source_clips_path=args.clips_path or "",
        source_clips_folders=None
    )
    
    print()
    if success:
        print("=== Import completed successfully! ===")
        print("Timeline is now available in DaVinci Resolve")
        sys.exit(0)
    else:
        print("=== Import failed! ===")
        print("Check the output above for error details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
