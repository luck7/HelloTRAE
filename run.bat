@echo off
setlocal

set "VENV=%~dp0.venv"
set "PYTHON=%VENV%\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo ERROR: venv python not found at "%PYTHON%".
    pause
    exit /b 1
)

echo Starting Battle City...
"%PYTHON%" -m pgzero "%~dp0main.py"

if errorlevel 1 (
    echo Game failed to run.
    pause
)
