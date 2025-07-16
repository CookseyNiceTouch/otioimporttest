#!/usr/bin/env python3
"""
Data Pipeline for DaVinci Resolve OTIO Workflow

Simplified pipeline with 3 specific workflows for AI agent usage:
1. Export workflow: Clear timeline_ref → Export OTIO → Convert to JSON
2. Clear edited: Clear timeline_edited folder
3. Import workflow: Convert JSON to OTIO → Import to Resolve

Designed to be called programmatically by AI agents.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any


class DataPipeline:
    """Simplified data pipeline for AI agent usage."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the data pipeline.
        
        Args:
            project_root: Path to project root (optional, auto-detected if not provided)
        """
        # Determine project root
        if project_root:
            self.project_root = Path(project_root).resolve()
        else:
            # Auto-detect project root from script location
            script_dir = Path(__file__).parent.resolve()
            self.project_root = script_dir.parent.parent  # Go up from backend/python_services/services/resolveautomation
        
        # Define standard directories
        self.data_dir = self.project_root / "data" / "timelineprocessing"
        self.timeline_ref_dir = self.data_dir / "timeline_ref"
        self.timeline_edited_dir = self.data_dir / "timeline_edited"
        self.scripts_dir = Path(__file__).parent
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for directory in [self.data_dir, self.timeline_ref_dir, self.timeline_edited_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _run_script(self, script_name: str, args: List[str]) -> bool:
        """
        Run a script with arguments.
        
        Args:
            script_name: Name of the script to run
            args: List of arguments to pass to the script
            
        Returns:
            True if successful, False otherwise
        """
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            print(f"ERROR: Script not found: {script_path}")
            return False
        
        # Build command
        cmd = ["uv", "run", str(script_path)] + args
        
        print(f"Running: {' '.join(cmd)}")
        try:
            # Fix Unicode encoding issues on Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                cmd, 
                capture_output=False, 
                text=True,
                encoding='utf-8',
                env=env,
                errors='replace'  # Replace problematic characters instead of crashing
            )
            return result.returncode == 0
        except Exception as e:
            print(f"ERROR: Failed to run script: {e}")
            return False
    
    def _clear_directory(self, directory: Path) -> bool:
        """
        Clear all files from a directory.
        
        Args:
            directory: Directory to clear
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Clearing directory: {directory}")
            file_count = 0
            for file in directory.glob("*"):
                if file.is_file():
                    file.unlink()
                    file_count += 1
                    print(f"  Deleted: {file.name}")
            
            if file_count == 0:
                print("  Directory was already empty")
            else:
                print(f"  Deleted {file_count} files")
            
            return True
        except Exception as e:
            print(f"ERROR: Failed to clear directory {directory}: {e}")
            return False
    
    def workflow_1_export(self, timeline_name: Optional[str] = None) -> bool:
        """
        Workflow 1: Export timeline from Resolve and convert to JSON.
        
        Steps:
        1. Clear contents of timeline_ref folder
        2. Export OTIO from Resolve into timeline_ref
        3. Convert OTIO to JSON
        
        Args:
            timeline_name: Specific timeline name to export (optional, uses current timeline)
            
        Returns:
            True if successful, False otherwise
        """
        print("=== WORKFLOW 1: EXPORT TIMELINE FROM RESOLVE ===")
        
        # Step 1: Clear timeline_ref folder
        print("Step 1: Clearing timeline_ref folder")
        if not self._clear_directory(self.timeline_ref_dir):
            return False
        print()
        
        # Step 2: Export OTIO from Resolve
        print("Step 2: Exporting OTIO from DaVinci Resolve")
        
        # Build export arguments
        export_args = ["--output", str(self.timeline_ref_dir / "exported_timeline.otio")]
        if timeline_name:
            export_args.extend(["--timeline", timeline_name])
        
        if not self._run_script("exportotio.py", export_args):
            print("[ERROR] OTIO export failed")
            return False
        
        print("[OK] OTIO export successful")
        print()
        
        # Step 3: Convert OTIO to JSON
        print("Step 3: Converting OTIO to JSON")
        
        # Find the exported OTIO file
        otio_files = list(self.timeline_ref_dir.glob("*.otio"))
        if not otio_files:
            print("ERROR: No OTIO file found after export")
            return False
        
        otio_file = otio_files[0]  # Should only be one since we cleared the directory
        json_args = [str(otio_file)]
        
        if not self._run_script("otio2json.py", json_args):
            print("[ERROR] OTIO to JSON conversion failed")
            return False
        
        print("[OK] OTIO to JSON conversion successful")
        print()
        
        # Find the generated JSON file
        json_files = list(self.timeline_ref_dir.glob("*.json"))
        if json_files:
            json_file = json_files[0]
            print(f"[OK] Workflow 1 completed successfully!")
            print(f"JSON file ready for editing: {json_file}")
            return True
        else:
            print("ERROR: No JSON file found after conversion")
            return False
    
    def workflow_2_clear_edited(self) -> bool:
        """
        Workflow 2: Clear timeline_edited folder.
        
        Returns:
            True if successful, False otherwise
        """
        print("=== WORKFLOW 2: CLEAR TIMELINE_EDITED FOLDER ===")
        
        success = self._clear_directory(self.timeline_edited_dir)
        
        if success:
            print("[OK] Workflow 2 completed successfully!")
        
        return success
    
    def workflow_3_import(self, timeline_name: Optional[str] = None, import_clips: bool = False) -> bool:
        """
        Workflow 3: Convert JSON to OTIO and import to Resolve.
        
        Steps:
        1. Convert JSON in timeline_edited to OTIO
        2. Import OTIO into Resolve
        
        Args:
            timeline_name: Name for imported timeline (optional)
            import_clips: Whether to import source clips (optional, default False)
            
        Returns:
            True if successful, False otherwise
        """
        print("=== WORKFLOW 3: IMPORT TIMELINE TO RESOLVE ===")
        
        # Step 1: Convert JSON to OTIO
        print("Step 1: Converting JSON to OTIO")
        
        # Find JSON file in timeline_edited
        json_files = list(self.timeline_edited_dir.glob("*.json"))
        if not json_files:
            print("ERROR: No JSON files found in timeline_edited directory")
            print(f"Please place your edited JSON file in: {self.timeline_edited_dir}")
            return False
        
        if len(json_files) > 1:
            print(f"WARNING: Multiple JSON files found, using most recent: {[f.name for f in json_files]}")
        
        json_file = max(json_files, key=lambda f: f.stat().st_mtime)
        print(f"Using JSON file: {json_file.name}")
        
        # Convert JSON to OTIO
        json2otio_args = [str(json_file), "--project-root", str(self.project_root)]
        
        if not self._run_script("json2otio.py", json2otio_args):
            print("[ERROR] JSON to OTIO conversion failed")
            return False
        
        print("[OK] JSON to OTIO conversion successful")
        print()
        
        # Step 2: Import OTIO into Resolve
        print("Step 2: Importing OTIO into DaVinci Resolve")
        
        # Find the generated OTIO file
        otio_files = list(self.timeline_edited_dir.glob("*.otio"))
        if not otio_files:
            print("ERROR: No OTIO file found after conversion")
            return False
        
        otio_file = max(otio_files, key=lambda f: f.stat().st_mtime)
        print(f"Using OTIO file: {otio_file.name}")
        
        # Import OTIO
        import_args = [str(otio_file)]
        if timeline_name:
            import_args.extend(["--name", timeline_name])
        if import_clips:
            import_args.append("--import-clips")
        
        if not self._run_script("importotio.py", import_args):
            print("[ERROR] OTIO import failed")
            return False
        
        print("[OK] OTIO import successful")
        print()
        print("[OK] Workflow 3 completed successfully!")
        print("Timeline is now available in DaVinci Resolve")
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of pipeline directories.
        
        Returns:
            Dictionary with status information
        """
        def get_dir_info(directory: Path) -> Dict[str, Any]:
            files = list(directory.glob("*"))
            file_info = []
            for file in files:
                if file.is_file():
                    file_info.append({
                        "name": file.name,
                        "size": file.stat().st_size,
                        "modified": file.stat().st_mtime
                    })
            return {
                "path": str(directory),
                "file_count": len(file_info),
                "files": file_info
            }
        
        return {
            "project_root": str(self.project_root),
            "timeline_ref": get_dir_info(self.timeline_ref_dir),
            "timeline_edited": get_dir_info(self.timeline_edited_dir)
        }


def main():
    """Main function for command-line testing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Data Pipeline for DaVinci Resolve OTIO Workflow - AI Agent Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflows:
  workflow-1          Export timeline from Resolve and convert to JSON
  workflow-2          Clear timeline_edited folder
  workflow-3          Convert JSON to OTIO and import to Resolve
  status              Show current pipeline status

