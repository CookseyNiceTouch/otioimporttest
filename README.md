# DaVinci Resolve OTIO Import Tool

A simple tool to import OpenTimelineIO (OTIO) files into DaVinci Resolve. This project provides a streamlined interface for testing OTIO import functionality with DaVinci Resolve's scripting API.

## Features

- **Simple Command-Line Interface**: Import OTIO files with a single command
- **Interactive Mode**: Prompts for file path if not provided
- **Flexible Options**: Custom timeline names, source clip import, and more
- **Robust Error Handling**: Clear feedback on success/failure
- **UV Package Management**: Modern Python dependency management

## Prerequisites

- **DaVinci Resolve Studio** (free version has limited API access)
- **Python 3.13+** 
- **UV Package Manager** ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **DaVinci Resolve Scripting Environment** properly configured

### DaVinci Resolve Setup

1. **Enable Scripting** in DaVinci Resolve:
   - Go to `DaVinci Resolve > Preferences > System > General`
   - Enable "External scripting using"
   - Set it to "Local" or "Network" as needed

2. **Configure Environment Variables** (if not auto-detected):
   ```bash
   # Windows
   set RESOLVE_SCRIPT_API="C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
   set RESOLVE_SCRIPT_LIB="C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
   set PYTHONPATH=%RESOLVE_SCRIPT_API%\Modules\;%PYTHONPATH%
   
   # macOS/Linux
   export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
   export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
   export PYTHONPATH="$RESOLVE_SCRIPT_API/Modules/:$PYTHONPATH"
   ```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd resolveimporttest
   ```

2. **Install UV** (if not already installed):
   ```bash
   # Windows (PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up the environment**:
   ```bash
   uv sync
   ```
   
   This will:
   - Create a virtual environment
   - Install all dependencies from `pyproject.toml`
   - Set up the project for development

## Usage

### Basic Usage

1. **Start DaVinci Resolve** and open a project
2. **Run the import tool**:
   ```bash
   uv run main.py exported_timeline.otio
   ```

### Command-Line Options

```bash
# Basic import
uv run main.py timeline.otio

# With custom timeline name
uv run main.py timeline.otio --name "My Custom Timeline"

# Import source clips into media pool
uv run main.py timeline.otio --import-clips

# Specify path to search for source clips
uv run main.py timeline.otio --clips-path "/path/to/media"

# Interactive mode (prompts for file path)
uv run main.py

# Get help
uv run main.py --help
```

### What the Script Does

1. **Connects to DaVinci Resolve**: Uses the DaVinci Resolve scripting API
2. **Validates Input**: Checks that the OTIO file exists and is accessible  
3. **Imports Timeline**: Creates a new timeline in the current project from the OTIO file
4. **Handles Conflicts**: Automatically renames timelines if name conflicts occur
5. **Provides Feedback**: Shows detailed information about the import process
6. **Displays Results**: Shows timeline details like duration, tracks, and item counts

### Example Output

```
=== DaVinci Resolve OTIO Import Tool ===

OTIO file: exported_timeline.otio

Starting OTIO import...

Importing DaVinci Resolve API...
[OK] DaVinciResolveScript module imported successfully
Connecting to DaVinci Resolve...
[OK] Connected to DaVinci Resolve successfully
[OK] Connected to project: My Project
[OK] Current media pool folder: Master
[OK] OTIO file: exported_timeline.otio
[OK] Timeline name: exported_timeline

Importing OTIO timeline...
[OK] Timeline 'exported_timeline' imported successfully!

Timeline details:
  Name: exported_timeline
  Duration: 1800 frames
  Start frame: 1001
  End frame: 2800
  Start timecode: 01:00:00:00
  Tracks - Video: 2, Audio: 4, Subtitle: 0
  Total video items: 12
  Total audio items: 8

=== Import completed successfully! ===
Timeline is now available in DaVinci Resolve
```

## Troubleshooting

### Common Issues

1. **"Could not connect to DaVinci Resolve"**:
   - Make sure DaVinci Resolve is running
   - Check that scripting is enabled in preferences
   - Verify you're using DaVinci Resolve Studio

2. **"Could not import DaVinciResolveScript module"**:
   - Check environment variables are set correctly
   - Verify the paths exist on your system
   - Try restarting your terminal after setting environment variables

3. **"Failed to import timeline from OTIO file"**:
   - Ensure the OTIO file is valid and not corrupted
   - Check that referenced media exists in your project
   - Try importing source clips first with `--import-clips`

### Getting Help

Run `uv run main.py --help` for detailed usage information.

## Development

The project structure is simple:
- `main.py`: Main entry point and CLI interface
- `importotio.py`: Core OTIO import functionality
- `datapipeline.py`: Extended pipeline functionality (not used by main.py)
- `pyproject.toml`: Project configuration and dependencies

## License

This project is for testing purposes. Please ensure you comply with DaVinci Resolve's licensing terms when using their scripting API.
