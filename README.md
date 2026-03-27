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
- Modernized layout and styling
- Interactive category table with per-row selection toggle
- Select All / Clear Selection controls
- Status messages and scan progress indicator

## Project structure

- `opencleaner.py` — executable entrypoint
- `src/opencleaner/gui.py` — desktop GUI
- `src/opencleaner/core.py` — scanner and cleanup engine
- `tests/test_core.py` — unit tests for core behavior

## Requirements

- Python 3.10+

## Run the app

```bash
python opencleaner.py
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