Examples:
  python datapipeline.py workflow-1
  python datapipeline.py workflow-1 --timeline "My Timeline"
  python datapipeline.py workflow-2
  python datapipeline.py workflow-3 --name "Edited Timeline"
  python datapipeline.py status
        """
    )
    
    parser.add_argument('workflow', choices=['workflow-1', 'workflow-2', 'workflow-3', 'status'], 
                       help='Workflow to execute')
    parser.add_argument('--project-root', help='Path to project root directory')
    parser.add_argument('--timeline', '-t', help='Timeline name (for workflow-1)')
    parser.add_argument('--name', '-n', help='Name for imported timeline (for workflow-3)')
    parser.add_argument('--import-clips', action='store_true', help='Import source clips (for workflow-3)')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    print("=== DaVinci Resolve OTIO Data Pipeline - AI Agent Version ===")
    print()
    
    # Initialize pipeline
    pipeline = DataPipeline(args.project_root)
    
    # Execute workflow
    success = True
    
    if args.workflow == 'workflow-1':
        success = pipeline.workflow_1_export(args.timeline)
    elif args.workflow == 'workflow-2':
        success = pipeline.workflow_2_clear_edited()
    elif args.workflow == 'workflow-3':
        success = pipeline.workflow_3_import(args.name, args.import_clips)
    elif args.workflow == 'status':
        import json
        status = pipeline.get_status()
        print("=== PIPELINE STATUS ===")
        print(json.dumps(status, indent=2))
        success = True
    
    print()
    if success:
        print("=== Operation completed successfully! ===")
        sys.exit(0)
    else:
        print("=== Operation failed! ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
