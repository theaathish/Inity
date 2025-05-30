@echo off
REM Build Windows installer for Inity
REM Developed by Aathish at Strucureo

echo 🏗️ Building Inity Windows Installer
echo Developed by Aathish at Strucureo
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Check if NSIS is available
where makensis >nul 2>&1
if errorlevel 1 (
    echo ❌ NSIS not found. Please install NSIS from https://nsis.sourceforge.io/
    echo Make sure makensis.exe is in your PATH
    pause
    exit /b 1
)

REM Run the installer builder
python build-installer.py

pause
