@echo off
setlocal

set "VENV=%~dp0.venv"
set "PGZRUN=%VENV%\Scripts\pgzrun.exe"

if not exist "%PGZRUN%" (
    echo ERROR: pgzrun not found. Trying pip install...
    "%VENV%\Scripts\pip.exe" install pgzero
)

echo Starting Battle City...
"%PGZRUN%" "%~dp0main.py"

if errorlevel 1 (
    echo Game failed to run.
    pause
)
