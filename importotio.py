#!/usr/bin/env python3
"""
DaVinci Resolve OTIO Import Tool

Pure importer that imports OTIO timeline files into DaVinci Resolve.
No hardcoded paths - designed to be used by datapipeline.py or standalone.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional, Dict, Any


def get_unique_timeline_name(project, base_timeline_name: str) -> str:
    """Get a unique timeline name by appending suffix if needed."""
    try:
        timeline_count = project.GetTimelineCount()
        existing_names = set()
        
        # Collect all existing timeline names
        for i in range(1, timeline_count + 1):
            existing_timeline = project.GetTimelineByIndex(i)
            if existing_timeline:
                existing_names.add(existing_timeline.GetName())
        
        # If base name doesn't exist, use it
        if base_timeline_name not in existing_names:
            return base_timeline_name
        
        # Find a unique name by appending suffix
        suffix = 1
        while True:
            candidate_name = f"{base_timeline_name} ({suffix})"
            if candidate_name not in existing_names:
                print(f"Timeline '{base_timeline_name}' already exists - using '{candidate_name}' instead")
                return candidate_name
            suffix += 1
            
            # Safety check to prevent infinite loop
            if suffix > 1000:
                print(f"Warning: Could not find unique name after 1000 attempts, using timestamp suffix")
                import time
                timestamp_suffix = int(time.time())
                return f"{base_timeline_name}_{timestamp_suffix}"
                
    except Exception as e:
        print(f"Warning: Could not check existing timelines: {e}")
        # Fallback to timestamp suffix
        import time
        timestamp_suffix = int(time.time())
        return f"{base_timeline_name}_{timestamp_suffix}"


def display_timeline_info(timeline) -> None:
    """Display imported timeline information."""
    try:
        print("Timeline details:")
        print(f"  Name: {timeline.GetName()}")
        print(f"  Duration: {timeline.GetEndFrame() - timeline.GetStartFrame() + 1} frames")
        print(f"  Start frame: {timeline.GetStartFrame()}")
        print(f"  End frame: {timeline.GetEndFrame()}")
        print(f"  Start timecode: {timeline.GetStartTimecode()}")
        
        # Get track counts
        video_tracks = timeline.GetTrackCount("video")
        audio_tracks = timeline.GetTrackCount("audio")
        subtitle_tracks = timeline.GetTrackCount("subtitle")
        
        print(f"  Tracks - Video: {video_tracks}, Audio: {audio_tracks}, Subtitle: {subtitle_tracks}")
        
        # List timeline items if there are any
        if video_tracks > 0:
            total_video_items = 0
            for track_idx in range(1, video_tracks + 1):
                items = timeline.GetItemListInTrack("video", track_idx)
                total_video_items += len(items)
            print(f"  Total video items: {total_video_items}")
        
        if audio_tracks > 0:
            total_audio_items = 0
            for track_idx in range(1, audio_tracks + 1):
                items = timeline.GetItemListInTrack("audio", track_idx)
                total_audio_items += len(items)
            print(f"  Total audio items: {total_audio_items}")
            
    except Exception as e:
        print(f"Warning: Could not get complete timeline information: {e}")


def import_otio_timeline(
    otio_file_path: str, 
    timeline_name: Optional[str] = None,
    import_source_clips: bool = False,
    source_clips_path: str = "",
    source_clips_folders: Optional[list] = None
) -> bool:
    """
    Import an OTIO timeline file into DaVinci Resolve.
    
    Args:
        otio_file_path: Path to the OTIO file to import
        timeline_name: Name for the imported timeline (optional, uses filename if not provided)
        import_source_clips: Whether to import source clips into media pool
        source_clips_path: Filesystem path to search for source clips
        source_clips_folders: Media Pool folder objects to search for clips
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import DaVinci Resolve API
        print("Importing DaVinci Resolve API...")
        import DaVinciResolveScript as dvr_script
        print("[OK] DaVinciResolveScript module imported successfully")
        
        # Connect to DaVinci Resolve
        print("Connecting to DaVinci Resolve...")
        resolve = dvr_script.scriptapp("Resolve")
        if not resolve:
            print("ERROR: Could not connect to DaVinci Resolve!")
            print("Make sure:")
            print("- DaVinci Resolve is running")
            print("- Scripting is enabled in DaVinci Resolve preferences")
            print("- You're running DaVinci Resolve Studio (free version has limited API access)")
            return False
        
        print("[OK] Connected to DaVinci Resolve successfully")
        
        # Get the current project
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject()
        if not project:
            print("ERROR: No project is currently open!")
            print("Please open a project in DaVinci Resolve first.")
            return False
        
        print(f"[OK] Connected to project: {project.GetName()}")
        
        # Get the media pool
        media_pool = project.GetMediaPool()
        current_folder = media_pool.GetCurrentFolder()
        print(f"[OK] Current media pool folder: {current_folder.GetName()}")
        print()
        
        # Validate OTIO file
        otio_file = Path(otio_file_path)
        if not otio_file.exists():
            print(f"ERROR: OTIO file does not exist: {otio_file}")
            return False
        
        if not otio_file.suffix.lower() == '.otio':
            print(f"WARNING: File doesn't have .otio extension: {otio_file}")
        
        print(f"[OK] OTIO file: {otio_file}")
        
        # Generate timeline name
        if timeline_name is None:
            base_timeline_name = otio_file.stem
        else:
            base_timeline_name = timeline_name
        
        # Get unique timeline name (adds suffix if needed)
        final_timeline_name = get_unique_timeline_name(project, base_timeline_name)
        print(f"[OK] Timeline name: {final_timeline_name}")
        print()
        
        # Set up import options
        import_options = {
            "timelineName": final_timeline_name,
            "importSourceClips": import_source_clips,
            "sourceClipsPath": source_clips_path,
            "sourceClipsFolders": source_clips_folders or []
        }
        
        print("Import options:")
        for key, value in import_options.items():
            print(f"  {key}: {value}")
        print()
        
        # Import the timeline
        print("Importing OTIO timeline...")
        timeline = media_pool.ImportTimelineFromFile(str(otio_file), import_options)
        
        # If import fails, try with importSourceClips enabled as fallback
        if not timeline and not import_source_clips:
            print("Initial import failed. Trying with source clips import enabled...")
            fallback_options = import_options.copy()
            fallback_options["importSourceClips"] = True
            timeline = media_pool.ImportTimelineFromFile(str(otio_file), fallback_options)
            
            if timeline:
                print("[OK] Fallback import method succeeded")
            else:
                print("[ERROR] All import methods failed")
        
        if timeline:
            print(f"[OK] Timeline '{timeline.GetName()}' imported successfully!")
            print()
            display_timeline_info(timeline)
            
            # Verify file size for reference
            try:
                file_size = otio_file.stat().st_size
                print(f"  Source file size: {file_size} bytes")
            except Exception:
                pass
            
            return True
        else:
            print("ERROR: Failed to import timeline from OTIO file!")
            print()
            print("Possible issues:")
            print("- OTIO file format is not compatible with this version of DaVinci Resolve")
            print(f"- Timeline name '{final_timeline_name}' conflicts with existing timeline")
            print("- Media referenced in OTIO file is not found in the project")
            print("- OTIO file contains unsupported elements or codec")
            print("- OTIO file may be corrupted or incorrectly formatted")
            print("- Check DaVinci Resolve console for more detailed error messages")
            print()
            print("Troubleshooting:")
            print("- Ensure the original media is imported into your media pool")
            print("- Check that media file paths in the OTIO match your project structure")
            print("- Try importing the source media first, then retry the timeline import")
            print("- Verify the OTIO file was generated correctly by json2otio.py")
            
            return False
            
    except ImportError as e:
        print(f"ERROR: Could not import DaVinciResolveScript module: {e}")
        print("Make sure the DaVinci Resolve scripting environment is properly configured.")
        print("Required environment variables:")
        print("- RESOLVE_SCRIPT_API")
        print("- RESOLVE_SCRIPT_LIB") 
        print("- PYTHONPATH")
        return False
    except KeyboardInterrupt:
        print("\nImport cancelled by user.")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {str(e)}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        return False


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Import OpenTimelineIO files into DaVinci Resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python importotio.py timeline.otio
  python importotio.py timeline.otio --name "My Timeline"
  python importotio.py timeline.otio --import-clips --clips-path /path/to/media
        """
    )
    
    parser.add_argument('input', help='Input OTIO file path')
    parser.add_argument('--name', '-n', help='Timeline name (optional, uses filename if not provided)')
    parser.add_argument('--import-clips', action='store_true', 
                       help='Import source clips into media pool')
    parser.add_argument('--clips-path', help='Filesystem path to search for source clips')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    print("=== DaVinci Resolve OTIO Import Tool ===")
    print("Importing OTIO timeline into DaVinci Resolve")
    print()
    
    success = import_otio_timeline(
        args.input,
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
        sys.exit(1)


if __name__ == "__main__":
    main()
