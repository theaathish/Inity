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
    exit 1
}

# Check if pip is available
try {
    $pipVersion = & pip --version 2>&1
    Write-ColorText ("pip found: " + $pipVersion) $Green
} catch {
    Write-ColorText "pip is not installed" $Red
    Write-Host "Please install pip first"
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
    exit 1
}

Write-ColorText "Installing Inity..." $Blue

try {
    # Install dependencies and Inity
    & pip install --user -r requirements.txt
    & pip install --user -e .
    
    Write-ColorText "Inity installed successfully!" $Green
} catch {
    Write-ColorText ("Installation failed: " + $_.Exception.Message) $Red
    exit 1
}

# Create batch file for easier access
$batchContent = "@echo off" + [Environment]::NewLine + "python -m smartenv.main %*"

$userPath = [Environment]::GetFolderPath('UserProfile')
$batchPath = Join-Path $userPath "inity.bat"
$batchContent | Out-File -FilePath $batchPath -Encoding ASCII

Write-Host ""
Write-ColorText "Inity installed successfully!" $Green
Write-Host ""

Write-ColorText ("Created batch file: " + $batchPath) $Blue
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
    & python -m smartenv.main --version
    Write-ColorText "Inity is ready to use!" $Green
} catch {
    Write-ColorText "Installation completed but test failed" $Yellow
    Write-Host "You may need to restart your command prompt"
}

# Cleanup
Set-Location $env:TEMP
Remove-Item $tempDir -Recurse -Force

Write-Host ""
Write-ColorText "Happy coding with Inity!" $Cyan
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
