@echo off
REM Build Windows installer for Inity
REM Developed by Aathish at Strucureo

echo Building Inity Windows Installer
echo Developed by Aathish at Strucureo
echo ====================================

REM Function to find Python
:FindPython
set PYTHON_CMD=
set PYTHON_FOUND=0

REM Check if python is in PATH
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    echo Python found in PATH
    goto :CheckNSIS
)

echo Python not found in PATH. Searching system...

REM Search common Python installation locations
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python*\python.exe"
    "%ProgramFiles%\Python*\python.exe"
    "%ProgramFiles(x86)%\Python*\python.exe"
    "%USERPROFILE%\anaconda3\python.exe"
    "%USERPROFILE%\miniconda3\python.exe"
    "%ProgramData%\Anaconda3\python.exe"
    "C:\Python*\python.exe"
) do (
    for %%f in (%%p) do (
        if exist "%%f" (
            "%%f" --version >nul 2>&1
            if not errorlevel 1 (
                set PYTHON_CMD=%%f
                set PYTHON_FOUND=1
                echo Found Python at: %%f
                goto :CheckNSIS
            )
        )
    )
)

if %PYTHON_FOUND%==0 (
    echo Python not found. Would you like to install Python? ^(Y/N^)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo Downloading Python installer...
        powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
        echo Installing Python...
        "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1
        echo Please restart this script after Python installation completes.
        pause
        exit /b 1
    ) else (
        echo Please install Python from https://python.org
        pause
        exit /b 1
    )
)

:CheckNSIS
REM Check if NSIS is available
where makensis >nul 2>&1
if errorlevel 1 (
    echo NSIS not found. Searching system...
    
    if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
        set NSIS_CMD=C:\Program Files (x86)\NSIS\makensis.exe
        echo Found NSIS at: C:\Program Files (x86)\NSIS\makensis.exe
        goto :Build
    )
    
    if exist "C:\Program Files\NSIS\makensis.exe" (
        set NSIS_CMD=C:\Program Files\NSIS\makensis.exe
        echo Found NSIS at: C:\Program Files\NSIS\makensis.exe
        goto :Build
    )
    
    echo NSIS not found. Please install NSIS from https://nsis.sourceforge.io/
    echo Make sure makensis.exe is in your PATH or install to default location
    pause
    exit /b 1
) else (
    set NSIS_CMD=makensis
    echo NSIS found in PATH
)

:Build
REM Run the installer builder with found Python
echo Using Python: %PYTHON_CMD%
"%PYTHON_CMD%" build-installer.py

pause
