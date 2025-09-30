@echo off
REM Installation script for ChordPro Processor (Windows)

echo ======================================================================
echo   ChordPro to FreeShow Processor - Installation (Windows)
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Install dependencies
echo Installing dependencies...
echo.

echo Installing PyYAML...
python -m pip install pyyaml --quiet
if errorlevel 1 (
    echo [WARNING] Could not install PyYAML
) else (
    echo [OK] PyYAML installed
)

echo Installing tqdm...
python -m pip install tqdm --quiet
if errorlevel 1 (
    echo [WARNING] Could not install tqdm
) else (
    echo [OK] tqdm installed
)

echo.
echo ======================================================================
echo   Installation Complete!
echo ======================================================================
echo.
echo Next steps:
echo   1. Run the processor:
echo      python main.py
echo.
echo   2. For local files:
echo      python main.py --local C:\path\to\files
echo.
echo   3. For help:
echo      python main.py --help
echo.
echo Press any key to exit...
pause >nul
