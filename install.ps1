# One-command installer for Inity on Windows
# Intelligent Python project environment setup tool
# Developed by Aathish at Strucureo
# Usage: iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/theaathish/Inity/main/install.ps1'))

$ErrorActionPreference = "Stop"

# Colors
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green  
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$Purple = [System.ConsoleColor]::Magenta
$Cyan = [System.ConsoleColor]::Cyan

function Write-ColorText {
    param($Text, $Color)
    $prevColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Text
    $Host.UI.RawUI.ForegroundColor = $prevColor
}

# Art banner
Write-ColorText " ___       _ _         " $Blue
Write-ColorText "|_ _|_ __ (_) |_ _   _ " $Blue
Write-ColorText " | || '_ \| | __| | | |" $Blue
Write-ColorText " | || | | | | |_| |_| |" $Blue
Write-ColorText "|___|_| |_|_|\__|\__, |" $Blue
Write-ColorText "                 |___/ " $Blue

Write-Host ""
Write-ColorText "Inity - Intelligent Python Project Setup Tool" $Purple
Write-ColorText "Developed by Aathish at Strucureo" $Cyan
Write-Host "=================================================="

Write-ColorText "Detecting system..." $Blue
Write-Host "OS: Windows"
Write-Host ("PowerShell: " + $PSVersionTable.PSVersion)

# Check if Python is available
try {
    $pythonVersion = & python --version 2>&1
    Write-ColorText ("Python found: " + $pythonVersion) $Green
} catch {
    Write-ColorText "Python is not installed or not in PATH" $Red
    Write-Host "Please install Python 3.8+ from https://python.org"
    Write-Host "Make sure to check Add Python to PATH during installation"
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = & pip --version 2>&1
    Write-ColorText ("pip found: " + $pipVersion) $Green
} catch {
    Write-ColorText "pip is not installed" $Red
    Write-Host "Please install pip first"
    Read-Host "Press Enter to exit"
    exit 1
}

# Create temporary directory
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
Set-Location $tempDir

Write-ColorText "Downloading Inity..." $Blue

# Download Inity
try {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "Using git to clone repository..."
        & git clone https://github.com/theaathish/Inity.git
        Set-Location Inity
    } else {
        Write-Host "Downloading as zip archive..."
        $zipPath = Join-Path $tempDir "inity.zip"
        Invoke-WebRequest -Uri "https://github.com/theaathish/Inity/archive/main.zip" -OutFile $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $tempDir
        Set-Location "Inity-main"
    }
} catch {
    Write-ColorText ("Failed to download Inity: " + $_.Exception.Message) $Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-ColorText "Installing Inity..." $Blue

try {
    # Create isolated virtual environment for Inity on Windows
    Write-Host "Creating isolated virtual environment for Inity..."
    $inityVenv = Join-Path $env:LOCALAPPDATA "inity-venv"
    
    # Remove existing venv if it exists
    if (Test-Path $inityVenv) {
        Remove-Item $inityVenv -Recurse -Force
    }
    
    # Create new virtual environment
    & python -m venv $inityVenv
    
    # Get the correct paths for the virtual environment
    $venvPython = Join-Path $inityVenv "Scripts\python.exe"
    $venvPip = Join-Path $inityVenv "Scripts\pip.exe"
    
    # Install in the virtual environment
    Write-Host "Installing dependencies in virtual environment..."
    & $venvPip install --upgrade pip
    & $venvPip install -r requirements.txt
    & $venvPip install .
    
    # Create wrapper batch file in user directory
    $batchContent = "@echo off" + [Environment]::NewLine + "`"$venvPython`" -m smartenv.main %*"
    
    $userPath = [Environment]::GetFolderPath('UserProfile')
    $batchPath = Join-Path $userPath "inity.bat"
    $batchContent | Out-File -FilePath $batchPath -Encoding ASCII
    
    Write-ColorText "Inity installed successfully!" $Green
    
} catch {
    Write-ColorText ("Installation failed: " + $_.Exception.Message) $Red
    Write-Host "Error details: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Manual installation instructions:"
    Write-Host "1. Install Python from https://python.org"
    Write-Host "2. Open Command Prompt and run:"
    Write-Host "   git clone https://github.com/theaathish/Inity.git"
    Write-Host "   cd Inity"
    Write-Host "   python -m venv .venv"
    Write-Host "   .venv\Scripts\activate"
    Write-Host "   pip install -r requirements.txt"
    Write-Host "   pip install ."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-ColorText "Inity installed successfully!" $Green
Write-Host ""

Write-ColorText ("Created launcher: " + $batchPath) $Blue
Write-ColorText "To use inity from anywhere add this to your PATH:" $Yellow
Write-Host "  1. Open Environment Variables settings"
Write-Host ("  2. Add " + $userPath + " to your PATH")
Write-Host ("  3. Or use full path: " + $batchPath)
Write-Host ""

Write-ColorText "Quick Start:" $Cyan
Write-Host "  inity --help                    # Show help"
Write-Host "  inity create my-awesome-project # Create new project"
Write-Host "  inity package search fastapi    # Search packages"
Write-Host ""

Write-ColorText "Documentation: https://github.com/theaathish/Inity" $Purple
Write-ColorText "Issues: https://github.com/theaathish/Inity/issues" $Purple
Write-Host ""

# Test installation
Write-ColorText "Testing installation..." $Blue
try {
    $testOutput = & $batchPath --version 2>&1
    Write-ColorText ("Inity is ready to use! " + $testOutput) $Green
} catch {
    Write-ColorText "Installation completed but test failed" $Yellow
    Write-Host "You may need to restart your command prompt"
}

# Cleanup
Set-Location $env:TEMP
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-ColorText "Happy coding with Inity!" $Cyan
Write-Host ""
Write-Host "Installation complete. Press Enter to continue..."
Read-Host
