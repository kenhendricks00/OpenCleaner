# OpenCleaner

OpenCleaner is a cross-platform system optimization and cleaning application that helps keep computers in optimal condition. It combines CCleaner-style cleanup functionality with a modern GUI experience.

## What it does

- Scans common safe-to-clean locations (temp files, caches, logs, downloads leftovers)
- Estimates reclaimable disk space by category
- Lets users select categories directly in the GUI
- Cleans selected categories with confirmation dialogs
- Rescans automatically to show updated state

## GUI highlights

- Native desktop application built with Tkinter/ttk
- Distinctive retro-futuristic command-center aesthetic
- High-contrast telemetry table with one-click arming/disarming per row
- Select All / Clear Selection controls
- Status messages and scan progress indicator

## Project structure

- `opencleaner.py` — executable entrypoint
- `src/opencleaner/gui.py` — desktop GUI
- `src/opencleaner/core.py` — scanner and cleanup engine
- `opencleaner.spec` — PyInstaller spec for packaging
- `scripts/build_windows_exe.ps1` — Windows build script
- `tests/test_core.py` — unit tests for core behavior

## Requirements

- Python 3.10+

## Run the app

```bash
python opencleaner.py
```

## Build a Windows `.exe`

Yes — OpenCleaner can be packaged as a Windows executable.

### Option A: PowerShell helper script

On Windows (PowerShell):

```powershell
./scripts/build_windows_exe.ps1
```

This creates a single-file GUI executable at:

- `dist/OpenCleaner.exe`

Use `-OneDir` if you prefer a folder build:

```powershell
./scripts/build_windows_exe.ps1 -OneDir
```

### Option B: Direct PyInstaller command

```powershell
py -3 -m pip install pyinstaller
py -3 -m PyInstaller --noconfirm --onefile --windowed --name OpenCleaner opencleaner.py
```

## Run tests

```bash
python -m unittest discover -s tests
```

## Roadmap

- Browser-specific cleaner modules
- Startup app management
- Scheduled auto-clean profiles
- Internationalization and accessibility improvements
