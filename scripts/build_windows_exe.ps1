Param(
    [switch]$OneDir
)

$ErrorActionPreference = "Stop"

Write-Host "[OpenCleaner] Creating virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

$python = ".venv\Scripts\python.exe"
$pip = ".venv\Scripts\pip.exe"

Write-Host "[OpenCleaner] Installing build dependencies..." -ForegroundColor Cyan
& $python -m pip install --upgrade pip
& $pip install pyinstaller

$distMode = if ($OneDir) { "--onedir" } else { "--onefile" }

Write-Host "[OpenCleaner] Building Windows executable ($distMode)..." -ForegroundColor Cyan
& $python -m PyInstaller $distMode --noconfirm --windowed --name OpenCleaner opencleaner.py

Write-Host "[OpenCleaner] Build complete. Check the dist/ folder." -ForegroundColor Green
