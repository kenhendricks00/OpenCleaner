from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import platform
import shutil
import tempfile
from typing import Iterable


@dataclass
class ScanItem:
    label: str
    paths: list[Path]
    bytes_size: int


@dataclass
class ScanReport:
    items: list[ScanItem]

    @property
    def total_bytes(self) -> int:
        return sum(item.bytes_size for item in self.items)


def human_readable_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def _existing_dirs(paths: Iterable[Path]) -> list[Path]:
    return [p for p in paths if p.exists() and p.is_dir()]


def candidate_directories() -> dict[str, list[Path]]:
    home = Path.home()
    system = platform.system().lower()

    targets: dict[str, list[Path]] = {
        "System temp": [Path(tempfile.gettempdir())],
        "User temp": [home / ".cache", home / "AppData" / "Local" / "Temp"],
        "Log files": [home / ".local" / "share" / "logs", home / "Library" / "Logs"],
        "Downloads leftovers": [home / "Downloads"],
    }

    if "windows" in system:
        local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
        targets["Windows caches"] = [
            local_app_data / "Temp",
            local_app_data / "Microsoft" / "Windows" / "INetCache",
        ]
    elif "darwin" in system:
        targets["macOS caches"] = [home / "Library" / "Caches"]
    else:
        targets["Linux caches"] = [home / ".cache", Path("/var/tmp")]

    return {k: _existing_dirs(v) for k, v in targets.items()}


def _folder_size(path: Path) -> int:
    total = 0
    try:
        for root, _, files in os.walk(path, topdown=True):
            for name in files:
                fpath = Path(root) / name
                try:
                    total += fpath.stat().st_size
                except (FileNotFoundError, PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        return 0
    return total


def run_scan() -> ScanReport:
    items: list[ScanItem] = []
    for label, dirs in candidate_directories().items():
        bytes_size = sum(_folder_size(d) for d in dirs)
        if dirs:
            items.append(ScanItem(label=label, paths=dirs, bytes_size=bytes_size))
    return ScanReport(items=items)


def clean_items(items: list[ScanItem]) -> tuple[int, int]:
    deleted_files = 0
    reclaimed = 0

    for item in items:
        for directory in item.paths:
            try:
                for entry in directory.iterdir():
                    try:
                        if entry.is_file() or entry.is_symlink():
                            size = entry.stat().st_size if entry.exists() else 0
                            entry.unlink(missing_ok=True)
                            deleted_files += 1
                            reclaimed += size
                        elif entry.is_dir():
                            size = _folder_size(entry)
                            shutil.rmtree(entry, ignore_errors=True)
                            deleted_files += 1
                            reclaimed += size
                    except (PermissionError, OSError):
                        continue
            except (PermissionError, FileNotFoundError, OSError):
                continue

    return deleted_files, reclaimed
