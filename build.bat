@echo off
REM Build script for Inity - Windows build
REM Developed by Aathish at Strucureo

echo 🏗️  Building Inity for Windows...
echo Developed by Aathish at Strucureo
echo ====================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run build script
echo Starting build process...
python build.py

echo ✅ Build completed!
pause
